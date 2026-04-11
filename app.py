import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

# ------------------------------
# PAGE CONFIG
# ------------------------------

st.set_page_config(
    page_title="UOG Scenario Tool",
    page_icon="📈",
    layout="wide"
)

# ------------------------------
# DARK THEME STYLE
# ------------------------------

st.markdown("""
<style>

body {
    background-color:#020617;
    color:white;
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
border:1px solid rgba(255,215,0,0.2);
}

</style>
""", unsafe_allow_html=True)

# ------------------------------
# MARKET DATA
# ------------------------------

ticker = yf.Ticker("UOG.L")

data = ticker.history(period="1d")

price = data["Close"].iloc[-1]

price_p = price * 100

shares_outstanding = 4.66e9

market_cap = price * shares_outstanding

# ------------------------------
# BLOOMBERG STYLE HEADER
# ------------------------------

st.markdown(
f"""
### UOG MARKET

**Price:** {price_p:.3f}p  
**Market Cap:** £{market_cap/1e6:.2f}M  
**Shares Outstanding:** 4.66B
"""
)

st.divider()

# ------------------------------
# SIDEBAR MENU
# ------------------------------

menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Scenario Lab",
        "Discovery Simulator",
        "Portfolio Impact",
        "Market Activity"
    ]
)

# ------------------------------
# DASHBOARD PAGE
# ------------------------------

if menu == "Dashboard":

    st.title("UOG Dashboard")

    hist = ticker.history(period="1y")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["Close"]*100,
        line=dict(color="gold",width=3),
        name="Price"
    ))

    fig.add_hline(
        y=price_p,
        line_color="white",
        line_dash="dot",
        annotation_text="Current Price"
    )

    fig.update_layout(
        height=420,
        plot_bgcolor="#020617",
        paper_bgcolor="#020617",
        font=dict(color="white")
    )

    st.plotly_chart(fig,use_container_width=True)

# ------------------------------
# SCENARIO LAB
# ------------------------------

elif menu == "Scenario Lab":

    st.title("Scenario Lab")

    rerate = st.slider(
        "Re-Rating Multiple",
        1.0,
        30.0,
        5.0,
        0.1
    )

    scenario_price = price_p * rerate

    scenario_price_slider = st.slider(
        "Scenario Share Price (p)",
        0.1,
        500.0,
        scenario_price
    )

    st.write(f"### Scenario Price: {scenario_price_slider:.2f}p")

    hist = ticker.history(period="1y")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["Close"]*100,
        line=dict(color="gold",width=3)
    ))

    fig.add_hline(
        y=price_p,
        line_color="white",
        line_dash="dot",
        annotation_text="Current Price"
    )

    fig.add_hline(
        y=scenario_price_slider,
        line_color="red",
        line_dash="dash",
        annotation_text="Scenario Price"
    )

    fig.update_layout(
        height=420,
        plot_bgcolor="#020617",
        paper_bgcolor="#020617",
        font=dict(color="white")
    )

    st.plotly_chart(fig,use_container_width=True)

# ------------------------------
# DISCOVERY SIMULATOR
# ------------------------------

elif menu == "Discovery Simulator":

    st.title("Walton Morant Discovery Simulator")

    discovery_size = st.slider(
        "Discovery Size (MMBO)",
        100,
        5000,
        1000
    )

    value_per_barrel = st.slider(
        "Value per Barrel ($)",
        5,
        80,
        20
    )

    ownership = st.slider(
        "UOG Ownership %",
        10,
        100,
        52
    )

    barrel_value = discovery_size * value_per_barrel * (ownership/100)

    total_value = barrel_value * 1_000_000

    estimated_price = (total_value / shares_outstanding) / 100

    st.write(f"### Estimated Share Price: {estimated_price:.2f}p")

    size_range = np.linspace(100,5000,30)
    value_range = np.linspace(5,80,30)

    X,Y = np.meshgrid(size_range,value_range)

    Z = (X*Y*(ownership/100)*1_000_000)/shares_outstanding/100

    fig = go.Figure(data=[go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale="YlOrRd"
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title="Discovery Size",
            yaxis_title="Value per Barrel",
            zaxis_title="Share Price"
        ),
        height=500
    )

    st.plotly_chart(fig,use_container_width=True)

# ------------------------------
# PORTFOLIO IMPACT
# ------------------------------

elif menu == "Portfolio Impact":

    st.title("Portfolio Impact")

    current_shares = st.number_input(
        "Current Shares",
        value=1_000_000
    )

    scenario_shares = st.slider(
        "Scenario Shares",
        1_000_000,
        250_000_000,
        current_shares,
        step=500_000
    )

    scenario_price = st.slider(
        "Scenario Share Price (p)",
        0.1,
        500.0,
        5.0
    )

    scenario_price = scenario_price / 100

    personal_current = current_shares * price
    personal_scenario = scenario_shares * scenario_price

    col1,col2 = st.columns(2)

    with col1:
        st.metric(
            "Current Value",
            f"£{personal_current:,.0f}"
        )

    with col2:
        st.metric(
            "Scenario Value",
            f"£{personal_scenario:,.0f}"
        )

# ------------------------------
# MARKET ACTIVITY
# ------------------------------

elif menu == "Market Activity":

    st.title("Market Activity")

    trades = ticker.history(period="1d",interval="1m")

    trades = trades.tail(20)

    st.dataframe(trades[["Close","Volume"]])
