import os
import re
import time
import json
import urllib.request
from typing import List, Dict, Any, Optional
import streamlit as st

# Load local .env file securely if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# yt-dlp Import for Real Title, Channel, & Full Description Extraction
from yt_dlp import YoutubeDL

# LangChain & Google GenAI Imports
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_text_splitters import RecursiveCharacterTextSplitter

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STITCH TERMINAL OBSIDIAN DESIGN SYSTEM
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="YouTube Copilot | Universal Video Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

STITCH_OBSIDIAN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg-pitch: #050505;
    --bg-obsidian: #121214;
    --bg-zinc: #18181b;
    --border-silver: #27272a;
    --border-hover: #444748;
    --border-bright: #ffffff;
    --text-pure-white: #ffffff;
    --text-silver: #a1a1aa;
    --text-muted: #71717a;
    --font-geist: 'Calibri', 'Segoe UI', Arial, sans-serif;
    --font-mono: 'Calibri', 'Segoe UI', Arial, sans-serif;
}

/* Base Reset & Background - Calibri Bold */
.stApp, .stApp *:not(.material-symbols-outlined), button, input, select, textarea, div, p, span:not(.material-symbols-outlined), h1, h2, h3, h4, h5, h6 {
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif !important;
    font-weight: 700 !important;
}

.material-symbols-outlined, 
span.material-symbols-outlined, 
i.material-symbols-outlined {
    font-family: 'Material Symbols Outlined' !important;
    font-weight: normal !important;
    font-style: normal !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    display: inline-block !important;
    white-space: nowrap !important;
    direction: ltr !important;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background-color: var(--bg-pitch) !important;
    color: var(--text-pure-white) !important;
}

header[data-testid="stHeader"] {
    background-color: rgba(5, 5, 5, 0.9) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--border-silver) !important;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: var(--bg-obsidian) !important;
    border-right: 1px solid var(--border-silver) !important;
}

section[data-testid="stSidebar"] * {
    color: var(--text-silver) !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label {
    color: var(--text-pure-white) !important;
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif !important;
    font-size: 13px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    font-weight: 700 !important;
}

/* Custom Cards & Panels */
.obsidian-card {
    background-color: var(--bg-obsidian);
    border: 1px solid var(--border-silver);
    border-radius: 6px;
    padding: 16px 20px;
    margin-bottom: 16px;
}

.chip-mono {
    display: inline-flex;
    align-items: center;
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-silver);
    background-color: var(--bg-zinc);
    border: 1px solid var(--border-silver);
    padding: 4px 10px;
    border-radius: 4px;
    margin-right: 6px;
}

/* High-Contrast Stark White Primary Buttons */
.stButton > button {
    background-color: #ffffff !important;
    color: #050505 !important;
    border: 1px solid #ffffff !important;
    border-radius: 6px !important;
    padding: 12px 20px !important;
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background-color: #e0e0e0 !important;
    color: #000000 !important;
    border-color: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15) !important;
}

/* Input Fields & Select Boxes */
.stTextInput input, div[data-baseweb="select"] > div {
    background-color: var(--bg-zinc) !important;
    border: 1px solid var(--border-silver) !important;
    border-radius: 6px !important;
    color: var(--text-pure-white) !important;
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
}

.stTextInput input:focus, div[data-baseweb="select"]:focus-within {
    border-color: var(--border-bright) !important;
    box-shadow: none !important;
}

/* Expanders */
.stExpander {
    background-color: var(--bg-obsidian) !important;
    border: 1px solid var(--border-silver) !important;
    border-radius: 6px !important;
    margin-bottom: 16px !important;
}

.stExpander > details > summary {
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    color: var(--text-pure-white) !important;
}

/* Chat Messages */
div[data-testid="stChatMessage"] {
    background-color: var(--bg-obsidian) !important;
    border: 1px solid var(--border-silver) !important;
    border-radius: 6px !important;
    padding: 14px 16px !important;
    margin-bottom: 12px !important;
    color: var(--text-pure-white) !important;
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif !important;
    font-weight: 700 !important;
}

div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
    background-color: var(--bg-zinc) !important;
    border-color: var(--border-silver) !important;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] {
    background-color: var(--bg-zinc) !important;
    border: 1px solid var(--border-silver) !important;
    border-radius: 6px !important;
}

div[data-testid="stChatInput"] textarea {
    color: var(--text-pure-white) !important;
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
}

div[data-testid="stChatInput"]:focus-within {
    border-color: var(--border-bright) !important;
}

