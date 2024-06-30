import numpy as np 
import pandas as pd
import streamlit as st 
from mlxtend.frequent_patterns import apriori, association_rules

st.set_page_config(
    page_title="Market Basket Analysis Dashboard",
    layout="wide",
)

@st.cache_data
def get_data():
    df = pd.read_excel('harve.xlsx').head(260000)
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df[df['Itemname'].notna()]
    df = df[df['Quantity'] > 0]
    df = df[df['Price'] > 0]
    df = df.drop(columns=['CustomerID', 'Country'])
    
    def get_season(date):
        if pd.isnull(date):
            return 'Unknown'
        month = date.month
        if month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Autumn'
        else:
            return 'Winter'

    def get_weekend_weekdays(date):
        if pd.isnull(date):
            return 'Unknown'
        return 'Weekend' if date.weekday() >= 5 else 'Weekday'

    df["Season"] = df["Date"].apply(get_season)    
    df["Weekday"] = df["Date"].apply(get_weekend_weekdays)
    
    # Data cleaning (tidak ditampilkan di dashboard)
    
    return df

def perform_mba(df, min_support=0.01, min_confidence=0.5):
    item_counts = df['Itemname'].value_counts(ascending=False)
    filtered_items = item_counts.loc[item_counts > 1].reset_index()['index']
    df = df[df['Itemname'].isin(filtered_items)]

    bill_counts = df['BillNo'].value_counts(ascending=False)
    filtered_bills = bill_counts.loc[bill_counts > 1].reset_index()['index']
    df = df[df['BillNo'].isin(filtered_bills)]
    
    pivot_table = pd.pivot_table(df[['BillNo','Itemname']], index='BillNo', columns='Itemname', aggfunc=lambda x: True, fill_value=False)
    
    frequent_itemsets = apriori(pivot_table, min_support=min_support,use_colnames=True)
    
    rules = association_rules(frequent_itemsets, "confidence", min_threshold = min_confidence)
    
    return rules.sort_values(by=['confidence', 'support'])

df = get_data()
st.title("Market Basket Analysis Dashboard")

# Filters
item_filter = st.selectbox("Select the Item", ['All'] + list(pd.unique(df["Itemname"])))
season_filter = st.selectbox("Select the Season", ['All'] + ['Summer', 'Spring', 'Autumn', 'Winter'])
weekday_filter = st.selectbox("Select the Weekday", ['All'] + ['Weekday', 'Weekend'])

# Filter data
filtered_df = df.copy()
if season_filter != 'All':
    filtered_df = filtered_df[filtered_df["Season"] == season_filter]
if weekday_filter != 'All':
    filtered_df = filtered_df[filtered_df["Weekday"] == weekday_filter]

# Perform MBA on filtered data
rules = perform_mba(filtered_df)
# rules = df
if item_filter != 'All':
    rules = rules[rules['antecedents'].apply(lambda x: item_filter in x)]
# Display association rules
st.subheader("Association Rules")
st.dataframe(rules)

st.subheader("Top 5 Cross-sell Rules")
crosssell_rules = rules[rules['lift'] > 1].sort_values('support', ascending=False).head(5)
st.dataframe(crosssell_rules)

# Display top 5 upsell rules
st.subheader("Top 5 Upsell Rules")
upselling_rules = rules[(rules['antecedents'].apply(len) == 1) & (rules['consequents'].apply(len) > 1)]

upselling_rules = upselling_rules.sort_values(by=['confidence', 'support'], ascending=False).head(5)
st.dataframe(upselling_rules)

# Display interpretation
if not rules.empty:
    antecedent = rules.iloc[0]['antecedents']
    consequent = rules.iloc[0]['consequents']
    st.write(f"Jika membeli {antecedent} pada {season_filter} di {weekday_filter}, maka kemungkinan membeli {consequent} secara bersamaan.")
else:
    st.write("Tidak ada rules yang ditemukan untuk kombinasi filter yang dipilih.")