import streamlit as st
import pandas as pd

def main():
  st.title("New Bill Form")
  menu = ["Home", "About"]
  choice = st.sidebar.selectbox("Menu", menu)
    
  if choice == "Home":
    st.subheader("Fill the form")
    
    with st.form(key = 'myform', clear_on_submit=True):
      BillNo = st.text_input("Bill Number: ")
      ItemName = st.text_input("Item Name: ")
      Quantity = st.text_input("Quantity: ")
      Date = st.date_input("Date: ")
      Price = st.text_input("Price: ")
      CustID = st.text_input("Customer Id: ")
      submit_button = st.form_submit_button(label='Submit')
    
    if submit_button:
      save_to_txt(BillNo, ItemName, Quantity, Date, Price, CustID)
      st.success()
      


def save_to_txt(BillNo, ItemName, Quantity, Date, Price, CustID):
    with open("Data.txt", "a") as file:
        file.write(f"{BillNo}; {ItemName}; {Quantity}; {Date}; {Price}; {CustID}\n")
    st.success("Data berhasil disimpan ke dalam file Data.txt")

main()