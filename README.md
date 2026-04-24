# Solana Address Analyzer (FastAPI + React)

A professional-grade Solana blockchain wallet analysis tool featuring a modern React frontend and a high-performance FastAPI backend.

## 📁 Project Structure

```
solana/
├── backend/            # Python FastAPI backend
│   ├── .env            # Configuration & API Keys
│   ├── main.py         # API entry point
│   ├── solana_engine.py # Core analysis logic
│   └── legacy/         # Original Streamlit implementation (Reference)
├── frontend/           # React + Vite frontend
│   ├── src/            # App source code
│   └── .env.local      # Frontend configuration
└── address classifier.xlsx # Persistent Excel database
```

## ✨ Features

- **Automated Classification**: Automatically identifies addresses as "Exchange" or "Private Wallet" based on activity volume.
- **Enriched Analysis**: Extracted detailed data for DeFi, NFT, and Transfer activities using Helius API.
- **Excel Integration**: Persistent storage of analysis results in a structured XLSX format.
- **Modern UI**: Figma-inspired design with real-time data visualization and activity tabs.
- **Production Ready**: Full environment variable support, CORS security, and structured logging.

## 🚀 Getting Started

### 1. Backend Setup
1. Navigate to `backend/`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Create a `.env` file (copy from `.env.example`).
4. Add your `HELIUS_API_KEY`.
5. Start the server: `python main.py`.

### 2. Frontend Setup
1. Navigate to `frontend/`.
2. Install dependencies: `npm install`.
3. Start the dev server: `npm run dev`.
4. Open `http://localhost:5173` in your browser.

## ⚙️ Configuration

- **Backend**: Configure `PORT` and `ALLOW_ORIGINS` in `backend/.env`.
- **Frontend**: Configure `VITE_API_URL` in `frontend/.env.local`.

## 📝 Notes

- Ensure the `address classifier.xlsx` file is not open in Excel while the backend is running to avoid permission errors.
- The `legacy/` folder contains the original Streamlit wrapper for backward compatibility and logic verification.

---
*Created by Antigravity AI Coding Assistant*
