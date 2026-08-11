from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import csv

# 1. Temporary team configuration: use the shared Gemini key while the private
# repository is under active development. Remove this line before delivery and
# use the GOOGLE_API_KEY environment variable described in the README instead.
os.environ["GOOGLE_API_KEY"] = "AQ.Ab8RN6JIcSChJrfh9GYXcgYcTGVNE3zlsnNs2Gmmo1WRrOsYPw"

# 2. Initialize FastAPI app
app = FastAPI()

# CORS setup: allows HTML/JS frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Read dataset
df = pd.read_csv("animal_storytelling_dataset.csv")

# 4. Define LLM models (General and Agentic)
# Fast model for generating raw insights
llm_flash = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.2)

# Powerful and creative model for emotional content generation (Agentic AI)
llm_pro = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7)

# 5. Define request structure coming from the frontend
class StoryRequest(BaseModel):
    animal_type: str # For example, "Dog" or "Cat" is sent from the frontend

class EvaluationRequest(BaseModel):
    humanGuess: str
    aiGuess: str
    clarity: str
    emotion: str
    trust: str
    overall: str
    comments: str

# 6. Create API Endpoint for story generation
@app.post("/generate-story")
async def generate_story(request: StoryRequest):
    try:

        # =========================================
        # STEP 1: Data Preparation & Statistical Extraction
        # =========================================

        animal_df = df[
            df["Animal Type"]
            .astype(str)
            .str.contains("Dog|Cat", case=False, na=False)
        ].copy()


        animal_df["DateTime"] = pd.to_datetime(
            animal_df["DateTime"]
        )


        # These five phases match the chart bands in compare.html exactly.
        # The AI receives the same temporal structure that the reader sees.
        story_periods = [
            ("2019 - Before COVID", "pre-covid", "2019-01-01", "2019-12-31"),
            ("Jan-Mar 2020 - COVID Arrives", "covid-arrival", "2020-01-01", "2020-03-31"),
            ("Apr-Sep 2020 - Quiet Months", "covid-low", "2020-04-01", "2020-09-30"),
            ("Oct 2020-Dec 2021 - Slow Recovery", "slow-recovery", "2020-10-01", "2021-12-31"),
            ("2022 - New Normal", "post-covid", "2022-01-01", "2022-12-31"),
        ]


        def analyze_period(data):

            monthly_data = data.groupby(data["DateTime"].dt.to_period("M"))
            total = len(data)

            adoption_data = data[
                data["Outcome Type"].astype(str).str.contains(
                    "Adoption", case=False, na=False
                )
            ]

            adoption_count = len(adoption_data)


            return {

                "total_records": int(total),

                "average_monthly_outcomes": round(float(monthly_data.size().mean()), 1),

                "dog_count": int(
                    (
                    data["Animal Type"]
                    .str.lower()
                    == "dog"
                    ).sum()
                ),

                "cat_count": int(
                    (
                    data["Animal Type"]
                    .str.lower()
                    == "cat"
                    ).sum()
                ),

                "adoption_count": int(
                    adoption_count
                ),

                "average_monthly_adoptions": round(
                    float(
                        adoption_data
                        .groupby(adoption_data["DateTime"].dt.to_period("M"))
                        .size()
                        .mean()
                    ),
                    1,
                ),

                "top_outcomes":
                    data["Outcome Type"]
                    .value_counts()
                    .head(5)
                    .to_dict()
            }

        statistics = {
            label: {
                "chart_period": chart_period,
                **analyze_period(
                    animal_df[
                        (animal_df["DateTime"] >= start)
                        & (animal_df["DateTime"] <= end)
                    ]
                ),
            }
            for label, chart_period, start, end in story_periods
        }


        data_report = str(statistics)



        # =========================================
        # STEP 2: Gemini Flash
        # Story Insight Extraction
        # =========================================


        prompt_1 = PromptTemplate.from_template(

"""
You are an expert data storyteller.

Analyze this animal shelter dataset summary.

Your task is NOT to write a story.

Extract only the most important storytelling insights
that can later be transformed into a human-centered story.

Focus on the five chart phases in the summary:

- 2019 before COVID
- January to March 2020, when COVID arrived
- April to September 2020, the quiet months
- October 2020 to December 2021, the slow recovery
- 2022, the new normal

Rules:

- Select only 3-5 important insights.
- Avoid listing many statistics.
- Do not create fictional characters.
- Do not make assumptions beyond the data.
- Write concise narrative observations.

Dataset summary:

{data}

"""
        )


        chain_1 = prompt_1 | llm_flash


        analysis_response = chain_1.invoke(
            {
                "data": data_report
            }
        )


        analysis_content = analysis_response.content

        analysis = (
            analysis_content[0]["text"]
            if isinstance(
                analysis_content,
                list
            )
            else str(analysis_content)
        )



        # =========================================
        # STEP 3: Gemini Pro
        # Human Interest Story Generation
        # =========================================


        prompt_2 = PromptTemplate.from_template(

"""
You are a professional human-interest story writer.

Create an emotional but realistic story based ONLY
on the following storytelling insights.

The story should feel similar to a magazine feature,
not a research report.

Required structure:

1. Opening:
Start in 2019, the first period represented in the chart.

Describe the shelter as a living place:
- visitors
- volunteers
- animals waiting
- daily rhythm

2. Characters:
Introduce two fictional representative animals:
- one dog
- one cat

They represent common experiences in the dataset.

3. COVID transition:
Show how the shelter became quieter:
- fewer visitors
- reduced activity
- uncertainty

Describe the emotional impact through the animals'
experiences.

4. Recovery:
Move through the slow recovery and into 2022.

Show how:
- adoption returned
- people searched for companionship
- the shelter changed

5. Ending:
Finish with a meaningful scene involving the animals.

The ending should communicate:
- hope
- companionship
- second chances


IMPORTANT STYLE RULES:

- Do NOT write an academic report.
- Do NOT explain every statistic.
- Do NOT use many percentages.
- Do NOT make unsupported claims.
- Do NOT turn the animals into real records.
- They are symbolic characters representing the dataset.
- Do NOT use em-dashes (—) to connect phrases. Use natural commas or periods.
- Avoid repetitive, dramatic AI sentence structures. Write naturally.
- Do not claim that an outcome increased, returned to normal, or exceeded 2019 unless the supplied data supports that statement.

INTERACTION MARKUP (required):

Return Markdown. For every narrative phase below, wrap at least one natural
period phrase in this exact HTML pattern. The span lets the web application
link the text to the correct chart band as the reader scrolls or clicks.

- 2019: <span class="chart-trigger" data-period="pre-covid" data-year="2019">in 2019</span>
- Jan-Mar 2020: <span class="chart-trigger" data-period="covid-arrival" data-year="2020">as COVID arrived</span>
- Apr-Sep 2020: <span class="chart-trigger" data-period="covid-low" data-year="2020">during the quiet months</span>
- Oct 2020-Dec 2021: <span class="chart-trigger" data-period="slow-recovery" data-year="2020-2021">during the slow recovery</span>
- 2022: <span class="chart-trigger" data-period="post-covid" data-year="2022">by 2022</span>

Use only the five data-period values above. Do not use any other HTML tags,
attributes, links, or code. Keep every trigger inside its relevant paragraph.

Use:
- scenes
- emotions
- observations
- simple human language

The reader should feel the transformation of the shelter.

Length:
700-1000 words.


Story insights:

{analysis}

"""
        )


        chain_2 = prompt_2 | llm_pro


        story_response = chain_2.invoke(
            {
                "analysis": analysis
            }
        )


        story_content = story_response.content

        final_story = (
            story_content[0]["text"]
            if isinstance(
                story_content,
                list
            )
            else str(story_content)
        )


        return {

            "success": True,

            "statistics":
                statistics,

            "story_insights":
                analysis,

            "story":
                final_story

        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)

        }

