import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import feedparser

st.set_page_config(page_title="Exploration Valuation Dashboard", layout="wide")

# ---------- GLOBAL STYLE ----------

st.markdown("""
<style>

body{
background:#020617;
color:#FFD700;
}

.block-container{
padding-top:1rem;
padding-bottom:1rem;
}

/* ticker */

.ticker{
position:sticky;
top:0;
background:#111827;
padding:8px;
font-weight:bold;
border-bottom:2px solid gold;
z-index:999;
}

/* slider styling */

div[data-baseweb="slider"] > div > div{
background:white !important;
height:6px;
}

div[data-baseweb="slider"] span{
background:gold !important;
}

div[data-baseweb="slider"] div[role="slider"]{
background:gold !important;
border:2px solid white !important;
}

/* reduce label spacing */

.stSlider label{
margin-bottom:-8px;
}

/* charts */

.js-plotly-plot{
box-shadow:0 0 10px rgba(255,215,0,0.4);
border-radius:8px;
}

</style>
""", unsafe_allow_html=True)

# ---------- STOCK SELECT ----------

ticker_symbol = st.selectbox(
"Select Exploration Stock",
["UOG.L","ECO.L","PANR.L","88E.L","RECAF"]
)

ticker = yf.Ticker(ticker_symbol)

# ---------- MARKET DATA ----------

intraday = ticker.history(period="1d", interval="5m")

price = intraday["Close"].iloc[-1]
prev_price = intraday["Close"].iloc[0]

price_p = price * 100

shares_outstanding = 4.66e9
market_cap = price * shares_outstanding

volume_today = intraday["Volume"].sum()
change_pct = ((price-prev_price)/prev_price)*100

# ---------- FLOATING TICKER ----------

