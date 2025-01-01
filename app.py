import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from marker.output import text_from_rendered
from marker.models import create_model_dict
from marker.converters.pdf import PdfConverter

from utils import get_llm_response

load_dotenv()

json_template = {
    "FEATURE_TYPE": "",
    "FEATURE": "",
    "DATE": "",
    "VALUE": "",
    "UNIT_OF_MEASUREMENT": "",
    "REFERENCE_RANGE": "",
    "CONDITION_STATUS": "",
}

# Function to upload the document


def upload_document(uploaded_file):
    """Save the uploaded document to the 'uploaded_files' folder and return its file path."""
    if uploaded_file is not None:
        try:
            # Create the folder if it doesn't exist
            upload_folder = "./uploaded_files"
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Get the original file name and path
            file_path = os.path.join(upload_folder, uploaded_file.name)

            # Write the file to the folder (this will overwrite if it already exists)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            return file_path
        except Exception as e:
            st.error(f"Error uploading file: {e}")
            return None
    return None


def extract_text_from_pdf(filepath):
    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(filepath=filepath)
    text, _, images = text_from_rendered(rendered)
    return text


# Function to generate Excel file from extracted data
def generate_output_file(result):
    records = result.split('\n\n')

    # Convert each record into a dictionary
    json_list = []
    for record in records:
        entry = {}
        lines = record.split('\n')
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                entry[key.strip()] = value.strip()

        # Replace occurrences of "\"\"" with an empty string
        entry = {k: (v if v != '\"\"' else '') for k, v in entry.items()}

        # Only add non-empty entries to json_list
        if entry:  # Check if the entry is not empty
            json_list.append(entry)

    # Convert the list of dictionaries to JSON format
    json_output = json.dumps(json_list, indent=4)

    # Load JSON back into Python objects
    entries = json.loads(json_output)

    df = pd.DataFrame(entries)

    # Display the DataFrame in Streamlit
    st.subheader("Extracted Billing Data")
    st.markdown(
        """
        <style>
        [data-testid=stElementToolbarButton]:first-of-type {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(df,)  # Display DataFrame in tabular format
    # st.table(df)

    # Generate Excel file and provide download link
    output_file = "output_data.xlsx"
    df.to_excel(output_file, index=False)

    # Add a download button for the Excel file
    st.download_button(
        label="Download Excel File",
        data=open(output_file, 'rb').read(),
        file_name=output_file,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.title("Document Extractor")
pdf_path = st.file_uploader(
    "Upload a document (PDF)", type=["pdf"])

# Submit button to trigger processing
submit_button = st.button("Submit", disabled=(pdf_path is None))

if submit_button:
    if pdf_path is not None:
        # Step 3: Process the document
        file_type = pdf_path.name.split(".")[-1].lower()
        file_path = upload_document(pdf_path)

        if file_path:
            st.write(f"Processing document: {pdf_path.name}")
            texts = extract_text_from_pdf(file_path)
            st.session_state['extracted_text'] = texts

            if texts:
                result = get_llm_response(
                    pdf_data=texts, json_template=json_template)

                if result:
                    # Store extracted summary data in session state
                    st.session_state['summary'] = result
                    st.session_state['generated'] = True
                else:
                    st.error("Failed to extract data from document.")
            else:
                st.error("No text extracted from the document.")
    else:
        st.warning(
            "Please upload a document before submitting.")

if st.session_state.get('extracted_text', False):
    with st.expander(f"View text extracted"):
        st.write(st.session_state['extracted_text'])

# Check if the summary was generated and display data
if st.session_state.get('generated', False):
    generate_output_file(st.session_state['summary'])
