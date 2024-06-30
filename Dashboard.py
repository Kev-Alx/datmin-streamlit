import numpy as np 
import pandas as pd
import streamlit as st 
from mlxtend.frequent_patterns import apriori, association_rules

st.set_page_config(
    page_title="Market Basket Analysis Dashboard",
    page_icon="✅",
    layout="wide",
)

@st.cache_data
def get_data():
    df = pd.read_excel('harve.xlsx')
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
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
    df = df[df['Itemname'].notna()]
    df = df[df['Quantity'] > 0]
    df = df[df['Price'] > 0]
    df['Total_Price'] = df['Quantity'] * df['Price']
    
    return df

def perform_mba(df, min_support=0.01, min_confidence=0.5):
    # Prepare data for MBA
    basket = df.groupby(['BillNo', 'Itemname'])['Quantity'].sum().unstack().fillna(0)
    basket = basket.applymap(lambda x: 1 if x > 0 else 0)
    
    # Generate frequent itemsets and association rules
    frequent_itemsets = apriori(basket, min_support=min_support, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    
    return rules

df = get_data()

st.title("Market Basket Analysis Dashboard")

# Filters
item_filter = st.selectbox("Select the Item", ['All'] + list(pd.unique(df["Itemname"])))
season_filter = st.selectbox("Select the Season", ['All'] + list(pd.unique(df["Season"])))
weekday_filter = st.selectbox("Select the Weekday", ['All'] + list(pd.unique(df["Weekday"])))

# Filter data
filtered_df = df.copy()
if item_filter != 'All':
    filtered_df = filtered_df[filtered_df["Itemname"] == item_filter]
if season_filter != 'All':
    filtered_df = filtered_df[filtered_df["Season"] == season_filter]
if weekday_filter != 'All':
    filtered_df = filtered_df[filtered_df["Weekday"] == weekday_filter]

# Perform MBA on filtered data
rules = perform_mba(filtered_df)

# Display association rules
st.subheader("Association Rules")
st.dataframe(rules)

# Display top 5 upsell rules
st.subheader("Top 5 Upsell Rules")
upsell_rules = rules[rules['lift'] > 1].sort_values('lift', ascending=False).head(5)
st.dataframe(upsell_rules)

# Display top 5 cross-sell rules
st.subheader("Top 5 Cross-sell Rules")
crosssell_rules = rules[rules['lift'] > 1].sort_values('support', ascending=False).head(5)
st.dataframe(crosssell_rules)

# Display interpretation
if not rules.empty:
    antecedent = rules.iloc[0]['antecedents']
    consequent = rules.iloc[0]['consequents']
    st.write(f"Jika membeli {antecedent} pada {season_filter} di {weekday_filter}, maka kemungkinan membeli {consequent} secara bersamaan.")
else:
    st.write("Tidak ada rules yang ditemukan untuk kombinasi filter yang dipilih.")