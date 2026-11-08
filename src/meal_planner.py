"""Feature 2 - Tavily search + LLM + Pydantic meal plan."""
import re

from pydantic import Field, create_model

from src.common import PlanError, clean_citations, describe_profile
from src.llm_client import generate_structured
from src.schemas import Meal, MealDay, MealPlan
from src.search import NUTRITION_DOMAINS, format_sources, gather_sources


SYSTEM = """You are a practical wellness meal-planning assistant for 'The Healthy Way'.

Your task is to create a personalized 30-day meal plan based on the user's submitted preferences and the numbered web sources provided.

PERSONALIZATION RULES:
- Use ALL user inputs when creating the meal plan. Never ignore a selected option.
- Goal: Adapt the meals to the user's selected goal:
  Lose Weight, Gain Weight, Maintain Weight, Eat Healthier, or Build Healthy Habits.
- Diet: Strictly follow the selected dietary preference:
  Regular Diet, Vegetarian, Vegan, Pescatarian, Halal Diet, or No Specific Diet.
- Meals per day: Generate exactly the number selected by the user (3, 4, or 5) for every day.
- Cuisine: Adapt meals to the selected cuisine. If not provided, use simple everyday dishes.
- Allergies: Completely exclude all listed allergens and ingredients containing them.
- Disliked Foods: Never include any disliked food.
- No Specific Diet means a general balanced diet, while still respecting allergies and dislikes.
- If an optional input is empty, use reasonable general defaults without inventing user preferences.

MEAL PLAN RULES:
- Create exactly 30 days of meals.
- Include clear meal labels (Breakfast, Lunch, Dinner, Snack, etc.).
- Use simple, affordable, accessible everyday ingredients.
- Provide variety throughout the month. Some meal repetition is acceptable.
- Keep meal names and descriptions short and practical.
- Avoid lengthy recipes and unnecessary nutritional explanations.
- Make meals realistic and easy to prepare.

HEALTH & SAFETY:
- Never provide calorie counts, macro numbers, fasting, detoxes, crash diets, supplements, or restrictive eating advice.
- For weight-management goals, focus on balanced portions, nutritious foods, and sustainable habits rather than restriction.
- For anyone under 18, do not frame meals around weight loss or weight gain; focus on regular, nourishing meals.
- Never make medical claims or promise specific weight results.
- This is general lifestyle guidance, not medical advice.
- Include a brief safety_note recommending consultation with a doctor or registered dietitian, especially for medical conditions, pregnancy, or eating-disorder concerns.

SOURCES:
- Base nutritional guidelines in the 'principles' section ONLY on the numbered web sources provided.
- Include the relevant source IDs in source_ids.
- Never invent sources or citations.
- If no relevant sources are provided, keep principles general and avoid unsupported health claims.

OUTPUT REQUIREMENTS:
- Return valid, structured JSON only. No Markdown or extra commentary.
- Include exactly 30 days.
- Each day must contain exactly the selected number of meals.
- Each meal should include:
  - name: Short meal name.
  - description: Brief description of the main ingredients.
- Include a short why_it_fits explaining how the plan supports the user's selected goal and preferences.
- Include a concise principles section with source_ids.
- Include a brief safety_note.
- Avoid repeated explanations and unnecessary text.

IMPORTANT:
The user's submitted inputs are the primary basis of personalization. The final meal plan must reflect their actual choices and restrictions, not a generic meal plan."""


def _allergy_hits(plan: MealPlan, allergies: str) -> list[str]:
    words = [w for w in re.split(r"[,\s;/]+", allergies.lower()) if len(w) >= 3]
    hits = []
    for day in plan.days:
        for m in day.meals:
            text = " ".join([m.name, m.description, *m.ingredients]).lower()
            hits += [w for w in words if w in text]
    return sorted(set(hits))


def _meal_plan_schema(meals_per_day: int) -> type[MealPlan]:
    day_schema = create_model(
        f"MealDay{meals_per_day}Meals",
        __base__=MealDay,
        meals=(list[Meal], Field(min_length=meals_per_day, max_length=meals_per_day)),
    )
    return create_model(
        f"ThirtyDayMealPlan{meals_per_day}Meals",
        __base__=MealPlan,
        days=(list[day_schema], Field(min_length=30, max_length=30)),
    )


def build_meal_plan(user: dict, label: str, prefs: dict):
    diet = prefs["diet"]
    goal = prefs["goal"]
    queries = [
        "healthy eating balanced plate vegetables whole grains protein dietary guidelines",
        f"{diet} healthy meal ideas balanced" if diet not in ("No preference", "No Specific Diet") else "healthy balanced meal ideas",
    ]
    if user["Age"] >= 18 and any(term in goal.lower() for term in ("weight", "lose", "gain")):
        queries.append("sustainable healthy weight management eating habits")
    sources, snippets = gather_sources(queries, NUTRITION_DOMAINS)

    base = (
        f"PERSON\n{describe_profile(user, label)}\n\n"
        f"PREFERENCES\nGoal: {goal}\nDiet: {diet}\nMeals per day: {prefs['meals_per_day']}\n"
        f"Allergies (must avoid): {prefs['allergies'] or 'none stated'}\n"
        f"Dislikes: {prefs['dislikes'] or 'none stated'}\nCuisine: {prefs['cuisine'] or 'no preference'}\n\n"
        f"SOURCES\n{format_sources(sources, snippets)}\n\n"
        f"Create the complete 30-day meal plan now. Return exactly 30 days numbered 1 through 30, "
        f"with exactly {prefs['meals_per_day']} meals in each day."
    )
    plan_schema = _meal_plan_schema(prefs["meals_per_day"])
    prompt = base
    last_issue = "We could not create a complete 30-day meal plan. Please try again."
    for _ in range(2):
        plan = generate_structured(SYSTEM, prompt, plan_schema, max_tokens=16000)
        if [day.day for day in plan.days] != list(range(1, 31)):
            last_issue = "We could not create a complete 30-day meal plan. Please try again."
            prompt = (
                f"{base}\n\nThe previous result did not number every day exactly once in order. "
                "Regenerate all 30 days, numbered sequentially from 1 to 30."
            )
            continue
        hits = _allergy_hits(plan, prefs["allergies"]) if prefs["allergies"] else []
        if not hits:
            clean_citations(plan.principles, sources)
            return plan, sources
        last_issue = "We could not create a plan that safely avoids your listed allergies. Please try again."
        prompt = f"{base}\n\nYour previous plan contained {', '.join(hits)}, which the person must avoid. Regenerate without it."
    raise PlanError(last_issue)
