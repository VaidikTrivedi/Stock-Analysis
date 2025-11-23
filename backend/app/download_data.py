import yfinance as yf
import pandas as pd
import sqlite3
import json
from datetime import datetime

def load_tickers():
    """Reads the config.json file and returns a unique set of all tickers."""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Combine both lists and remove duplicates by converting to a set
    all_tickers = set(config['purchased_stocks']) | set(config['watchlist'])
    return list(all_tickers)

def init_database():
    """Creates the database and the 'stock_prices' table if it doesn't exist."""
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    
    # We use 'IF NOT EXISTS' to avoid errors on subsequent runs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_prices (
        Date TEXT,
        Open REAL,
        High REAL,
        Low REAL,
        Close REAL,
        "Adj Close" REAL,
        Volume INTEGER,
        Ticker TEXT,
        PRIMARY KEY (Date, Ticker) 
    )
    ''')
    conn.commit()
    return conn

def fetch_and_store_data(conn, tickers):
    """
    Fetches historical data for each ticker and stores it in the SQLite database.
    """
    cursor = conn.cursor()
    
    for ticker in tickers:
        try:
            print(f"--- Fetching data for {ticker} ---")
            
            # Download historical data from yfinance
            # 'period="max"' gets all available data
            stock_data = yf.download(ticker, period="max")
            
            if stock_data.empty: # type: ignore
                print(f"Could not find data for {ticker}. Skipping.")
                continue
                
            # Add the ticker symbol as a column for storage
            stock_data['Ticker'] = ticker # type: ignore
            
            # Reset the index to turn the 'Date' (which is the index) into a column
            stock_data.reset_index(inplace=True) # type: ignore
            
            # Convert Date to string format for SQLite compatibility
            stock_data['Date'] = stock_data['Date'].dt.strftime('%Y-%m-%d') # type: ignore
            
            # Ensure columns are in the correct order and all present
            columns_needed = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ticker']
            stock_data = stock_data[columns_needed] # type: ignore
            
            # Use 'executemany' for efficient batch insertion
            # 'OR IGNORE' skips duplicate entries (based on the PRIMARY KEY)
            tuples_to_insert = [tuple(row) for row in stock_data.to_numpy()]
            cursor.executemany('''
            INSERT OR IGNORE INTO stock_prices (
                Date, Open, High, Low, Close, Volume, Ticker
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', tuples_to_insert)
            
            conn.commit()
            print(f"Successfully stored data for {ticker}.")
            
        except Exception as e:
            print(f"Error fetching/storing {ticker}: {e}")

def main():
    tickers = load_tickers()
    conn = init_database()
    fetch_and_store_data(conn, tickers)
    conn.close()
    print("\nData download complete.")

if __name__ == "__main__":
    main()