import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
import io
import os

st.title("InsightLite - Smart Business Dashboard")
st.write("Upload your sales data (CSV, Excel, or ZIP file).")

# Upload file (accepts csv, xlsx, or zip)
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "zip"])

def extract_zip(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as z:
        # Find first Excel or CSV file
        for file in z.namelist():
            if file.endswith(".csv"):
                return pd.read_csv(z.open(file))
            elif file.endswith(".xlsx"):
                return pd.read_excel(z.open(file))
    return None

df = None
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".zip"):
            df = extract_zip(uploaded_file)
        elif uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)

        if df is not None:
            st.success("File loaded successfully!")
            st.write("### Data Preview:")
            st.dataframe(df.head())

            # Check required columns
            needed_cols = ['Date', 'Product', 'Customer', 'Sales']
            missing = [col for col in needed_cols if col not in df.columns]
            if missing:
                st.error(f"Missing required columns: {missing}")
            else:
                df['Date'] = pd.to_datetime(df['Date'])
                
                # Daily sales
                daily_sales = df.groupby('Date')['Sales'].sum().reset_index()
                st.write("## Daily Sales Over Time")
                fig, ax = plt.subplots()
                sns.lineplot(data=daily_sales, x='Date', y='Sales', ax=ax)
                plt.xticks(rotation=45)
                st.pyplot(fig)

                # Product sales
                product_sales = df.groupby('Product')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)
                st.write("## Product Sales Summary")
                fig2, ax2 = plt.subplots()
                sns.barplot(data=product_sales, x='Sales', y='Product', ax=ax2)
                st.pyplot(fig2)

                # Customer frequency
                customer_freq = df['Customer'].value_counts().reset_index()
                customer_freq.columns = ['Customer', 'Purchases']
                st.write("## Customer Purchase Frequency")
                fig3, ax3 = plt.subplots()
                sns.barplot(data=customer_freq.head(10), x='Purchases', y='Customer', ax=ax3)
                st.pyplot(fig3)
        else:
            st.error("No readable CSV or Excel file found in the ZIP.")
    except Exception as e:
        st.error(f"Failed to process the file: {e}")
