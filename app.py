import streamlit as st
import pandas as pd
import phonenumbers
import io
import os

# Function to convert numbers to E.164 format
def convert_to_e164(number, default_country="US"):  # Default country is Pakistan ("PK")
    try:
        parsed_number = phonenumbers.parse(str(number), default_country)
        if phonenumbers.is_possible_number(parsed_number) and phonenumbers.is_valid_number(parsed_number):
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        else:
            return None  # Return None for invalid numbers
    except phonenumbers.NumberParseException:
        return None

# Title of the App
st.title("Landline Number Remover with E.164 Formatter")

# File upload
st.write("Upload the Landline Numbers file and Total Data file:")
landline_file = st.file_uploader("Landline Numbers File (Excel)", type=["xlsx"])
total_data_file = st.file_uploader("Total Data File (Excel)", type=["xlsx"])

if landline_file and total_data_file:
    # Read uploaded files without headers
    landline_df = pd.read_excel(landline_file, header=None)
    total_data_df = pd.read_excel(total_data_file, header=None)

    # Assume the first column contains the data
    landline_numbers = set(landline_df.iloc[:, 0])  # First column from landline file

    # Filter out the rows in Total Data File based on the first column
    filtered_total_data_df = total_data_df[~total_data_df.iloc[:, 0].isin(landline_numbers)]

    # Convert phone numbers to E.164 format
    filtered_total_data_df.iloc[:, 0] = filtered_total_data_df.iloc[:, 0].apply(convert_to_e164)

    # Remove rows where conversion to E.164 failed
    filtered_total_data_df = filtered_total_data_df.dropna(subset=[filtered_total_data_df.columns[0]])

    # Show preview of results
    st.write("Filtered and Formatted Total Data File (Preview):")
    st.dataframe(filtered_total_data_df)

    # Extract the original file name without the extension
    original_file_name = os.path.splitext(total_data_file.name)[0]

    # Download filtered and formatted file
    @st.cache_data
    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
        output.seek(0)  # Reset the pointer to the beginning of the stream
        return output.getvalue()

    filtered_data = convert_df_to_excel(filtered_total_data_df)
    st.download_button(
        label="Download Filtered and Formatted Total Data File",
        data=filtered_data,
        file_name=f"Filtered_{original_file_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
