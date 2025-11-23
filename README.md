# Stock Tracker & Forecasting Dashboard

A full-stack application for downloading, storing, analyzing, and forecasting stock prices with sentiment analysis. The backend is built with FastAPI (Python), and the frontend is built with React and Chakra UI.

---

## Features

- **Download Historical Stock Data:** Fetches data using Yahoo Finance and stores it in a local SQLite database.
- **Sentiment Analysis:** Integrates sentiment scores for each ticker (extendable for your own sentiment pipeline).
- **Technical Analysis:** Computes indicators like RSI, MACD, and SMAs using `pandas_ta`.
- **Forecasting:** Uses Facebook Prophet to predict future prices (1 month, 1 year, 5 years, 10 years).
- **Interactive Frontend:** Users can enter a ticker, see a progress bar, and view all generated graphs in a modern UI.
- **REST API:** Backend exposes endpoints for analysis and graph retrieval.

---

## Project Structure

```
backend/
  app/
    analysis.py           # Orchestrates analysis and plotting
    analyze_and_predict.py# Technical analysis & Prophet forecasting
    analyze_sentiment.py  # (Optional) Sentiment pipeline
    database.py           # DB access helpers
    download_data.py      # Downloads and stores stock data
    main.py               # FastAPI entrypoint
    sentiment.py          # Forecasting helpers
    config.json           # Tickers config
    stocks.db             # SQLite database
frontend/
  public/
    index.html
  src/
    App.js                # Main React app
    index.js              # Entry point
  package.json
requirements.txt          # Backend Python dependencies
```

---

## Setup Instructions

### 1. Clone the Repository
```sh
git clone https://github.com/VaidikTrivedi/Stock-Analysis.git
cd Stock-Tracker
```

### 2. Backend Setup (FastAPI)

#### a. Create a Python virtual environment (recommended)
```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

#### b. Install dependencies
```sh
pip install -r backend/requirements.txt
```

#### c. Download stock data
Edit `backend/app/config.json` to add your tickers, then run:
```sh
cd backend/app
python download_data.py
```

#### d. Start the backend server
```sh
cd backend/app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup (React + Chakra UI)

#### a. Install dependencies
```sh
cd frontend
npm install
```

#### b. Start the frontend
```sh
npm start
```

The app will be available at [http://localhost:3000](http://localhost:3000)

---

## Usage

1. **Enter a Ticker:**
   - On the web UI, enter a stock ticker (e.g., `AAPL`, `NVDA`) and click "Analyze".
2. **Processing:**
   - A progress spinner will show while the backend fetches, analyzes, and forecasts the data.
3. **View Results:**
   - Forecast graphs for 1-Month, 1-Year, 5-Year, and 10-Year intervals will be displayed.
   - Historical prices are shown in blue; predicted prices are green (upward trend) or red (downward trend).
   - You can switch between forecast intervals using tabs.

---

## API Endpoints

- `POST /analyze`  
  Request: `{ "ticker": "AAPL" }`  
  Response: JSON with forecast data and plot IDs.

- `GET /graph/{plot_id}`  
  Returns: PNG image of the requested forecast graph.

---

## Customization & Extending

- **Add More Technical Indicators:** Edit `analyze_and_predict.py`.
- **Change/Extend Sentiment Analysis:** Add your own logic in `analyze_sentiment.py` and integrate with the DB.
- **Change Forecasting Model:** Swap Prophet for another model in `sentiment.py` and `analyze_and_predict.py`.
- **UI Enhancements:** Edit `frontend/src/App.js` and use Chakra UI components for more features.

---

## Troubleshooting

- **Blank Graphs:** Ensure matplotlib uses the 'Agg' backend (already set in code).
- **Import Errors:** All imports are now absolute or sys.path-patched for direct script execution.
- **Database Issues:** Make sure `stocks.db` exists and is populated by running `download_data.py`.

---

## License
MIT (or your preferred license)

---

## Credits
- [yfinance](https://github.com/ranaroussi/yfinance)
- [pandas_ta](https://github.com/twopirllc/pandas-ta)
- [Prophet](https://facebook.github.io/prophet/)
- [Chakra UI](https://chakra-ui.com/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

## Disclaimer
This project is for educational purposes only. Stock market prediction is highly speculative and not suitable for financial decision-making. Use at your own risk.
