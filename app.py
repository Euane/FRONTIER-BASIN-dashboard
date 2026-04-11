import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
from PIL import Image, ImageDraw
import io
import os

# --------------------------------
# PAGE CONFIG
# --------------------------------

st.set_page_config(
    page_title="UOG Scenario Tool",
    page_icon="icon.png",
    layout="wide"
)

# --------------------------------
# DASHBOARD STYLE
# --------------------------------

st.markdown("""
<style>

body{
background-color:#020617;
color:white;
}

h1,h2,h3{
color:#FFD700;
}

div[data-testid="stMetric"]{
background:#111827;
border-radius:10px;
padding:10px;
border:1px solid rgba(255,215,0,0.2);
}

</style>
""", unsafe_allow_html=True)

# --------------------------------
# HERO SLIDE CAROUSEL
# --------------------------------

slides_folder = "hero"
slides = sorted(os.listdir(slides_folder))

if "slide_index" not in st.session_state:
    st.session_state.slide_index = 0

current_slide = slides[st.session_state.slide_index]

st.image(f"{slides_folder}/{current_slide}", use_column_width=True)

col1, col2, col3 = st.columns([1,3,1])

with col1:
    if st.button("◀"):
        st.session_state.slide_index = (
            st.session_state.slide_index - 1
        ) % len(slides)

with col3:
    if st.button("▶"):
        st.session_state.slide_index = (
            st.session_state.slide_index + 1
        ) % len(slides)

# --------------------------------
# MARKET DATA
# --------------------------------

ticker = yf.Ticker("UOG.L")

data = ticker.history(period="1d")

price = data["Close"].iloc[-1]

shares_outstanding = 4.66e9

market_cap = price * shares_outstanding

price_p = price * 100

st.title("LIVE UOG MARKET")

st.write(f"{price_p:.3f}p ▲ | £{market_cap/1e6:.1f}M mcap | 4.66B shares")

# --------------------------------
# CHART CONTROLS
# --------------------------------

show_chart = st.toggle("Show Price Chart", True)

timeframe = st.radio(
"Timeframe",
["Daily","Weekly","1M","3M","6M","1Y","2Y"],
horizontal=True
)

if timeframe=="Daily":
    hist=ticker.history(period="1d",interval="5m")
elif timeframe=="Weekly":
    hist=ticker.history(period="7d",interval="30m")
elif timeframe=="1M":
    hist=ticker.history(period="1mo")
elif timeframe=="3M":
    hist=ticker.history(period="3mo")
elif timeframe=="6M":
    hist=ticker.history(period="6mo")
elif timeframe=="1Y":
    hist=ticker.history(period="1y")
else:
    hist=ticker.history(period="2y")

# --------------------------------
# SCENARIO LAB
# --------------------------------

with st.expander("Scenario Lab", True):

    rerate = st.slider(
        "Re-Rating Multiple",
        1.0,
        30.0,
        5.0,
        0.1
    )

    scenario_price_p = price_p * rerate

    scenario_price_slider = st.slider(
        "Scenario Share Price (p)",
        0.1,
        500.0,
        scenario_price_p
    )

# --------------------------------
# DISCOVERY SIMULATOR
# --------------------------------

with st.expander("Walton Morant Discovery Simulator", True):

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

    st.write(f"Estimated Share Price from Discovery: **{estimated_price:.2f}p**")

# --------------------------------
# 3D DISCOVERY SURFACE
# --------------------------------

size_range = np.linspace(100,5000,30)
value_range = np.linspace(5,80,30)

X,Y = np.meshgrid(size_range,value_range)

Z = (X*Y*(ownership/100)*1_000_000)/shares_outstanding/100

fig3d = go.Figure(data=[go.Surface(
    x=X,
    y=Y,
    z=Z,
    colorscale="YlOrRd"
)])

fig3d.update_layout(
    title="Discovery Value Surface (Share Price p)",
    scene=dict(
        xaxis_title="Discovery Size (MMBO)",
        yaxis_title="Value per Barrel ($)",
        zaxis_title="Share Price (p)"
    ),
    height=500
)

st.plotly_chart(fig3d,use_container_width=True)

# --------------------------------
# HOLDINGS
# --------------------------------

with st.expander("Your Holding", True):

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

# --------------------------------
# VALUATION
# --------------------------------

scenario_price = scenario_price_slider / 100

scenario_market_cap = scenario_price * shares_outstanding

personal_current = current_shares * price
personal_scenario = scenario_shares * scenario_price

col1,col2 = st.columns(2)

with col1:

    st.metric(
        "Market Cap (Current)",
        f"£{market_cap/1e6:.2f}M"
    )

    st.metric(
        "Market Cap (Scenario)",
        f"£{scenario_market_cap/1e9:.2f}B"
    )

with col2:

    st.metric(
        "Personal Value (Current)",
        f"£{personal_current:,.0f}"
    )

    st.metric(
        "Personal Value (Scenario)",
        f"£{personal_scenario:,.0f}"
    )

# --------------------------------
# PRICE TARGET CHART
# --------------------------------

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist["Close"]*100,
    mode="lines",
    line=dict(color="gold",width=3),
    name="Price"
))

fig.add_hline(
    y=price_p,
    line_color="white",
    line_dash="dot",
    annotation_text=f"Current {price_p:.3f}p"
)

fig.add_hline(
    y=scenario_price_slider,
    line_color="red",
    line_dash="dash",
    annotation_text=f"Scenario {scenario_price_slider:.2f}p"
)

fig.update_layout(
height=350,
plot_bgcolor="#020617",
paper_bgcolor="#020617",
font=dict(color="white")
)

st.plotly_chart(fig,use_container_width=True)

# --------------------------------
# SCENARIO CARD
# --------------------------------

st.subheader("Share Scenario")

def create_card():

    img = Image.new("RGB",(800,800),(10,15,25))
    draw = ImageDraw.Draw(img)

    draw.text((50,50),"UOG Scenario Tool",fill="gold")

    draw.text((50,200),f"Current Price {price_p:.3f}p",fill="white")

    draw.text((50,250),f"Scenario Price {scenario_price_slider:.2f}p",fill="white")

    draw.text((50,400),"Market Cap",fill="gold")

    draw.text((50,450),f"Current £{market_cap:,.0f}",fill="white")

    draw.text((50,500),f"Scenario £{scenario_market_cap:,.0f}",fill="white")

    draw.text((50,650),"Personal Value",fill="gold")

    draw.text((50,700),f"Current £{personal_current:,.0f}",fill="white")

    draw.text((50,740),f"Scenario £{personal_scenario:,.0f}",fill="white")

    buf=io.BytesIO()
    img.save(buf,"PNG")

    return buf

if st.button("Generate Scenario Card"):

    img=create_card()

    st.download_button(
        "Download Scenario Image",
        data=img,
        file_name="uog_scenario.png",
        mime="image/png"
    )
