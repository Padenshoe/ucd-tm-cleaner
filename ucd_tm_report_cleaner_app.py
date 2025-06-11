
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="UCD TM Report Cleaner", layout="centered")

st.title("🧹 UCD TM Report Cleaner")
st.write("Upload your UCD Custom TM Excel report and this tool will extract employee names and flag entries based on custom hour thresholds.")

uploaded_file = st.file_uploader("📁 Upload your Excel file", type=["xlsx"])

# Let user set thresholds
st.sidebar.header("Set Thresholds")
lower_bound = st.sidebar.number_input("Flag if under this many hours:", min_value=0, max_value=100, value=32)
upper_bound = st.sidebar.number_input("Flag if over this many hours:", min_value=0, max_value=100, value=45)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        df['Is_Name'] = df.iloc[:, 1].astype(str).str.contains(",", na=False)
        df['Employee Name'] = df.loc[df['Is_Name'], df.columns[1]]
        df['Employee Name'] = df['Employee Name'].ffill()

        df['Is_Total'] = df.iloc[:, 0].astype(str).str.contains("Total for Period", case=False, na=False)
        total_df = df[df['Is_Total']].copy()
        total_df['Total Hours'] = pd.to_numeric(total_df.iloc[:, 1], errors='coerce')

        outlier_totals = total_df[(total_df['Total Hours'] < lower_bound) | (total_df['Total Hours'] > upper_bound)]
        cleaned = outlier_totals[['Employee Name', 'Total Hours']].reset_index(drop=True)

        st.success(f"✅ Showing results under {lower_bound} or over {upper_bound} hours.")
        st.dataframe(cleaned)

        # Option to download the cleaned data
        buffer = BytesIO()
        cleaned.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button("📥 Download Cleaned Report", buffer, file_name="Filtered_Total_Periods.xlsx")

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
