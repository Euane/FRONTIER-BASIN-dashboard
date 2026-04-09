import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")

st.title("Walton-Morant Exploration Intelligence Platform")

# GLOBAL ASSUMPTIONS

st.sidebar.header("Global Assumptions")

value_per_barrel = st.sidebar.slider("Value per Barrel ($)",3,12,5)

shares_outstanding = st.sidebar.number_input(
"Shares Outstanding",
value=4.66e9
)

usd_gbp = st.sidebar.slider("USD → GBP",0.6,1.0,0.8)

# MARKET DATA

st.header("UOG Market Price")

try:
    ticker = yf.Ticker("UOG.L")
    hist = ticker.history(period="1mo")
    st.line_chart(hist["Close"])
except:
    st.write("Market data unavailable")

# BASIN STRUCTURE

st.header("Basin Resources")

drill_ready = st.slider("Drill Ready (Billion bbl)",0.1,2.0,0.85)
major_leads = st.slider("Major Leads (Billion bbl)",0.5,5.0,3.0)
additional = st.slider("Additional Leads (Billion bbl)",0.5,5.0,3.2)

basin = pd.DataFrame({
"Category":["Drill Ready","Major Leads","Additional Leads"],
"Barrels":[drill_ready,major_leads,additional]
})

fig = px.bar(
basin,
x="Category",
y="Barrels",
title="Basin Resource Structure (Billion Barrels)"
)

st.plotly_chart(fig,use_container_width=True)

# PROSPECT PORTFOLIO

st.header("Prospect Portfolio Model")

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

st.metric(
"Expected Portfolio Value ($M)",
round(portfolio_value,1)
)

fig2 = px.bar(
prospects,
x="Prospect",
y="Risked_Value_$M",
title="Risked Value by Prospect"
)

st.plotly_chart(fig2,use_container_width=True)

# DISCOVERY SIMULATOR

st.header("Discovery Simulator")

discovery_size = st.slider("Discovery Size (MMBO)",100,2000,500)
discovery_value = st.slider("Value per Barrel ($)",3,12,6)

unrisked = discovery_size * discovery_value

cos = st.slider("Chance of Success (%)",5,40,20)

risked = unrisked * (cos/100)

st.metric("Risked Discovery Value ($M)",risked)

# SHARE PRICE

st.header("Share Price Conversion")

risked_gbp = risked * usd_gbp * 1e6
share_price = risked_gbp / shares_outstanding

st.metric("Estimated Share Price",f"{share_price*100:.2f}p")

# TAKEOVER SCENARIOS

st.header("Takeover Scenarios")

take100 = (100e6 / shares_outstanding)*100
take300 = (300e6 / shares_outstanding)*100

table = pd.DataFrame({
"Company Value":["£100M","£300M"],
"Share Price (pence)":[take100,take300]
})

st.table(table)

# PERSONAL HOLDING

st.header("Personal Holding Calculator")

shares_owned = st.number_input(
"Shares Owned",
value=18500000
)

future_price = st.slider(
"Future Share Price (pence)",
0.1,20.0,5.0
)

holding_value = shares_owned * (future_price/100)

st.metric("Holding Value (£)",f"{holding_value:,.0f}")