/* Video Frame Container */
div[data-testid="stVideo"] {
    border: 1px solid var(--border-silver);
    border-radius: 6px;
    overflow: hidden;
    background-color: var(--bg-obsidian);
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 4px;
    height: 4px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: var(--border-silver);
    border-radius: 0px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--border-hover);
}

/* Monospace YouTube Timestamp Links */
a[href*="youtube.com/watch"] {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.06) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    border: 1px solid #27272a !important;
    text-decoration: none !important;
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
}

a[href*="youtube.com/watch"]:hover {
    background: #27272a !important;
    border-color: #ffffff !important;
    color: #ffffff !important;
}
</style>
"""
st.markdown(STITCH_OBSIDIAN_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. UNIVERSAL CONTEXT PIPELINE (LAYER A & LAYER B)
# -----------------------------------------------------------------------------

def extract_video_id(url_or_id: str) -> Optional[str]:
    """Extracts 11-character YouTube video ID from various URL formats or raw ID."""
    if not url_or_id:
        return None
    url_or_id = url_or_id.strip()
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    pattern = r'(?:v=|\/shorts\/|\/embed\/|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url_or_id)
    return match.group(1) if match else None


def format_seconds_to_timestamp(seconds: float) -> str:
    """Formats floating seconds to MM:SS or HH:MM:SS string."""
    seconds_int = int(seconds)
    hours = seconds_int // 3600
    minutes = (seconds_int % 3600) // 60
    secs = seconds_int % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


@st.cache_data(show_spinner=False)
def fetch_youtube_metadata(video_url: str) -> Dict[str, str]:
    """Extracts REAL Video Title, Channel Name, and FULL Video Description using yt-dlp."""
    video_id = extract_video_id(video_url)
    clean_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else video_url

    meta = {
        "title": f"YouTube Video ({video_id or 'Unknown'})",
        "description": "No description provided.",
        "channel": "YouTube Creator"
    }

    try:
        ydl_opts = {
            'extract_flat': True,
            'skip_download': True,
            'quiet': True,
            'no_warnings': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            if info:
                meta["title"] = info.get("title") or meta["title"]
                meta["description"] = info.get("description") or meta["description"]
                meta["channel"] = info.get("uploader") or info.get("channel") or meta["channel"]
                return meta
    except Exception:
        pass

    try:
        req = urllib.request.Request(
            f"https://www.youtube.com/oembed?url={clean_url}&format=json",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            meta["title"] = data.get("title", meta["title"])
            meta["channel"] = data.get("author_name", meta["channel"])
    except Exception:
        pass

    return meta


@st.cache_data(show_spinner=False)
def fetch_youtube_transcript(video_id: str) -> List[Dict[str, Any]]:
    """Extracts spoken captions with start timestamps using youtube-transcript-api."""
    try:
        raw_transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
            except Exception:
                transcript = transcript_list.find_generated_transcript(['en'])
            raw_transcript = transcript.fetch()
        except Exception:
            return []
    except Exception:
        return []

    formatted_items = []
    for entry in raw_transcript:
        start_seconds = int(entry.get('start', 0))
        formatted_time = format_seconds_to_timestamp(start_seconds)
        youtube_url = f"https://www.youtube.com/watch?v={video_id}&t={start_seconds}s"
        formatted_items.append({
            "text": entry.get("text", "").strip(),
            "start_seconds": start_seconds,
            "duration": entry.get("duration", 0),
            "formatted_time": formatted_time,
            "youtube_url": youtube_url
        })
    return formatted_items


@st.cache_resource(show_spinner=False)
def build_vector_engine(
    video_id: str,
    _transcript_items: List[Dict[str, Any]],
    api_key: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    embedding_model: str = "models/text-embedding-004"
) -> Optional[Chroma]:
    """Stores transcript chunks in ChromaDB with text-embedding-004."""
    if not _transcript_items:
        return None

    documents = []
    for item in _transcript_items:
        doc = Document(
            page_content=item["text"],
            metadata={
                "start_seconds": item["start_seconds"],
                "formatted_time": item["formatted_time"],
                "youtube_url": item["youtube_url"],
                "source": video_id
            }
        )
        documents.append(doc)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    split_docs = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=embedding_model,
        google_api_key=api_key
    )

    return Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        collection_name=f"yt_{video_id}_{int(time.time())}"
    )


# -----------------------------------------------------------------------------
# 3. LAYER C: DIRECT PROMPT INJECTION & CONVERSATIONAL QA ENGINE
# -----------------------------------------------------------------------------

def run_copilot_query(
    user_query: str,
    video_url: str,
    retrieved_chunks: list,
    api_key: str,
    model_name: str = "gemini-3.5-flash-lite",
    chat_history: list = None
) -> str:
    """Executes Copilot Query with Direct Video Metadata & Description Injection."""
    meta = fetch_youtube_metadata(video_url)
    v_id = extract_video_id(video_url)

    if retrieved_chunks:
        context_text = "\n\n".join([f"[{doc.metadata.get('formatted_time', '00:00')}] {doc.page_content}" for doc in retrieved_chunks])
    else:
        context_text = "No spoken transcript captions available for this video."

    system_prompt = f"""You are YouTube Copilot, YouTube's official "Ask Gemini" video assistant.
