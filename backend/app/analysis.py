import matplotlib.pyplot as plt
import io
import base64
import uuid
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database
import sentiment
import analyze_and_predict

def save_plot_to_file(fig):
    plot_id = str(uuid.uuid4())
    file_path = f"/tmp/{plot_id}.png"
    fig.savefig(file_path)
    plt.close(fig)
    return plot_id

def analyze_ticker(ticker):
    # Load and analyze data
    full_data = database.load_data_from_db(ticker)
    if full_data is None:
        raise Exception(f"No data found for {ticker}")
    full_data.drop(['Adj Close'], axis=1, inplace=True)
    ta_data = analyze_and_predict.perform_technical_analysis(full_data.copy())
    if len(ta_data.dropna()) < 2:
        raise Exception("Not enough data after technical analysis for prediction.")
    # Generate forecasts and plots
    results = {}
    for name, days in [("1-Month", 30), ("1-Year", 365), ("5-Year", 365*5), ("10-Year", 365*10)]:
        print(f"NAME - {name}")
        forecast, fig = sentiment.predict_future(ta_data, days, name, return_fig=True)
        # print(f"Forecast - {forecast}")
        plot_id = save_plot_to_file(fig=fig)
        # Convert forecast DataFrame to dict safely
        if isinstance(forecast, pd.DataFrame):
            forecast_dict = forecast.to_dict()
        elif isinstance(forecast, dict):
            forecast_dict = forecast
        else:
            forecast_dict = {}
        results[name] = {"forecast": forecast_dict, "plot_id": plot_id}
    return results
