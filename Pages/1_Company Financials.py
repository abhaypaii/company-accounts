import streamlit as st
import yfinance as yf
import pandas as pd
from millify import millify

if 'exchanges' not in st.session_state:
    st.session_state.exchanges = []

if 'tickers' not in st.session_state:
    st.session_state.tickers = []

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

if 'disable' not in st.session_state:
    st.session_state.disable = True

if 'allsymbols' not in st.session_state:
    st.session_state.allsymbols = pd.DataFrame({
        'ticker' : [''],
        'name' : [''],
        'exchange' : ['']
    })

if 'allexchanges' not in st.session_state:
    st.session_state.allexchanges = []

st.session_state.all_symbols = pd.read_csv("Files/symbols.csv")
all_symbols = st.session_state.all_symbols

st.session_state.all_exchanges = pd.unique(all_symbols['exchange'])
all_exchanges = st.session_state.all_exchanges

st.session_state.exchanges = st.sidebar.multiselect("Select exchanges", all_exchanges, default = all_exchanges)
ex_companies = all_symbols[all_symbols['exchange'].isin(st.session_state.exchanges)]
ex_companies = ex_companies['ticker'] + " - " + ex_companies['name']
companies = ex_companies.reset_index(drop=True)

watchlist = st.sidebar.multiselect("Company Watchlist", companies)
st.session_state.watchlist = watchlist

if watchlist == []:
    st.session_state.disable = True
    st.session_state.tickers = []
else:
    st.session_state.disable = False
    st.session_state.tickers = [s.split(" - ")[0] for s in watchlist]
    stocks = yf.download(tickers=list(st.session_state.tickers), period='max')

