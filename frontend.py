"""
Streamlit Frontend for Stock Analysis Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os


def load_cached_results():
    """Load cached model results."""
    cache_file = "cached_results.json"
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except:
            return None
    return None


def get_stock_data_for_period(stock_data_df, ticker, period_start, period_end):
    """Get stock data for a specific period."""
    ticker_data = stock_data_df[stock_data_df["Ticker"] == ticker].copy()
    ticker_data["Date"] = pd.to_datetime(ticker_data["Date"])
    
    mask = (ticker_data["Date"] >= pd.to_datetime(period_start)) & (ticker_data["Date"] <= pd.to_datetime(period_end))
    period_data = ticker_data[mask].copy()
    
    if len(period_data) == 0:
        return None, None
    
    period_data = period_data.sort_values("Date")
    
    if len(period_data) > 0:
        start_price = period_data["Adj Close"].iloc[0]
        end_price = period_data["Adj Close"].iloc[-1]
        pct_change = ((end_price / start_price) - 1) * 100
    else:
        pct_change = 0
    
    return period_data, pct_change


def calculate_stock_stats(stock_data_df, ticker, current_date):
    """Calculate key stock statistics."""
    ticker_data = stock_data_df[stock_data_df["Ticker"] == ticker].copy()
    ticker_data["Date"] = pd.to_datetime(ticker_data["Date"])
    ticker_data = ticker_data.sort_values("Date")
    
    current_idx = ticker_data[ticker_data["Date"] <= pd.to_datetime(current_date)]
    if len(current_idx) == 0:
        return {}
    
    current_price = current_idx["Adj Close"].iloc[-1]
    
    # 1 Year return
    one_year_ago = pd.to_datetime(current_date) - timedelta(days=365)
    one_year_data = ticker_data[ticker_data["Date"] >= one_year_ago]
    if len(one_year_data) > 0:
        one_year_return = ((current_price / one_year_data["Adj Close"].iloc[0]) - 1) * 100
    else:
        one_year_return = None
    
    # Volatility (annualized)
    returns = ticker_data["Adj Close"].pct_change().dropna()
    if len(returns) > 0:
        volatility = returns.std() * np.sqrt(252) * 100  # Annualized
    else:
        volatility = None
    
    # 52-week high/low
    fifty_two_weeks = ticker_data[ticker_data["Date"] >= one_year_ago]
    if len(fifty_two_weeks) > 0:
        week_high = fifty_two_weeks["Adj Close"].max()
        week_low = fifty_two_weeks["Adj Close"].min()
    else:
        week_high = None
        week_low = None
    
    # Current vs 52-week
    if week_high and week_low:
        vs_high = ((current_price / week_high) - 1) * 100
        vs_low = ((current_price / week_low) - 1) * 100
    else:
        vs_high = None
        vs_low = None
    
    return {
        "current_price": current_price,
        "one_year_return": one_year_return,
        "volatility": volatility,
        "week_high": week_high,
        "week_low": week_low,
        "vs_52w_high": vs_high,
        "vs_52w_low": vs_low
    }


def main():
    st.set_page_config(
        page_title="Stock Analysis Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for blue-black theme
    st.markdown("""
        <style>
        .main {
            background-color: #0a0e27;
            color: #e0e0e0;
        }
        .stButton>button {
            background-color: #1e3a8a;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #3b82f6;
        }
        .metric-card {
            background-color: #1e293b;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #334155;
        }
        .prediction-action {
            text-align: center;
            padding: 2rem;
            margin: 1rem 0;
            border-radius: 10px;
            font-size: 2rem;
            font-weight: bold;
        }
        .action-BUY {
            background-color: #1e40af;
            color: white;
        }
        .action-SHORT {
            background-color: #991b1b;
            color: white;
        }
        .action-HOLD {
            background-color: #475569;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Load cached results
    results = load_cached_results()
    
    if results is None:
        st.error("No cached results found. Please run the model first.")
        st.info("Run: python launcher.py")
        return
    
    # Extract data
    predictions_df = pd.DataFrame(results.get("predictions", []))
    backtest_results = results.get("backtest_results", {})
    economic_data = results.get("economic_data", {})
    market_data = results.get("market_data", {})
    stock_data_df = pd.DataFrame(results.get("stock_data", []))
    
    if predictions_df.empty:
        st.error("No predictions available.")
        return
    
    # Sidebar
    st.sidebar.title("📊 Stock Analysis Dashboard")
    
    available_tickers = sorted(predictions_df["Ticker"].unique().tolist())
    selected_ticker = st.sidebar.selectbox("Select Stock", available_tickers)
    
    # Get prediction for selected ticker
    ticker_pred = predictions_df[predictions_df["Ticker"] == selected_ticker]
    
    if ticker_pred.empty:
        st.error(f"No prediction available for {selected_ticker}")
        return
    
    pred_row = ticker_pred.iloc[0]
    current_date = pred_row["Date"]
    current_price = pred_row["Adj Close"]
    action = pred_row["Action"]
    down_prob = pred_row["Down"]
    flat_prob = pred_row["Flat"]
    up_prob = pred_row["Up"]
    
    # Main content
    st.title(f"Stock Analysis: {selected_ticker}")
    st.markdown(f"**Current Price:** ${current_price:.2f} | **Date:** {current_date}")
    
    # Movement History Section
    st.header("📈 Movement History")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    periods = {
        "1 Day": 1,
        "15 Days": 15,
        "1 Month": 30,
        "5 Years": 1825,
        "Max": None
    }
    
    selected_period = None
    period_label = None
    
    with col1:
        if st.button("1 Day"):
            selected_period = 1
            period_label = "1 Day"
    with col2:
        if st.button("15 Days"):
            selected_period = 15
            period_label = "15 Days"
    with col3:
        if st.button("1 Month"):
            selected_period = 30
            period_label = "1 Month"
    with col4:
        if st.button("5 Years"):
            selected_period = 1825
            period_label = "5 Years"
    with col5:
        if st.button("Max"):
            selected_period = None
            period_label = "Max"
    
    # Default to Max
    if selected_period is None and period_label is None:
        selected_period = None
        period_label = "Max"
    
    # Calculate period
    end_date = pd.to_datetime(current_date)
    if selected_period is None:
        start_date = stock_data_df["Date"].min()
    else:
        start_date = end_date - timedelta(days=selected_period)
    
    period_data, pct_change = get_stock_data_for_period(stock_data_df, selected_ticker, start_date, end_date)
    
    if period_data is not None and len(period_data) > 0:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=period_data["Date"],
            y=period_data["Adj Close"],
            mode='lines',
            name=selected_ticker,
            line=dict(color='#3b82f6', width=2)
        ))
        fig.update_layout(
            title=f"Price Movement - {period_label}",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            template="plotly_dark",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show % change
        if pct_change is not None:
            color = "green" if pct_change >= 0 else "red"
            st.markdown(f"<p style='text-align: right; color: {color}; font-size: 1.2rem;'><b>Change: {pct_change:+.2f}%</b></p>", unsafe_allow_html=True)
    
    # Prediction Section
    st.header("🔮 Prediction Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Pie chart
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Rise', 'Neutral', 'Fall'],
            values=[up_prob * 100, flat_prob * 100, down_prob * 100],
            marker=dict(colors=['#3b82f6', '#64748b', '#ef4444']),
            hole=0.4,
            textinfo='label+percent',
            textfont=dict(size=14, color='white')
        )])
        fig_pie.update_layout(
            title="Price Movement Probability",
            template="plotly_dark",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("### Probabilities")
        st.metric("Rise", f"{up_prob*100:.1f}%")
        st.metric("Neutral", f"{flat_prob*100:.1f}%")
        st.metric("Fall", f"{down_prob*100:.1f}%")
    
    # Action Recommendation
    action_class = f"action-{action}"
    st.markdown(f'<div class="{action_class} prediction-action">{action}</div>', unsafe_allow_html=True)
    
    # Model Variables Section
    st.header("📋 Model Variables")
    
    st.markdown("""
    The model uses the following key variables:
    - **1. Stock's Own History (AR1-like)**: Historical price movements, returns (1, 5, 15, 30 day), momentum, volatility, RSI, drawdown
    - **2. Overall Market Conditions**: S&P 500 (^GSPC) performance and volatility
    - **3. Industry Conditions**: Via ETFs (XLK, XLF, etc.) and sector performance
    - **4. Economic Variables**: Interest rates, inflation, unemployment rate
    """)
    
    # Economic Conditions Section
    st.header("💼 Economic Conditions")
    
    if economic_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            unemployment = economic_data.get("Unemployment_Rate")
            if unemployment is not None:
                st.metric("Unemployment Rate", f"{unemployment:.2f}%")
        
        with col2:
            interest = economic_data.get("Interest_Rate")
            if interest is not None:
                st.metric("Interest Rate", f"{interest:.2f}%")
        
        with col3:
            inflation_yoy = economic_data.get("Inflation_YoY")
            if inflation_yoy is not None:
                st.metric("Inflation Rate (YoY)", f"{inflation_yoy:.2f}%")
            else:
                inflation_raw = economic_data.get("Inflation_Rate")
                if inflation_raw is not None:
                    st.metric("Inflation Rate (Index)", f"{inflation_raw:.2f}")
    
    # Market Performance Section
    st.header("📊 Market Performance (^GSPC)")
    
    if "^GSPC" in market_data:
        spx_data = market_data["^GSPC"]
        spx_dates = pd.to_datetime(spx_data["dates"])
        spx_prices = spx_data["prices"]
        
        fig_spx = go.Figure()
        fig_spx.add_trace(go.Scatter(
            x=spx_dates,
            y=spx_prices,
            mode='lines',
            name='S&P 500',
            line=dict(color='#10b981', width=2)
        ))
        fig_spx.update_layout(
            title="S&P 500 Performance",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_spx, use_container_width=True)
    
    # Backtest Statistics & Stock Info
    st.header("📊 Backtest Statistics & Stock Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Backtest Results")
        if selected_ticker in backtest_results:
            bt = backtest_results[selected_ticker]
            st.metric("Accuracy", f"{bt.get('accuracy', 0)*100:.1f}%")
            st.metric("F1 Score (Macro)", f"{bt.get('f1_macro', 0):.3f}")
            st.metric("Log Loss", f"{bt.get('log_loss', 0):.3f}")
            st.metric("Number of Folds", f"{bt.get('n_folds', 0)}")
    
    with col2:
        st.subheader("Stock Statistics")
        stats = calculate_stock_stats(stock_data_df, selected_ticker, current_date)
        
        if stats.get("one_year_return") is not None:
            st.metric("1 Year Return", f"{stats['one_year_return']:.2f}%")
        
        if stats.get("volatility") is not None:
            st.metric("Volatility (Annualized)", f"{stats['volatility']:.2f}%")
        
        if stats.get("week_high") is not None:
            st.metric("52-Week High", f"${stats['week_high']:.2f}")
        
        if stats.get("week_low") is not None:
            st.metric("52-Week Low", f"${stats['week_low']:.2f}")
        
        if stats.get("vs_52w_high") is not None:
            color = "normal"
            st.metric("vs 52-Week High", f"{stats['vs_52w_high']:.2f}%")


if __name__ == "__main__":
    main()

