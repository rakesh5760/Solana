from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import solana_engine as engine
import pandas as pd

app = FastAPI(title="Solana Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_address(
    address: str = Body(..., embed=True),
    start_date: str = Body(..., embed=True),
    end_date: str = Body(..., embed=True)
):
    """
    Main endpoint to analyze a Solana address.
    Expects address, start_date, and end_date in 'YYYY-MM-DD HH:MM' format.
    """
    if not address:
        raise HTTPException(status_code=400, detail="Address is required")

    # 1. Check if already in DB
    already_in_db = engine.is_address_in_main_db(address)
    
    # 2. Convert dates to Unix
    try:
        start_ts = engine.dt_str_to_unix_utc(start_date)
        end_ts = engine.dt_str_to_unix_utc(end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")

    # 3. Get signatures and classify
    try:
        sign_entries = engine.get_signatures_in_range(address, start_ts, end_ts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching signatures: {e}")

    count = len(sign_entries)
    label = engine.classify_from_count(count)

    # 4. Save classification to DB
    try:
        engine.append_to_address_type_db(address, start_date, end_date, count, label)
    except Exception as e:
        print(f"Warning: Could not save to DB: {e}")

    result = {
        "address": address,
        "classification": label,
        "transactionCount": count,
        "alreadyInDB": already_in_db,
        "data": {
            "transactions": [],
            "transfers": [],
            "defi": [],
            "nft": []
        }
    }

    # 5. If not exchange, fetch enriched data
    if label == "not a exchange":
        enriched_txs = engine.get_enriched_transactions_for_signatures(sign_entries)
        
        if enriched_txs:
            result["data"]["transactions"] = engine.build_transactions_list(enriched_txs, address)
            result["data"]["transfers"] = engine.build_transfers_list(enriched_txs, address)
            result["data"]["defi"] = engine.build_defi_list(enriched_txs, address)
            result["data"]["nft"] = engine.build_nft_list(enriched_txs, address)
            
            # Save to Active DB
            try:
                engine.map_and_save_active_db(address, start_date, end_date, result["data"])
            except Exception as e:
                print(f"Warning: Could not save to Active DB: {e}")

    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
