import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from tradingview_ta import TA_Handler, Interval
from datetime import datetime

st.title("📊 Forex & Stock Zone Screener Dashboard")

# --- Center Page Controls ---

# Market Selection
market = st.selectbox("Select Market", ["Forex", "Stocks"])

# Pair Selection based on market
if market == "Forex":
    pair = st.selectbox("Select Pair", ["EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD","USDCHF","NZDUSD"])
else:
    pair = st.selectbox("Select Stock", ["AAPL","MSFT","GOOGL","AMZN","TSLA","META","NFLX"])

# Timeframe Selection
timeframe = st.selectbox("Select Timeframe", ["5m", "15m", "1h", "4h", "1d"])

# Zone Type Selection
zone_type = st.multiselect("Select Zone Type", ["Supply", "Demand", "Both"], default=["Both"])

# Fresh / Tested Selection
fresh_option = st.radio("Select Zone Status", ["Fresh", "Tested", "All"], index=0)

# --- TradingView Handler ---
interval_map = {
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES,
    "1h": Interval.INTERVAL_1_HOUR,
    "4h": Interval.INTERVAL_4_HOURS,
    "1d": Interval.INTERVAL_1_DAY
}

if market == "Forex":
    screener = "forex"
    exchange = "FX_IDC"
else:
    screener = "america"
    exchange = "NASDAQ"

handler = TA_Handler(
    symbol=pair,
    screener=screener,
    exchange=exchange,
    interval=interval_map[timeframe]
)

# --- Session State to store candles ---
if "candles" not in st.session_state:
    st.session_state.candles = []

# Get latest candle
def get_latest_candle():
    analysis = handler.get_analysis()
    candle = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "open": analysis.indicators["open"],
        "high": analysis.indicators["high"],
        "low": analysis.indicators["low"],
        "close": analysis.indicators["close"]
    }
    return candle

# Supply / Demand detection (simplified)
def detect_zone(candle):
    body = abs(candle["close"] - candle["open"])
    if body < 0.0005:  # Small body candle as base
        if candle["close"] > candle["open"]:
            return "Demand"
        else:
            return "Supply"
    return None

# Update candles
latest_candle = get_latest_candle()
st.session_state.candles.append(latest_candle)
candles = st.session_state.candles

# Detect zones
zones = []
for candle in candles:
    z_type = detect_zone(candle)
    if z_type:
        zones.append({
            "pair": pair,
            "time": candle["time"],
            "high": candle["high"],
            "low": candle["low"],
            "zone_type": z_type,
            "fresh": True,  # For demo, all fresh
            "distance": round(abs(latest_candle["close"] - candle["high"]),5)
        })

df_zones = pd.DataFrame(zones)

# Ensure columns exist
for col in ["pair","time","high","low","zone_type","fresh","distance"]:
    if col not in df_zones.columns:
        df_zones[col] = pd.Series(dtype="object")

# Apply zone type filter
if zone_type and "Both" not in zone_type:
    df_zones = df_zones[df_zones["zone_type"].isin(zone_type)]

# Apply fresh/tested filter
if fresh_option == "Fresh":
    df_zones = df_zones[df_zones["fresh"]==True]
elif fresh_option == "Tested":
    df_zones = df_zones[df_zones["fresh"]==False]

# --- Display Table ---
st.subheader(f"Latest Zones for {pair} ({timeframe})")
st.dataframe(df_zones.tail(20))

# --- Plot Candlestick + Zones ---
fig = go.Figure()
if df_zones.shape[0]>0:
    for _, row in df_zones.iterrows():
        color = "Green" if row["zone_type"]=="Demand" else "Red"
        fig.add_shape(
            type="rect",
            x0=row["time"], x1=row["time"],
            y0=row["low"], y1=row["high"],
            line=dict(color=color),
            fillcolor=color,
            opacity=0.3
        )

st.plotly_chart(fig)
