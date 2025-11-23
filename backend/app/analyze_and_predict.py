import pandas as pd
import pandas_ta as ta
import sqlite3
from prophet import Prophet
import matplotlib.pyplot as plt

# --- IMPORTANT DISCLAIMER ---
# This script is for educational purposes only. 
# Stock market prediction is extremely difficult and highly speculative.
# Past performance and model forecasts are NOT a guarantee of future results.
# DO NOT make financial decisions based solely on this script's output.

def load_data_from_db(ticker):
    """Loads price and sentiment data for a specific ticker from the database."""
    conn = sqlite3.connect('stocks.db')
    
    # Load prices
    # We parse 'Date' column as datetime objects directly
    prices_df = pd.read_sql_query(
        f"SELECT * FROM stock_prices WHERE ticker = '{ticker}'", 
        # "SELECT * FROM stock_prices",
        conn, 
        parse_dates=['Date']
    )
    prices_df.set_index('Date', inplace=True)
    
    # Load sentiment
    sentiment_df = pd.read_sql_query(
        f"SELECT * FROM sentiment_scores WHERE ticker = '{ticker}'", 
        conn,
        parse_dates=['Date']
    )
    sentiment_df.set_index('Date', inplace=True)
    
    conn.close()
    
    if prices_df.empty:
        return None
        
    # Combine the price and sentiment data
    combined_df = prices_df.join(sentiment_df.drop('Ticker', axis=1))
    
    # Fill missing sentiment values (e.g., weekends) with 0 or forward-fill
    combined_df['Sentiment'] = combined_df['Sentiment'].fillna(0) 
    
    return combined_df.reset_index() # Reset index to have 'Date' as a column

def perform_technical_analysis(df):
    """Calculates technical indicators and appends them to the DataFrame."""
    print("--- Performing Technical Analysis ---")
    
    # Calculate 14-day Relative Strength Index (RSI)
    df.ta.rsi(length=14, append=True)
    
    # Calculate Moving Average Convergence Divergence (MACD)
    # This appends 3 columns: MACD, MACD_Histogram, MACD_Signal
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    
    # Calculate 50-day and 200-day Simple Moving Averages (SMA)
    df.ta.sma(length=50, append=True)
    df.ta.sma(length=200, append=True)
    
    # Clean up NaN values created by the indicators (at the start of the data)
    df.dropna(inplace=True)
    
    return df

def predict_future(df, days_ahead, forecast_name):
    """
    Uses Prophet to forecast future stock prices.
    """
    print(f"--- Generating {forecast_name} forecast ---")
    
    # Prophet requires very specific column names:
    # 'ds' for the date
    # 'y' for the value to predict (we'll use 'Close')
    prophet_df = df.rename(columns={
        'Date': 'ds',
        'Close': 'y',
        'Sentiment': 'sentiment' # our external regressor
    })
    
    # Initialize the model and add our sentiment as an extra regressor
    model = Prophet()
    model.add_regressor('sentiment')
    
    # Fit the model to our data
    model.fit(prophet_df)
    
    # Create a DataFrame for future dates
    future = model.make_future_dataframe(periods=days_ahead)
    
    # We need to provide the 'sentiment' for the future.
    # Since we can't know future sentiment, we'll assume it's neutral (0)
    # A more advanced model might try to predict sentiment itself.
    future['sentiment'] = 0
    
    # Merge known past sentiment values
    future = future.merge(prophet_df[['ds', 'sentiment']], on='ds', how='left')
    future['sentiment'] = future['sentiment_y'].fillna(future['sentiment_x']).drop(columns=['sentiment_x', 'sentiment_y'])

    # Generate the forecast
    forecast = model.predict(future)
    
    # --- Displaying the forecast ---
    print(f"Forecast for {forecast_name}:")
    # 'yhat' is the predicted value
    # 'yhat_lower' and 'yhat_upper' are the uncertainty intervals
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

    # Plot historical and predicted prices with trend color
    plot_forecast_with_trend(df, forecast, forecast_name)
    
    # Plot the forecast
    # This will show the historical data, the forecast, and the uncertainty
    fig1 = model.plot(forecast)
    plt.title(f'{forecast_name} Forecast')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()

    # Plot the components (trend, weekly/yearly seasonality)
    

    # [Image of Prophet forecast components plot showing trend and seasonality]
    fig2 = model.plot_components(forecast)
    plt.show()

def plot_forecast_with_trend(df, forecast, forecast_name):
    """
    Plots historical prices and predicted prices with color based on trend.
    Historical: blue
    Predicted: green (upward trend), red (downward trend)
    """
    import matplotlib.dates as mdates

    # Historical data
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Close'], color='blue', label='Historical Price')

    # Predicted data
    forecast_pred = forecast[forecast['ds'] > df['Date'].max()]
    if not forecast_pred.empty:
        # Determine trend: compare first and last predicted value
        last_hist_date = df['Date'].max()
        last_hist_price = df[df['Date'] == last_hist_date]['Close'].values[0]

        first_pred_date = forecast_pred['ds'].iloc[0]
        first_pred = forecast_pred['yhat'].iloc[0]
        first_pred_price = forecast_pred['yhat'].iloc[0]

        connected_dates = [last_hist_date, first_pred_date]
        connected_prices = [last_hist_price, first_pred_price]

        # Plot the connecting line
        plt.plot(connected_dates, connected_prices, color='gray', linestyle='--', linewidth=1)

        last_pred = forecast_pred['yhat'].iloc[-1]
        trend_color = 'green' if last_pred > first_pred else 'red'
        plt.plot(forecast_pred['ds'], forecast_pred['yhat'], color=trend_color, label=f'Predicted Price ({forecast_name})')
    
    plt.title(f'{forecast_name} Forecast')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()    

def main():
    # --- CONFIGURATION ---
    # Let's analyze one ticker from your list
    global TICKER_TO_ANALYZE
    TICKER_TO_ANALYZE = "AAPL" 
    
    # 1. Load Data
    full_data = load_data_from_db(TICKER_TO_ANALYZE)
    
    if full_data is None:
        print(f"No data found for {TICKER_TO_ANALYZE}. Exiting.")
        return
    
    # Dropping Adj Close values because it's no present in API
    full_data.drop(['Adj Close'], axis=1, inplace=True)

    # 2. Perform Technical Analysis
    ta_data = perform_technical_analysis(full_data.copy())
    print("\nLatest Technical Analysis Data:")
    print(ta_data.tail())

    # Check for minimum rows required by Prophet
    if len(ta_data.dropna()) < 2:
        print("Not enough data after technical analysis for prediction. Skipping forecast.")
        return
    
    # 3. Perform Predictions
    # 1-Month (approx 30 days)
    predict_future(ta_data, days_ahead=30, forecast_name="1-Month")
    
    # 1-Year (365 days)
    predict_future(ta_data, days_ahead=365, forecast_name="1-Year")
    
    # 5-Year (365 * 5 days)
    print("\n--- 5-Year Forecast Note ---")
    print("Forecasting 5 years out is HIGHLY speculative. The uncertainty")
    print("interval will be very large, and the model relies on past")
    print("trends continuing, which is unlikely in finance.")
    predict_future(ta_data, days_ahead=365*5, forecast_name="5-Year")
    predict_future(ta_data, days_ahead=365*10, forecast_name="10-Year")
    print("Done")


if __name__ == "__main__":
    main()