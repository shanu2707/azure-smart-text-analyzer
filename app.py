import streamlit as st
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# --- Page Configuration ---
st.set_page_config(
    page_title="Azure AI Text Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS Styling ---
st.markdown(
    """
    <style>
    .hero-banner {
        background: linear-gradient(135deg, #0078D4 0%, #005A9E 60%, #003B70 100%);
        padding: 1.75rem 2rem;
        border-radius: 14px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 14px rgba(0, 120, 212, 0.2);
    }
    .hero-banner h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }
    .hero-banner p {
        margin: 0.4rem 0 0 0;
        font-size: 1.02rem;
        opacity: 0.92;
    }
    .topic-pill {
        display: inline-block;
        background-color: #EBF5FF;
        color: #005A9E;
        border: 1px solid #B3D7FF;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.25rem 0.35rem 0.25rem 0;
    }
    .sentence-card {
        padding: 0.75rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.6rem;
        border-left: 5px solid #0078D4;
        background-color: #F8FAFC;
        color: #1E293B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Azure Credentials ---
AZURE_KEY = st.secrets["AZURE_KEY"]
AZURE_ENDPOINT = st.secrets["AZURE_ENDPOINT"]

# --- Sample Presets ---
SAMPLES = {
    "Custom Text": "",
    "Positive Product Review": (
        "The cloud deployment workflow with Microsoft Azure and Streamlit was remarkably smooth! "
        "Setting up the AI Language resource took less than five minutes, and the sentiment analysis "
        "accuracy exceeded my expectations."
    ),
    "Mixed Customer Feedback": (
        "The user interface looks clean and modern, and response times are super fast. "
        "However, the initial configuration documentation felt confusing and took extra time to troubleshoot."
    ),
    "AI & Cloud Study Note": (
        "Natural Language Processing enables applications to extract structured insights such as key phrases, "
        "entities, and emotional tone from unstructured human text using pretrained transformer models."
    ),
}

# --- Sidebar ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/f/fa/Microsoft_Azure.svg", width=48)
    st.title("Control Panel")
    st.caption("Powered by **Azure AI Language**")

    selected_sample = st.selectbox("Load a Demo Sample:", list(SAMPLES.keys()))
    show_sentences = st.toggle("Show sentence-level breakdown", value=True)

    st.divider()
    st.markdown(
        """
        **Capabilities:**
        - Overall & sentence sentiment
        - Confidence score distribution
        - Automated key phrase extraction
        """
    )

# --- Hero Header ---
st.markdown(
    """
    <div class="hero-banner">
        <h1>✨ Azure AI Smart Text Analyzer</h1>
        <p>Extract real-time sentiment intelligence, confidence metrics, and key topics using Microsoft Azure Cognitive Services.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Main Layout: Two Columns ---
left_col, right_col = st.columns([1.05, 1.15], gap="large")

with left_col:
    st.subheader("📝 Input Text")
    user_text = st.text_area(
        "Paste an article, review, feedback, or study notes below:",
        value=SAMPLES[selected_sample],
        height=230,
        placeholder="Type or paste any English paragraph here...",
    )

    words = len(user_text.split()) if user_text.strip() else 0
    chars = len(user_text)
    st.caption(f"**Words:** {words}  |  **Characters:** {chars}")

    analyze_clicked = st.button("🚀 Analyze with Azure AI", type="primary", use_container_width=True)

with right_col:
    st.subheader("📊 AI Insights")

    if analyze_clicked:
        if not user_text.strip():
            st.warning("Please enter some text or choose a sample from the sidebar first.")
        else:
            with st.spinner("Analyzing text via Azure AI Language..."):
                try:
                    client = TextAnalyticsClient(
                        endpoint=AZURE_ENDPOINT,
                        credential=AzureKeyCredential(AZURE_KEY),
                    )
                    docs = [user_text.strip()]

                    sentiment = client.analyze_sentiment(documents=docs)[0]
                    phrases = client.extract_key_phrases(documents=docs)[0]

                    # --- Top KPI Metrics ---
                    tone = sentiment.sentiment.capitalize()
                    tone_emoji = {"Positive": "🟢", "Negative": "🔴", "Neutral": "🟡", "Mixed": "🟣"}.get(tone, "🔵")

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Overall Tone", f"{tone_emoji} {tone}")
                    m2.metric("Positive", f"{sentiment.confidence_scores.positive * 100:.0f}%")
                    m3.metric("Neutral", f"{sentiment.confidence_scores.neutral * 100:.0f}%")
                    m4.metric("Negative", f"{sentiment.confidence_scores.negative * 100:.0f}%")

                    # --- Confidence Bar Chart ---
                    st.markdown("#### Confidence Distribution")
                    chart_data = {
                        "Positive": sentiment.confidence_scores.positive,
                        "Neutral": sentiment.confidence_scores.neutral,
                        "Negative": sentiment.confidence_scores.negative,
                    }
                    st.bar_chart(chart_data, height=180)

                    # --- Key Phrases as Styled Badges ---
                    st.markdown("#### 🏷️ Key Topics Extracted")
                    if phrases.key_phrases:
                        pills_html = "".join(
                            [f'<span class="topic-pill">{phrase}</span>' for phrase in phrases.key_phrases]
                        )
                        st.markdown(pills_html, unsafe_allow_html=True)
                    else:
                        st.info("No distinct key phrases detected.")

                    # --- Sentence-by-Sentence Breakdown ---
                    if show_sentences and sentiment.sentences:
                        st.markdown("#### 🔍 Sentence-Level Sentiment")
                        border_colors = {
                            "positive": "#16A34A",
                            "negative": "#DC2626",
                            "neutral": "#D97706",
                        }
                        for idx, sent in enumerate(sentiment.sentences, start=1):
                            s_label = sent.sentiment.lower()
                            color = border_colors.get(s_label, "#0078D4")
                            st.markdown(
                                f"""
                                <div class="sentence-card" style="border-left-color: {color};">
                                    <strong>Sentence {idx} ({sent.sentiment.capitalize()}):</strong> {sent.text}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                except Exception as exc:
                    st.error(f"Azure API Error: {exc}")
    else:
        st.info("👈 Enter text on the left (or pick a demo preset in the sidebar) and click **Analyze with Azure AI**.")