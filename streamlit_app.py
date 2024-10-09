import streamlit as st

st.set_page_config(
    page_title="Abhay's Company Accounts App",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': 'A personal project by abhaypai@vt.edu',
    }
)

financials_page = st.Page(
    page = "Pages/1_Company Financials.py",
    title = "Company Financials"
)

pg = st.navigation(
    {
        "Pages" : [financials_page]
    }
)

st.sidebar.text("Made by Abhay Pai")
st.sidebar.text("(@abhaypaii)")
pg.run()
