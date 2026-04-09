import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.markdown(
"""
<style>
.main-title {
font-size:42px;
font-weight:700;
color:white;
text-align:center;
}
.subtitle {
font-size:18px;
text-align:center;
color:#d9b46c;
}
.metric-box {
background-color:#1f2b3a;
padding:15px;
border-radius:10px;
text-align:center;
}
</style>
""",
unsafe_allow_html=True
)

st.markdown(
'<div class="main-title">Walton-Morant Exploration Intelligence Hub</div>',
unsafe_allow_html=True
)

st.markdown(
'<div class="subtitle">Interactive dashboard for investment analysis</div>',
unsafe_allow_html=True
)

st.divider()

# ---------------------------------------------------
# GLOBAL ASSUMPTIONS
# ---------------------------------------------------

st.sidebar.header("Model Assumptions")

value_per_barrel = st.sidebar.slider("Value per Barrel ($)",3,12,5)

shares_outstanding = st.sidebar.number_input(
"Shares Outstanding",
value=4.66e9
)

usd_gbp = st.sidebar.slider("USD → GBP",0.6,1.0,0.8)

# ---------------------------------------------------
# TOP DASHBOARD ROW
# ---------------------------------------------------

col1,col2,col3 = st.columns(3)

# Basin summary

with col1:

    st.subheader("Basin Resource Summary")

    drill_ready = st.slider("Drill Ready Prospects (MMBO)",200,1200,850)

    basin_total = st.slider("Total Basin Potential (Billion bbl)",2.0,10.0,7.0)

    basin_df = pd.DataFrame({
    "Category":["Drill Ready","Remaining Basin"],
    "Value":[drill_ready/1000, basin_total - (drill_ready/1000)]
    })

    fig = px.bar(
    basin_df,
    x="Category",
    y="Value",
    title="Basin Potential (Billion Barrels)"
    )

    st.plotly_chart(fig,use_container_width=True)

# Market price

with col2:

    st.subheader("UOG Market Price")

    try:

        ticker = yf.Ticker("UOG.L")
        hist = ticker.history(period="1mo")

        st.metric("Current Price (£)",round(hist["Close"].iloc[-1],4))

        st.line_chart(hist["Close"])

    except:

        st.write("Market data unavailable")

# Scenario simulator

with col3:

    st.subheader("Quick Scenario Simulator")

    discovery_size = st.slider("Discovery Size (MMBO)",100,2000,300)

    discovery_value = st.slider("Value per Barrel ($)",3,12,5)

    cos = st.slider("Chance of Success (%)",5,40,20)

    estimated_value = discovery_size * discovery_value
    risked_value = estimated_value * (cos/100)

    st.metric("Estimated Discovery Value ($M)",estimated_value)
    st.metric("Risked Discovery Value ($M)",risked_value)

# ---------------------------------------------------
# PROSPECT PORTFOLIO
# ---------------------------------------------------

st.divider()

st.header("Walton-Morant Risked Prospects")

prospects = pd.DataFrame({

"Prospect":["Colibri","Oriole","Streamertail"],
"Resource_MMBO":[406,220,221],
"COS":[0.19,0.16,0.15]

})

gb = GridOptionsBuilder.from_dataframe(prospects)
gb.configure_default_column(editable=True)

grid = AgGrid(
prospects,
gridOptions=gb.build(),
update_mode="MODEL_CHANGED"
)

prospects = pd.DataFrame(grid["data"])

prospects["Unrisked_Value_$M"] = prospects["Resource_MMBO"] * value_per_barrel
prospects["Risked_Value_$M"] = prospects["Unrisked_Value_$M"] * prospects["COS"]

portfolio_value = prospects["Risked_Value_$M"].sum()

st.metric("Total Risked Prospect Value ($M)",round(portfolio_value,1))

fig2 = px.bar(
prospects,
x="Prospect",
y="Risked_Value_$M",
title="Risked Prospect Values"
)

st.plotly_chart(fig2,use_container_width=True)

# ---------------------------------------------------
# MARKET CAP VS BASIN SCALE
# ---------------------------------------------------

st.divider()

st.header("Market Cap vs Basin Scale")

market_cap = st.slider("Market Cap (£M)",1,500,7)

comparison = pd.DataFrame({

"Metric":["Market Cap (£M)","Drill Ready (MMBO)","Basin Potential (MMBO)"],
"Value":[market_cap,drill_ready,basin_total*1000]

})

fig3 = px.bar(comparison,x="Metric",y="Value")

st.plotly_chart(fig3,use_container_width=True)

# ---------------------------------------------------
# SHARE VALUE
# ---------------------------------------------------

st.divider()

st.header("Personal Share Value")

shares_owned = st.number_input("Shares Owned",value=18500000)

future_price = st.slider("Future Share Price (pence)",0.1,20.0,2.0)

holding_value = shares_owned * (future_price/100)

st.metric("Holding Value (£)",f"{holding_value:,.0f}")

# ---------------------------------------------------
# TAKEOVER SCENARIOS
# ---------------------------------------------------

st.divider()

st.header("Takeover Scenarios")

take100 = (100e6 / shares_outstanding)*100
take300 = (300e6 / shares_outstanding)*100

table = pd.DataFrame({

"Company Value":["£100M","£300M"],
"Share Price (pence)":[take100,take300]

})

st.table(table)