# 7. Endpoint for saving evaluations
@app.post("/submit-evaluation")
async def submit_evaluation(eval_req: EvaluationRequest):
    file_path = "evaluations.csv"
    file_exists = os.path.isfile(file_path)
    
    # Find the number of existing rows for naming users (User1, User2...)
    user_num = 1
    if file_exists:
        with open(file_path, "r", encoding="utf-8") as f:
            user_num = sum(1 for row in f) # count lines. header is line 1, so next is user N if we have N lines. (1 header + 1 user = 2 lines -> next is User2)
            
    user_id = f"User{user_num}"

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["UserID", "HumanGuess", "AIGuess", "Clarity", "Emotion", "Trust", "Overall", "Comments"])
        
        writer.writerow([
            user_id,
            eval_req.humanGuess,
            eval_req.aiGuess,
            eval_req.clarity,
            eval_req.emotion,
            eval_req.trust,
            eval_req.overall,
            eval_req.comments
        ])
    return {"success": True, "message": "Evaluation saved"}

# 8. Endpoint for retrieving evaluation stats
@app.get("/results-data")
async def get_results_data():
    file_path = "evaluations.csv"
    if not os.path.isfile(file_path):
        return {"success": False, "message": "No evaluations yet"}
        
    df_evals = pd.read_csv(file_path)
    total = len(df_evals)
    if total == 0:
        return {"success": False, "message": "No evaluations yet"}

    # Count votes (Story A is assumed Human and Story B is assumed AI, but we count preference votes across criteria)
    # Story A = Human (in our scenario)
    def calc_percent(col_name, target_val):
        count = (df_evals[col_name] == target_val).sum()
        return round((count / total) * 100) if total > 0 else 0

    stats = {
        "clarity": {
            "human_pct": calc_percent("Clarity", "storyA"),
            "ai_pct": calc_percent("Clarity", "storyB"),
            "human_score": round((calc_percent("Clarity", "storyA") / 100) * 5, 1),
            "ai_score": round((calc_percent("Clarity", "storyB") / 100) * 5, 1)
        },
        "emotion": {
            "human_pct": calc_percent("Emotion", "storyA"),
            "ai_pct": calc_percent("Emotion", "storyB"),
            "human_score": round((calc_percent("Emotion", "storyA") / 100) * 5, 1),
            "ai_score": round((calc_percent("Emotion", "storyB") / 100) * 5, 1)
        },
        "trust": {
            "human_pct": calc_percent("Trust", "storyA"),
            "ai_pct": calc_percent("Trust", "storyB"),
            "human_score": round((calc_percent("Trust", "storyA") / 100) * 5, 1),
            "ai_score": round((calc_percent("Trust", "storyB") / 100) * 5, 1)
        },
        "overall": {
            "human_pct": calc_percent("Overall", "storyA"),
            "ai_pct": calc_percent("Overall", "storyB"),
            "human_score": round((calc_percent("Overall", "storyA") / 100) * 5, 1),
            "ai_score": round((calc_percent("Overall", "storyB") / 100) * 5, 1)
        }
    }
    
    # Calculate total votes across all 4 criteria
    total_human_votes = (
        (df_evals["Clarity"] == "storyA").sum() +
        (df_evals["Emotion"] == "storyA").sum() +
        (df_evals["Trust"] == "storyA").sum() +
        (df_evals["Overall"] == "storyA").sum()
    )
    
    total_ai_votes = (
        (df_evals["Clarity"] == "storyB").sum() +
        (df_evals["Emotion"] == "storyB").sum() +
        (df_evals["Trust"] == "storyB").sum() +
        (df_evals["Overall"] == "storyB").sum()
    )

    # Find dominant criterion for Story A (Human)
    criteria_human_votes = {
        "Clarity": (df_evals["Clarity"] == "storyA").sum(),
        "Emotion": (df_evals["Emotion"] == "storyA").sum(),
        "Trust": (df_evals["Trust"] == "storyA").sum(),
        "Overall Quality": (df_evals["Overall"] == "storyA").sum()
    }
    dominant = max(criteria_human_votes, key=criteria_human_votes.get) if total > 0 else "N/A"
    overall_winner = "Human Story" if total_human_votes >= total_ai_votes else "AI Story"

    # Guess Accuracy
    correct_human_guesses = (df_evals["HumanGuess"] == "storyA").sum()
    correct_ai_guesses = (df_evals["AIGuess"] == "storyB").sum()
    
    guess_stats = {
        "human_correct_pct": round((correct_human_guesses / total) * 100) if total > 0 else 0,
        "ai_correct_pct": round((correct_ai_guesses / total) * 100) if total > 0 else 0
    }

    return {
        "success": True,
        "total_responses": int(total),
        "total_human_votes": int(total_human_votes),
        "total_ai_votes": int(total_ai_votes),
        "dominant_criterion": dominant,
        "overall_winner": overall_winner,
        "guess_stats": guess_stats,
        "stats": stats
    }
