import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import datetime
from django.shortcuts import render

def dashboard(request):
    ticker = request.GET.get('ticker', 'AAPL').upper()
    error_message = None
    stock_info = {}
    plot_div = ""

    try:
        # Fetch data
        stock = yf.Ticker(ticker)
        df = stock.history(period='1y')
        
        if df.empty:
            error_message = f"No data found for ticker '{ticker}'. Please check the symbol."
        else:
            # Calculate indicators
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
            
            # Create Plotly graph
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index,
                        open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'], name='Price'))
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode='lines', name='SMA 20', line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], mode='lines', name='EMA 20', line=dict(color='cyan')))
            
            fig.update_layout(
                title=f'{ticker} Price Analysis',
                yaxis_title='Price',
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            plot_div = fig.to_html(full_html=False, include_plotlyjs='cdn')
            
            # Basic Info
            info = stock.info
            stock_info = {
                'name': info.get('longName', ticker),
                'current_price': round(df['Close'].iloc[-1], 2),
                'market_cap': info.get('marketCap', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'summary': info.get('longBusinessSummary', 'No summary available.')[:500] + '...'
            }

    except Exception as e:
        error_message = f"Error fetching data: {str(e)}"

    return render(request, 'analysis/dashboard.html', {
        'plot_div': plot_div,
        'ticker': ticker,
        'stock_info': stock_info,
        'error_message': error_message
    })
