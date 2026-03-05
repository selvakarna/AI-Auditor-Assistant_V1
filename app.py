import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd
import re
from pdf2image import convert_from_bytes

st.title("AI Universal Document Extractor")

uploaded_file = st.file_uploader("Upload Any Document PDF", type=["pdf"])

def extract_text_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:
            t = page.extract_text()

            if t:
                text += t

    return text


def ocr_pdf(file):

    text = ""

    images = convert_from_bytes(file.read())

    for img in images:
        text += pytesseract.image_to_string(img)

    return text


def extract_values(text):

    results = {}

    salary_pattern = r"(GROSS|SALARY|EARNINGS)[^\d]*(\d{3,})"
    total_pattern = r"(TOTAL)[^\d]*(\d{3,})"
    invoice_pattern = r"(INVOICE)[^\d]*(\d+)"

    salary_match = re.search(salary_pattern, text, re.IGNORECASE)
    total_match = re.search(total_pattern, text, re.IGNORECASE)
    invoice_match = re.search(invoice_pattern, text, re.IGNORECASE)

    if salary_match:
        results["Salary/Gross"] = salary_match.group(2)

    if total_match:
        results["Total Amount"] = total_match.group(2)

    if invoice_match:
        results["Invoice Number"] = invoice_match.group(2)

    return results


if uploaded_file:

    text = extract_text_pdf(uploaded_file)

    if len(text) < 20:
        text = ocr_pdf(uploaded_file)

    results = extract_values(text)

    if results:

        df = pd.DataFrame(results.items(), columns=["Field", "Value"])

        st.subheader("Extracted Data")

        st.table(df)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Results",
            csv,
            "extracted_data.csv",
            "text/csv"
        )

    else:
        st.warning("No data detected. Document format may be different.")
