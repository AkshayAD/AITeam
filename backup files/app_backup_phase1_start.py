import streamlit as st
import pandas as pd
import os
import json
import io # Added for Excel download
import markdown # Added for HTML report generation
from src.utils import configure_genai, get_gemini_response, process_uploaded_file, generate_data_profile_summary, extract_text_from_docx, extract_text_from_pdf

# Page configuration
st.set_page_config(
    page_title="AI Data Analysis Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure Gemini API (initial check, actual calls use session state key)
configure_genai(api_key=st.session_state.get("gemini_api_key", os.getenv("GEMINI_API_KEY")))


# Initialize session state variables if they don't exist
if 'project_initialized' not in st.session_state:
    st.session_state.project_initialized = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'data_uploaded' not in st.session_state:
    st.session_state.data_uploaded = False
if 'dataframes' not in st.session_state:
    st.session_state.dataframes = {}
if 'data_profiles' not in st.session_state:
    st.session_state.data_profiles = {}
if 'data_texts' not in st.session_state: # To store text from non-tabular files
    st.session_state.data_texts = {}
if 'manager_plan' not in st.session_state:
    st.session_state.manager_plan = None
if 'analyst_summary' not in st.session_state:
    st.session_state.analyst_summary = None
if 'associate_guidance' not in st.session_state:
    st.session_state.associate_guidance = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = [] # Structure: [{"task": "...", "suggested_code": "...", "ai_text_result": "...", "insights": "..."}]
if 'final_report' not in st.session_state:
    st.session_state.final_report = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'consultation_response' not in st.session_state: # To store temporary consultation responses
    st.session_state.consultation_response = None
if 'consultation_persona' not in st.session_state: # To store which persona was consulted
    st.session_state.consultation_persona = None
if 'reviewer_prompt_template' not in st.session_state: # New Reviewer Persona
    st.session_state.reviewer_prompt_template = """
You are an AI Project Director acting as a reviewer. Your role is to provide strategic oversight and quality control on the analysis project.

**Context:**
Project Name: {project_name}
Problem Statement: {problem_statement}
Current Project Stage: {current_stage}
Relevant Project Artifacts:
User's Specific Review Request: {specific_request}

**Your Task:**
Review the provided project artifacts and context based on the user's specific request (if any) or provide a general strategic review if no specific request is given. Focus on:
1.  Strategic Alignment: Does the current work align with the overall project goals and problem statement?
2.  Methodology Soundness: Is the approach logical and appropriate? Are there any potential flaws?
3.  Risk Identification: Are there any potential risks or roadblocks?
4.  Clarity & Communication: Is the information presented clearly? Is it suitable for the intended audience?
5.  Business Impact: Does the analysis effectively address potential value or impact?

Provide constructive feedback and actionable recommendations. Use clear, professional language.
"""
if 'reviewer_response' not in st.session_state: # To store temporary reviewer responses
    st.session_state.reviewer_response = None
if 'reviewer_specific_request' not in st.session_state: # Store the user's specific request for the reviewer
    st.session_state.reviewer_specific_request = None


# LLM and Persona Settings
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY")
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = "gemini-2.5-flash-preview-04-17" # Default model
if 'manager_prompt_template' not in st.session_state:
    st.session_state.manager_prompt_template = """
You are an AI Data Analysis Manager acting as a consultant. Your primary role is to translate business problems into structured analytical projects.

**Context:**
Project Name: {project_name}
Problem Statement: {problem_statement}
Data Context: {data_context}
Available Data Files: {file_info}

**Your Task:**
1.  Clarify Business Objectives: If the problem statement is unclear, ask specific questions to understand the core business goals and desired outcomes.
2.  Develop a Structured Analysis Plan: Create a clear, step-by-step plan (numbered list) outlining the analytical approach. This should include:
    *   Data Understanding & Preparation: Initial checks, potential cleaning needs, feature engineering ideas.
    *   Key Analytical Questions & Hypotheses: Specific, testable questions and hypotheses directly linked to the business objectives.
    *   Proposed Methodologies: Suggest appropriate statistical or analytical techniques for each step.
    *   Risk Assessment: Identify potential challenges (data limitations, methodology constraints).
    *   Expected Deliverables: Outline the anticipated outputs (e.g., summary statistics, visualizations, model results, insights).
3.  Maintain Professionalism: Use clear, concise language suitable for a consulting engagement. State any assumptions made.
"""
if 'analyst_prompt_template' not in st.session_state:
    st.session_state.analyst_prompt_template = """
You are an AI Data Analyst acting as a consultant. Your role is to perform rigorous, objective data exploration and summarization.

**Context:**
Problem Statement: {problem_statement}
Manager's Analysis Plan:
{manager_plan}
Data Profile Summary (from automated profiling):
{data_profiles_summary}

**Your Task:**
1.  Provide a Comprehensive Data Assessment: Based *only* on the provided data profiles and context, write a detailed summary covering:
    *   Key Characteristics: Describe data types, distributions (if available in profile), unique values, etc.
    *   Data Quality Issues: Highlight missing values, potential outliers (based on min/max if numeric), inconsistencies, or other red flags identified in the profile.
    *   Relevance to Plan: Assess how well the available data seems suited to address the Manager's plan and the problem statement. Identify potential gaps or limitations.
    *   Initial Observations: Note any immediate patterns or points of interest suggested by the profile *without making unsupported assumptions*.
2.  Be Objective and Precise: Stick to the facts presented in the data profile. Clearly state any limitations of the profile itself. Use precise language.
3.  Document Clearly: Structure your summary logically.
"""
if 'associate_prompt_template' not in st.session_state:
    st.session_state.associate_prompt_template = """
You are an AI Senior Data Associate acting as a consultant. Your role is to guide the analytical execution by refining the plan and defining specific tasks based on initial data understanding.

**Context:**
Problem Statement: {problem_statement}
Manager's Analysis Plan:
{manager_plan}
Analyst's Data Summary:
{analyst_summary}

**Your Task:**
1.  Refine Initial Analysis Steps: Based on the Analyst's summary, refine the first few steps of the Manager's plan.
2.  Formulate Testable Hypotheses: Define 2-3 specific, measurable hypotheses relevant to the business problem that can be tested with the available data.
3.  Identify Key Checks: Highlight critical data quality checks or edge cases to investigate based on the Analyst's findings.
4.  Outline Next Analysis Tasks: Provide the Analyst with 2-3 *concrete, actionable* next tasks. Specify the exact analysis, columns involved, and the expected output (e.g., 'Calculate correlation matrix for columns A, B, C using Polars', 'Generate frequency counts and bar chart for categorical column X using Polars and Plotly', 'Visualize distribution of column Z using a histogram with Plotly').
5.  Develop Narrative: Briefly outline the initial storyline or angle for exploration based on the hypotheses and tasks.
6.  Be Strategic and Detailed: Ensure guidance is practical, statistically sound, and clearly linked to the overall project goals.
"""
if 'analyst_task_prompt_template' not in st.session_state:
    st.session_state.analyst_task_prompt_template = """
You are an AI Data Analyst acting as a consultant. Execute the requested analysis task rigorously and objectively using the specified tools.

**Context:**
Problem Statement: {problem_statement}
Previous Analysis Tasks Completed: {previous_results_summary}
Current Analysis Task: {task_to_execute}
Data Source File: {file-name}
Available Columns: {available_columns}
Data Sample (first 5 rows as JSON):
{data_sample}

**Your Task:** Execute the analysis task using **Polars** for data manipulation and **Plotly Express (px)** for visualization. Provide the following in separate, clearly marked sections:

1.  Approach: Briefly explain the steps you will take to perform the analysis.
2.  Python Code: Provide the complete, executable Python code using Polars (imported as `pl`) and Plotly Express (imported as `px`). Assume the data is loaded into a Polars DataFrame named `df`. For visualizations, generate the Plotly figure object (e.g., `fig = px.scatter(df, ...)`). **Only output the code required for this specific task.**
3.  Results: Describe the key results obtained from executing the code (e.g., calculated statistics, model coefficients, patterns observed). If a visualization was created, describe what it shows.
4.  Key Insights: State 1-2 objective insights derived *directly* from these results, linking them back to the analysis task if possible. Avoid speculation.

**Important:** If you encounter issues (e.g., data type problems, missing columns needed for the task), clearly state the issue in the Results section instead of attempting to proceed with invalid code. Use professional and precise language.
"""
if 'associate_review_prompt_template' not in st.session_state:
    st.session_state.associate_review_prompt_template = """
You are an AI Senior Data Associate acting as a consultant. Critically review the analysis performed by the Analyst.

**Context:**
Problem Statement: {problem_statement}
Original Analysis Guidance Provided to Analyst:
{associate_guidance}
Analysis Results Provided by Analyst:
{analysis_results_summary}

**Your Task:** Provide a structured review covering:
1.  Adherence to Guidance: Did the Analyst correctly execute the tasks outlined in the guidance? Were the specified methods/tools used?
2.  Quality of Results: Are the results clearly presented? Are the insights logical and directly supported by the results?
3.  Progress Towards Goal: How well do these results contribute to answering the overall problem statement or testing the defined hypotheses?
4.  Potential Issues/Limitations: Identify any limitations in the analysis performed, potential biases, or areas needing further investigation.
5.  Recommended Next Steps: Suggest the next logical analysis tasks or refinements based on these findings. Be specific.

**Maintain Objectivity:** Base your review strictly on the provided context. Use clear, constructive language.
"""
if 'manager_report_prompt_template' not in st.session_state:
    st.session_state.manager_report_prompt_template = """
You are an AI Data Analysis Manager acting as a consultant. Synthesize the project findings into a professional report for a business audience.

**Context:**
Project Name: {project_name}
Problem Statement: {problem_statement}
Original Analysis Plan:
{manager_plan}
Data Summary Provided by Analyst:
{analyst_summary}
Summary of Analysis Results & Insights:
{analysis_results_summary}

**Your Task:** Generate a coherent final report in Markdown format. Structure the report as follows:

1.  Executive Summary: Briefly state the problem, the approach taken, and the main conclusions/recommendations (2-3 key sentences).
2.  Key Findings & Business Impact: Use bullet points to highlight the most important insights derived from the analysis. Explain the potential business implications of each finding.
3.  Analysis Overview: Briefly describe the data used and the main analytical steps performed (referencing the plan).
4.  Detailed Findings: Elaborate on the key findings, referencing specific analyses or results where appropriate. Include visualizations if they were central to the findings (describe them).
5.  Limitations & Assumptions: Clearly state any limitations of the data or analysis and any key assumptions made.
6.  Recommendations & Next Steps: Provide actionable recommendations based on the findings. Suggest concrete next steps if further analysis is warranted.

**Focus on Clarity and Impact:** Use clear, non-technical language where possible. Ensure the narrative flows logically and emphasizes the business relevance of the findings.
"""


# Function to reset the session state
def reset_session():
    st.session_state.project_initialized = False
    st.session_state.current_step = 0
    st.session_state.data_uploaded = False
    st.session_state.dataframes = {}
    st.session_state.data_profiles = {}
    st.session_state.manager_plan = None
    st.session_state.analyst_summary = None
    st.session_state.associate_guidance = None
    st.session_state.analysis_results = []
    st.session_state.final_report = None
    st.conversation_history = []
    st.reviewer_prompt_template = """
You are an AI Project Director acting as a reviewer. Your role is to provide strategic oversight and quality control on the analysis project.

**Context:**
Project Name: {project_name}
Problem Statement: {problem_statement}
Current Project Stage: {current_stage}
Relevant Project Artifacts:
User's Specific Review Request: {specific_request}

**Your Task:**
Review the provided project artifacts and context based on the user's specific request (if any) or provide a general strategic review if no specific request is given. Focus on:
1.  Strategic Alignment: Does the current work align with the overall project goals and problem statement?
2.  Methodology Soundness: Is the approach logical and appropriate? Are there any potential flaws?
3.  Risk Identification: Are there any potential risks or roadblocks?
4.  Clarity & Communication: Is the information presented clearly? Is it suitable for the intended audience?
5.  Business Impact: Does the analysis effectively address potential value or impact?

Provide constructive feedback and actionable recommendations. Use clear, professional language.
"""
    st.session_state.reviewer_response = None
    st.session_state.reviewer_specific_request = None


# Add a message to the conversation history
def add_to_conversation(role, content):
    st.session_state.conversation_history.append({
        "role": role,
        "content": content
    })

# Main application
def main():
    # Sidebar
    with st.sidebar:
        st.title("AI Data Analysis Assistant")
        st.markdown("---")
        
        # Project navigation
        st.subheader("Navigation")
        
        if st.session_state.project_initialized:
            step_options = [
                "1. Project Setup",
                "2. Manager Planning",
                "3. Data Understanding",
                "4. Analysis Guidance",
                "5. Analysis Execution",
                "6. Final Report"
            ]
            selected_step = st.selectbox("Go to step:", step_options, index=st.session_state.current_step)
            st.session_state.current_step = step_options.index(selected_step)
            
            if st.button("Reset Project"):
                reset_session()
                st.rerun()
        
        st.markdown("---")
        st.markdown("### AI Team")
        st.markdown("🧠 **Manager**: Creates analysis plan")
        st.markdown("📊 **Analyst**: Examines data details")
        st.markdown("🔍 **Associate**: Guides analysis execution")
        st.markdown("⭐ **Reviewer**: Provides on-demand strategic review") # Added Reviewer

        st.markdown("---")
        st.subheader("LLM & Persona Settings")

        # Gemini API Key Input
        st.session_state.gemini_api_key = st.text_input(
            "Gemini API Key",
            value=st.session_state.gemini_api_key,
            type="password",
            help="Enter your Google Gemini API key. You can get one from Google AI Studio."
        )

        # Gemini Model Selection
        model_options = [
            "gemini-2.5-flash-preview-04-17",
            "gemini-2.5-pro-preview-03-25",
            "gemini-2.0-flash",
            "Custom"
        ]
        selected_model_option = st.selectbox(
            "Select Gemini Model",
            model_options,
            index=model_options.index(st.session_state.gemini_model) if st.session_state.gemini_model in model_options else model_options.index("Custom")
        )

        if selected_model_option == "Custom":
            st.session_state.gemini_model = st.text_input(
                "Enter Custom Model Name",
                value=st.session_state.gemini_model if st.session_state.gemini_model not in model_options else "",
                help="Enter the exact name of the Gemini model you want to use."
            )
        else:
            st.session_state.gemini_model = selected_model_option

        # Persona Prompt Editing
        with st.expander("Edit Persona Prompts"):
            st.session_state.manager_prompt_template = st.text_area(
                "Manager Prompt Template",
                value=st.session_state.manager_prompt_template,
                height=200,
                key="manager_prompt_input"
            )
            st.session_state.analyst_prompt_template = st.text_area(
                "Analyst Data Summary Prompt Template",
                value=st.session_state.analyst_prompt_template,
                height=200,
                key="analyst_summary_prompt_input"
            )
            st.session_state.associate_prompt_template = st.text_area(
                "Associate Guidance Prompt Template",
                value=st.session_state.associate_prompt_template,
                height=200,
                key="associate_guidance_prompt_input"
            )
            st.session_state.analyst_task_prompt_template = st.text_area(
                "Analyst Task Execution Prompt Template",
                value=st.session_state.analyst_task_prompt_template,
                height=200,
                key="analyst_task_prompt_input"
            )
            st.session_state.associate_review_prompt_template = st.text_area(
                "Associate Review Prompt Template",
                value=st.session_state.associate_review_prompt_template,
                height=200,
                key="associate_review_prompt_input"
            )
            st.session_state.manager_report_prompt_template = st.text_area(
                "Manager Report Prompt Template",
                value=st.session_state.manager_report_prompt_template,
                height=200,
                key="manager_report_prompt_input"
            )
            # Added Reviewer Prompt Text Area
            st.session_state.reviewer_prompt_template = st.text_area(
                "Reviewer Prompt Template",
                value=st.session_state.reviewer_prompt_template,
                height=200,
                key="reviewer_prompt_input"
            )

    # Main content area
    if not st.session_state.project_initialized:
        # Step 1: Project Setup
        st.title("🚀 Start a New Data Analysis Project")
        
        with st.form("project_setup_form"):
            st.subheader("Project Details")
            project_name = st.text_input("Project Name")
            problem_statement = st.text_area("Problem Statement / Goal", 
                                            placeholder="Describe what you want to learn from your data...")
            data_context = st.text_area("Data Context (Optional)", 
                                       placeholder="Provide any background information about your data...")
            
            st.subheader("Upload Data")
            uploaded_files = st.file_uploader(
                "Upload Data Files",
                type=["csv", "xlsx", "docx", "pdf"], # Added supported types
                accept_multiple_files=True
            )

            submit_button = st.form_submit_button("Start Analysis")

            if submit_button:
                if not project_name or not problem_statement or not uploaded_files:
                    st.error("Please provide a project name, problem statement, and at least one data file.")
                else:
                    # Process uploaded files
                    st.session_state.dataframes = {} # Clear previous dataframes
                    st.session_state.data_profiles = {} # Clear previous profiles
                    st.session_state.data_texts = {} # Clear previous texts

                    with st.spinner("Processing data files..."):
                        for uploaded_file in uploaded_files:
                            df, profile, text_content = process_uploaded_file(uploaded_file)
                            if df is not None:
                                st.session_state.dataframes[uploaded_file.name] = df
                                st.session_state.data_profiles[uploaded_file.name] = profile
                            if text_content:
                                st.session_state.data_texts[uploaded_file.name] = text_content

                        if st.session_state.dataframes or st.session_state.data_texts:
                            st.session_state.data_uploaded = True
                            st.session_state.project_initialized = True
                            st.session_state.current_step = 1

                            # Add initial project details and file info to conversation history
                            file_summary = "Uploaded Files:\n"
                            for file_name in st.session_state.dataframes.keys():
                                file_summary += f"- Tabular Data: {file_name}\n"
                            for file_name in st.session_state.data_texts.keys():
                                file_summary += f"- Text Content: {file_name}\n"


                            add_to_conversation("user", f"Project: {project_name}\nProblem Statement: {problem_statement}\nData Context: {data_context}\n\n{file_summary}")

                            # Store project details in session state
                            st.session_state.project_name = project_name
                            st.session_state.problem_statement = problem_statement
                            st.session_state.data_context = data_context

                            st.success("Project initialized successfully!")
                            st.rerun()
                        else:
                            st.error("No usable data or text content found in the uploaded files.")

    else:
        # Display the current step based on navigation
        if st.session_state.current_step == 0:
            # Project Setup (already completed)
            st.title("Project Setup")
            st.success("Project has been set up successfully!")
            st.write(f"**Project Name:** {st.session_state.project_name}")
            st.write(f"**Problem Statement:** {st.session_state.problem_statement}")
            if st.session_state.data_context:
                st.write(f"**Data Context:** {st.session_state.data_context}")
            
            st.subheader("Uploaded Data Files")
            for file_name in st.session_state.dataframes.keys():
                st.write(f"- {file_name}")
            
            if st.button("Continue to Manager Planning"):
                st.session_state.current_step = 1
                st.rerun()
                
        elif st.session_state.current_step == 1:
            # Step 2: Manager Planning
            st.title("👨‍💼 AI Manager - Analysis Planning")
            
            if st.session_state.manager_plan is None:
                with st.spinner("AI Manager is creating an analysis plan..."):
                    # Prepare the prompt for the Manager
                    file_info = ""
                    for file_name, profile in st.session_state.data_profiles.items():
                        file_info += f"\nFile: {file_name}\n"
                        file_info += f"- Columns: {', '.join(profile['columns'])}\n"
                        file_info += f"- Dimensions: {profile['shape'][0]} rows × {profile['shape'][1]} columns\n"
                    
                    manager_prompt = f"""
                    Problem Statement: {st.session_state.problem_statement}
                    
                    Data Context: {st.session_state.data_context}
                    
                    Available Data Files: {file_info}
                    
                    Based on this information, create a structured, step-by-step analytical plan. 
                    The plan should cover data understanding, cleaning (if likely needed), 
                    exploratory analysis, specific analyses relevant to the goal, and final synthesis. 
                    Output this plan as a numbered list.
                    """
                    
                    # Get response from Gemini API
                    manager_response = get_gemini_response(manager_prompt, persona="manager")
                    
                    if manager_response:
                        st.session_state.manager_plan = manager_response
                        add_to_conversation("manager", manager_response)
            
            if st.session_state.manager_plan:
                st.markdown("### Analysis Plan")
                st.markdown(st.session_state.manager_plan)
                
                # Allow user to provide feedback
                with st.expander("Provide feedback to the Manager"):
                    manager_feedback = st.text_area("Your feedback:", key="manager_feedback")
                    if st.button("Send Feedback"):
                        if manager_feedback:
                            add_to_conversation("user", f"Feedback on plan: {manager_feedback}")
                            
                            # Process the feedback with Gemini
                            feedback_prompt = f"""
                            Original Analysis Plan: 
                            {st.session_state.manager_plan}
                            
                            User Feedback: 
                            {manager_feedback}
                            
                            Please revise the analysis plan based on this feedback. 
                            Keep the same structured format with numbered steps.
                            """
                            
                            with st.spinner("AI Manager is revising the plan..."):
                                revised_plan = get_gemini_response(feedback_prompt, persona="manager")
                                if revised_plan:
                                    st.session_state.manager_plan = revised_plan
                                    add_to_conversation("manager", revised_plan)
                                    st.success("Plan updated based on your feedback!")
                                    st.rerun()

                # --- Cross-Persona Consultation ---
                with st.expander("Consult another AI Persona"):
                    consult_persona_options = ["Analyst", "Associate"]
                    selected_consult_persona = st.selectbox("Consult:", consult_persona_options, key="consult_manager")
                    consult_request = st.text_area("Your consultation request:", key="consult_request_manager")
                    if st.button("Request Consultation", key="consult_button_manager"):
                        if consult_request:
                            with st.spinner(f"Consulting AI {selected_consult_persona}..."):
                                # Prepare context for consultation
                                consult_context = f"""
                                Current Project Stage: Manager Planning
                                Project Name: {st.session_state.project_name}
                                Problem Statement: {st.session_state.problem_statement}
                                Current Analysis Plan:
                                {st.session_state.manager_plan}

                                User's Consultation Request for you ({selected_consult_persona}):
                                {consult_request}

                                Please provide your feedback or suggestions based on this request and the current plan.
                                """
                                consult_response = get_gemini_response(consult_context, persona=selected_consult_persona.lower())
                                if consult_response and not consult_response.startswith("Error:"):
                                    st.session_state.consultation_response = consult_response
                                    st.session_state.consultation_persona = selected_consult_persona
                                    add_to_conversation(selected_consult_persona.lower(), f"Consultation Response:\n{consult_response}")
                                elif consult_response:
                                    st.error(f"Consultation Error: {consult_response}")
                        else:
                            st.warning("Please enter your consultation request.")

                # Display consultation response if available
                if st.session_state.consultation_response and st.session_state.consultation_persona:
                    st.markdown(f"#### Consultation Response from AI {st.session_state.consultation_persona}")
                    st.markdown(st.session_state.consultation_response)
                    # Clear after displaying once
                    st.session_state.consultation_response = None
                    st.session_state.consultation_persona = None
                # --- End Consultation ---

                # --- Reviewer Section ---
                with st.expander("⭐ Request Review from Project Director"):
                    reviewer_request = st.text_area("Specific Review Instructions (Optional):", key="review_request_manager")
                    if st.button("Get Review", key="review_button_manager"):
                        with st.spinner("Project Director is reviewing the plan..."):
                            # Gather context for reviewer
                            project_artifacts = f"Analyst's Data Summary:\\n{st.session_state.analyst_summary}"
                            review_context_prompt = st.session_state.reviewer_prompt_template.format(
                                project_name=st.session_state.project_name,
                                problem_statement=st.session_state.problem_statement,
                                current_stage="Data Understanding",
                                project_artifacts=project_artifacts,
                                specific_request=reviewer_request if reviewer_request else "Provide a general strategic review of the data summary."
                            )

                            # Call LLM as reviewer
                            review_response = get_gemini_response(review_context_prompt, persona="reviewer")

                            if review_response and not review_response.startswith("Error:"):
                                st.session_state.reviewer_response = review_response
                                st.session_state.reviewer_specific_request = reviewer_request # Store request for display clarity
                                add_to_conversation("reviewer", f"Review Request: {reviewer_request}\n\nReview Response:\n{review_response}")
                            elif review_response:
                                st.error(f"Reviewer Error: {review_response}")
                            else:
                                st.error("Failed to get response from Reviewer.")

                # Display reviewer response if available
                if st.session_state.reviewer_response:
                    st.markdown("#### ⭐ Project Director's Review")
                    if st.session_state.reviewer_specific_request:
                        st.caption(f"Review focus: {st.session_state.reviewer_specific_request}")
                    st.markdown(st.session_state.reviewer_response)
                    # Clear after displaying once to avoid showing stale reviews on rerun
                    st.session_state.reviewer_response = None
                    st.session_state.reviewer_specific_request = None
                # --- End Reviewer Section ---


                if st.button("Continue to Data Understanding"):
                    st.session_state.current_step = 2
                    st.rerun()

        elif st.session_state.current_step == 2:
            # Step 3: Data Understanding
            st.title("📊 AI Analyst - Data Understanding")
            
            if st.session_state.analyst_summary is None:
                with st.spinner("AI Analyst is examining the data..."):
                    # Generate data profile summaries
                    all_profiles_summary = ""
                    for file_name, profile in st.session_state.data_profiles.items():
                        profile_summary = generate_data_profile_summary(profile)
                        all_profiles_summary += f"\n## {file_name}\n{profile_summary}\n"
                    
                    # Prepare the prompt for the Analyst
                    analyst_prompt = f"""Problem Statement: {st.session_state.problem_statement}

Manager's Analysis Plan:
{st.session_state.manager_plan}

Data Profile Summary:
{all_profiles_summary}

Based on this information, provide a comprehensive summary of the data.
Explain the key characteristics, potential challenges, and initial observations
that might be relevant to the analysis plan. Focus on data quality, completeness,
and how well it aligns with the problem statement.
"""
                    
                    # Get response from Gemini API
                    analyst_response = get_gemini_response(analyst_prompt, persona="analyst")
                    
                    if analyst_response:
                        st.session_state.analyst_summary = analyst_response
                        add_to_conversation("analyst", analyst_response)
            
            if st.session_state.analyst_summary:
                # Display data profiles
                with st.expander("View Data Profiles", expanded=False):
                    for file_name, df in st.session_state.dataframes.items():
                        st.subheader(f"File: {file_name}")
                        st.dataframe(df.head(10))
                        
                        profile = st.session_state.data_profiles[file_name]
                        st.write(f"Dimensions: {profile['shape'][0]} rows × {profile['shape'][1]} columns")
                        
                        # Display missing values
                        missing_values = pd.Series(profile['missing_values'])
                        if missing_values.sum() > 0:
                            st.write("Missing Values:")
                            st.dataframe(missing_values[missing_values > 0])
                
                # Display analyst summary
                st.markdown("### Data Summary")
                st.markdown(st.session_state.analyst_summary)

                # --- Reviewer Section ---
                with st.expander("⭐ Request Review from Project Director"):
                    # Add a placeholder or initial content
                    st.write("Use this section to request a strategic review of the data understanding from the Project Director.")

                    reviewer_request = st.text_area("Specific Review Instructions (Optional):", key="review_request_analyst_summary")
                    if st.button("Get Review", key="review_button_analyst_summary"):
                        with st.spinner("Project Director is reviewing the data summary..."):
                            # Gather context for reviewer
                            project_artifacts = f"Analyst's Data Summary:\\n{st.session_state.analyst_summary}"
                            review_context_prompt = st.session_state.reviewer_prompt_template.format(
                                project_name=st.session_state.project_name,
                                problem_statement=st.session_state.problem_statement,
                                current_stage="Data Understanding",
                                project_artifacts=project_artifacts,
                                specific_request=reviewer_request if reviewer_request else "Provide a general strategic review of the data summary."
                            )

                            # Call LLM as reviewer
                            review_response = get_gemini_response(review_context_prompt, persona="reviewer")

                            if review_response and not review_response.startswith("Error:"):
                                st.session_state.reviewer_response = review_response
                                st.session_state.reviewer_specific_request = reviewer_request # Store request for display clarity
                                add_to_conversation("reviewer", f"Review Request: {reviewer_request}\n\nReview Response:\n{review_response}")
                            elif review_response:
                                st.error(f"Reviewer Error: {review_response}")
                            else:
                                st.error("Failed to get response from Reviewer.")

                # Display reviewer response if available
                if st.session_state.reviewer_response:
                    st.markdown("#### ⭐ Project Director's Review")
                    if st.session_state.reviewer_specific_request:
                        st.caption(f"Review focus: {st.session_state.reviewer_specific_request}")
                    st.markdown(st.session_state.reviewer_response)
                    # Clear after displaying once to avoid showing stale reviews on rerun
                    st.session_state.reviewer_response = None
                    st.session_state.reviewer_specific_request = None
                # --- End Reviewer Section ---

                if st.button("Continue to Analysis Guidance"):
                    st.session_state.current_step = 3
                    st.rerun()

if __name__ == "__main__":
    main()
