# Solana Address Classifier & Activity Extractor

This project is a Streamlit application that analyzes Solana wallet addresses and extracts activity using the Helius API.

---

## 📁 Project Structure

```
project-folder/
│
├─ app.py                     # Main Streamlit application
│
└─ address classifier.xlsx    # Excel database with 3 sheets:
   ├─ Address Type DB         # Address + classification
   ├─ Archival DB             # Reserved for future expansion
   └─ Active DB               # Flattened enriched activity
```

---

## ✨ Core Features

* Count transactions in a given date/time range
* Classify addresses:

  * `exchange` (> 15 tx)
  * `not a exchange` (<= 15 tx)
* Prevent duplicate entries in the database
* Fetch enriched blockchain activity for non-exchange addresses:

  * Transactions
  * Transfers
  * DeFi Activities
  * NFT Activities
* Display results inside Streamlit UI (tabs)
* Append normalized data into Excel without overwriting existing content

---

## 🧪 Output Flow

### 1) Existing Address

If the address already exists in **Address Type DB**, the app stops and shows:

```
This address is already available in the main DB.
```

### 2) New Address

1. Count transactions
2. Classify as exchange / not exchange
3. Append classification row to **Address Type DB**

### 3) Address = "exchange"

```
Address classified as 'exchange'. Skipping detailed enriched activity.
```

### 4) Address = "not a exchange"

* Fetch enriched data
* Display in UI tabs
* Append flattened rows to **Active DB**

Example UI message:

```
Appended 42 rows to sheet 'Active DB'.
```

---

## 🔑 Requirements

* Python 3.9+
* Valid Helius API key
* Dependencies listed in `requirements.txt`

---

## ⚙️ Installation

Install dependencies:

```
pip install -r requirements.txt
```

---

## ▶️ Run the App

From the project folder:

```
streamlit run app.py
```

---

## 📝 Notes

* Free Helius API limits apply
* The app only analyzes transactions within the selected date/time range
* Excel file is persistent and updated incrementally
* Existing sheets are preserved without overwrite

---

## 📌 Summary

This application helps you:

* Analyze Solana addresses
* Classify behavior
* Extract enriched blockchain activity
* Store everything in a structured Excel database

---

## 🚀 Optional Improvements

* Add screenshots
* Docker support
* Data export dashboard
* Database backend instead of Excel
