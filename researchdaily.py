import streamlit as st
import requests
import time
import google.generativeai as genai
import os
import json

st.set_page_config(page_title="ResearchDaily", layout="centered", menu_items={})

# -------------------- LOAD LOTTIE --------------------
def load_lottie(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

book_anim = load_lottie("Book.json")

# -------------------- API KEYS --------------------
gemini_api_key = os.getenv("GEMINI_API")
ss_api_key = os.getenv("SEMANTIC_SCHOLAR_API")

if not gemini_api_key or not ss_api_key:
    st.error("⚠️ One or more API keys are missing. Please set GEMINI_API and SEMANTIC_SCHOLAR_API.")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

# -------------------- TYPE EFFECT --------------------
def type_text(text, speed=0.02):
    placeholder = st.empty()
    typed = ""
    for char in text:
        typed += char
        placeholder.markdown(typed)
        time.sleep(speed)

# -------------------- TONE --------------------
def get_tone_and_temperature(choice):
    settings = {
        '1': ('professional', 0.3),
        '2': ('conversational', 0.6),
        '3': ('bold', 0.9),
        '4': ('creative', 1.0)
    }
    return settings[choice]

# -------------------- FETCH PAPERS --------------------
def fetch_papers(query, limit, retries=3, delay=5):
    url = 'https://api.semanticscholar.org/graph/v1/paper/search'
    params = {
        'query': query,
        'limit': limit,
        'fields': 'title,authors,year,abstract',
    }
    headers = {'x-api-key': ss_api_key}

    for attempt in range(retries):
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            time.sleep(delay * (attempt + 1))
        else:
            return response

    return response

# -------------------- GENERATE SUMMARY --------------------
def generate_summary(title, abstract, tone, temperature):
    if not abstract:
        return 'No abstract available.'

    tone_map = {
        'professional': 'Use a formal academic tone with precise, structured language.',
        'conversational': 'Explain clearly in a friendly way.',
        'bold': 'Be assertive and highlight key insights.',
        'creative': 'Use engaging and imaginative perspectives.'
    }

    top_k_map = {
        'professional': 20,
        'conversational': 40,
        'bold': 50,
        'creative': 80
    }

    top_p_map = {
        'professional': 0.7,
        'conversational': 0.8,
        'bold': 0.9,
        'creative': 0.95
    }

    prompt = f"""
You are an AI-powered research assistant.

Summarize this research paper in 150–200 words.

Title: {title}
Abstract: {abstract}

Tone: {tone_map[tone]}
"""

    try:
        time.sleep(1)
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': temperature,
                'top_k': top_k_map[tone],
                'top_p': top_p_map[tone],
                'max_output_tokens': 600
            }
        )
        return response.text
    except Exception as e:
        return f'Error generating summary: {e}'

# -------------------- UI STYLES --------------------
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

# -------------------- HEADER (BOOK ANIMATION + TITLE) --------------------
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:center;">
    <lottie-player 
        src='data:application/json,{json.dumps(book_anim)}'
        background='transparent'  
        speed='1'  
        style='width:90px;height:90px;'  
        loop  
        autoplay>
    </lottie-player>
    <h2 style="margin-left:10px;">ResearchDaily</h2>
</div>

<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
""", unsafe_allow_html=True)

# -------------------- INPUTS --------------------
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
            st.error("Could not fetch papers.")
        elif response.status_code == 200:
            data = response.json()

            if not data.get('data'):
                st.error("No results returned.")
            else:
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