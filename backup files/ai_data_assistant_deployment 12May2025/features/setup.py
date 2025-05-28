import streamlit as st
import os
import json
import io
import markdown
import re
import openpyxl
import pandas as pd
import polars as pl

from src.utils import configure_genai, get_gemini_response, process_uploaded_file
from prompts import (
    MANAGER_PROMPT_TEMPLATE, ANALYST_PROMPT_TEMPLATE, ASSOCIATE_PROMPT_TEMPLATE,
    ANALYST_TASK_PROMPT_TEMPLATE, ASSOCIATE_REVIEW_PROMPT_TEMPLATE,
    MANAGER_REPORT_PROMPT_TEMPLATE, REVIEWER_PROMPT_TEMPLATE
)
from src.ui_helpers import add_download_buttons, add_to_conversation # Import necessary helpers

def display_setup_step():
    """Displays the Project Setup step."""
    st.title("🚀 Start New Analysis Project")
    with st.form("project_setup_form"):
        st.subheader("1. Project Details")
        project_name = st.text_input("Project Name", st.session_state.get("project_name", "Analysis Project"))
        problem_statement = st.text_area("Problem Statement / Goal", st.session_state.get("problem_statement", ""), placeholder="Describe what you want to achieve...")
        data_context = st.text_area("Data Context (Optional)", st.session_state.get("data_context", ""), placeholder="Background info about the data...")

        st.subheader("2. Upload Data")
        uploaded_files = st.file_uploader(
            "Upload CSV, XLSX, DOCX, or PDF files",
            type=["csv", "xlsx", "docx", "pdf"],
            accept_multiple_files=True,
            key="file_uploader"
        )

        submit_button = st.form_submit_button("🚀 Start Analysis")

        if submit_button:
            if not st.session_state.gemini_api_key:
                 st.error("Please enter your Gemini API Key in the sidebar first!")
            elif not project_name or not problem_statement or not uploaded_files:
                st.error("Project Name, Problem Statement, and at least one Data File are required.")
            else:
                # Reset previous project data if any
                st.session_state.dataframes = {}
                st.session_state.data_profiles = {}
                st.session_state.data_texts = {}
                st.session_state.analysis_results = []
                st.session_state.conversation_history = []
                # Clear previous AI outputs
                st.session_state.manager_plan = None
                st.session_state.analyst_summary = None
                st.session_state.associate_guidance = None
                st.session_state.final_report = None

                with st.spinner("Processing uploaded files..."):
                    success_count = 0
                    error_messages = []
                    for uploaded_file in uploaded_files:
                        try:
                            # Use Polars for CSV/Excel directly
                            df, profile, text_content = process_uploaded_file(uploaded_file)
                            if df is not None: # df is now a Polars DataFrame
                                st.session_state.dataframes[uploaded_file.name] = df
                                st.session_state.data_profiles[uploaded_file.name] = profile
                                success_count += 1
                            if text_content:
                                st.session_state.data_texts[uploaded_file.name] = text_content
                                # Only count as success if no dataframe was extracted for this file
                                if df is None:
                                    success_count +=1
                        except Exception as e:
                            error_messages.append(f"Error processing {uploaded_file.name}: {e}")

                    if error_messages:
                        for msg in error_messages:
                            st.error(msg)

                    if success_count > 0:
                        st.session_state.data_uploaded = True
                        st.session_state.project_initialized = True
                        st.session_state.current_step = 1 # Move to Manager Planning
                        st.session_state.project_name = project_name
                        st.session_state.problem_statement = problem_statement
                        st.session_state.data_context = data_context

                        # Add initial info to conversation
                        file_summary = "Uploaded Files:\n"
                        for name in st.session_state.dataframes.keys(): file_summary += f"- Tabular: {name} ({st.session_state.dataframes[name].height} rows, {st.session_state.dataframes[name].width} cols)\n" # Use Polars attributes
                        for name in st.session_state.data_texts.keys(): file_summary += f"- Text: {name}\n"
                        init_msg = f"Project: {project_name}\nProblem: {problem_statement}\nContext: {data_context}\n\n{file_summary}"
                        add_to_conversation("user", init_msg)

                        st.success("Project initialized!")
                        st.rerun()
                    else:
                        st.error("No usable data or text content could be extracted. Please check file formats or content.")

    # Display summary after form submission or on reload if initialized
    if st.session_state.project_initialized:
        st.subheader("Project Summary")
        st.write(f"**Project Name:** {st.session_state.project_name}")
        st.write(f"**Problem Statement:** {st.session_state.problem_statement}")
        if st.session_state.data_context: st.write(f"**Data Context:** {st.session_state.data_context}")

        st.subheader("Uploaded Data Summary")
        if st.session_state.dataframes:
            for name, df in st.session_state.dataframes.items(): st.write(f"- Tabular: {name} ({df.height} rows, {df.width} cols)") # Use Polars attributes
        if st.session_state.data_texts:
            for name in st.session_state.data_texts.keys(): st.write(f"- Text Document: {name}")

        col1, col2 = st.columns([1,4])
        with col1:
            if st.button("Next: Manager Planning"):
                st.session_state.current_step = 1
                st.rerun()
        add_download_buttons("Setup")
