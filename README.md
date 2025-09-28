# TechScreen - Hiring Assistant Chatbot

An intelligent screening assistant built with Streamlit + OpenAI GPT-4.

## Features
- Collects candidate details
- Tech stack–based interview question generation
- Coherent chat handling
- Fallback & exit mechanism

## Run Locally

1. Clone the repo
2. Add your OpenAI API key to `.env`
3. Install requirements:
   ```
   pip install -r requirements.txt
   ```
4. Launch the app:
   ```
   streamlit run app.py
   ```

## Notes
- Data is not stored; privacy-friendly by default
- Add `data/candidates.csv` if you want to save form inputs
