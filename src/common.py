from src.profile_analysis import PLAIN_NAME, _value_text
from src.schemas import Principle, Source


class PlanError(Exception):
    """Raised when a plan cannot be produced safely."""


def describe_profile(user: dict, label: str) -> str:
    bmi = user["Weight"] / user["Height"] ** 2
    lines = [
        f"Estimated category: {str(label).replace('_', ' ')}",
        f"Age: {user['Age']}",
        f"Gender: {user['Gender']}",
        f"Height: {user['Height']} m, weight: {user['Weight']} kg, BMI {bmi:.1f}",
    ]
    for col in ["family_history_with_overweight", "FAVC", "FCVC", "NCP", "CAEC", "SMOKE",
                "CH2O", "SCC", "FAF", "TUE", "CALC", "MTRANS"]:
        lines.append(f"{PLAIN_NAME[col]}: {_value_text(col, user)}")
    return "\n".join(lines)


def clean_citations(principles: list[Principle], sources: list[Source]) -> None:
    """Drop source numbers the model invented."""
    valid = {s.id for s in sources}
    for p in principles:
        p.source_ids = sorted({i for i in p.source_ids if i in valid})
