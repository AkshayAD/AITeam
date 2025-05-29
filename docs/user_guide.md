# User Guide for AI Data Analysis Assistant

This guide will help you understand how to use the AI Data Analysis Assistant application effectively.

## Getting Started

The AI Data Analysis Assistant is designed to guide you through a structured data analysis process using a team of AI personas:

- **AI Manager**: Creates analysis plans and final reports
- **AI Analyst**: Examines data and executes analysis tasks
- **AI Associate**: Provides guidance and hypotheses for analysis

## Step 1: Starting a New Project

1. When you first open the application, you'll see the "Start a New Data Analysis Project" screen.
2. Fill in the following information:
   - **Project Name**: Give your analysis project a descriptive name
   - **Problem Statement / Goal**: Clearly describe what you want to learn from your data
   - **Data Context (Optional)**: Provide any background information about your data
3. Upload one or more CSV files containing the data you want to analyze
4. Click "Start Analysis" to begin

## Step 2: Manager Planning

1. The AI Manager will create a structured analysis plan based on your problem statement and data
2. Review the plan carefully to ensure it addresses your needs
3. If you want changes to the plan:
   - Expand the "Provide feedback to the Manager" section
   - Enter your feedback (e.g., "Please add more focus on customer segmentation")
   - Click "Send Feedback" to get a revised plan
4. When you're satisfied with the plan, click "Continue to Data Understanding"

## Step 3: Data Understanding

1. The AI Analyst will examine your data and provide a comprehensive summary
2. You can view the raw data by expanding the "View Data Profiles" section
3. If you have questions about your data:
   - Expand the "Ask the Analyst about the data" section
   - Enter your question (e.g., "What are the main issues with data quality?")
   - Click "Ask Question" to get a detailed answer
4. When you're ready to proceed, click "Continue to Analysis Guidance"

## Step 4: Analysis Guidance

1. The AI Associate will provide specific hypotheses and analysis tasks based on your data and goals
2. Review the guidance to ensure it aligns with your objectives
3. If you want changes to the guidance:
   - Expand the "Provide feedback to the Associate" section
   - Enter your feedback (e.g., "I'd like to focus more on trend analysis")
   - Click "Send Feedback" to get revised guidance
4. When you're satisfied with the guidance, click "Continue to Analysis Execution"

## Step 5: Analysis Execution

1. The application will display the analysis tasks suggested by the AI Associate
2. To execute a task:
   - Enter a description of the specific analysis you want to perform
   - Click "Execute Task" to have the AI Analyst perform the analysis
3. The AI Analyst will provide:
   - An explanation of the approach
   - The Python code that would be used
   - The results of the analysis
   - Key insights derived from the results
4. You can execute multiple analysis tasks by:
   - Reviewing the completed analyses
   - Entering a new task description
   - Clicking "Execute New Task"
5. After completing at least two analyses, you can get the AI Associate's review by clicking "Get Associate's Review of Results"
6. When you're ready for the final report, click "Generate Final Report"

## Step 6: Final Report

1. The AI Manager will generate a comprehensive report based on all analyses performed
2. The report includes:
   - Executive Summary
   - Key Findings/Takeaways
   - Overview of Analysis Performed
   - Detailed Findings
   - Limitations
   - Recommendations/Next Steps
3. If you want changes to the report:
   - Expand the "Provide feedback on the final report" section
   - Enter your feedback
   - Click "Send Feedback" to get a revised report
4. The app also renders a styled HTML report using a Jinja2 template.
   Click "Download Styled HTML" to save it locally.

## Navigation

- You can navigate between different steps using the dropdown menu in the sidebar
- The conversation history with all AI personas is available in the sidebar
- You can reset the project at any time by clicking "Reset Project" in the sidebar

## Tips for Effective Use

1. **Be specific in your problem statement**: The clearer your goal, the better the AI can help you
2. **Provide context about your data**: Background information helps the AI understand your domain
3. **Give feedback when needed**: Don't hesitate to ask for revisions if the AI's output doesn't meet your needs
4. **Ask follow-up questions**: Use the question features to get clarification or deeper insights
5. **Execute multiple analyses**: More analyses lead to a more comprehensive final report
6. **Review the code provided**: The AI shows you the Python code it would use, which can be educational

## Example Use Cases

- **Customer Segmentation**: Upload customer data to identify distinct customer groups
- **Sales Trend Analysis**: Analyze sales data to identify patterns and seasonality
- **Product Performance**: Compare metrics across different products
- **Market Research**: Analyze survey data to extract insights
- **Financial Analysis**: Examine financial data to identify opportunities or risks
