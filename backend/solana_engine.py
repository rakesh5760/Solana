import os
import time as pytime
from datetime import datetime, date, time as dtime, timezone
from typing import List, Dict, Any, Optional

import pandas as pd
import requests

# --------------------------------------------------
# CONFIG – Helius + Excel
# --------------------------------------------------
HELIUS_API_KEY = "e55a9037-16cd-4a90-84a8-1ddc17caac79"
HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
ENHANCED_TX_URL = f"https://api.helius.xyz/v0/transactions?api-key={HELIUS_API_KEY}"

MAX_PAGES = 100
PAGE_LIMIT = 1000
LAMPORTS_PER_SOL = 1_000_000_000
EXCEL_FILE = "address classifier.xlsx"

ACTIVE_DB_DEFAULT_COLUMNS = [
    "Address", "Chain", "Date of Retrival", "From Date", "To Date", "Type Tx", 
    "Signature", "block", "time", "action", "from", "to", "by", "value(sol)", 
    "value $", "amount( amount of token)", "fee", "program", "token", 
    "platform", "source", "nft", "Price", "collection", "marketplace",
]

# --------------------------------------------------
# Helper functions
# --------------------------------------------------
def combine_date_time_to_str(d: date, t: dtime) -> str:
    dt = datetime(d.year, d.month, d.day, t.hour, t.minute)
    return dt.strftime("%Y-%m-%d %H:%M")

def dt_str_to_unix_utc(dt_str: str) -> int:
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())

