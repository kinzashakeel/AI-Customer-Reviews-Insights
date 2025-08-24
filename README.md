# 📊 AI-Powered Customer Reviews Analyzer

This project extracts **structured insights** (positives, negatives, problems, solutions) from customer reviews using **Google Gemini AI** and provides an interactive **Streamlit UI** for analysis, visualization, and CSV export.

---

## 🚀 Features
- ✍️ Input any customer review + rating
- 🤖 AI-powered structured extraction:
  - Positive aspects
  - Negative aspects
  - Problems
  - Suggested solutions
- 📜 View all reviews in a table
- ⬇️ Export results to CSV
- 📈 Actionable insights for business decisions

---

## 🏗 Architecture
![System Architecture](architecture.png)

1. **Streamlit UI** – for entering reviews and displaying insights  
2. **Gemini API** – processes reviews and returns structured JSON  (flash-2.5)
3. **Session State + Pandas** – stores all reviews and insights  
4. **Visualization & CSV Export** – makes insights actionable  

---

## 🛠 Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/review-analyzer.git
   cd review-analyzer
2. Install Libraries
   ```bash
    pip install -r requirements.txt
4. Add your Gemini API key:
In Streamlit, add it under Secrets (for deployment) or as an environment variable locally:
   ```bash
   export GEMINI_API_KEY="your_google_api_key_here"
5. Run the app:
   ```bash
   streamlit run app.py

**Deployment on Streamlit Cloud**
* Push your repo to GitHub
* Go to Streamlit Cloud
* Create a new app → Select this repo → File: app.py
* Add your GEMINI_API_KEY under App Settings → Secrets
  
**Actionability**

* Businesses can track recurring issues (e.g., delivery delays).
* Monitor strengths and weaknesses in customer feedback.
* Use structured data for dashboards, trend analysis, and decision-making.

**Example Output**<br/>
Input:
"The delivery was late but the customer service was very helpful."
```bash
Extracted Insights:
{
"positive": ["helpful customer service"],
"negative": ["late delivery"],
"problems": ["delivery delay"],
"solutions": ["improve delivery process"]
}

