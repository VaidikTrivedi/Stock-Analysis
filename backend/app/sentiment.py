import sys
import os
import matplotlib
matplotlib.use('Agg')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_and_predict import plot_forecast_with_trend
from prophet import Prophet
import matplotlib.pyplot as plt

def predict_future(df, days_ahead, forecast_name, return_fig=True):
    prophet_df = df.rename(columns={
        'Date': 'ds',
        'Close': 'y',
        'Sentiment': 'sentiment'
    })
    model = Prophet()
    model.add_regressor('sentiment')
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=days_ahead)
    future['sentiment'] = 0
    future = future.merge(prophet_df[['ds', 'sentiment']], on='ds', how='left')
    future['sentiment'] = future['sentiment_y'].fillna(future['sentiment_x'])
    future = future.drop(columns=['sentiment_x', 'sentiment_y'])
    forecast = model.predict(future)
    plot_forecast_with_trend(df, forecast, forecast_name)
    fig = plt.gcf()  # Get the current figure after plotting
    if return_fig:
        return forecast, fig
    return forecast
