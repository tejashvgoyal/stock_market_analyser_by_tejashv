import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

def get_stock_data(ticker, start_date, end_date):
    """
    Fetches stock data from Yahoo Finance.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            return None, f"No data found for ticker '{ticker}'. It might be delisted or incorrect."
        return data, None
    except Exception as e:
        return None, f"An error occurred: {e}"

def plot_stock_chart(data, ticker):
    """
    Creates an interactive candlestick chart using Plotly.
    """
    fig = go.Figure()

    # Create Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlestick'
    ))

    # Add 50-day Moving Average
    data['MA50'] = data['Close'].rolling(window=50).mean()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['MA50'],
        mode='lines',
        name='50-Day Moving Average',
        line=dict(color='orange', width=1)
    ))

    # Add 200-day Moving Average
    data['MA200'] = data['Close'].rolling(window=200).mean()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['MA200'],
        mode='lines',
        name='200-Day Moving Average',
        line=dict(color='purple', width=1)
    ))

    # Update layout for a professional look
    fig.update_layout(
        title=f'{ticker} Stock Analysis',
        yaxis_title='Stock Price (USD)',
        xaxis_title='Date',
        xaxis_rangeslider_visible=True,  # Adds a slider to zoom
        template='plotly_dark'  # Use a dark theme
    )
    
    return fig

def format_large_number(num):
    """
    Formats large numbers (Market Cap) into B (Billions) or T (Trillions).
    """
    if num is None or not isinstance(num, (int, float)):
        return 'N/A'
    if num > 1_000_000_000_000:
        return f"${num/1_000_000_000_000:.2f} T"
    if num > 1_000_000_000:
        return f"${num/1_000_000_000:.2f} B"
    if num > 1_000_000:
        return f"${num/1_000_000:.2f} M"
    return f"${num:,.2f}"

# --- Streamlit App ---

st.set_page_config(page_title="Stock Analyzer", layout="wide")
st.title('📈 Stock Data Analyzer')

# Sidebar for user inputs
st.sidebar.header('User Input')
ticker_symbol = st.sidebar.text_input('Enter Stock Ticker', 'AAPL').upper()

# Date range selection
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input('Start Date', pd.to_datetime('2023-01-01'))
with col2:
    end_date = st.date_input('End Date', pd.to_datetime('today'))

# Button to fetch data
if st.sidebar.button('Analyze Stock'):
    if ticker_symbol:
        # Fetch data
        data, error = get_stock_data(ticker_symbol, start_date, end_date)
        
        if error:
            st.error(error)
        else:
            st.success(f"Displaying data for {ticker_symbol}")

            # Display the interactive chart
            st.header(f'Interactive Stock Chart')
            fig = plot_stock_chart(data, ticker_symbol)
            st.plotly_chart(fig, use_container_width=True)

            # -----------------------------------------------------------------
            # --- 🚀 NEW AESTHETIC STOCK INFO SECTION ---
            # -----------------------------------------------------------------
            st.header(f'{ticker_symbol} Company Information')
            try:
                stock_info = yf.Ticker(ticker_symbol).info
                
                # --- 1. Logo and Company Name/Info ---
                # --- 1. Logo and Company Name/Info ---
                col1, col2 = st.columns([1, 4])
                with col1:
                    logo_url = stock_info.get('logo_url', '')
                    if logo_url: # Only display if the URL is not empty
                        st.image(logo_url, width=100)
                    else:
                        st.caption("No Logo") # Optional: show a placeholder
                
                with col2:
                    st.subheader(stock_info.get('longName', 'N/A'))
                    st.markdown(f"**Sector:** {stock_info.get('sector', 'N/A')}")
                    st.markdown(f"**Industry:** {stock_info.get('industry', 'N/A')}")
                    st.markdown(f"**Website:** [{stock_info.get('website', 'N/A')}]({stock_info.get('website', '#')})")

                # --- 2. Business Summary (in an expander) ---
                st.subheader('Business Summary')
                with st.expander('Click to read summary'):
                    st.write(stock_info.get('longBusinessSummary', 'No summary available.'))

                # --- 3. Key Financial Metrics in Columns ---
                st.subheader('Key Financial Metrics')
                
                # Use .get() to safely access keys that might not exist
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Current Price", 
                        value=f"${stock_info.get('currentPrice', 0):.2f}"
                    )
                    st.metric(
                        label="Market Cap", 
                        value=format_large_number(stock_info.get('marketCap'))
                    )
                
                with col2:
                    st.metric(
                        label="Trailing P/E", 
                        value=f"{stock_info.get('trailingPE', 0):.2f}"
                    )
                    st.metric(
                        label="Dividend Yield", 
                        value=f"{stock_info.get('dividendYield', 0) * 100:.2f}%"
                    )

                with col3:
                    st.metric(
                        label="52-Week High", 
                        value=f"${stock_info.get('fiftyTwoWeekHigh', 0):.2f}"
                    )
                    st.metric(
                        label="52-Week Low", 
                        value=f"${stock_info.get('fiftyTwoWeekLow', 0):.2f}"
                    )
                
            except Exception as e:
                st.error(f"Could not fetch stock info: {e}")
                st.warning("Note: The yfinance .info object can be unreliable. Some data may be missing.")
            
            # --- END OF NEW SECTION ---
            
            # Display raw data
            st.header('Raw Stock Data (Last 10 Days)')
            st.dataframe(data.tail(10)) # Show the last 10 rows
    else:
        st.warning('Please enter a stock ticker.')

else:
    st.info('Enter a stock ticker in the sidebar and click "Analyze Stock".')