def get_reports(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials
    financials.columns = financials.columns.year.astype(str)

    cashflow = stock.cashflow
    cashflow.columns = cashflow.columns.year.astype(str)

    balancesheet = stock.balancesheet
    balancesheet.columns = balancesheet.columns.year.astype(str)

    return financials, cashflow, balancesheet

c1,c2 = st.columns([1,1])
with c1:
    st.title("Financial Reports")
with c2:
    if st.session_state.tickers:
        display_ticker = st.selectbox("Ticker", st.session_state.tickers)
    else:
        display_ticker = st.selectbox("Ticker", ["No ticker selected"], disabled=True)
        st.error("Enter at least one symbol")


if not st.session_state.disable:
    financials, cashflow, balancesheet = get_reports(display_ticker)
    tab1, tab2, tab3 = st.tabs(['Financials', 'Cash Flow', 'Balance Sheet'])
    year1 = financials.columns[0]
    year0 = financials.columns[1]
    with tab1:
        try:
            financials.index = financials.index.str.strip()
            cols = st.columns(5)
            with cols[0]:
                st.metric("EBITDA", value = "$"+millify(financials.loc["Normalized EBITDA", year1], precision = 2), 
                        delta = millify(financials.loc["Normalized EBITDA", year1] - financials.loc["Normalized EBITDA", year0], precision = 2))
            with cols[1]:
                st.metric("Net Income", value = "$"+millify(financials.loc["Net Income", year1], precision = 2), 
                        delta = millify(financials.loc["Net Income", year1] - financials.loc["Net Income", year0], precision = 2))
            with cols[2]:
                st.metric("Total Revenue", value = "$"+millify(financials.loc["Total Revenue", year1], precision = 2), 
                        delta = millify(financials.loc["Total Revenue", year1] - financials.loc["Total Revenue", year0], precision = 2))
            with cols[3]:
                st.metric("Earnings Per Share", value = "$"+millify(financials.loc["Diluted EPS", year1], precision = 2), 
                        delta = millify(financials.loc["Diluted EPS", year1] - financials.loc["Diluted EPS", year0], precision = 2))
            with cols[4]:
                roe1 = financials.loc["Net Income", year1]/balancesheet.loc["Stockholders Equity", year1]
                roe0 = financials.loc["Net Income", year0]/balancesheet.loc["Stockholders Equity", year0]
                st.metric("Return on Equity", value = millify(roe1, precision = 2), 
                        delta = millify(roe1-roe0, precision = 2))
            with st.container(height=500):
                st.subheader("Annual Financial Report")
                st.table(financials)
        except:
            st.write(display_ticker+" does not have sufficient financial data")
    with tab2:
        try:
            cols = st.columns(5)
            with cols[0]:
                fcf1 = cashflow.loc['Free Cash Flow', year1]
                fcf0 = cashflow.loc['Free Cash Flow', year0]
                st.metric("Free Cash Flow", value = "$"+millify(fcf1, precision=2), delta = millify(fcf1-fcf0, precision=2) )
            with cols[1]:
                ocf1 = cashflow.loc['Operating Cash Flow', year1]
                ocf0 = cashflow.loc['Operating Cash Flow', year0]
                st.metric("Operating Cash Flow", value = "$"+millify(ocf1, precision=2), delta = millify(ocf1-ocf0, precision=2) )
            with cols[2]:
                icf1 = cashflow.loc['Investing Cash Flow', year1]
                icf0 = cashflow.loc['Investing Cash Flow', year0]
                st.metric("Investing Cash Flow", value = "$"+millify(icf1, precision=2), delta = millify(icf1-icf0, precision=2) )
            with cols[3]:
                fincf1 = cashflow.loc['Financing Cash Flow', year1]
                fincf0 = cashflow.loc['Financing Cash Flow', year0]
                st.metric("Financing Cash Flow", value = "$"+millify(fincf1, precision=2), delta = millify(fincf1-fincf0, precision=2) )
            with cols[4]:
                ncf1 = ocf1 + icf1 + fincf1
                ncf0 = ocf0 + icf0 + fincf0
                st.metric("Net Cash Flow", value = "$"+millify(ncf1, precision=2), delta = millify(ncf1-ncf0, precision=2) )
            with st.container(height=500):
                st.subheader("Statement of Cash Flow")
                st.table(cashflow)
        except:
            st.write(display_ticker+" does not have sufficient cash flow data")
    with tab3:
            try:
                cols = st.columns(6)
                with cols[0]:
                    se1 = balancesheet.loc["Stockholders Equity", year1]
                    se0 = balancesheet.loc["Stockholders Equity", year0]
                    st.metric("Stockholders Equity", value="$"+millify(balancesheet.loc["Stockholders Equity", year1], precision = 2), 
                            delta = millify(balancesheet.loc["Stockholders Equity", year1] - balancesheet.loc["Stockholders Equity", year0]))
                with cols[1]:
                    st.metric("Retained Earnings", value="$"+millify(balancesheet.loc["Retained Earnings", year1], precision = 2), 
                            delta = millify(balancesheet.loc["Retained Earnings", year1] - balancesheet.loc["Retained Earnings", year0]))
                with cols[2]:
                    ta1 = balancesheet.loc["Total Assets", year1]
                    ta0 = balancesheet.loc["Total Assets", year0]
                    tl1 = ta1-se1
                    tl0 = ta0-se0
                    st.metric("Total Assets", value="$"+millify(balancesheet.loc["Total Assets", year1], precision = 2), 
                            delta = millify(balancesheet.loc["Total Assets", year1] - balancesheet.loc["Total Assets", year0]))
                with cols[3]:
                    st.metric("Total Liabilities", value="$"+millify(tl1, precision = 2), 
                            delta = millify(tl1 - tl0, precision=2))
                    
                with cols[4]:
                    st.metric("Debt-to-Equity Ratio", value= millify(tl1/se1, precision = 2), 
                            delta = millify(tl1/se1 - tl0/se0, precision=2))
                with cols[5]:
                    ca1, cl1 = balancesheet.loc['Current Assets', year1], balancesheet.loc['Current Liabilities', year1]
                    ca0, cl0 = balancesheet.loc['Current Assets', year0], balancesheet.loc['Current Liabilities', year0]
                    st.metric("Current Ratio", value = millify(ca1/cl1, precision=2), delta = millify(ca1/cl1 - ca0/cl0, precision=2))

                with st.container(height=500):
                    st.subheader("Balance Sheet")
                    st.table(balancesheet)
            except:
                st.write(display_ticker+" does not have sufficient balance sheet data")
