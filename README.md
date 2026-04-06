# 📄 ResearchDaily

**ResearchDaily** is a Streamlit-based web application that helps users discover and understand academic research papers quickly. It fetches papers from the Semantic Scholar API and generates detailed summaries using Google Gemini AI.

---


🚀 **Live Demo:** [Try the app](https://researchdaily.streamlit.app/)

**ResearchDaily** is a Streamlit-based web

---

## 🚀 Features

* 🔍 Search research papers by topic
* 📚 Fetch results from Semantic Scholar
* 🤖 AI-generated summaries (Gemini)
* 🎯 Multiple tone options:

  * Professional
  * Conversational
  * Bold
  * Creative
* 🎨 Clean UI with custom styling
* ⚡ Fast and interactive experience

---

## 🎯 Tone & Model Parameters

The application allows users to select different tones for AI-generated summaries.
Each tone maps to specific **generation parameters** that control creativity, diversity, and style.

### 🔧 Tone Configuration

* **Professional** *(temperature: 0.3, top-k: 20, top-p: 0.7)*
  → Formal, academic, structured summaries with minimal randomness

* **Conversational** *(temperature: 0.6, top-k: 40, top-p: 0.8)*
  → Friendly, easy-to-understand explanations with moderate variation

* **Bold** *(temperature: 0.9, top-k: 50, top-p: 0.9)*
  → Strong, assertive, highlights key insights

* **Creative** *(temperature: 1.0, top-k: 80, top-p: 0.95)*
  → Highly expressive, imaginative, and diverse output

---

### 🤖 Model Settings

* **Model:** `gemini-3.1-flash-lite-preview`
* **Max Output Tokens:** `600`
* **Temperature Range:** `0.3 → 1.0`
* **Top-k Range:** `20 → 80`
* **Top-p Range:** `0.7 → 0.95`

---

### ⚙️ Parameter Explanation

* **Temperature** → Controls randomness (lower = more accurate, higher = more creative)
* **Top-k** → Limits selection to the top *k* most likely tokens
* **Top-p (nucleus sampling)** → Selects from tokens whose cumulative probability reaches *p*
* **Max Output Tokens** → Controls maximum response length

---

### 💡 How It Works

1. User selects a tone
2. System maps tone → parameters (temperature, top-k, top-p)
3. Gemini generates summary based on:

   * Paper title
   * Abstract
   * Selected tone configuration

---

This setup ensures:

* High accuracy for professional use
* Balanced readability for conversational mode
* Strong emphasis in bold mode
* Maximum creativity in creative mode

---

## 🛠️ Tech Stack

* **Frontend & App Framework:** Streamlit
* **API:** Semantic Scholar API
* **AI Model:** Google Gemini
* **Language:** Python

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/httpsfahim/researchdaily
cd researchdaily
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔑 Setup API Keys

Create environment variables (or use Streamlit secrets):

```
GEMINI_API=your_gemini_api_key
SEMANTIC_SCHOLAR_API=your_semantic_scholar_api_key
```

---

## ▶️ Run the App

```bash
streamlit run researchdaily.py
```

---

## 🌐 Deployment

This app is deployed using **Streamlit Community Cloud**.

To deploy:

1. Push your code to GitHub
2. Connect repo in Streamlit Cloud
3. Add secrets in settings
4. Deploy

---

## 🎨 UI Highlights

* Dark green theme (`#314733`)
* White search input for clarity
* Black action buttons
* Minimal and distraction-free layout

---

## 📌 Example Use

* Enter topic: `Artificial Intelligence`
* Select number of papers
* Choose tone
* Click **Search**
* Get summarized research instantly

---

## ⚠️ Notes

* API keys are required for full functionality
* Do NOT expose your API keys publicly
* Streamlit Cloud may not fully hide toolbar (platform limitation)

---

## 🤝 Contributing

Feel free to fork this repository and improve it. Pull requests are welcome!

---

## 📄 License

This project is for educational and personal use.

---

## 💡 Future Improvements

* Add clickable paper links
* Export summaries (PDF/CSV)
* Faster parallel processing
* Better UI components (cards, animations)

---

## 🙌 Acknowledgements

* Semantic Scholar
* Google Gemini
* Streamlit

---

⭐ If you like this project, consider giving it a star!
