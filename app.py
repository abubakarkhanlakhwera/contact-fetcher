import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re

st.title("PDF Data Extractor with Prefix Modifier")

# Upload PDF
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

# User input for prefix
prefix = st.text_input("Prefix to add (e.g., area_name )")

# Column to exclude from prefix
exclude_column = st.selectbox("Exclude column from prefix", options=["Mobile", "Name"])

# Optional custom filename
custom_filename = st.text_input("Custom filename (optional, no need to add .csv)", value="")

if uploaded_file:
    # Read PDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    extracted_rows = []

    # Extract data
    for page in doc:
        text = page.get_text()
        mobile_match = re.search(r"Mobile[#:\s]+(03\d{9})", text)
        name_line_match = re.search(r"Name[:\s]+(.+)", text, re.IGNORECASE)
        name = None
        if name_line_match:
            name_line = name_line_match.group(1).strip()
            name_parts = re.split(r"\s{2,}", name_line)
            name = name_parts[0].strip()
        if name and mobile_match:
            mobile = mobile_match.group(1).strip()
            extracted_rows.append({'Name': name, 'Mobile': mobile})

    if extracted_rows:
        df = pd.DataFrame(extracted_rows)

        # Add prefix to all columns except the excluded one
        for col in df.columns:
            if col != exclude_column:
                df[col] = prefix + df[col].astype(str)

        # Show data
        st.subheader("Modified Data")
        st.dataframe(df)

        # Prepare for download
        csv = df.to_csv(index=False).encode('utf-8')
        final_filename = f"{custom_filename or prefix}.csv"

        # Download button
        st.download_button("Download Modified CSV", csv, final_filename, "text/csv")
    else:
        st.warning("No valid name and mobile pairs found in the PDF.")
