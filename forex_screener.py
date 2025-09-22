import streamlit as st
import pandas as pd
import random
from datetime import datetime

# 🎯 Title
st.title("📊 Forex Demand-Supply Zone Screener (Test Mode)")

# Sidebar selections
pair = st.sidebar.selectbox("Select Pair", ["EURUSD", "GBPUSD", "USDJPY"])
timeframe = st.sidebar.selectbox("Select Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"])

zone_type = st.sidebar.multiselect("Zone Type", ["RBR", "RBD", "DBR", "DBD"], 
                                   default=["RBR", "RBD", "DBR", "DBD"])
fresh_only = st.sidebar.checkbox("Show Fresh Zones Only", value=True)

# Generate fake OHLC data for testing
data = []
for i in range(20):
    data.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "open": round(1.10 + random.uniform(-0.01, 0.01), 5),
        "high": round(1.11 + random.uniform(-0.01, 0.01), 5),
        "low": round(1.09 + random.uniform(-0.01, 0.01), 5),
        "close": round(1.10 + random.uniform(-0.01, 0.01), 5),
        "zone_type": random.choice(["RBR", "RBD", "DBR", "DBD"]),
        "fresh": random.choice([True, False])
    })

df = pd.DataFrame(data)

# Apply filters
if fresh_only:
    df = df[df["fresh"] == True]
if zone_type:
    df = df[df["zone_type"].isin(zone_type)]

# Display final table
st.subheader(f"Latest Zones for {pair} ({timeframe})")
st.dataframe(df)