st.markdown(f"""
<div class="ticker">
{ticker_symbol} | Price {price_p:.3f}p | Change {change_pct:+.2f}% |
Volume {volume_today:,.0f} | Market Cap £{market_cap/1e6:.2f}M
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------- MENU ----------

menu = st.sidebar.selectbox(
"Menu",
[
"Dashboard",
"Your Portfolio",
"Market Activity",
"Discovery Simulator",
"Live News",
"Exploration Intelligence Feed",
"Global Exploration Map"
]
)

# ---------- DASHBOARD ----------

if menu == "Dashboard":

    hist = ticker.history(period="6mo")

    hist["MA5"] = hist["Close"].rolling(5).mean()
    hist["MA20"] = hist["Close"].rolling(20).mean()
    hist["MA50"] = hist["Close"].rolling(50).mean()

    show_ma5 = st.checkbox("MA5",True)
    show_ma20 = st.checkbox("MA20",True)
    show_ma50 = st.checkbox("MA50",True)
    show_volume = st.checkbox("Volume",True)

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist["Open"],
        high=hist["High"],
        low=hist["Low"],
        close=hist["Close"]
    ))

    if show_ma5:
        fig.add_trace(go.Scatter(x=hist.index,y=hist["MA5"],line=dict(color="lime"),name="MA5"))

    if show_ma20:
        fig.add_trace(go.Scatter(x=hist.index,y=hist["MA20"],line=dict(color="gold"),name="MA20"))

    if show_ma50:
        fig.add_trace(go.Scatter(x=hist.index,y=hist["MA50"],line=dict(color="orange"),name="MA50"))

    if show_volume:
        fig.add_trace(go.Bar(x=hist.index,y=hist["Volume"],name="Volume",yaxis="y2"))
        fig.update_layout(yaxis2=dict(overlaying="y",side="right"))

    st.plotly_chart(fig,use_container_width=True)

# ---------- PORTFOLIO ----------

elif menu == "Your Portfolio":

    shares = st.number_input("Your Shares",value=1000000)

    rerate = st.select_slider(
    "Rerating Multiple",
    options=[1,2,3,4,5,7,10,15,20,25]
    )

    scenario_price = price * rerate

    scenario_value = shares * scenario_price
    current_value = shares * price

    pct = ((scenario_value-current_value)/current_value)*100

    st.write(f"Current Value: £{current_value:,.0f}")
    st.write(f"Scenario Value: £{scenario_value:,.0f}")
    st.write(f"Change: {pct:.1f}%")

# ---------- MARKET ACTIVITY ----------

elif menu == "Market Activity":

    hist = ticker.history(period="5d", interval="5m")

    hist["Prev"]=hist["Close"].shift(1)

    buy=(hist["Close"]>hist["Prev"]).sum()
    sell=(hist["Close"]<hist["Prev"]).sum()

    total=buy+sell

    buy_pct=buy/total*100
    sell_pct=sell/total*100

    st.progress(buy_pct/100)

    st.write(f"BUY {buy_pct:.1f}%")
    st.write(f"SELL {sell_pct:.1f}%")

# ---------- DISCOVERY SIMULATOR ----------

elif menu == "Discovery Simulator":

    discovery = st.slider("Discovery Size (MMBO)",100,5000,1000)

    oil_price = st.slider("Oil Price ($)",40,120,70)

    cos = st.slider("Chance of Success (%)",5,80,20)

    value = discovery * oil_price * 0.52 * 1_000_000

    price_est = (value/shares_outstanding) * 100
    expected = price_est * (cos/100)

    # ---------- COMPACT VALUE ROW ----------

    st.markdown(f"""
    <div style="
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:12px;
    font-size:13px;
    margin-top:-6px;
    margin-bottom:-6px;
    ">

    <div>
    <span style="color:white">Discovery Price</span><br>
    <b style="color:gold">{price_est:.2f}p</b>
    </div>

    <div>
    <span style="color:white">Probability Weighted</span><br>
    <b style="color:gold">{expected:.2f}p</b>
    </div>

    <div>
    <span style="color:white">Oil Price</span><br>
    <b style="color:gold">${oil_price}</b>
    </div>

    <div>
    <span style="color:white">COS</span><br>
    <b style="color:gold">{cos}%</b>
    </div>

    </div>
    """, unsafe_allow_html=True)

    # ---------- VALUE LADDER ----------

    ladder_sizes=[100,500,1000,2000,5000]
    ladder_prices=[]

    for size in ladder_sizes:
        value=size*oil_price*0.52*1_000_000
        ladder_prices.append((value/shares_outstanding)*100)

    fig=go.Figure()

    fig.add_trace(go.Bar(
        x=[str(x)+" MMBO" for x in ladder_sizes],
        y=ladder_prices,
        marker_color="gold"
    ))

    fig.add_hline(
        y=price_p,
        line_dash="dash",
        line_color="red",
        annotation_text="Current Price"
    )

    fig.update_layout(
        height=420,
        margin=dict(t=10,b=10,l=10,r=10),
        plot_bgcolor="#020617",
        paper_bgcolor="#020617",
        font=dict(color="#FFD700")
    )

    st.plotly_chart(fig,use_container_width=True)

# ---------- LIVE NEWS ----------

elif menu == "Live News":

    news=ticker.news

    keywords=["discovery","drilling","flow test","farm-out","resource"]

    for article in news[:10]:

        title=article.get("title","")
        link=article.get("link","")

        if any(word in title.lower() for word in keywords):
            st.markdown("### 🚨 Exploration Alert")

        st.markdown(f"{title}")
        st.markdown(f"[Read article]({link})")
        st.divider()

# ---------- RSS FEED ----------

elif menu == "Exploration Intelligence Feed":

    feeds={
    "Energy Voice":"https://www.energyvoice.com/feed/",
    "Offshore Magazine":"https://www.offshore-mag.com/rss"
    }

    for source,url in feeds.items():

        st.subheader(source)

        feed=feedparser.parse(url)

        for entry in feed.entries[:5]:

            st.write(entry.title)
            st.write(entry.link)
            st.divider()

# ---------- GLOBAL MAP ----------

elif menu == "Global Exploration Map":

    basin_locations = pd.DataFrame({

    "Company":[
    "United Oil & Gas",
    "Eco Atlantic",
    "Pantheon Resources",
    "88 Energy",
    "ReconAfrica"
    ],

    "Latitude":[18.2,6.0,69.5,70.0,-18.5],
    "Longitude":[-76.7,-57.0,-150.0,-148.0,20.0]

    })

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        lon = basin_locations["Longitude"],
        lat = basin_locations["Latitude"],
        text = basin_locations["Company"],
        mode = "markers",
        marker = dict(size = 12,color = "gold")
    ))

    st.plotly_chart(fig,use_container_width=True)
