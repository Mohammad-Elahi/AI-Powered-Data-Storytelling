# AI-Powered Data Storytelling

This project explores the difference between human-written and AI-generated stories based on raw data. It transforms complex structured data from the [Austin Animal Center Outcomes dataset](https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes-10-01-2013-to-05-05-/9t4d-g238/about_data) into accessible, natural language narratives. For the AI generation pipeline, the project employs a general LLM for data analysis and initial story generation, paired with an **Agentic LLM to moderate and enhance the emotional content** of the narrative. Finally, it provides an interactive interface for users to compare both versions and evaluate their quality, emotional engagement, and trustworthiness through a user study.

## Key Features

* **Dynamic AI Pipeline:** Built with Python, FastAPI, and LangChain to process dataset rows into cohesive narratives.
* **Agentic AI Integration:** Utilizes a custom-prompted LLM agent to add empathy, tone, and an emotional layer to purely factual data.
* **Interactive Data Stories:** Each narrative has its own linked outcome chart. Scrolling or selecting tagged period phrases highlights the relevant chart phase; readers can also choose a bounded outcome metric or select a phase in the chart.
* **Interactive Comparison:** A web interface that allows users to seamlessly compare a human-authored story ("The Shelter That Grew Quiet") against dynamically generated AI outputs.
* **Evaluation & Engagement:** Enables users to assess the emotional impact and effectiveness of both storytelling methods.

## Project Structure

- **Frontend/**: Contains the user interface (HTML, CSS, JS). Users can read the stories, try to guess their origins, and submit evaluations.
- **Backend/**: A Python FastAPI server that reads the dataset, communicates with the Gemini API to generate AI stories, and stores user evaluations in a CSV file.

## Prerequisites

- Python 3.9+
- A Google Gemini API Key

## How to Run Locally

Follow these steps to run the project on your local machine:

### 1. Start the Backend
1. **Open your terminal or PowerShell and Navigate to the `Backend` directory:**
   ```bash
   cd Backend
   ```
   *(Tip for Windows users: You can also open the `Backend` folder, right-click in the empty space, and select **"Open in Terminal"**).*
2. **Create a virtual environment (Mandatory):**
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment:**
   - On Windows (Command Prompt):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - On Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - On Mac/Linux:
     ```bash
     source venv/bin/activate
     ```
   *(Note: You must see `(venv)` at the beginning of your terminal line before proceeding!)*

5. **Install the required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```
6. **(Optional) Set your Gemini API key:**
   *Note: An API key is already pre-configured in `Backend/main.py` for evaluation purposes. You can skip this step and proceed to run the server.*
   - On Windows PowerShell:
     ```powershell
     $env:GOOGLE_API_KEY = "your-gemini-api-key"
     ```
   - On macOS/Linux:
     ```bash
     export GOOGLE_API_KEY="your-gemini-api-key"
     ```
7. **Run the FastAPI server:**
   ```bash
   python -m uvicorn main:app --reload
   ```
   The backend will start running at `http://127.0.0.1:8000`.

### 2. Run the Frontend
You do not need a special server for the frontend!
Simply navigate to the `Frontend` folder and double-click `index.html` to open it in your web browser. 

*(Alternatively, you can use the "Live Server" extension in VS Code for a better development experience).*

## Datasets
- [Austin Animal Center Outcomes Dataset](https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes-10-01-2013-to-05-05-/9t4d-g238/about_data)
