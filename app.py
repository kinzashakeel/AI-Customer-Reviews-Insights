import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import json
import re

# -------------------- Configure Gemini --------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]  # 🔑 Store API key in Streamlit secrets
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------- AI Processing --------------------
def extract_insights_ai(review_text: str) -> dict:
    prompt = f"""
    Extract insights from this customer review.

    Review: "{review_text}"

    Return ONLY JSON (no explanation, no markdown). Example:

    {{
      "positive": ["good service"],
      "negative": ["slow delivery"],
      "problems": ["checkout error"],
      "solutions": ["improve checkout process"]
    }}
    """
    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"positive": [], "negative": [], "problems": [], "solutions": [raw_text]}

# -------------------- Storage --------------------
if "reviews" not in st.session_state:
    st.session_state.reviews = []

def add_review(review_text, rating=5):
    insights = extract_insights_ai(review_text)
    new_review = {
        "review_id": f"R{len(st.session_state.reviews)+1:05d}",
        "date": str(datetime.today().date()),
        "rating": int(rating),
        "original_text": review_text,
        "positive": insights.get("positive", []),
        "negative": insights.get("negative", []),
        "problems": insights.get("problems", []),
        "solutions": insights.get("solutions", [])
    }
    st.session_state.reviews.append(new_review)
    return insights, pd.DataFrame(st.session_state.reviews)

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Customer Review Insights", layout="wide")
st.title("📊 Customer Review Insights with Gemini")

with st.form("review_form"):
    review_text = st.text_area("✍️ Enter customer review", height=120)
    rating = st.slider("⭐ Rating", 1, 5, 5)
    submitted = st.form_submit_button("🔍 Analyze Review")

if submitted and review_text.strip():
    with st.spinner("Analyzing review..."):
        insights, df = add_review(review_text, rating)
    st.subheader("✅ Extracted Insights")
    st.json(insights)

if st.session_state.reviews:
    st.subheader("📜 All Reviews")
    df = pd.DataFrame(st.session_state.reviews)
    st.dataframe(df, use_container_width=True)

    # Download as CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Reviews as CSV", csv, "reviews.csv", "text/csv")
