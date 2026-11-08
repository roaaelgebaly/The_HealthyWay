# The Healthy Way 

**The Healthy Way is a Machine Learning and Agentic AI wellness project.** It combines a machine-learning model for health-profile analysis with AI agents that use a person's preferences and relevant health sources to create personalized meal and activity plans.

Users start with a short health profile and receive a statistical estimate, a plain-language explanation of the factors behind it, and the option to create a 30-day meal plan or a gradual activity plan.

The goal is to encourage realistic, supportive everyday habits—not to provide a diagnosis or medical prescription.

## Machine Learning and Agentic AI

- **Machine Learning model:** The health-category prediction model uses the Random Forest algorithm and achieved **95% accuracy** during model evaluation. SHAP is used to explain which profile factors influenced the prediction.
- **Agentic AI planning:** The meal- and activity-planning workflows use AI with the user's profile and preferences, search for relevant guidance through Tavily, and produce structured plans with cited sources. The meal-planning agent creates a personalized 30-day plan; the activity-planning agent creates a gradual four-week plan.
- **AI-generated explanations:** Groq generates plain-language explanations for model results and structured wellness plans. These outputs are general information, not medical advice.

## Features

- **Health profile analysis:** Uses the trained Random Forest pipeline to estimate a weight category and show BMI and the factors that most influenced the estimate.
- **Easy-to-understand explanation:** Turns influential factors into plain-language notes and gentle tips, while clarifying that the result is a statistical estimate rather than a diagnosis.
- **Personalized meal plan:** Generates a 30-day plan with 3, 4, or 5 meals per day, tailored to the user's goal, diet, cuisine preferences, allergies, and disliked foods.
- **Gradual activity plan:** Creates a four-week program based on current activity, available time, preferred setting, and any stated limitations.
- **Health references:** Retrieves guidance from reputable health websites and displays sources alongside generated plans.
- **Space-inspired, wellness-focused interface:** Provides separate, responsive pages for the health profile, meal planning, and physical activity.

## Technology

- **Frontend:** React and Vite
- **Backend:** FastAPI and Pydantic
- **Machine Learning:** Random Forest with scikit-learn; SHAP for model explanations
- **Agentic AI and structured text generation:** Groq
- **Health source search and retrieval:** Tavily

## Requirements

- Python 3.10 or later
- Node.js 18 or later and npm
- A [Groq API key](https://console.groq.com/) for generated explanations and plans
- A [Tavily API key](https://app.tavily.com/) for searching health references

## Setup and Run on Windows

Open PowerShell in the project directory and create a Python environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a file named `.env` in the project root and add your API keys:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key

# Optional; defaults to openai/gpt-oss-120b
LLM_MODEL=openai/gpt-oss-120b
```

Start the API from the project root:

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

In a second PowerShell window, start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, usually `http://localhost:5173`.

> Start the API from the project root so it can locate `obesity_model_pipeline.pkl` and the `.env` file.

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Check whether the API is running |
| `POST /api/analyze` | Analyze a health profile |
| `POST /api/meal-plan` | Generate a meal plan |
| `POST /api/fitness-plan` | Generate a physical activity plan |

Interactive FastAPI documentation is available at `http://127.0.0.1:8000/docs` while the API is running.

## Project Structure

```text
api/
  main.py                 API endpoints and request validation
frontend/
  src/
    components/           UI pages and result components
    App.jsx               Application page navigation
    api.js                API client
src/
  model_service.py        Model loading, prediction, and explanation
  profile_analysis.py     Health profile explanations
  meal_planner.py         Meal plan generation
  fitness_planner.py      Activity plan generation
  search.py               Health reference search
  schemas.py              Request and response data models
streamlit/
  app.py                  Streamlit interface for experimentation
obesity_model_pipeline.pkl
ObesityDataSet_raw_and_data_sinthetic.csv
Obesity_Model_Training.ipynb
```

## Privacy and Responsible Use

- Health profile data and preferences are sent to the configured Groq service to generate explanations and plans. Never expose API keys in the frontend or commit them to public files.
- Tavily searches the web using queries related to the requested plan.
- Model outputs are statistical estimates, not diagnoses, and do not establish medical causes.
- Plans are general educational information, not medical advice. Consult a doctor or registered dietitian, especially if you have a medical condition, are pregnant, or have concerns about eating.
- Do not use the application as a substitute for medical care or to make high-risk health changes.

## Development Notes

- The model path is relative to the working directory: `obesity_model_pipeline.pkl`.
- During development, the frontend proxies `/api` requests to `http://localhost:8000`.
- Restart the FastAPI server after changing `.env` or API code if it is not running with `--reload`.
