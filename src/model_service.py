import joblib
import numpy as np
import pandas as pd
import shap
from functools import lru_cache

MODEL_PATH = "obesity_model_pipeline.pkl"


@lru_cache(maxsize=1)
def load_model():
    model = joblib.load(MODEL_PATH)
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    explainer = shap.TreeExplainer(classifier)
    return model, preprocessor, classifier, explainer


def predict(model, user_data: pd.DataFrame):
    label = model.predict(user_data)[0]
    probs = pd.DataFrame(
        {"Category": model.classes_, "Probability": model.predict_proba(user_data)[0]}
    ).sort_values("Probability", ascending=False, ignore_index=True)
    return label, probs


def _readable(raw_name: str, user_row: pd.Series) -> str:
    """'cat__Gender_Male' -> 'Gender = Male', 'num__Weight' -> 'Weight'."""
    name = raw_name.split("__", 1)[-1]
    for col in sorted(user_row.index, key=len, reverse=True):
        if name.startswith(col + "_"):
            return f"{col} = {name[len(col) + 1:]}"
    return name


def explain(preprocessor, classifier, explainer, user_data: pd.DataFrame, label, top_n: int = 8):
    """Return the SHAP Explanation for the predicted class plus a tidy top-feature table."""
    X = preprocessor.transform(user_data)
    if hasattr(X, "toarray"):
        X = X.toarray()
    X = np.asarray(X)

    sv = explainer(X)
    ci = list(classifier.classes_).index(label)
    values = sv.values[0, :, ci] if sv.values.ndim == 3 else sv.values[0]
    base = np.atleast_1d(sv.base_values[0])[ci] if np.ndim(sv.base_values) > 1 else sv.base_values[0]
    names = list(preprocessor.get_feature_names_out())

    expl = shap.Explanation(values=values, base_values=base, data=X[0], feature_names=names)

    row = user_data.iloc[0]
    table = pd.DataFrame({
        "feature": [_readable(n, row) for n in names],
        "shap": values,
    })
    table["direction"] = np.where(table["shap"] >= 0, "pushes toward", "pushes away from")
    table = table.reindex(table["shap"].abs().sort_values(ascending=False).index).head(top_n)
    return expl, table.reset_index(drop=True)