Your goal is to provide direct, accurate, natural, and comprehensive answers to ANY question asked about this video (Title: "{meta['title']}", ID: {v_id}).

=== VIDEO METADATA & DESCRIPTION ===
Title: {meta['title']}
Channel: {meta['channel']}
Full Description:
{meta['description'] if meta['description'] else "No description provided."}

=== TRANSCRIPT CONTEXT ===
{context_text}

=== STRICT RESPONSE & FORMATTING RULES ===
1. DIRECT NATURAL ANSWERS: Give thorough, well-structured, clear answers directly addressing what the user asked (like YouTube's "Ask Gemini" feature). Format key sections using bold text or bullet points.
2. CLICKABLE TIMESTAMPS: Whenever mentioning a timestamp, chapter, quote, or key moment, format it as a clickable markdown timestamp link: [MM:SS](https://www.youtube.com/watch?v={v_id}&t=Xs) or [HH:MM:SS](https://www.youtube.com/watch?v={v_id}&t=Xs).
3. NO INTERNAL MATH OR CONVERSIONS: Output ONLY clean markdown text and timestamp links. DO NOT print raw math formulas, seconds conversions, or scratchpad calculations (e.g. NEVER write "1:16:54 -> 3600 + 16*60 = 4614s").
4. GROUNDED INTELLIGENCE: Rely on the video title, description, and captions provided above. If no spoken captions exist, use the full description. If information is not available, state: "The video description and captions do not contain this information."
"""

    messages = [("system", system_prompt)]
    
    if chat_history:
        for m in chat_history:
            if m["role"] == "user":
                messages.append(("human", m["content"]))
            elif m["role"] == "assistant":
                messages.append(("ai", m["content"]))

    messages.append(("human", "{input}"))

    prompt = ChatPromptTemplate.from_messages(messages)
    
    model_to_use = model_name or "gemini-3.5-flash-lite"
    llm = ChatGoogleGenerativeAI(model=model_to_use, google_api_key=api_key, temperature=0.1)
    chain = prompt | llm

    response = chain.invoke({"input": user_query})
    return response.content


def generate_executive_summary(
    video_url: str,
    transcript_items: List[Dict[str, Any]],
    api_key: str,
    model_name: str = "gemini-3.5-flash-lite"
) -> str:
    """Generates Executive Summary using direct metadata description injection."""
    meta = fetch_youtube_metadata(video_url)
    video_id = extract_video_id(video_url)
    
    transcript_text = "\n".join([
        f"[{item['formatted_time']}] {item['text']} (URL: {item['youtube_url']})"
        for item in transcript_items
    ]) if transcript_items else "[No Spoken Transcript Captions Available]"

    if len(transcript_text) > 80000:
        transcript_text = transcript_text[:80000] + "\n...[Transcript Truncated]"

    system_prompt = f"""You are YouTube Copilot, YouTube's official "Ask Gemini" video analyst.

=== VIDEO METADATA & DESCRIPTION ===
Title: {meta['title']}
Channel: {meta['channel']}
Full Description:
{meta['description']}

=== SPOKEN TRANSCRIPT CAPTIONS ===
{transcript_text}

Generate a structured Executive Summary formatted as:
1. 📌 **Overview**: 2-3 sentence high-level synthesis.
2. 🔑 **Key Takeaways & Chapters / Tracklist**: Bullet points with clickable Markdown timestamp links `[MM:SS](https://www.youtube.com/watch?v={video_id}&t=Xs)`.
3. 💡 **Actionable Insights / Core Conclusions**: 2-3 key takeaways.

DO NOT print raw math formulas or scratchpad seconds calculations.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Generate Executive Summary for this video.")
    ])

    model_to_use = model_name or "gemini-3.5-flash-lite"
    llm = ChatGoogleGenerativeAI(model=model_to_use, google_api_key=api_key, temperature=0.2)
    chain = prompt | llm

    return chain.invoke({}).content


