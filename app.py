import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re

# ----- Custom Styling -----
st.set_page_config(page_title="PDF Data Extractor", layout="centered")

st.markdown("""
    <style>
        body {
            background-color: #f9f9f9;
        }
        .main {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        h1 {
            color: #4A90E2;
        }
        .stTextInput>div>div>input {
            background-color: #f1f3f5;
        }
        .stSelectbox>div>div>div>div {
            background-color: #f1f3f5;
        }
        .stButton>button {
            background-color: #4A90E2;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5em 1em;
        }
        .stDownloadButton>button {
            background-color: #27ae60;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5em 1em;
        }
        .stDataFrame {
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# ----- Title -----
st.title("📄 PDF Data Extractor with Prefix Modifier")

# ----- Upload PDF -----
st.header("Step 1: Upload and Setup")
uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

# ----- User Inputs -----
prefix = st.text_input("🔤 Enter a prefix to add (e.g., area_name )")
exclude_column = st.selectbox("🚫 Exclude column from prefix", options=["Mobile", "Name"])
custom_filename = st.text_input("📝 Optional custom filename (no need to add .csv)", value="")

# ----- Data Extraction Logic -----
if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    extracted_rows = []

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

        for col in df.columns:
            if col != exclude_column:
                df[col] = prefix + df[col].astype(str)

        # Show data
        st.header("📊 Preview of Modified Data")
        st.dataframe(df)

        # Prepare download
        csv = df.to_csv(index=False).encode('utf-8')
        final_filename = f"{custom_filename or prefix}.csv"

        st.download_button("⬇️ Download Modified CSV", csv, final_filename, "text/csv")
    else:
        st.warning("⚠️ No valid Name and Mobile pairs found in the PDF.")
else:
    st.info("📂 Please upload a PDF to get started.")
