import streamlit as st
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

AZURE_KEY = st.secrets["AZURE_KEY"]
AZURE_ENDPOINT = st.secrets["AZURE_ENDPOINT"]

st.set_page_config(page_title="Azure Smart Text Analyzer", page_icon="☁️")
st.title("☁️ Smart Text Analyzer (Azure AI)")
st.write("Analyze sentiment and extract key insights powered by Microsoft Azure.")

user_text = st.text_area("Enter text, a review, or study notes:", height=150)

if st.button("Analyze Text") and user_text.strip():
    try:
        client = TextAnalyticsClient(
            endpoint=AZURE_ENDPOINT,
            credential=AzureKeyCredential(AZURE_KEY),
        )
        docs = [user_text.strip()]

        sentiment = client.analyze_sentiment(documents=docs)[0]
        st.subheader("1. Sentiment Analysis")
        st.success(f"**Overall Tone:** {sentiment.sentiment.capitalize()}")
        st.write(
            f"Positive: `{sentiment.confidence_scores.positive:.2f}` | "
            f"Neutral: `{sentiment.confidence_scores.neutral:.2f}` | "
            f"Negative: `{sentiment.confidence_scores.negative:.2f}`"
        )

        phrases = client.extract_key_phrases(documents=docs)[0]
        st.subheader("2. Key Topics Extracted")
        if phrases.key_phrases:
            st.write(", ".join([f"**{p}**" for p in phrases.key_phrases]))
        else:
            st.write("No key phrases detected.")
    except Exception as exc:
        st.error(f"Request failed: {exc}")