# -----------------------------------------------------------------------------
# 4. SIDEBAR CONFIGURATION (TERMINAL OBSIDIAN STYLE)
# -----------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []
if "summary" not in st.session_state:
    st.session_state.summary = None
if "video_id" not in st.session_state:
    st.session_state.video_id = None
if "metadata" not in st.session_state:
    st.session_state.metadata = None
if "transcript_data" not in st.session_state:
    st.session_state.transcript_data = None

# Secure backend API Key loading (Never exposed in UI input boxes)
api_key = os.getenv("GOOGLE_API_KEY", "")

with st.sidebar:
    st.markdown('<div class="chip-mono" style="margin-bottom: 12px;">SYSTEM CONFIG</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="font-family: \'Calibri\', sans-serif; font-size: 18px; font-weight: 700; color: #ffffff; margin-top: 0;">⚙️ Model Preferences</h2>', unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: #27272a; margin: 16px 0;'/>", unsafe_allow_html=True)
    chat_model = st.selectbox(
        "Gemini AI Model Selection",
        options=["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.6-flash"],
        index=0
    )
    
    top_k = st.slider("Retrieval Top-K Chunks", min_value=2, max_value=10, value=4, step=1)
    chunk_size = st.slider("Chunk Size", min_value=500, max_value=1500, value=800, step=50)
    chunk_overlap = st.slider("Chunk Overlap", min_value=0, max_value=300, value=120, step=10)
    
    st.markdown("<hr style='border-color: #27272a; margin: 16px 0;'/>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Session & Cache", use_container_width=True):
        st.session_state.messages = []
        st.session_state.summary = None
        st.session_state.video_id = None
        st.session_state.metadata = None
        st.session_state.transcript_data = None
        st.cache_resource.clear()
        st.cache_data.clear()
        st.toast("Session memory cleared!", icon="✨")
        st.rerun()


# -----------------------------------------------------------------------------
# 5. DASHBOARD & CONVERSATIONAL UI (STITCH DUAL-COLUMN OBSIDIAN GRID)
# -----------------------------------------------------------------------------

# Top Header Layout
st.markdown("""
<div style="border-bottom: 1px solid #27272a; padding-bottom: 16px; margin-bottom: 24px;">
    <div class="chip-mono" style="margin-bottom: 8px;">YOUTUBE COPILOT // TERMINAL OBSIDIAN</div>
    <h1 style="font-family: 'Geist', sans-serif; font-size: 28px; font-weight: 700; color: #ffffff; margin: 0;">⚡ YouTube Copilot</h1>
    <p style="font-family: 'Geist', sans-serif; font-size: 14px; color: #a1a1aa; margin-top: 4px; margin-bottom: 0;">Universal Video Intelligence • Ask ANY Question About ANY Video (Powered by Gemini 3.5 Flash)</p>
</div>
""", unsafe_allow_html=True)

url_input = st.text_input(
    "Enter YouTube URL or Video ID",
    value="",
    placeholder="Paste YouTube URL or Video ID here (e.g. https://www.youtube.com/watch?v=dQw4w9WgXcQ)..."
)

current_video_id = extract_video_id(url_input)

if not api_key:
    st.warning("⚠️ GOOGLE_API_KEY environment variable is missing. Please add it to your local .env file.", icon="🔑")
    st.stop()

if not current_video_id:
    st.info("🎬 Please paste a YouTube URL or Video ID above to begin video analysis.", icon="🎬")
    st.stop()


if current_video_id:
    video_watch_url = f"https://www.youtube.com/watch?v={current_video_id}"

    if st.session_state.video_id != current_video_id:
        st.session_state.video_id = current_video_id
        st.session_state.messages = []
        st.session_state.summary = None
        st.session_state.metadata = None
        st.session_state.transcript_data = None

    if st.session_state.metadata is None:
        with st.spinner("🔍 Layer A: Extracting real video metadata & description..."):
            st.session_state.metadata = fetch_youtube_metadata(video_watch_url)

    if st.session_state.transcript_data is None:
        with st.spinner("⏳ Layer B: Extracting spoken captions & building vector index..."):
            st.session_state.transcript_data = fetch_youtube_transcript(current_video_id)

    meta = st.session_state.metadata
    transcript_items = st.session_state.transcript_data

    vectorstore = None
    retriever = None
    if transcript_items:
        with st.spinner("🧠 Layer B: Indexing vector memory in ChromaDB..."):
            try:
                vectorstore = build_vector_engine(
                    video_id=current_video_id,
                    _transcript_items=transcript_items,
                    api_key=api_key,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                if vectorstore:
                    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
            except Exception:
                pass

    col_left, col_right = st.columns([6, 5], gap="large")

    # LEFT COLUMN: EMBEDDED VIDEO PLAYER, METADATA, & SUMMARY ENGINE
    with col_left:
        st.markdown('<div class="chip-mono" style="margin-bottom: 8px;">VIDEO STREAM & METADATA</div>', unsafe_allow_html=True)
        st.video(video_watch_url)
        
        st.markdown(f"""
        <div class="obsidian-card" style="margin-top: 12px;">
            <div style="font-family: 'Geist', sans-serif; font-weight: 700; font-size: 17px; color: #ffffff; margin-bottom: 4px; line-height: 1.3;">{meta['title']}</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #a1a1aa; margin-bottom: 12px;">Channel: {meta['channel']}</div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                <span class="chip-mono">ID: {current_video_id}</span>
                <span class="chip-mono">CAPTIONS: {len(transcript_items)} CHUNKS</span>
                <a href="{video_watch_url}" target="_blank" class="chip-mono" style="text-decoration: none; color: #ffffff !important;">OPEN YOUTUBE ↗</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if meta.get('description'):
            with st.expander("📄 View Video Description & Metadata", expanded=False):
                st.caption(meta['description'])

        st.markdown('<div class="chip-mono" style="margin-top: 16px; margin-bottom: 8px;">INTELLIGENCE SYNTHESIS</div>', unsafe_allow_html=True)
        if st.button("⚡ Generate Executive Summary", type="primary", use_container_width=True):
            with st.spinner("✨ Synthesizing metadata & transcript with Gemini..."):
                try:
                    summary_res = generate_executive_summary(
                        video_url=video_watch_url,
                        transcript_items=transcript_items,
                        api_key=api_key,
                        model_name=chat_model
                    )
                    st.session_state.summary = summary_res
                    st.toast("Executive Summary generated!", icon="⚡")
                except Exception as e:
                    st.error(f"Failed to generate summary: {str(e)}")

        if st.session_state.summary:
            with st.expander("📝 Executive Summary Output", expanded=True):
                st.markdown(st.session_state.summary)

    # RIGHT COLUMN: CONVERSATIONAL COPILOT RAG PANEL
    with col_right:
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #27272a; padding-bottom: 8px; margin-bottom: 12px;">
            <h3 style="font-family: 'Geist', sans-serif; font-size: 16px; font-weight: 600; color: #ffffff; margin: 0;">💬 Conversational Copilot</h3>
            <span class="chip-mono" style="color: #ffffff; border-color: #ffffff;">LIVE COPILOT</span>
        </div>
        """, unsafe_allow_html=True)

        with st.container(height=580):
            if not st.session_state.messages:
                st.markdown("""
                <div style="text-align: center; padding: 40px 20px; color: #a1a1aa; font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: 0.05em;">
                    [ COPILOT INITIALIZED // ASK ANY QUESTION ABOUT THIS VIDEO ]
                </div>
                """, unsafe_allow_html=True)

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg["role"] == "assistant" and msg.get("sources"):
                        with st.expander("🔍 View Retrieved Sources"):
                            for idx, doc in enumerate(msg["sources"], 1):
                                time_str = doc.metadata.get("formatted_time", "00:00")
                                yt_url = doc.metadata.get("youtube_url", "#")
                                st.markdown(f"**Source {idx}** • [`{time_str}`]({yt_url})")
                                st.caption(doc.page_content)

        user_query = st.chat_input("Ask a question about this video...")

        if user_query:
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                with st.spinner("🤖 Layer C: Inspecting metadata & transcript context..."):
                    try:
                        retrieved_chunks = []
                        if retriever:
                            retrieved_chunks = retriever.invoke(user_query)

                        answer_text = run_copilot_query(
                            user_query=user_query,
                            video_url=video_watch_url,
                            retrieved_chunks=retrieved_chunks,
                            api_key=api_key,
                            model_name=chat_model,
                            chat_history=st.session_state.messages[:-1]
                        )

                        st.markdown(answer_text)

                        if retrieved_chunks:
                            with st.expander("🔍 View Retrieved Sources"):
                                for idx, doc in enumerate(retrieved_chunks, 1):
                                    time_str = doc.metadata.get("formatted_time", "00:00")
                                    yt_url = doc.metadata.get("youtube_url", "#")
                                    st.markdown(f"**Source {idx}** • [`{time_str}`]({yt_url})")
                                    st.caption(doc.page_content)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer_text,
                            "sources": retrieved_chunks
                        })

                    except Exception as e:
                        st.error(f"❌ Error generating response: {str(e)}")
