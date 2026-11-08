"""Feature 1 - plain-language explanation of the prediction and its main influencing factors."""
import pandas as pd

from src.llm_client import LLMError, generate_structured
from src.schemas import FactorNote, ProfileExplanation

SYSTEM = """You are a warm, supportive wellness writer for 'The Healthy Way'.
You explain a statistical estimate to an everyday person who knows nothing about data science.

How to write:
- Use ONLY the plain factor names and values given to you. Never use column codes, abbreviations
  (such as FAVC, FCVC, CALC, TUE, FAF), or technical words like SHAP, feature, model weights, or probabilities.
- Write like a kind friend: short, clear sentences, no jargon, no shaming.
- Talk about the factors in the order given (most influential first). Pick at most 4.
- For each factor: say in simple words how it related to the result, and give ONE practical, gentle tip
  when the factor is something a person can change (food, water, activity, screen time, alcohol, smoking,
  transportation, snacking). For things a person cannot change (age, gender, family history, height),
  leave the tip as an empty string and just explain it kindly.
- 'Weight relative to height' is BMI. Explain it simply; its tip should be about steady, sustainable habits,
  never about a target weight or a number of calories.

Safety rules:
- This is a statistical estimate, NOT a diagnosis, and it does not prove what causes anyone's weight.
- Never suggest crash diets, calorie targets, fasting, supplements, or medication.
- Tips are general lifestyle ideas; mention a doctor or registered dietitian for personal medical advice
  (especially for smoking, alcohol, or any health concern).
- Use only the data provided. Do not invent numbers or facts about the person."""

PLAIN_NAME = {
    "Weight": "Weight relative to height", "Height": "Weight relative to height",
    "Age": "Age", "Gender": "Gender",
    "family_history_with_overweight": "Family history of overweight",
    "FAVC": "Eating high-calorie foods often",
    "FCVC": "Vegetables with meals",
    "NCP": "Number of main meals per day",
    "CAEC": "Snacking between meals",
    "SMOKE": "Smoking",
    "CH2O": "Daily water intake",
    "SCC": "Tracking calories",
    "FAF": "Weekly physical activity",
    "TUE": "Daily time on phones, computers and other screens",
    "CALC": "Alcohol consumption",
    "MTRANS": "Usual way of getting around",
}

SCALES = {
    "FCVC": {1: "rarely or never", 2: "sometimes", 3: "with every meal"},
    "CH2O": {1: "less than 1 liter", 2: "1 to 2 liters", 3: "more than 2 liters"},
    "FAF": {0: "none", 1: "1 to 2 days a week", 2: "2 to 4 days a week", 3: "4 to 5 days a week"},
    "TUE": {0: "0 to 2 hours a day", 1: "3 to 5 hours a day", 2: "more than 5 hours a day"},
}
FREQ = {"no": "never", "Sometimes": "sometimes", "Frequently": "frequently", "Always": "always"}
YES_NO = {"family_history_with_overweight", "FAVC", "SMOKE", "SCC"}


def _value_text(col: str, user: dict) -> str:
    v = user[col]
    if col == "Weight":
        return f"BMI {user['Weight'] / user['Height'] ** 2:.1f} ({user['Weight']} kg, {user['Height']} m)"
    if col in SCALES:
        return SCALES[col].get(int(round(v)), str(v))
    if col == "Age":
        return f"{v} years old"
    if col == "NCP":
        return f"{int(round(v))} per day"
    if col in ("CALC", "CAEC"):
        return FREQ.get(v, str(v))
    if col == "MTRANS":
        return str(v).replace("_", " ").lower()
    if col in YES_NO:
        return str(v)
    return str(v)


def summarize_factors(user: dict, top: pd.DataFrame, limit: int = 5) -> list[dict]:
    """Merge SHAP rows into one entry per real-world factor, described in everyday words."""
    totals: dict[str, float] = {}
    for r in top.itertuples():
        col = r.feature.split(" = ")[0]
        if col not in PLAIN_NAME:
            continue
        col = "Weight" if col == "Height" else col  # height and weight are explained together as BMI
        totals[col] = totals.get(col, 0.0) + float(r.shap)

    grand = sum(abs(v) for v in totals.values()) or 1.0
    out = []
    for col, s in sorted(totals.items(), key=lambda kv: abs(kv[1]), reverse=True)[:limit]:
        share = abs(s) / grand
        out.append({
            "factor": PLAIN_NAME[col],
            "value": _value_text(col, user),
            "strength": "strong" if share >= 0.30 else "moderate" if share >= 0.12 else "small",
            "direction": "toward" if s >= 0 else "away from",
        })
    return out


def _fallback(label: str, factors: list[dict]) -> ProfileExplanation:
    """Used when the LLM is unavailable, so the app still gives a useful answer."""
    pretty = str(label).replace("_", " ")
    return ProfileExplanation(
        summary=(f"Based on what you shared, your profile is closest to the '{pretty}' category. "
                 "This is a statistical estimate, not a diagnosis."),
        key_factors=[
            FactorNote(factor=f["factor"],
                       note=f"Your answer ({f['value']}) had a {f['strength']} influence on this result.",
                       tip="")
            for f in factors[:3]
        ] or [FactorNote(factor="Your answers", note="They were combined to produce this estimate.", tip="")],
        when_to_talk_to_a_professional=("For personal advice about weight or health, "
                                        "talk to a doctor or registered dietitian."),
    )


def analyze_profile(user: dict, label: str, probs: pd.DataFrame, top: pd.DataFrame):
    """Returns (ProfileExplanation, error_message_or_None). `probs` is kept for API compatibility."""
    factors = summarize_factors(user, top)
    lines = "\n".join(
        f"- {f['factor']}: {f['value']} ({f['strength']} influence, pushing {f['direction']} this result)"
        for f in factors
    )
    payload = (
        f"Result category: {str(label).replace('_', ' ')}\n"
        f"Most influential factors, strongest first:\n{lines}\n\n"
        "Explain this result and these factors to the person in simple, friendly language."
    )
    try:
        return generate_structured(SYSTEM, payload, ProfileExplanation), None
    except LLMError as e:
        return _fallback(label, factors), str(e)
