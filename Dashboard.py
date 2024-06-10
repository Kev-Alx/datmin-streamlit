import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Customer Behavior Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("Customer Behavior Analysis", anchor="customer-behavior-analysis")
# Upload file
uploaded_file = st.file_uploader("Please Import Your Transaction Data", type="txt")
if uploaded_file is None:
    data = pd.read_csv("data/data.csv", encoding='latin-1')
    df1 = preprocessing(data)
    st.subheader("Dataset")
    col1, col2, col3 = st.columns(3)
    col1.metric("Number of Transactions", df1.InvoiceNo.nunique())
    col2.metric("Number of Customers", df1.CustomerID.nunique())
    col3.metric("Average Revenue", f'${round(df1.Total.sum()/df1.InvoiceNo.nunique(),2)}')
    c = st.empty()
    # Add image
    url = "https://www.kaggle.com/carrie1/ecommerce-data"
    st.image("data/image.png", width=750)
    st.caption("🗳 Source : Kaggle [link](%s) " % url, unsafe_allow_html=True)

else:
    df1 = pd.read_csv(uploaded_file, encoding='latin-1')
    c = st.empty()
    c.dataframe(df1.head(7))