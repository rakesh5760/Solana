#!/usr/bin/env python3
"""
Streamlit wrapper for Solana Address Classifier.
Refactored to use solana_engine.py for core logic.
"""
import streamlit as st
import requests
import pandas as pd
from datetime import date, time as dtime
import solana_engine as engine

# --------------------------------------------------
# Streamlit App UI
# --------------------------------------------------
st.set_page_config(page_title="Solana Address Classifier + Enriched Viewer", layout="wide")
st.title("Solana Address Classifier + Enriched Activity (Helius)")

if not engine.HELIUS_API_KEY or "YOUR_HELIUS_API_KEY_HERE" in engine.HELIUS_API_KEY:
    st.error("Please set HELIUS_API_KEY in solana_engine.py.")
    st.stop()

address = st.text_input("Solana Address", help="Wallet or account address")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date")
    start_time = st.time_input("Start Time", value=dtime(0, 0))
with col2:
    end_date = st.date_input("End Date")
    end_time = st.time_input("End Time", value=dtime(23, 59))

if st.button("Analyze Address"):
    if not address:
        st.error("Please enter an address.")
        st.stop()

    if engine.is_address_in_main_db(address):
        st.warning("This address is already available in the main DB.")
        st.stop()

    start_dt_str = engine.combine_date_time_to_str(start_date, start_time)
    end_dt_str = engine.combine_date_time_to_str(end_date, end_time)

    start_ts = engine.dt_str_to_unix_utc(start_dt_str)
    end_ts = engine.dt_str_to_unix_utc(end_dt_str)

    st.write(f"**Start (UTC):** {start_dt_str} → `{start_ts}`")
    st.write(f"**End (UTC):** {end_dt_str} → `{end_ts}`")

    # STEP 1: count & classify
    with st.spinner("Counting transactions in this range..."):
        try:
            sign_entries = engine.get_signatures_in_range(address, start_ts, end_ts)
        except requests.RequestException as e:
            st.error(f"Error calling getSignaturesForAddress: {e}")
            st.stop()

    count = len(sign_entries)
    label = engine.classify_from_count(count)

    st.subheader("Classification Summary")
    c1, c2 = st.columns(2)
    with c1: st.metric("Transactions in Range", count)
    with c2: st.metric("Label", label)

    try:
        engine.append_to_address_type_db(address, start_dt_str, end_dt_str, count, label)
        st.success("Appended to sheet 'Address Type DB'.")
    except Exception as e:
        st.warning(f"Could not append to 'Address Type DB': {e}")

    if label == "exchange":
        st.info("Address classified as 'exchange'. Skipping detailed enriched activity.")
        st.stop()

    # STEP 2: NOT exchange => fetch enriched data
    st.info("Address classified as 'not a exchange'. Fetching enriched activity...")
    with st.spinner("Fetching enriched transactions..."):
        enriched_txs = engine.get_enriched_transactions_for_signatures(sign_entries)

    st.write(f"Enriched transactions fetched: **{len(enriched_txs)}**")
    if not enriched_txs:
        st.warning("No enriched data found for these transactions.")
        st.stop()

    tx_data = {
        "transactions": engine.build_transactions_list(enriched_txs, address),
        "transfers": engine.build_transfers_list(enriched_txs, address),
        "defi": engine.build_defi_list(enriched_txs, address),
        "nft": engine.build_nft_list(enriched_txs, address)
    }

    tab_tx, tab_tr, tab_def, tab_nf = st.tabs(["Transactions", "Transfers", "DeFi Activities", "NFT Activities"])
    
    with tab_tx: st.subheader("Transactions"); st.dataframe(pd.DataFrame(tx_data["transactions"]), use_container_width=True)
    with tab_tr: st.subheader("Transfers"); st.dataframe(pd.DataFrame(tx_data["transfers"]), use_container_width=True)
    with tab_def: st.subheader("DeFi Activities"); st.dataframe(pd.DataFrame(tx_data["defi"]), use_container_width=True)
    with tab_nf: st.subheader("NFT Activities"); st.dataframe(pd.DataFrame(tx_data["nft"]), use_container_width=True)

    # STEP 3: push to Active DB
    try:
        msg = f"Appended {engine.map_and_save_active_db(address, start_dt_str, end_dt_str, tx_data)} rows to sheet 'Active DB'."
        st.success(msg)
    except Exception as e:
        st.warning(f"Could not append to 'Active DB': {e}")
