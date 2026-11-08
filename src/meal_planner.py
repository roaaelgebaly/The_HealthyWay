"""Feature 2 - Tavily search + LLM + Pydantic meal plan."""
import re

from pydantic import Field, create_model

from src.common import PlanError, clean_citations, describe_profile
from src.llm_client import generate_structured
from src.schemas import Meal, MealDay, MealPlan
from src.search import NUTRITION_DOMAINS, format_sources, gather_sources

SYSTEM = """You are The Healthy Way, a practical meal-planning assistant.

Create a personalized 7-day meal plan using the user's inputs.

RULES:
- Respect the selected goal, diet, cuisine, allergies, dislikes, and meals per day.
- Generate exactly 7 days and exactly 3, 4, or 5 meals daily, as selected.
- Each meal must have a label, short name, and brief description.
- Use affordable, accessible, everyday ingredients.
- Never include allergens, disliked foods, or unsuitable meals.

CUISINE:
- Choose normal, familiar home-cooked meals that fit the selected cuisine.
- Avoid stereotypical dishes, excessive traditional foods, exotic recipes, and unrelated international dishes.
- For Egyptian cuisine, prioritize realistic everyday Egyptian home cooking. Don't keep repeating koshari, falafel, or mahshi.
- Variety should come from ordinary daily meals, not famous dishes.

HEALTH:
- No calories, macros, fasting, detoxes, supplements, crash diets, or restrictive advice.
- Focus on balanced meals and sustainable habits.
- For users under 18, don't frame meals around weight loss or gain.
- Include a short safety note recommending professional advice when appropriate.

SOURCES:
- Use only provided numbered sources for nutritional principles.
- Include valid source IDs. Never invent citations.
- If no sources exist, keep principles general.

OUTPUT:
Return valid JSON only:
{
  "days": [
    {
      "day": 1,
      "meals": [
        {"label": "Breakfast", "name": "...", "description": "..."}
      ]
    }
  ],
  "why_it_fits": "...",
  "principles": {
    "text": "...",
    "source_ids": []
  },
  "safety_note": "..."
}

IMPORTANT:
Exactly 7 days. Never exceed the selected meals per day. Prioritize natural everyday food choices and the user's actual preferences."""

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
        f"SevenDayMealPlan{meals_per_day}Meals",
        __base__=MealPlan,
        days=(list[day_schema], Field(min_length=7, max_length=7)),
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
        f"Create the complete 7-day meal plan now. Return exactly 7 days numbered 1 through 7, "
        f"with exactly {prefs['meals_per_day']} meals in each day."
    )
    plan_schema = _meal_plan_schema(prefs["meals_per_day"])
    prompt = base
    last_issue = "We could not create a complete 7-day meal plan. Please try again."
    for _ in range(2):
        plan = generate_structured(SYSTEM, prompt, plan_schema, max_tokens=6000)
        if [day.day for day in plan.days] != list(range(1, 8)):
            last_issue = "We could not create a complete 7-day meal plan. Please try again."
            prompt = (
                f"{base}\n\nThe previous result did not number every day exactly once in order. "
                "Regenerate all 7 days, numbered sequentially from 1 to 7."
            )
            continue
        hits = _allergy_hits(plan, prefs["allergies"]) if prefs["allergies"] else []
        if not hits:
            clean_citations(plan.principles, sources)
            return plan, sources
        last_issue = "We could not create a plan that safely avoids your listed allergies. Please try again."
        prompt = f"{base}\n\nYour previous plan contained {', '.join(hits)}, which the person must avoid. Regenerate without it."
    raise PlanError(last_issue)
