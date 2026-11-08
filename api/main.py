import logging
from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.common import PlanError
from src.fitness_planner import build_fitness_plan
from src.llm_client import LLMError
from src.meal_planner import build_meal_plan
from src.model_service import explain, load_model, predict
from src.profile_analysis import analyze_profile
from src.search import SearchError

log = logging.getLogger("healthy_way")
YesNo = Literal["yes", "no"]
Freq = Literal["no", "Sometimes", "Frequently", "Always"]


class Profile(BaseModel):
    Gender: Literal["Female", "Male"]
    Age: int = Field(ge=1, le=100)
    Height: float = Field(ge=0.5, le=2.5)
    Weight: float = Field(ge=10, le=300)
    family_history_with_overweight: YesNo
    FAVC: YesNo
    FCVC: float = Field(ge=1, le=3)
    NCP: float = Field(ge=1, le=4)
    CAEC: Freq
    SMOKE: YesNo
    CH2O: float = Field(ge=1, le=3)
    SCC: YesNo
    FAF: float = Field(ge=0, le=3)
    TUE: float = Field(ge=0, le=2)
    CALC: Freq
    MTRANS: Literal["Public_Transportation", "Automobile", "Walking", "Motorbike", "Bike"]


class MealPlanRequest(BaseModel):
    profile: Profile
    label: str = Field(min_length=1, max_length=80)
    goal: str = Field(min_length=1, max_length=80)
    diet: str = Field(min_length=1, max_length=40)
    meals_per_day: Literal[3, 4, 5]
    allergies: str = Field(default="", max_length=200)
    dislikes: str = Field(default="", max_length=200)
    cuisine: str = Field(default="", max_length=60)


class FitnessPlanRequest(BaseModel):
    profile: Profile
    label: str = Field(min_length=1, max_length=80)
    goal: str = Field(min_length=1, max_length=80)
    minutes_per_day: int = Field(ge=10, le=90)
    setting: str = Field(min_length=1, max_length=80)
    limitations: str = Field(default="", max_length=200)


app = FastAPI(title="The Healthy Way API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _warm_model() -> None:
    load_model() 


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(profile: Profile):
    user_data = pd.DataFrame([profile.model_dump()])
    try:
        model, preprocessor, classifier, explainer = load_model()
        label, probs = predict(model, user_data)
        _, top = explain(preprocessor, classifier, explainer, user_data, label)
        user = user_data.iloc[0].to_dict()
        narrative, llm_error = analyze_profile(user, label, probs, top)
    except Exception as e:  # noqa: BLE001
        log.exception("analysis failed")
        raise HTTPException(status_code=500, detail="The model could not process this profile.") from e

    return {
        "label": str(label),
        "bmi": round(profile.Weight / profile.Height**2, 1),
        "probabilities": [{"category": str(r.Category), "probability": float(r.Probability)}
                          for r in probs.itertuples()],
        "top_features": [{"feature": r.feature, "shap": float(r.shap), "direction": r.direction}
                         for r in top.itertuples()],
        "narrative": narrative.model_dump(),
        "llm_error": llm_error,
    }


def _plan_error(exc: Exception) -> HTTPException:
    if isinstance(exc, PlanError):
        return HTTPException(status_code=422, detail=str(exc))
    if isinstance(exc, (SearchError, LLMError)):
        return HTTPException(status_code=503, detail=str(exc))
    log.exception("plan generation failed", exc_info=exc)
    return HTTPException(status_code=500, detail="The plan could not be generated.")


@app.post("/api/meal-plan")
def meal_plan(request: MealPlanRequest):
    user = request.profile.model_dump()
    prefs = request.model_dump(exclude={"profile", "label"})
    try:
        plan, sources = build_meal_plan(user, request.label, prefs)
    except (PlanError, SearchError, LLMError) as e:
        raise _plan_error(e) from e
    except Exception as e:  # noqa: BLE001
        log.exception("meal plan generation failed")
        raise HTTPException(status_code=500, detail="The meal plan could not be generated.") from e
    return {"plan": plan.model_dump(), "sources": [source.model_dump() for source in sources]}


@app.post("/api/fitness-plan")
def fitness_plan(request: FitnessPlanRequest):
    user = request.profile.model_dump()
    prefs = request.model_dump(exclude={"profile", "label"})
    try:
        plan, sources = build_fitness_plan(user, request.label, prefs)
    except (PlanError, SearchError, LLMError) as e:
        raise _plan_error(e) from e
    except Exception as e:  # noqa: BLE001
        log.exception("fitness plan generation failed")
        raise HTTPException(status_code=500, detail="The fitness plan could not be generated.") from e
    return {"plan": plan.model_dump(), "sources": [source.model_dump() for source in sources]}
