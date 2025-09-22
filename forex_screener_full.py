import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from tradingview_ta import TA_Handler, Interval
from datetime import datetime

st.title("📊 Forex Demand-Supply Zone Screener (Full Version)")

# Sidebar Controls
pair = st.sidebar.selectbox("Select Pair", ["EURUSD", "GBPUSD", "USDJPY"])
timeframe = st.sidebar.selectbox("Select Timeframe", ["5m", "15m", "1h", "4h", "1d"])
zone_type_filter = st.sidebar.multiselect("Zone Type", ["RBR", "RBD", "DBR", "DBD"],
                                   default=["RBR", "RBD", "DBR", "DBD"])
fresh_only = st.sidebar.checkbox("Show Fresh Zones Only", value=True)

# Map timeframe to TradingView interval
interval_map = {
    "5m": Interval.INTERVAL_5_MINUTES,
    "15m": Interval.INTERVAL_15_MINUTES,
    "1h": Interval.INTERVAL_1_HOUR,
    "4h": Interval.INTERVAL_4_HOURS,
    "1d": Interval.INTERVAL_1_DAY
}

handler = TA_Handler(
    symbol=pair,
    screener="forex",
    exchange="FX_IDC",
    interval=interval_map[timeframe]
)

# Session state to store candles
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

# Detect zone type based on previous, base, next candle
def detect_zone_type(prev_candle, base_candle, next_candle):
    if prev_candle["close"] > prev_candle["open"] and next_candle["close"] > next_candle["open"]:
        return "RBR"
    elif prev_candle["close"] > prev_candle["open"] and next_candle["close"] < next_candle["open"]:
        return "RBD"
    elif prev_candle["close"] < prev_candle["open"] and next_candle["close"] > next_candle["open"]:
        return "DBR"
    elif prev_candle["close"] < prev_candle["open"] and next_candle["close"] < next_candle["open"]:
        return "DBD"
    return None

# Check if zone is fresh
def is_fresh_zone(zone_high, zone_low, current_price):
    if zone_low <= current_price <= zone_high:
        return False  # Tested
    return True

# Update candles
latest_candle = get_latest_candle()
st.session_state.candles.append(latest_candle)
candles = st.session_state.candles

# Detect zones
zones = []
for i in range(1, len(candles)-1):
    prev_candle = candles[i-1]
    base_candle = candles[i]
    next_candle = candles[i+1]
    
    # Base candle condition: small body
    if abs(base_candle["close"] - base_candle["open"]) < 0.0005:
        z_type = detect_zone_type(prev_candle, base_candle, next_candle)
        if z_type:
            zones.append({
                "pair": pair,
                "time": base_candle["time"],
                "high": base_candle["high"],
                "low": base_candle["low"],
                "zone_type": z_type,
                "fresh": is_fresh_zone(base_candle["high"], base_candle["low"], latest_candle["close"]),
                "distance": round(abs(latest_candle["close"] - base_candle["high"]),5)
            })

df_zones = pd.DataFrame(zones)

# Apply filters
if fresh_only:
    df_zones = df_zones[df_zones["fresh"] == True]
if zone_type_filter:
    df_zones = df_zones[df_zones["zone_type"].isin(zone_type_filter)]

# Display Table
st.subheader(f"Latest Zones for {pair} ({timeframe})")
st.dataframe(df_zones.tail(20))

# Plot Candlestick + Zones
fig = go.Figure()
if df_zones.shape[0] > 0:
    # Plot base candle rectangles
    for _, row in df_zones.iterrows():
        color = "Red" if row["zone_type"] in ["RBR", "DBR"] else "Blue"
        fig.add_shape(
            type="rect",
            x0=row["time"], x1=row["time"],
            y0=row["low"], y1=row["high"],
            line=dict(color=color),
            fillcolor=color,
            opacity=0.3
        )

st.plotly_chart(fig)
