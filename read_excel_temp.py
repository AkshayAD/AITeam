import pandas as pd
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read_excel_temp.py <excel_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)

    try:
        df = pd.read_excel(file_path)
        # Print relevant columns for analysis, handling potential missing columns
        relevant_cols = [
            'Overall Grade', 'Structure', 'Approach', 'Segmentation',
            'Grounding of Assumptions', 'Calculations', 'Communication',
            'Interviewer Notes', 'Raw LLM Output'
        ]
        cols_to_print = [col for col in relevant_cols if col in df.columns]

        if not cols_to_print:
            print("Error: None of the expected columns found in the Excel file.")
            # Print all columns if expected ones are missing to help diagnose
            print("Available columns:", df.columns.tolist())
        else:
            # Use to_string() to ensure the full content is printed without truncation
            print(df[cols_to_print].to_string())

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)
