import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import sqlite3
import json
from datetime import datetime

def load_tickers():
    """Reads the config.json file and returns a unique set of all tickers."""
    with open('config.json', 'r') as f:
        config = json.load(f)
    all_tickers = set(config['purchased_stocks']) | set(config['watchlist'])
    return list(all_tickers)

def init_database():
    """Initializes the database and sentiment_scores table."""
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sentiment_scores (
        Date TEXT,
        Ticker TEXT,
        Sentiment REAL,
        PRIMARY KEY (Date, Ticker)
    )
    ''')
    conn.commit()
    return conn

def get_sentiment(tickers, conn):
    """
    Scrapes Finviz for news headlines and calculates a daily sentiment score.
    """
    analyzer = SentimentIntensityAnalyzer()
    cursor = conn.cursor()
    
    # We must set a User-Agent header to mimic a browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    for ticker in tickers:
        print(f"--- Getting sentiment for {ticker} ---")
        try:
            url = f"https://finviz.com/quote.ashx?t={ticker}"
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Failed to load page for {ticker}. Status: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the news table
            news_table = soup.find('table', {'id': 'news-table'})
            if not news_table:
                print(f"Could not find news table for {ticker}.")
                continue

            sentiments = []
            current_date = None

            for row in news_table.findAll('tr'):
                # Get the headline text
                headline = row.a.text
                
                # Get the date/time 
                date_data = row.td.text
                date_data = date_data.replace('\r\n', '')
                date_data = date_data.replace('  ', '') # Example: 'Oct-31-25 10:00PM'
                date_data = date_data.split(' ')
                
                if len(date_data) == 2:
                    # This row has a new date
                    current_date = date_data[0]
                else:
                    # This row uses the date from a previous row
                    pass
                
                # Convert date from 'Oct-31-25' to '2025-10-31'
                try:
                    parsed_date = datetime.strptime(current_date, '%b-%d-%y').strftime('%Y-%m-%d')
                except ValueError:
                    # Handle cases where date might be 'Today' or just a time
                    parsed_date = datetime.now().strftime('%Y-%m-%d')
                
                # Get the VADER sentiment score
                # 'compound' score is a single value from -1 (very neg) to +1 (very pos)
                score = analyzer.polarity_scores(headline)['compound']
                sentiments.append({'date': parsed_date, 'score': score})
            
            if not sentiments:
                print(f"No headlines found for {ticker}.")
                continue

            # Convert to DataFrame and calculate the average score per day
            df = pd.DataFrame(sentiments)
            daily_avg_sentiment = df.groupby('date')['score'].mean().reset_index()
            
            # Store in the database
            for _, row in daily_avg_sentiment.iterrows():
                cursor.execute('''
                INSERT OR REPLACE INTO sentiment_scores (Date, Ticker, Sentiment)
                VALUES (?, ?, ?)
                ''', (row['date'], ticker, row['score']))
            
            conn.commit()
            print(f"Stored daily sentiment for {ticker}.")
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

def main():
    tickers = load_tickers()
    conn = init_database()
    get_sentiment(tickers, conn)
    conn.close()
    print("\nSentiment analysis complete.")

if __name__ == "__main__":
    main()