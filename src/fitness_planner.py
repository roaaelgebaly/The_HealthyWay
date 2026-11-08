"""Feature 3 - Tavily search + LLM + Pydantic gradual fitness tasks."""
from src.common import clean_citations, describe_profile
from src.llm_client import generate_structured
from src.schemas import FitnessPlan
from src.search import FITNESS_DOMAINS, format_sources, gather_sources

SYSTEM = """You are a careful wellness-education writer for 'The Healthy Way'. You turn physical-activity guidance
from the numbered web sources into a gradual 4-week beginner plan personalised to the person's current activity.

Rules:
- Base each guideline in 'principles' ONLY on the numbered sources and cite them in source_ids. Never invent sources.
- Start where the person is. If weekly activity is 'none' or low, week 1 must be very light (about 60-90 minutes
  total per week, mostly walking or easy movement). Increase by no more than 50% per week; never more than
  150 minutes in week 1.
- Each task must fit within the daily minutes the person has available.
- Match the setting (home, outdoors, gym) and avoid equipment they do not have.
- If limitations or injuries are listed, use only low-impact options and say to check with a clinician first.
- Never promise weight loss or results, never prescribe pushing through pain, extreme workouts, or fasting.
- If the person is under 18, follow youth guidance from the sources and keep it playful and age-appropriate.
- Use plain words. No jargon, no column codes.
- safety_notes: stop if pain, dizziness or chest discomfort; check with a doctor before starting if the person has
  a medical condition; this is general lifestyle guidance, not medical advice."""


def build_fitness_plan(user: dict, label: str, prefs: dict):
    if user["Age"] < 18:
        queries = ["physical activity guidelines children adolescents daily active play"]
    else:
        queries = ["physical activity guidelines adults weekly minutes moderate activity muscle strengthening"]
    queries.append("beginner friendly exercise routine start slowly gradually increase walking")
    sources, snippets = gather_sources(queries, FITNESS_DOMAINS)

    payload = (
        f"PERSON\n{describe_profile(user, label)}\n\n"
        f"PREFERENCES\nGoal: {prefs['goal']}\nMinutes available per day: {prefs['minutes_per_day']}\n"
        f"Setting: {prefs['setting']}\nLimitations or injuries: {prefs['limitations'] or 'none stated'}\n\n"
        f"SOURCES\n{format_sources(sources, snippets)}\n\nCreate the 4-week gradual plan."
    )
    plan = generate_structured(SYSTEM, payload, FitnessPlan, max_tokens=4000)
    clean_citations(plan.principles, sources)
    return plan, sources
