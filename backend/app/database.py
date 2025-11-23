# Place your database loading and utility functions here
import sqlite3
import pandas as pd

def load_data_from_db(ticker):
    conn = sqlite3.connect('stocks.db')
    prices_df = pd.read_sql_query(
        f"SELECT * FROM stock_prices WHERE Ticker = '{ticker}'", 
        conn, 
        parse_dates=['Date']
    )

    prices_df.set_index('Date', inplace=True)
    sentiment_df = pd.read_sql_query(
        f"SELECT * FROM sentiment_scores WHERE ticker = '{ticker}'", 
        conn,
        parse_dates=['Date']
    )
    sentiment_df.set_index('Date', inplace=True)
    conn.close()
    if prices_df.empty:
        return None
    combined_df = prices_df.join(sentiment_df.drop('Ticker', axis=1))
    combined_df['Sentiment'] = combined_df['Sentiment'].fillna(0)
    return combined_df.reset_index()
