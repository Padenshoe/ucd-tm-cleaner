
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="UCD TM Report Cleaner", layout="centered")

st.title("🧹 UCD TM Report Cleaner")
st.write("Upload your UCD Custom TM Excel report and this tool will extract employee names and flag any 'Total for Period' values under 32 or over 45 hours.")

uploaded_file = st.file_uploader("📁 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        df['Is_Name'] = df.iloc[:, 1].astype(str).str.contains(",", na=False)
        df['Employee Name'] = df.loc[df['Is_Name'], df.columns[1]]
        df['Employee Name'] = df['Employee Name'].ffill()

        df['Is_Total'] = df.iloc[:, 0].astype(str).str.contains("Total for Period", case=False, na=False)
        total_df = df[df['Is_Total']].copy()
        total_df['Total Hours'] = pd.to_numeric(total_df.iloc[:, 1], errors='coerce')

        outlier_totals = total_df[(total_df['Total Hours'] < 32) | (total_df['Total Hours'] > 45)]
        cleaned = outlier_totals[['Employee Name', 'Total Hours']].reset_index(drop=True)

        st.success("✅ Processed successfully! Preview below:")
        st.dataframe(cleaned)

        # Option to download the cleaned data
        buffer = BytesIO()
        cleaned.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button("📥 Download Cleaned Report", buffer, file_name="Filtered_Total_Periods.xlsx")

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
