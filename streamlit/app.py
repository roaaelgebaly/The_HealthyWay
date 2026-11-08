import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt

# 1. Load saved pipeline
import sys
import types

if 'sklearn.compose._column_transformer' in sys.modules:
    mod = sys.modules['sklearn.compose._column_transformer']
else:
    mod = types.ModuleType('sklearn.compose._column_transformer')
    sys.modules['sklearn.compose._column_transformer'] = mod

if not hasattr(mod, '_RemainderColsList'):
    class _RemainderColsList(list):
        pass
    mod._RemainderColsList = _RemainderColsList

@st.cache_resource
def load_model():
    model = joblib.load("obesity_model_pipeline.pkl")

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]

    explainer = shap.TreeExplainer(classifier)

    return model, preprocessor, classifier, explainer


model, preprocessor, classifier, explainer = load_model()


# 2. App title
st.title("Health & Fitness AI Assistant")

st.write(
    "Enter your information to predict your obesity category "
    "and understand the factors influencing the model prediction."
)


# 3. User input
with st.form("user_form"):

    gender = st.selectbox("Gender", ["Female", "Male"])

    age = st.number_input("Age", min_value=1, max_value=100, value=23)

    height = st.number_input(
        "Height (meters)", min_value=0.5, max_value=2.5, value=1.65
    )

    weight = st.number_input(
        "Weight (kg)", min_value=10.0, max_value=300.0, value=75.0
    )

    family_history = st.selectbox(
        "Family history with overweight", ["yes", "no"]
    )

    favc = st.selectbox("Frequent consumption of high caloric food", ["yes", "no"])

    fcvc = st.number_input("Vegetable consumption", 1.0, 3.0, 2.0)

    ncp = st.number_input("Number of main meals", 1, 4, 3)

    caec = st.selectbox(
        "Eating between meals",
        ["no", "Sometimes", "Frequently", "Always"]
    )

    smoke = st.selectbox("Do you smoke?", ["yes", "no"])

    ch2o = st.number_input("Water consumption", 1.0, 3.0, 2.0)

    scc = st.selectbox("Monitor calories?", ["yes", "no"])

    faf = st.number_input("Physical activity frequency", 0.0, 3.0, 1.0)

    tue = st.number_input("Screen time", 0.0, 2.0, 1.0)

    calc = st.selectbox(
        "Alcohol consumption",
        ["no", "Sometimes", "Frequently", "Always"]
    )

    mtrans = st.selectbox(
        "Transportation",
        [
            "Public_Transportation",
            "Automobile",
            "Walking",
            "Motorbike",
            "Bike"
        ]
    )

    submitted = st.form_submit_button("Predict")


# 4. Prediction
if submitted:

    user_data = pd.DataFrame([{
        "Gender": gender,
        "Age": age,
        "Height": height,
        "Weight": weight,
        "family_history_with_overweight": family_history,
        "FAVC": favc,
        "FCVC": fcvc,
        "NCP": ncp,
        "CAEC": caec,
        "SMOKE": smoke,
        "CH2O": ch2o,
        "SCC": scc,
        "FAF": faf,
        "TUE": tue,
        "CALC": calc,
        "MTRANS": mtrans
    }])

    # Prediction using full pipeline
    prediction = model.predict(user_data)[0]

    st.success(f"Predicted Obesity Category: {prediction}")

    # Class probabilities
    probabilities = model.predict_proba(user_data)[0]

    probability_df = pd.DataFrame({
        "Category": model.classes_,
        "Probability": probabilities
    })

    st.subheader("Prediction Probabilities")

    st.dataframe(probability_df)

    # 5. SHAP Explanation
    st.subheader("Why did the model make this prediction?")

    transformed_data = preprocessor.transform(user_data)

    shap_explanation = explainer(transformed_data)

    class_index = list(classifier.classes_).index(prediction)

    class_explanation = shap.Explanation(
        values=shap_explanation.values[0, :, class_index],
        base_values=shap_explanation.base_values[0, class_index],
        data=transformed_data[0].toarray().ravel()
        if hasattr(transformed_data[0], "toarray")
        else transformed_data[0],
        feature_names=preprocessor.get_feature_names_out()
    )

    fig, ax = plt.subplots()

    shap.plots.waterfall(
        class_explanation,
        show=False
    )

    st.pyplot(fig)

    plt.close(fig)

    st.info(
        "SHAP explains how the model's features influenced its prediction. "
        "It does not establish medical causes."
    )
