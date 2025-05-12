import streamlit as st
import markdown # Added for HTML report generation

from prompts import MANAGER_REPORT_PROMPT_TEMPLATE # Import specific prompts
from src.utils import configure_genai, get_gemini_response
from src.ui_helpers import (
    add_to_conversation,
    check_api_key,
    add_download_buttons,
    format_results_markdown # Import necessary helpers
)

def display_final_report_step():
    """Displays the Final Report step."""
    st.title("📝 6. AI Manager - Final Report")
    if not check_api_key(): st.stop()

    st.info("This step synthesizes the project findings into a final report using the AI Manager.")

    # Check if prerequisites are met
    if not st.session_state.manager_plan or not st.session_state.analyst_summary or not st.session_state.analysis_results:
        missing = [] # Correct indentation for this block
        if not st.session_state.manager_plan: missing.append("Manager Plan (Step 2)")
        if not st.session_state.analyst_summary: missing.append("Analyst Summary (Step 3)")
        if not st.session_state.analysis_results: missing.append("Analysis Results (Step 5)")
        st.warning(f"Requires: {', '.join(missing)} to generate the report. Please complete previous steps.")
        # Add buttons to go back?
        if st.button("Go to Manager Planning"): st.session_state.current_step = 1; st.rerun()
        if st.button("Go to Data Understanding"): st.session_state.current_step = 2; st.rerun()
        if st.button("Go to Analysis Execution"): st.session_state.current_step = 4; st.rerun()
        st.stop()

    # Generate Report Button
    if st.session_state.final_report is None:
        if st.button("Generate Final Report"):
            if not check_api_key(): st.stop()
            with st.spinner("AI Manager is drafting the final report..."):
                # Prepare context for report generation
                try:
                    results_summary = format_results_markdown(st.session_state.analysis_results) # Use markdown formatter

                    prompt = st.session_state.manager_report_prompt_template.format(
                        project_name=st.session_state.project_name,
                        problem_statement=st.session_state.problem_statement,
                        manager_plan=st.session_state.manager_plan,
                        analyst_summary=st.session_state.analyst_summary,
                        analysis_results_summary=results_summary
                    )

                    report_response = get_gemini_response(prompt, persona="manager", model=st.session_state.gemini_model)

                    if report_response and not report_response.startswith("Error:"):
                        st.session_state.final_report = report_response
                        add_to_conversation("manager", f"Generated Final Report:\n{report_response}")
                        st.success("Final report generated!")
                        st.rerun() # Rerun to display the report
                    else:
                        st.error(f"Failed to generate report: {report_response}")
                        add_to_conversation("system", f"Error generating final report: {report_response}")

                except KeyError as e:
                    st.error(f"Prompt Formatting Error: Missing key {e} in Manager Report Prompt template. Please check the template in sidebar settings.")
                    add_to_conversation("system", f"Error formatting Manager Report prompt: Missing key {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred during report generation: {e}")
                    add_to_conversation("system", f"Error during report generation: {e}")

    # Display Report and Download
    if st.session_state.final_report:
        st.markdown("### Final Report Draft")
        st.markdown(st.session_state.final_report)

        # Allow download of the report itself
        try:
            st.download_button(
                 label="Download Report (Markdown)",
                 data=st.session_state.final_report,
                 file_name=f"{st.session_state.project_name}_Final_Report.md",
                 mime="text/markdown",
                 key="download_report_md"
            )
        except Exception as e:
            st.error(f"Error creating report download button: {e}")

        # Optional: Convert Markdown to HTML for better preview or other formats?
        try:
            html_report = markdown.markdown(st.session_state.final_report)
            st.download_button(
               label="Download Report (HTML)",
               data=html_report,
               file_name=f"{st.session_state.project_name}_Final_Report.html",
               mime="text/html",
               key="download_report_html"
               )
        except Exception as e:
            st.warning(f"Could not generate HTML download: {e}")


    add_download_buttons("FinalReport")
