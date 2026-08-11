# ⚡ YouTube Copilot - Universal Video RAG Intelligence Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/frontend-Streamlit-red.svg)](https://streamlit.io/)
[![Node.js](https://img.shields.io/badge/backend-Node.js-green.svg)](https://nodejs.org/)
[![Google Gemini](https://img.shields.io/badge/LLM-Gemini%203.5%20Flash-purple.svg)](https://ai.google.dev/)
[![VectorDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange.svg)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**YouTube Copilot** is an enterprise-grade Retrieval-Augmented Generation (RAG) video intelligence platform inspired by YouTube's official *"Ask Gemini"* feature. It enables users to ask **ANY question** about ANY YouTube video genre—including Technical Lectures, Coding Tutorials, Podcasts, Music Mixes, Comedy Sketches, and Vlogs—receiving low-latency, strictly grounded answers accompanied by **clickable timestamp links `[MM:SS]`**.

---

## 🌟 Key Highlights & Features

- 🧠 **Universal 3-Layer Context Pipeline**: Dynamically ingests video metadata, full descriptions, and timed spoken transcript captions.
- 🎵 **Music & Non-Dialogue Video Support**: Directly inspects raw video metadata and description fields first for written tracklists, eliminating 0-chunk fallback errors in DJ mixes or music videos.
- ⏱️ **Interactive Timestamp Seeking**: AI responses cite exact timestamps `[MM:SS]` that directly seek and play the embedded YouTube video iFrame upon click.
- 🎨 **Obsidian Glassmorphism Visual UI**: Features ambient floating background lighting, neon glows, responsive card lifts, smooth keyframe animations, and seamless Dark/Light theme toggling.
- ⚡ **Dual Dashboard Engine**: Runs both a native **Streamlit Dashboard** (`app.py`) and a standalone **Single-Page Web Application** (`server.js` + `index.html`).

---

## 🏗️ Architecture & 3-Layer RAG Pipeline

```
                       ┌───────────────────────────────┐
                       │   YouTube Video Submission    │
                       └───────────────┬───────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                │                                             │
      ┌─────────▼─────────┐                         ┌─────────▼─────────┐
      │  Layer A: Metadata│                         │ Layer B: Captions │
      │  & Description    │                         │ Transcript API    │
      │  (yt-dlp/oEmbed)  │                         └─────────┬─────────┘
      └─────────┬─────────┘                                   │
                │                                   ┌─────────▼─────────┐
                │                                   │ Text Splitter     │
                │                                   │ (~800ch, 120ov)   │
                │                                   └─────────┬─────────┘
                │                                             │
                │                                   ┌─────────▼─────────┐
                │                                   │ Vector DB Index   │
                │                                   │ ChromaDB +        │
                │                                   │ text-embedding-004│
                │                                   └─────────┬─────────┘
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       │
                            ┌──────────▼──────────┐
                            │ Layer C: Direct     │
                            │ Description + RAG   │
                            │ Gemini Prompt Injection
                            └──────────┬──────────┘
                                       │
                            ┌──────────▼──────────┐
                            │ Grounded Answer with│
                            │ Clickable Timestamps│
                            └─────────────────────┘
```

1. **Layer A (Raw Metadata Extraction)**: Dynamically fetches Title, Channel Name, and FULL Video Description using `yt-dlp` / oEmbed.
2. **Layer B (Timed Captions Vector Indexing)**: Extracts transcript captions with start timestamps, chunks text with `RecursiveCharacterTextSplitter` (~800 chars, 120 overlap), and stores vector embeddings in ChromaDB using `text-embedding-004`.
3. **Layer C (Direct Prompt Context QA Engine)**: Direct prompt injection passes full raw description + retrieved vector chunks into Google Gemini 3.5 Flash, strictly grounding answers and preventing hallucinations.

---

## 🚀 Quickstart & Setup Guide

### Prerequisites
- Python `3.10+`
- Node.js `18+`
- A free [Google Gemini API Key](https://aistudio.google.com/)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/youtube-copilot-rag.git
cd youtube-copilot-rag
```

### 2. Environment Setup & Dependencies
```bash
# Create and activate Python virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install required Python packages
pip install -r requirements.txt
```

### 3. Set Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## 💻 Running the Application

### Option A: Standalone Web Dashboard (Node.js Server)
```bash
node server.js
```
Open **[http://localhost:8000/](http://localhost:8000/)** in your browser.

### Option B: Streamlit Dashboard
```bash
streamlit run app.py
```
Open **[http://localhost:8501/](http://localhost:8501/)** in your browser.

---

## 📂 Repository Structure

```
.
├── app.py                 # Streamlit RAG Application Backend
├── server.js              # Node.js Server & REST API Endpoint Handler
├── index.html             # Standalone Single-Page Application (HTML5)
├── styles.css             # Glassmorphism Design System & Keyframe Animations
├── app.js                 # Interactive Frontend JS & iFrame Player Integration
├── transcript_helper.py   # Python Metadata & Caption Extraction Helper
├── requirements.txt       # Python Dependency Specifications
├── .gitignore             # Git Exclusion Manifest
└── README.md              # Project Documentation
```

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for details.
