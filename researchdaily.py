import streamlit as st
import requests
import time
import google.generativeai as genai
import os

st.set_page_config(page_title="ResearchDaily", layout="centered", menu_items={})

# Load API keys
gemini_api_key = os.getenv("GEMINI_API")
ss_api_key = os.getenv("SEMANTIC_SCHOLAR_API")

# Warn on load if keys are missing
if not gemini_api_key or not ss_api_key:
    st.error("⚠️ One or more API keys are missing. Please set GEMINI_API and SEMANTIC_SCHOLAR_API.")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')


# -------------------- TYPING ANIMATION --------------------

def type_text(text, speed=0.02):
    placeholder = st.empty()
    typed = ""
    for char in text:
        typed += char
        placeholder.markdown(typed)
        time.sleep(speed)


# -------------------- FUNCTIONS --------------------

def get_tone_and_temperature(choice):
    settings = {
        '1': ('professional', 0.3),
        '2': ('conversational', 0.6),
        '3': ('bold', 0.9),
        '4': ('creative', 1.0)
    }
    return settings[choice]


def fetch_papers(query, limit, retries=3, delay=5):
    if retries == 0:
        return None

    url = 'https://api.semanticscholar.org/graph/v1/paper/search'
    params = {
        'query': query,
        'limit': limit,
        'fields': 'title,authors,year,abstract',
    }
    headers = {'x-api-key': ss_api_key}
    response = None

    for attempt in range(retries):
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            wait = delay * (attempt + 1)
            time.sleep(wait)
        else:
            return response

    return response


def generate_summary(title, abstract, tone, temperature):
    if not abstract:
        return 'No abstract available.'

    tone_map = {
        'professional': 'Use a formal academic tone with precise, structured language. Maintain objectivity and clarity throughout.',
        'conversational': 'Explain clearly in a friendly, approachable way as if talking to a curious peer.',
        'bold': 'Be assertive and direct. Highlight impactful insights.',
        'creative': 'Use vivid, engaging and imaginative perspectives.'
    }

    prompt = f"""
SYSTEM INSTRUCTION:
You are an advanced AI-powered research assistant. Your role is to analyze academic research papers and generate clear, accurate, and insightful summaries. You adapt your tone based on user preference while maintaining factual correctness and depth.

TONE:
{tone_map[tone]}

TASK:
Summarize the given research paper in 150–200 words.

CONTEXT:
This is a scholarly research paper retrieved from Semantic Scholar. The content represents academic work, so your explanation should reflect proper understanding of research structure, including objectives, methodology, findings, and implications.

INPUT DATA:
Title: {title}
Abstract: {abstract}

OUTPUT REQUIREMENTS:
- Write in a well-structured paragraph format (no bullet points)
- Clearly explain:
  • the purpose of the research  
  • the methodology (if implied)  
  • key findings  
  • why the research is important  
- Avoid generic phrases and repetition  
- Do not hallucinate information beyond the abstract  
- Maintain clarity, coherence, and readability  

FINAL INSTRUCTION:
Produce a concise, insightful, and human-like summary that demonstrates true understanding of the research, not just rephrasing.
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': temperature,
                'max_output_tokens': 600
            }
        )
        return response.text
    except Exception as e:
        if '429' in str(e) or 'quota' in str(e).lower():
            time.sleep(5)
            try:
                response = model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': temperature,
                        'max_output_tokens': 600
                    }
                )
                return response.text
            except Exception as e2:
                return f'Error generating summary: {e2}'
        return f'Error generating summary: {e}'


# -------------------- UI --------------------

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

body, .stApp {
    background-color: #314733;
}

h1, h2, h3, p, div, span, label {
    color: white !important;
}

.stTextInput input {
    background-color: white !important;
    color: black !important;
}

.stButton button {
    background-color: black !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📄 ResearchDaily")

query = st.text_input("Enter a research topic")
limit = st.slider("Number of papers", 1, 10, 3)

tone_choice = st.radio(
    "Choose tone",
    ["1", "2", "3", "4"],
    format_func=lambda x: {
        "1": "Professional",
        "2": "Conversational",
        "3": "Bold",
        "4": "Creative"
    }[x]
)

search = st.button("Search")


# -------------------- MAIN --------------------

if search:
    if not query:
        st.warning("Please enter a research topic.")
    elif not gemini_api_key or not ss_api_key:
        st.error("API keys are missing.")
    else:
        tone, temperature = get_tone_and_temperature(tone_choice)

        with st.spinner("Fetching papers..."):
            response = fetch_papers(query, limit + 5)

        if response is None:
            st.error("Could not fetch papers (retries set to 0).")
        elif response.status_code == 200:
            data = response.json()
            papers = [p for p in data.get('data', []) if p.get('abstract')]
            papers = papers[:limit]

            if not papers:
                st.error("No papers with abstracts found.")
            else:
                for i, paper in enumerate(papers, start=1):
                    title = paper.get('title')
                    authors = ', '.join([a.get('name') for a in paper.get('authors', []) if a.get('name')])
                    year = paper.get('year')
                    abstract = paper.get('abstract')

                    type_text(f"### {i}. {title}")
                    type_text(f"**Authors:** {authors}")
                    type_text(f"**Year:** {year}")

                    with st.spinner(f"Summarizing paper {i}..."):
                        summary = generate_summary(title, abstract, tone, temperature)

                    type_text(summary)
                    st.divider()

        else:
            st.error(f"Error: {response.status_code}")