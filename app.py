import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import json
import matplotlib.pyplot as plt
import re

# -------------------- Gemini API --------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"] 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------- Preprocessing Cleaning ----------
def clean_review_text(text: str) -> str:
    """Cleans input review text for AI processing"""
    text = str(text)
    text = re.sub(r'<.*?>', ' ', text)  # Remove HTML tags
    text = re.sub(r'http\S+|www\S+', ' ', text)  # Remove URLs
    text = text.encode('ascii', 'ignore').decode('ascii')  # Remove emojis/non-ascii
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize spaces
    return text

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
    review_text = clean_review_text(review_text)
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
st.title("AI-Powered Customer Review Insights")

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

# ----------------- Visualization -----------------
st.subheader("📊 Visualization of Insights")

if st.button("Show Visualizations"):   # ✅ Only runs when clicked
    if 'df' in locals() and not df.empty:
        # Safely count Positive & Negative mentions
        pos_count = df["positive"].apply(lambda x: len(x) if isinstance(x, list) else 0).sum()
        neg_count = df["negative"].apply(lambda x: len(x) if isinstance(x, list) else 0).sum()

        if pos_count + neg_count > 0:
            col1, col2 = st.columns(2)

            # Bar Chart
            with col1:
                st.markdown("### 🔎 Positive vs Negative (Bar Chart)")
                fig, ax = plt.subplots()
                ax.bar(["Positive", "Negative"], [pos_count, neg_count], color=["green", "red"])
                ax.set_ylabel("Mentions")
                st.pyplot(fig)

            # Pie Chart
            with col2:
                st.markdown("### 🥧 Sentiment Distribution (Pie Chart)")
                fig2, ax2 = plt.subplots()
                ax2.pie([pos_count, neg_count], labels=["Positive", "Negative"], autopct="%1.1f%%", colors=["green", "red"])
                st.pyplot(fig2)
        else:
            st.info("No positive/negative insights to visualize yet. Try adding more reviews!")
    else:
        st.warning("⚠️ No reviews available yet. Add some reviews first to see visualization.")