def unix_to_str_utc(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def format_relative_time(ts: Optional[int]) -> str:
    if not ts: return ""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60: return f"{seconds}s ago"
    minutes = seconds // 60
    if minutes < 60: return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24: return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"

def safe_float(x: Any) -> Optional[float]:
    if x is None: return None
    try: return float(x)
    except Exception: return None

# --------------------------------------------------
# Core Logic
# --------------------------------------------------
def get_signatures_in_range(address: str, start_ts: int, end_ts: int) -> List[Dict[str, Any]]:
    collected: List[Dict[str, Any]] = []
    before: Optional[str] = None
    pages = 0
    finished_by_time = False

    while True:
        if MAX_PAGES and pages >= MAX_PAGES: break
        pages += 1
        params_obj = {"limit": PAGE_LIMIT}
        if before: params_obj["before"] = before
        payload = {"jsonrpc": "2.0", "id": 1, "method": "getSignaturesForAddress", "params": [address, params_obj]}
        resp = requests.post(HELIUS_RPC_URL, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json().get("result", [])
        if not result: break
        for entry in result:
            block_time = entry.get("blockTime")
            if block_time is None: continue
            if block_time >= end_ts: continue
            if block_time < start_ts:
                finished_by_time = True
                break
            collected.append(entry)
        if finished_by_time: break
        before = result[-1]["signature"]
    return collected

def classify_from_count(count: int) -> str:
    return "not a exchange" if count <= 15 else "exchange"

def is_address_in_main_db(address: str) -> bool:
    if not os.path.exists(EXCEL_FILE): return False
    try: df = pd.read_excel(EXCEL_FILE, sheet_name="Address Type DB")
    except ValueError: return False
    if "Address" not in df.columns: return False
    return df["Address"].astype(str).eq(str(address)).any()

def append_to_address_type_db(address: str, from_dt: str, to_dt: str, count: int, label: str):
    row = {"Address": address, "From": from_dt, "To": to_dt, "Count": count, "Exchange / ! Exchange": label}
    new_df = pd.DataFrame([row])
    if os.path.exists(EXCEL_FILE):
        try: existing = pd.read_excel(EXCEL_FILE, sheet_name="Address Type DB")
        except ValueError: existing = pd.DataFrame(columns=new_df.columns)
        for col in new_df.columns:
            if col not in existing.columns: existing[col] = None
        updated = pd.concat([existing, new_df], ignore_index=True)
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            updated.to_excel(writer, sheet_name="Address Type DB", index=False)
    else:
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            new_df.to_excel(writer, sheet_name="Address Type DB", index=False)

def get_enriched_transactions_for_signatures(sign_entries: List[Dict[str, Any]], batch_size: int = 100) -> List[Dict[str, Any]]:
    all_txs: List[Dict[str, Any]] = []
    signatures = [e.get("signature") for e in sign_entries if e.get("signature")]
    for i in range(0, len(signatures), batch_size):
        batch = signatures[i:i + batch_size]
        if not batch: continue
        body = {"transactions": batch}
        try:
            resp = requests.post(ENHANCED_TX_URL, json=body, timeout=30)
            resp.raise_for_status()
        except requests.RequestException: continue
        data = resp.json()
        if isinstance(data, list): all_txs.extend(data)
        pytime.sleep(0.05)
    return all_txs

# --------------------------------------------------
# Data Formatters (returning lists of dicts for API)
# --------------------------------------------------
def build_transactions_list(txs: List[dict], main_address: str) -> List[Dict[str, Any]]:
    rows = []
    for tx in txs:
        sig = tx.get("signature", "")
        block = tx.get("slot") or tx.get("slotNumber") or tx.get("blockNumber")
        ts = tx.get("timestamp") or tx.get("blockTime")
        time_rel = format_relative_time(ts)
        events = tx.get("events") or {}
        has_nft = bool(events.get("nft"))
        has_defi = any(k.lower() != "nft" for k in events.keys())
        has_transfers = bool(tx.get("nativeTransfers") or tx.get("tokenTransfers"))

        if has_defi: action = "DeFi"
        elif has_nft: action = "NFT"
        elif has_transfers: action = "Transfer"
        else: action = "System"

        by_addr = tx.get("feePayer")
        if not by_addr:
            acc_data = tx.get("accountData") or []
            if acc_data: by_addr = acc_data[0].get("account")

        fee_lamports = tx.get("fee")
        if fee_lamports is None:
            meta = tx.get("meta") or {}
            fee_lamports = meta.get("fee")
        fee_sol = (fee_lamports / LAMPORTS_PER_SOL) if fee_lamports is not None else None

        value_sol = None
        for acc in tx.get("accountData") or []:
            if acc.get("account") == main_address:
                native_change_lamports = acc.get("nativeBalanceChange") or 0
                native_change_sol = abs(native_change_lamports) / LAMPORTS_PER_SOL
                if native_change_sol > 0: value_sol = native_change_sol
                break
        if value_sol is None:
            total_value_sol = 0.0
            for nt in tx.get("nativeTransfers") or []:
                from_acc = nt.get("fromUserAccount"); to_acc = nt.get("toUserAccount")
                amt_sol = (nt.get("amount") or 0) / LAMPORTS_PER_SOL
                if from_acc == main_address or to_acc == main_address: total_value_sol += abs(amt_sol)
            if total_value_sol > 0: value_sol = total_value_sol
        if value_sol is None and by_addr == main_address and fee_sol is not None: value_sol = abs(fee_sol)

        programs = set()
        for ev in events.values():
            ev_list = ev if isinstance(ev, list) else [ev]
            for e in ev_list:
                if isinstance(e, dict):
                    for key in ("programId", "program", "source", "protocol"):
                        val = e.get(key)
                        if isinstance(val, str): programs.add(val)
        programs_str = ", ".join(sorted(programs)) if programs else ""

        rows.append({
            "signature": sig, "block": block, "time": time_rel, "action": action,
            "by": by_addr or "", "value": round(value_sol, 8) if value_sol is not None else None,
            "fee": round(fee_sol, 8) if fee_sol is not None else None, "programs": programs_str
        })
    return rows

def build_transfers_list(txs: List[dict], main_address: str) -> List[Dict[str, Any]]:
    rows = []
    for tx in txs:
        sig = tx.get("signature", ""); ts = tx.get("timestamp") or tx.get("blockTime")
        time_rel = format_relative_time(ts)
        for nt in tx.get("nativeTransfers") or []:
            from_acc = nt.get("fromUserAccount"); to_acc = nt.get("toUserAccount")
            if main_address not in (from_acc, to_acc): continue
            amt_sol = (nt.get("amount") or 0) / LAMPORTS_PER_SOL
            if from_acc == main_address and to_acc == main_address: action = "Self Transfer"; signed_amt = 0.0
            elif from_acc == main_address: action = "Send"; signed_amt = -amt_sol
            else: action = "Receive"; signed_amt = amt_sol
            rows.append({
                "signature": sig, "time": time_rel, "action": action, "from": from_acc, "to": to_acc,
                "amount": round(signed_amt, 8), "value": round(abs(signed_amt), 8), "token": "SOL"
            })
        for tt in tx.get("tokenTransfers") or []:
            from_acc = tt.get("fromUserAccount"); to_acc = tt.get("toUserAccount")
            if main_address not in (from_acc, to_acc): continue
            amt = safe_float(tt.get("tokenAmount"))
            if from_acc == main_address and to_acc == main_address: action = "Self Transfer"; signed_amt = 0.0
            elif from_acc == main_address: action = "Send"; signed_amt = -amt if amt is not None else 0
            else: action = "Receive"; signed_amt = amt if amt is not None else 0
            rows.append({
                "signature": sig, "time": time_rel, "action": action, "from": from_acc, "to": to_acc,
                "amount": round(signed_amt, 8), "value": round(abs(signed_amt), 8), "token": tt.get("mint") or "TOKEN"
            })
    return rows

def build_defi_list(txs: List[dict], main_address: str) -> List[Dict[str, Any]]:
    rows = []
    for tx in txs:
        sig = tx.get("signature", ""); ts = tx.get("timestamp") or tx.get("blockTime")
        time_rel = format_relative_time(ts); events = tx.get("events") or {}
        for key, ev in events.items():
            if key.lower() == "nft": continue
            ev_list = ev if isinstance(ev, list) else [ev]
            for e in ev_list:
                if not isinstance(e, dict): continue
                action = e.get("type") or key.upper()
                from_addr = e.get("userAccount") or e.get("user") or e.get("owner") or e.get("trader") or main_address
                amount = None; value = None; platform = e.get("protocol") or e.get("platform")
                source = e.get("source") or e.get("program") or e.get("programId")
                if key == "swap":
                    native_in = e.get("nativeInput")
                    if isinstance(native_in, dict):
                        lamports = safe_float(native_in.get("amount"))
                        if lamports is not None:
                            amount = lamports / LAMPORTS_PER_SOL; value = amount
                            from_addr = native_in.get("account") or from_addr
                    if amount is None:
                        token_inputs = e.get("tokenInputs") or []
                        if token_inputs:
                            ti = token_inputs[0]; from_addr = ti.get("userAccount") or from_addr
                            raw = ti.get("rawTokenAmount") or {}; raw_amt = raw.get("tokenAmount")
                            decimals = raw.get("decimals") or 0
                            if raw_amt is not None:
                                try: amount = float(raw_amt) / (10 ** decimals)
                                except: pass
                    inner_swaps = e.get("innerSwaps") or []
                    if inner_swaps:
                        info = (inner_swaps[0] or {}).get("programInfo") or {}
                        platform = platform or info.get("programName") or info.get("source")
                        source = source or info.get("source")
                if amount is None: amount = e.get("amountIn") or e.get("amount")
                if value is None: value = e.get("amountInSol") or e.get("value")
                rows.append({
                    "signature": sig, "time": time_rel, "action": action, "from": from_addr,
                    "amount": round(safe_float(amount) or 0, 8), "value": round(safe_float(value) or 0, 8),
                    "platform": platform or "", "source": source or ""
                })
    return rows

def build_nft_list(txs: List[dict], main_address: str) -> List[Dict[str, Any]]:
    rows = []
    for tx in txs:
        sig = tx.get("signature", ""); ts = tx.get("timestamp") or tx.get("blockTime")
        time_rel = format_relative_time(ts); events = tx.get("events") or {}
        nft_ev = events.get("nft")
        if not nft_ev: continue
        ev_list = nft_ev if isinstance(nft_ev, list) else [nft_ev]
        for e in ev_list:
            if not isinstance(e, dict): continue
            price = safe_float(e.get("amountInSol") or e.get("price"))
            rows.append({
                "signature": sig, "time": time_rel, "action": e.get("type") or "NFT",
                "nftName": e.get("nftName") or e.get("name") or e.get("mint") or "",
                "price": round(price, 8) if price is not None else 0,
                "from": e.get("from") or e.get("seller") or "", "to": e.get("to") or e.get("buyer") or "",
                "collection": e.get("collection") or e.get("collectionName") or "",
                "marketplace": e.get("marketplace") or e.get("platform") or ""
            })
    return rows

# --------------------------------------------------
# Active DB logic
# --------------------------------------------------
def get_active_db_columns() -> List[str]:
    if os.path.exists(EXCEL_FILE):
        try:
            xls = pd.ExcelFile(EXCEL_FILE)
            if "Active DB" in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name="Active DB")
                if not df.empty: return list(df.columns)
        except: pass
    return ACTIVE_DB_DEFAULT_COLUMNS[:]

def append_to_active_db(new_rows: pd.DataFrame):
    cols = get_active_db_columns()
    for c in cols:
        if c not in new_rows.columns: new_rows[c] = None
    new_rows = new_rows[cols]
    if os.path.exists(EXCEL_FILE):
        xls = pd.ExcelFile(EXCEL_FILE)
        sheets = {name: pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names}
        existing = sheets.get("Active DB")
        if existing is None: existing = pd.DataFrame(columns=cols)
        else:
            for c in cols:
                if c not in existing.columns: existing[c] = None
            existing = existing[cols]
        combined = pd.concat([existing, new_rows], ignore_index=True)
        sheets["Active DB"] = combined
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            for name, df_sheet in sheets.items():
                df_sheet.to_excel(writer, sheet_name=name, index=False)
    else:
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            new_rows.to_excel(writer, sheet_name="Active DB", index=False)

def map_and_save_active_db(address: str, from_dt: str, to_dt: str, tx_data: Dict[str, List[Dict[str, Any]]]):
    cols = get_active_db_columns()
    today = datetime.now().strftime("%Y-%m-%d")
    all_rows = []
    
    mapping = {
        "transactions": ("transaction", {"signature": 6, "block": 7, "time": 8, "action": 9, "by": 12, "value": 13, "fee": 16, "programs": 17}),
        "transfers": ("transfer", {"signature": 6, "time": 8, "action": 9, "from": 10, "to": 11, "value": 14, "amount": 15, "token": 18}),
        "defi": ("defiactivity", {"signature": 6, "time": 8, "action": 9, "from": 10, "value": 14, "amount": 15, "platform": 19, "source": 20}),
        "nft": ("nftactivity", {"signature": 6, "time": 8, "action": 9, "from": 10, "to": 11, "nftName": 21, "price": 22, "collection": 23, "marketplace": 24})
    }
    
    for key, (type_val, fields) in mapping.items():
        for r in tx_data.get(key, []):
            row = {c: None for c in cols}
            row[cols[0]] = address; row[cols[1]] = "solana"; row[cols[2]] = today
            row[cols[3]] = from_dt; row[cols[4]] = to_dt; row[cols[5]] = type_val
            for f_key, col_idx in fields.items():
                row[cols[col_idx]] = r.get(f_key)
            all_rows.append(row)
    
    if all_rows:
        append_to_active_db(pd.DataFrame(all_rows))
        return len(all_rows)
    return 0
