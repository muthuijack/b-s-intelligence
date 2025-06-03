import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("InsightLite - Smart Business Dashboard")

st.write("Upload your sales data (Excel or CSV) to get started.")

# Upload file
uploaded_file = st.file_uploader("Choose your Excel or CSV file", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        # Read file based on extension
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("File uploaded successfully!")

        st.write("### Data Preview:")
        st.dataframe(df.head())

        # Check necessary columns exist
        needed_cols = ['Date', 'Product', 'Customer', 'Sales']
        missing_cols = [col for col in needed_cols if col not in df.columns]

        if missing_cols:
            st.error(f"Your file is missing these required columns: {missing_cols}")
        else:
            # Convert Date column to datetime
            df['Date'] = pd.to_datetime(df['Date'])

            # Daily Sales over time
            daily_sales = df.groupby('Date')['Sales'].sum().reset_index()

            st.write("## Daily Sales Over Time")
            fig, ax = plt.subplots()
            sns.lineplot(data=daily_sales, x='Date', y='Sales', ax=ax)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Product sales summary
            product_sales = df.groupby('Product')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)

            st.write("## Product Sales Summary")
            fig2, ax2 = plt.subplots()
            sns.barplot(data=product_sales, x='Sales', y='Product', ax=ax2)
            st.pyplot(fig2)

            # Customer purchase frequency
            customer_freq = df['Customer'].value_counts().reset_index()
            customer_freq.columns = ['Customer', 'Purchases']

            st.write("## Customer Purchase Frequency")
            fig3, ax3 = plt.subplots()
            sns.barplot(data=customer_freq.head(10), x='Purchases', y='Customer', ax=ax3)
            st.pyplot(fig3)

    except Exception as e:
        st.error(f"Error reading file: {e}")
from fpdf import FPDF
import tempfile
import os

def save_fig_as_image(fig, filename):
    fig.savefig(filename, format='png', bbox_inches='tight')

if st.button("📄 Export Report as PDF"):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save each figure as an image
            fig_paths = []
            for i, fig in enumerate([fig, fig2, fig3], start=1):
                path = os.path.join(tmpdir, f"chart_{i}.png")
                save_fig_as_image(fig, path)
                fig_paths.append(path)

            # Create PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "InsightLite Sales Report", ln=True, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.ln(10)

            titles = ["Daily Sales Over Time", "Product Sales Summary", "Top Customers"]
            for title, img_path in zip(titles, fig_paths):
                pdf.cell(0, 10, title, ln=True)
                pdf.image(img_path, w=180)
                pdf.ln(10)

            pdf_path = os.path.join(tmpdir, "Sales_Report.pdf")
            pdf.output(pdf_path)

            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Download PDF Report", f, file_name="Sales_Report.pdf")

    except Exception as e:
        st.error(f"Error generating PDF: {e}")
