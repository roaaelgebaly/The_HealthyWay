"""Pydantic models for structured LLM outputs."""
from pydantic import BaseModel, Field


class Source(BaseModel):
    id: int = Field(ge=1)
    title: str
    url: str


class Principle(BaseModel):
    text: str
    source_ids: list[int] = Field(default_factory=list)


class FactorNote(BaseModel):
    factor: str = Field(description="Plain everyday name of the factor, e.g. 'Time spent on screens'")
    note: str = Field(description="1-2 simple sentences on how this factor related to the result")
    tip: str = Field(default="", description="One gentle, practical suggestion for this factor. "
                                               "Empty string if the factor cannot be changed (age, gender, family history).")


class ProfileExplanation(BaseModel):
    summary: str = Field(description="2-3 sentence plain-language summary of the result")
    key_factors: list[FactorNote] = Field(min_length=1, max_length=4)
    when_to_talk_to_a_professional: str


class Meal(BaseModel):
    type: str
    name: str
    description: str
    ingredients: list[str] = Field(min_length=1)
    why_it_fits: str


class MealDay(BaseModel):
    day: int = Field(ge=1, le=7)
    meals: list[Meal] = Field(min_length=3, max_length=5)


class MealPlan(BaseModel):
    overview: str
    principles: list[Principle] = Field(min_length=1)
    days: list[MealDay] = Field(min_length=7, max_length=7)
    safety_note: str


class FitnessTask(BaseModel):
    title: str
    description: str
    duration_minutes: int = Field(ge=1)
    times_per_week: int = Field(ge=1, le=7)
    intensity: str


class FitnessWeek(BaseModel):
    week: int = Field(ge=1, le=4)
    focus: str
    weekly_minutes: int = Field(ge=0)
    tasks: list[FitnessTask] = Field(min_length=1)


class FitnessPlan(BaseModel):
    overview: str
    principles: list[Principle] = Field(min_length=1)
    weeks: list[FitnessWeek] = Field(min_length=4, max_length=4)
    safety_notes: list[str] = Field(min_length=1)
