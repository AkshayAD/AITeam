# Deployment Guide for AI Data Analysis Assistant

This guide provides detailed instructions for deploying the AI Data Analysis Assistant application using different methods, depending on your technical expertise and requirements.

## Option 1: Streamlit Community Cloud (Recommended for Non-Technical Users)

Streamlit Community Cloud is a free hosting service that allows you to deploy Streamlit applications directly from GitHub repositories. This is the easiest option for non-technical users.

### Prerequisites
- A GitHub account
- A Google account (to get a Gemini API key)

### Step-by-Step Instructions

1. **Get a Gemini API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the key for later use

2. **Create a GitHub Repository**
   - Sign in to [GitHub](https://github.com)
   - Create a new repository (e.g., "ai-data-assistant")
   - Upload all the project files to this repository:
     - app.py
     - src/utils.py
     - requirements.txt
     - README.md
   - Do NOT upload your .env file (it contains your API key)

3. **Deploy to Streamlit Community Cloud**
   - Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository, branch (main), and the main file path (app.py)
   - Under "Advanced settings", add a secret:
     - Key: `GEMINI_API_KEY`
     - Value: Your Gemini API key from step 1
   - Click "Deploy"

4. **Access Your Application**
   - Once deployed, Streamlit will provide a public URL for your application
   - Share this URL with anyone who needs to use the application
   - No installation or setup is required for end users

## Option 2: Local Installation

This option requires some technical knowledge but allows you to run the application on your local machine.

### Prerequisites
- Python 3.10 or higher installed on your computer
- Basic familiarity with command line operations

### Step-by-Step Instructions

1. **Download the Code**
   - Download the project files to your computer
   - Extract them to a folder (e.g., "ai-data-assistant")

2. **Get a Gemini API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the key for later use

3. **Set Up the Environment**
   - Open a terminal or command prompt
   - Navigate to the project folder:
     ```
     cd path/to/ai-data-assistant
     ```
   - Create a virtual environment (optional but recommended):
     ```
     python -m venv venv
     ```
   - Activate the virtual environment:
     - Windows: `venv\Scripts\activate`
     - macOS/Linux: `source venv/bin/activate`
   - Install the required dependencies:
     ```
     pip install -r requirements.txt
     ```

4. **Configure the API Key**
   - Create a file named `.env` in the project folder
   - Add your Gemini API key to this file:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```
   - Replace `your_gemini_api_key_here` with your actual API key

5. **Run the Application**
   - In the terminal, run:
     ```
     streamlit run app.py
     ```
   - The application will open in your default web browser at `http://localhost:8501`

## Option 3: Docker Deployment

For users with Docker experience, this option provides a containerized solution.

### Prerequisites
- Docker installed on your system
- Basic familiarity with Docker commands

### Step-by-Step Instructions

1. **Create a Dockerfile**
   - Create a file named `Dockerfile` in the project folder with the following content:
     ```dockerfile
     FROM python:3.10-slim

     WORKDIR /app

     COPY requirements.txt .
     RUN pip install --no-cache-dir -r requirements.txt

     COPY . .

     EXPOSE 8501

     CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
     ```

2. **Build the Docker Image**
   - Open a terminal in the project folder
   - Run:
     ```
     docker build -t ai-data-assistant .
     ```

3. **Run the Docker Container**
   - Run:
     ```
     docker run -p 8501:8501 -e GEMINI_API_KEY=your_gemini_api_key_here ai-data-assistant
     ```
   - Replace `your_gemini_api_key_here` with your actual Gemini API key
   - Access the application at `http://localhost:8501`

## Troubleshooting

### API Key Issues
- If you see an error about the Gemini API key, make sure:
  - You've correctly set up the `.env` file (for local installation)
  - You've added the secret in Streamlit Community Cloud (for cloud deployment)
  - You've included the `-e` flag with the API key (for Docker deployment)

### Installation Problems
- If you encounter issues installing dependencies:
  - Make sure you're using Python 3.10 or higher
  - Try updating pip: `pip install --upgrade pip`
  - Install dependencies one by one to identify problematic packages

### Application Not Loading
- Check if Streamlit is running (you should see output in the terminal)
- Make sure port 8501 is not being used by another application
- Try accessing the application at the Network URL shown in the terminal

## Security Considerations

- Never share your Gemini API key publicly
- Do not commit the `.env` file to version control
- For production deployments, consider using more secure methods for storing API keys
- Be mindful of data privacy when uploading sensitive CSV files
