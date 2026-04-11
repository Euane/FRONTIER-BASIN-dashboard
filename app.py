import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="UOG Scenario Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# DARK GOLD STYLE
# -------------------------------------------------

st.markdown("""
<style>

body {
    background-color:#020617;
    color:#FFD700;
}

h1,h2,h3 {
    color:#FFD700;
}

section[data-testid="stSidebar"] {
    background-color:#020617;
}

div[data-testid="stMetric"]{
background:#111827;
border-radius:10px;
padding:10px;
border:1px solid rgba(255,215,0,0.25);
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# MARKET DATA
# -------------------------------------------------

ticker = yf.Ticker("UOG.L")

intraday = ticker.history(period="1d", interval="5m")

price = intraday["Close"].iloc[-1]

prev_price = intraday["Close"].iloc[0]

price_p = price * 100

shares_outstanding = 4.66e9

market_cap = price * shares_outstanding

volume_today = intraday["Volume"].sum()

change_pct = ((price - prev_price) / prev_price) * 100

# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.markdown(
f"""
### UOG LIVE MARKET

Price **{price_p:.3f}p** | Change **{change_pct:+.2f}%** |  
Market Cap **£{market_cap/1e6:.2f}M** | Volume **{volume_today:,.0f}** | Shares **4.66B**
"""
)

st.divider()

# -------------------------------------------------
# BUY / SELL PRESSURE
# -------------------------------------------------

hist_pressure = ticker.history(period="5d", interval="5m")

hist_pressure["Prev"] = hist_pressure["Close"].shift(1)

buy = (hist_pressure["Close"] > hist_pressure["Prev"]).sum()
sell = (hist_pressure["Close"] < hist_pressure["Prev"]).sum()

total = buy + sell

buy_pct = (buy / total) * 100
sell_pct = (sell / total) * 100

st.subheader("Market Pressure")

st.progress(buy_pct/100)

col1, col2 = st.columns(2)

with col1:
    st.metric("BUY Pressure", f"{buy_pct:.1f}%")

with col2:
    st.metric("SELL Pressure", f"{sell_pct:.1f}%")

st.divider()

# -------------------------------------------------
# MENU
# -------------------------------------------------

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Portfolio Impact",
        "Market Activity",
        "Scenario Lab",
        "Discovery Simulator"
    ]
)

# -------------------------------------------------
# TIMEFRAME MAP
# -------------------------------------------------

timeframe_map = {
"1d":"1d",
"2d":"2d",
"3d":"3d",
"1w":"5d",
"1w":"7d",
"2w":"14d",
"3w":"21d",
"1m":"1mo",
"3m":"3mo",
"6m":"6mo",
"1y":"1y",
"2y":"2y"
}

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

if menu == "Dashboard":

    st.title("UOG Dashboard")

    timeframe = st.selectbox("Chart Timeframe", list(timeframe_map.keys()))

    hist = ticker.history(period=timeframe_map[timeframe])

    show_rerating = st.toggle("Show Rerating Ladder", True)
    show_discovery = st.toggle("Show Discovery Ladder", False)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["Close"]*100,
        line=dict(color="gold", width=3)
    ))

    fig.add_hline(
        y=price_p,
        line_color="white",
        line_dash="dot",
        annotation_text="Current"
    )

    # ----------------------------
    # RERATING LADDER
    # ----------------------------

    if show_rerating:

        rerating_levels = [1.5,2,2.5,3,4,5,7,10,15,20,25]

        for level in rerating_levels:

            target_price = price_p * level

            implied_mcap = (target_price/100) * shares_outstanding

            fig.add_hline(
                y=target_price,
                line_dash="dot",
                line_color="orange",
                annotation_text=f"{level}x | {target_price:.2f}p | £{implied_mcap/1e6:.1f}M",
                annotation_position="right"
            )

    # ----------------------------
    # DISCOVERY LADDER
    # ----------------------------

    if show_discovery:

        discovery_sizes = [500,1000,2000,5000]

        value_per_barrel = 20
        ownership = 0.52

        for size in discovery_sizes:

            total_value = size * value_per_barrel * ownership * 1_000_000

            price_estimate = (total_value / shares_outstanding) * 100

            fig.add_hline(
                y=price_estimate,
                line_dash="dash",
                line_color="cyan",
                annotation_text=f"{size}MMBO | {price_estimate:.2f}p",
                annotation_position="left"
            )

    fig.update_layout(
        height=500,
        plot_bgcolor="#020617",
        paper_bgcolor="#020617",
        font=dict(color="#FFD700")
    )

    st.plotly_chart(fig,use_container_width=True)

# -------------------------------------------------
# PORTFOLIO IMPACT
# -------------------------------------------------

elif menu == "Portfolio Impact":

    st.title("Portfolio Impact")

    current_shares = st.number_input("Current Shares", value=1_000_000)

    scenario_shares = st.slider(
        "Scenario Shares",
        1_000_000,
        250_000_000,
        current_shares
    )

    scenario_price = st.slider(
        "Scenario Share Price (p)",
        0.1,
        500.0,
        price_p
    )

    scenario_price = scenario_price / 100

    current_value = current_shares * price
    scenario_value = scenario_shares * scenario_price

    pct_change = ((scenario_value - current_value) / current_value) * 100

    col1,col2,col3 = st.columns(3)

    col1.metric("Current Value", f"£{current_value:,.0f}")
    col2.metric("Scenario Value", f"£{scenario_value:,.0f}")
    col3.metric("Change", f"{pct_change:.1f}%")

# -------------------------------------------------
# MARKET ACTIVITY
# -------------------------------------------------

elif menu == "Market Activity":

    st.title("Market Activity")

    trades = ticker.history(period="5d", interval="5m")

    trades = trades.reset_index()

    trades["Prev"] = trades["Close"].shift(1)

    def classify(row):
        if row["Close"] > row["Prev"]:
            return "Buy"
        elif row["Close"] < row["Prev"]:
            return "Sell"
        return "NEUTRAL"

    trades["Side"] = trades.apply(classify, axis=1)

    table = trades[["Datetime","Close","Volume","Side"]]

    table.columns = ["Time","Price","Volume","Side"]

    st.dataframe(table.tail(200),use_container_width=True)

# -------------------------------------------------
# SCENARIO LAB
# -------------------------------------------------

elif menu == "Scenario Lab":

    st.title("Scenario Lab")

    rerate = st.slider("Re-Rating Multiple",1.0,30.0,5.0)

    scenario_price = price_p * rerate

    st.write(f"Scenario Price: **{scenario_price:.2f}p**")

# -------------------------------------------------
# DISCOVERY SIMULATOR
# -------------------------------------------------

elif menu == "Discovery Simulator":

    st.title("Walton Morant Discovery Simulator")

    discovery_size = st.slider("Discovery Size (MMBO)",100,5000,1000)
    value_per_barrel = st.slider("Value per Barrel ($)",5,80,20)
    ownership = st.slider("UOG Ownership %",10,100,52)

    total_value = discovery_size * value_per_barrel * (ownership/100) * 1_000_000

    price_estimate = (total_value / shares_outstanding) * 100

    st.write(f"Estimated Share Price: **{price_estimate:.2f}p**")

    size_range = np.linspace(100,5000,30)
    value_range = np.linspace(5,80,30)

    X,Y = np.meshgrid(size_range,value_range)

    Z = (X*Y*(ownership/100)*1_000_000)/shares_outstanding*100

    fig = go.Figure(data=[go.Surface(x=X,y=Y,z=Z,colorscale="YlOrRd")])

    fig.update_layout(
        scene=dict(
            xaxis_title="Discovery Size",
            yaxis_title="Value per Barrel",
            zaxis_title="Share Price (p)"
        ),
        height=500
    )

    st.plotly_chart(fig,use_container_width=True)
