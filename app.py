import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from PIL import Image, ImageDraw
import io

st.set_page_config(layout="centered")

# --------------------------------------------------
# PREMIUM DARK + GOLD STYLE
# --------------------------------------------------

st.markdown("""
<style>

body{
background: radial-gradient(circle at top,#0a0f1a,#020617);
color:white;
}

.block-container{
max-width:900px;
padding-top:1rem;
}

.banner{
background:linear-gradient(145deg,#111827,#020617);
border-radius:14px;
padding:16px;
text-align:center;

box-shadow:
0 0 40px rgba(255,200,0,0.25),
inset 0 0 15px rgba(255,200,0,0.08);

margin-bottom:18px;
}

.banner-title{
font-size:13px;
color:#9ca3af;
letter-spacing:3px;
}

.banner-value{
font-size:28px;
font-weight:700;
color:#ffd166;
margin-top:6px;
text-shadow:0 0 12px rgba(255,200,0,0.6);
}

.card{
background:linear-gradient(145deg,#1e293b,#0f172a);
border-radius:14px;
padding:16px;

box-shadow:
0 0 30px rgba(255,200,0,0.18),
inset 0 0 10px rgba(255,200,0,0.05);

margin-bottom:12px;
}

.metric{
font-size:32px;
font-weight:700;
color:#ffd166;
text-align:center;

text-shadow:0 0 10px rgba(255,200,0,0.5);
}

.section{
font-size:22px;
font-weight:700;
color:#ffd166;
margin-top:24px;
margin-bottom:10px;
}

</style>
""",unsafe_allow_html=True)

# --------------------------------------------------
# LIVE MARKET DATA
# --------------------------------------------------

ticker = yf.Ticker("UOG.L")

try:
    price = ticker.history(period="1d")["Close"].iloc[-1]
except:
    price = 0.0023

shares_outstanding = 4.66e9
market_cap = price * shares_outstanding

# --------------------------------------------------
# MARKET BANNER
# --------------------------------------------------

st.markdown(f"""
<div class="banner">

<div class="banner-title">LIVE UOG MARKET</div>

<div class="banner-value">
{price*100:.2f} GBX | £{market_cap:,.0f} | 4.66B shares
</div>

</div>
""",unsafe_allow_html=True)

# --------------------------------------------------
# PRICE CHART
# --------------------------------------------------

data = ticker.history(period="1mo")

fig = px.line(data,y="Close")

fig.update_traces(
line_color="#ffd166",
line_width=3
)

fig.update_layout(
template="plotly_dark",
plot_bgcolor="#020617",
paper_bgcolor="#020617",
height=240
)

st.plotly_chart(fig,use_container_width=True)

# --------------------------------------------------
# BASIN GRAPHIC
# --------------------------------------------------

st.image("hero.png",use_column_width=True)

# --------------------------------------------------
# SCENARIO LAB
# --------------------------------------------------

st.markdown('<div class="section">Scenario Lab</div>',unsafe_allow_html=True)

cos = st.slider("Chance of Success (COS)",10,50,35)

share_price = st.slider("Share Price Scenario (pence)",0.1,20.0,6.0)

shares_owned = st.slider(
"Personal Shares Owned",
1_000_000,
250_000_000,
1_000_000,
step=500_000
)

# --------------------------------------------------
# CALCULATIONS
# --------------------------------------------------

scenario_market_cap = (share_price/100) * shares_outstanding
personal_value = shares_owned * (share_price/100)
multiple = share_price / 0.23

# --------------------------------------------------
# RESULTS
# --------------------------------------------------

st.markdown('<div class="section">Scenario Results</div>',unsafe_allow_html=True)

col1,col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="card">
    <div class="metric">£{scenario_market_cap:,.0f}</div>
    <div style="text-align:center">Market Cap Scenario</div>
    </div>
    """,unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
    <div class="metric">£{personal_value:,.0f}</div>
    <div style="text-align:center">Personal Holding Value</div>
    </div>
    """,unsafe_allow_html=True)

# --------------------------------------------------
# RERATING BAR
# --------------------------------------------------

st.markdown('<div class="section">Multiple-X Re-Rating</div>',unsafe_allow_html=True)

st.progress(min(multiple/30,1.0))

st.write(f"**{multiple:.1f}× vs current price (0.23p)**")

# --------------------------------------------------
# COS → VALUATION CURVE
# --------------------------------------------------

cos_values = list(range(10,51))

values=[]

for c in cos_values:
    cap = scenario_market_cap * (c/50)
    values.append(cap)

df = pd.DataFrame({
"COS":cos_values,
"MarketCap":values
})

fig2 = px.line(df,x="COS",y="MarketCap")

fig2.update_traces(line_color="#ffd166",line_width=3)

fig2.update_layout(
template="plotly_dark",
plot_bgcolor="#020617",
paper_bgcolor="#020617",
height=300
)

st.plotly_chart(fig2,use_container_width=True)

# --------------------------------------------------
# QUICK SCENARIOS
# --------------------------------------------------

col1,col2,col3 = st.columns(3)

col1.button("5p → £233M")
col2.button("10p → £466M")
col3.button("15p → £699M")

# --------------------------------------------------
# SHAREABLE SCENARIO CARD
# --------------------------------------------------

st.markdown('<div class="section">Share Scenario</div>',unsafe_allow_html=True)

def create_scenario_card():

    img = Image.new("RGB",(800,800),(10,15,25))
    draw = ImageDraw.Draw(img)

    draw.text((50,50),"Walton Morant Scenario",fill=(255,200,80))

    draw.text((50,150),f"COS: {cos}%",fill="white")
    draw.text((50,200),f"Share Price: {share_price}p",fill="white")
    draw.text((50,250),f"Shares Owned: {shares_owned:,}",fill="white")

    draw.text((50,380),"Market Cap Scenario",fill=(255,200,80))
    draw.text((50,420),f"£{scenario_market_cap:,.0f}",fill="white")

    draw.text((50,520),"Personal Holding Value",fill=(255,200,80))
    draw.text((50,560),f"£{personal_value:,.0f}",fill="white")

    draw.text((50,660),f"{multiple:.1f}× vs current price",fill="white")

    buffer = io.BytesIO()
    img.save(buffer,"PNG")

    return buffer

if st.button("Generate Shareable Scenario Card"):

    img = create_scenario_card()

    st.download_button(
        label="Download Scenario Image",
        data=img,
        file_name="uog_scenario.png",
        mime="image/png"
    )
