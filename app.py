import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import feedparser

st.set_page_config(page_title="Exploration Intelligence Terminal", layout="wide")

# ---------------- MOBILE UI ----------------

st.markdown("""
<style>

body {background:#020617;color:#FFD700;}

.block-container{
padding-top:0.2rem;
padding-bottom:0.2rem;
}

.ticker{
position:sticky;
top:0;
background:#111827;
padding:4px;
border-bottom:2px solid gold;
font-size:12px;
font-weight:bold;
z-index:999;
}


div[data-baseweb="slider"] > div > div{
background:white !important;
height:5px;
}

div[data-baseweb="slider"] span{
background:gold !important;
}

div[data-baseweb="slider"] div[role="slider"]{
background:gold !important;
border:2px solid white !important;
}

[data-testid="stDataFrame"]{
font-size:12px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- DATA FUNCTIONS ----------------

@st.cache_resource
def get_ticker(ticker):
    return yf.Ticker(ticker)

@st.cache_data(ttl=300)
def get_intraday(ticker):
    try:
        return yf.Ticker(ticker).history(period="1d", interval="5m")
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_history(ticker, period="6mo"):
    try:
        return yf.Ticker(ticker).history(period=period)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=86400)
def get_shares(ticker):

    try:
        tk = get_ticker(ticker)

        fast = tk.fast_info
        shares = fast.get("sharesOutstanding")

        if shares and shares > 0:
            return shares

    except:
        pass

    # fallback shares (prevents crashes)
    fallback = {
        "UOG.L": 4.42e9,
        "ECO.L": 2.42e9,
        "PANR.L": 1.20e9,
        "88E.L": 8.90e9,
        "RECAF": 2.10e8
    }

    return fallback.get(ticker, 1e9)

# ---------------- CONTROL BAR STATE ----------------

if "tf" not in st.session_state:
    st.session_state.tf = "6M"

if "ma5" not in st.session_state:
    st.session_state.ma5 = False

if "ma20" not in st.session_state:
    st.session_state.ma20 = False

if "ma50" not in st.session_state:
    st.session_state.ma50 = False

if "vol" not in st.session_state:
    st.session_state.vol = False

# ---------------- STOCK SELECT ----------------



ticker_symbol = st.selectbox(
"Stock",
["UOG.L","ECO.L","PANR.L","88E.L","RECAF"]
)


Currency_symbol = st.selectbox(
"Curency",
["USD","GBP","CAD","EUR","JMD"]
)



intraday = get_intraday(ticker_symbol)

if not intraday.empty:
    price_p = intraday["Close"].iloc[-1]
else:
    price_p = 0.25

price_gbp = price_p / 100

shares_outstanding = get_shares(ticker_symbol)

market_cap = price_gbp * shares_outstanding

# ---------------- HEADER ----------------

st.markdown(f"""

{ticker_symbol} | {price_p:.3f}p | Shares {shares_outstanding/1e9:.2f}B | MCap £{market_cap/1e6:.2f}M | Pe £{market_cap/1e6:.2f}M

""", unsafe_allow_html=True)


# ---------------- HAMBURGER MENU ----------------

if "menu_open" not in st.session_state:
    st.session_state.menu_open=False

if "page" not in st.session_state:
    st.session_state.page="Dashboard"

col1,col2=st.columns([1,10])

with col1:
    if st.button("☰"):
        st.session_state.menu_open=not st.session_state.menu_open

pages=[
"Dashboard",
"Market Activity",
"Your Portfolio",
"Discovery Simulator",
"Multi-Ticker Comparison",
"Drilling Catalysts",
"RNS Alerts",
"Exploration Intelligence",
"Exploration Map",
"Basin Bubble Map"
]

if st.session_state.menu_open:
    for p in pages:
        if st.button(p):
            st.session_state.page=p
            st.session_state.menu_open=False

page=st.session_state.page

# ---------------- DASHBOARD ----------------

if page=="Dashboard":

    period_map={
    "1D":"1d",
    "1W":"7d",
    "1M":"1mo",
    "3M":"3mo",
    "6M":"6mo",
    "1Y":"1y"
    }

    hist=get_history(ticker_symbol,period_map[st.session_state.tf])

    if not hist.empty:

        hist["MA5"]=hist["Close"].rolling(5).mean()
        hist["MA20"]=hist["Close"].rolling(20).mean()
        hist["MA50"]=hist["Close"].rolling(50).mean()

        fig=go.Figure()

        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist["Open"],
            high=hist["High"],
            low=hist["Low"],
            close=hist["Close"]
        ))

        if st.session_state.ma5:
            fig.add_trace(go.Scatter(x=hist.index,y=hist["MA5"],line=dict(color="lime")))

        if st.session_state.ma20:
            fig.add_trace(go.Scatter(x=hist.index,y=hist["MA20"],line=dict(color="gold")))

        if st.session_state.ma50:
            fig.add_trace(go.Scatter(x=hist.index,y=hist["MA50"],line=dict(color="orange")))

        if st.session_state.vol:
            fig.add_trace(go.Bar(x=hist.index,y=hist["Volume"],yaxis="y2"))
            fig.update_layout(yaxis2=dict(overlaying="y",side="right"))

        st.plotly_chart(fig,use_container_width=True)

# ---------------- MARKET ACTIVITY ----------------

elif page=="Market Activity":

    hist=get_history(ticker_symbol,"5d")

    if not hist.empty:

        hist["Change"]=hist["Close"].pct_change()*100
        hist["Trade"]=np.where(hist["Change"]>0,"Buy","Sell")

        st.dataframe(hist[["Close","Volume","Change","Trade"]])

# ---------------- PORTFOLIO ----------------

elif page=="Your Portfolio":

    shares_owned=st.number_input("Shares",value=1000000)

    value=shares_owned*price_gbp

    st.markdown(f"### Holding Value £{value:,.0f}")

    reratings=[1,1.25,1.5,2,2.25,2.5,3,3.5,4,4.5,5,6,7,10,15,20,25]

    data=[]

    for r in reratings:

        new_price=price_p*r
        val=shares_owned*(new_price/100)

        data.append([f"{r}x",f"{new_price:.2f}p",f"£{val:,.0f}"])

    st.table(pd.DataFrame(data,columns=["Rerating","Price","Value"]))

# ---------------- DISCOVERY SIMULATOR ----------------

elif page=="Discovery Simulator":

    discovery=st.slider("Discovery MMBO",100,5000,1000)
    oil_price=st.slider("Oil Price $",40,120,70)
    cos=st.slider("Chance of Success %",5,80,20)

    discovery_value=discovery*oil_price*0.52*1_000_000

    price_est_p=(discovery_value/shares_outstanding)*100

    expected=price_est_p*(cos/100)

    st.write("Discovery Price",f"{price_est_p:.2f}p")
    st.write("Probability Weighted",f"{expected:.2f}p")

# ---------------- MULTI TICKER ----------------

elif page=="Multi-Ticker Comparison":

    tickers=["UOG.L","ECO.L","PANR.L","88E.L","RECAF"]

    oil_price=st.slider("Oil Price",40,120,70)

    ladder=[100,500,1000,2000,5000]

    fig=go.Figure()

    for t in tickers:

        shares=get_shares(t)

        prices=[(size*oil_price*0.52*1_000_000/shares)*100 for size in ladder]

        fig.add_trace(go.Scatter(x=ladder,y=prices,mode="lines+markers",name=t))

    st.plotly_chart(fig,use_container_width=True)

# ---------------- DRILLING ----------------

elif page=="Drilling Catalysts":

    df=pd.DataFrame({
    "Company":["UOG","Eco Atlantic","Pantheon","88 Energy","ReconAfrica"],
    "Prospect":["Walton Morant","Orinduik","Kodiak","Hickory","Kavango"],
    "Stage":["Planning","Drilling","Testing","Drilling","Exploration"]
    })

    st.dataframe(df)

# ---------------- RNS ----------------

elif page=="RNS Alerts":

    feed=feedparser.parse("https://www.investegate.co.uk/Rss.aspx")

    for entry in feed.entries[:20]:

        if ticker_symbol.split(".")[0].lower() in entry.title.lower():

            st.markdown("🚨 **RNS Alert**")
            st.write(entry.title)
            st.write(entry.link)
            st.divider()

# ---------------- NEWS ----------------

elif page=="Exploration Intelligence":

    keywords=["discovery","drilling","well","spud","farm","seismic"]

    feeds={
    "Energy Voice":"https://www.energyvoice.com/feed/",
    "Rigzone":"https://www.rigzone.com/news/rss/rigzone_headlines/",
    "OilPrice":"https://oilprice.com/rss/main"
    }

    for name,url in feeds.items():

        feed=feedparser.parse(url)

        for entry in feed.entries:

            title=entry.title.lower()

            if any(k in title for k in keywords):

                st.markdown(f"**{entry.title}**")
                st.write(entry.link)
                st.divider()

# ---------------- MAP ----------------

elif page=="Exploration Map":

    df=pd.DataFrame({
    "Company":["UOG","Eco Atlantic","Pantheon","88 Energy","ReconAfrica"],
    "Lat":[18.2,6.0,69.5,70.0,-18.5],
    "Lon":[-76.7,-57,-150,-148,20]
    })

    fig=go.Figure()

    fig.add_trace(go.Scattergeo(
    lon=df["Lon"],
    lat=df["Lat"],
    text=df["Company"],
    mode="markers",
    marker=dict(size=12,color="gold")
    ))

    st.plotly_chart(fig,use_container_width=True)

# ---------------- BASIN MAP ----------------

elif page=="Basin Bubble Map":

    df=pd.DataFrame({
    "Company":["UOG","Eco Atlantic","Pantheon","88 Energy","ReconAfrica"],
    "Lat":[18.2,6.0,69.5,70.0,-18.5],
    "Lon":[-76.7,-57,-150,-148,20],
    "Basin":[2.4,2.9,17,6,120]
    })

    fig=go.Figure()

    fig.add_trace(go.Scattergeo(
    lon=df["Lon"],
    lat=df["Lat"],
    text=df["Company"],
    mode="markers",
    marker=dict(size=df["Basin"]*0.5,color="gold")
    ))

    st.plotly_chart(fig,use_container_width=True)

# ---------------- BOTTOM CONTROL BAR ----------------

col1,col2,col3,col4,col5=st.columns(5)

with col1:
    st.session_state.tf=st.selectbox("TF",["1D","1W","1M","3M","6M","1Y"],index=4,label_visibility="collapsed")

with col2:
    st.session_state.ma5=st.checkbox("MA5",value=st.session_state.ma5)

with col3:
    st.session_state.ma20=st.checkbox("MA20",value=st.session_state.ma20)

with col4:
    st.session_state.ma50=st.checkbox("MA50",value=st.session_state.ma50)

with col5:
    st.session_state.vol=st.checkbox("Vol",value=st.session_state.vol)
