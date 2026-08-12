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
# 1. PAGE CONFIGURATION & GLASSMORPHISM VISUAL DESIGN SYSTEM
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="YouTube Copilot | Universal Video Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

GLASSMORPHISM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-gradient: linear-gradient(135deg, #0b0f19 0%, #1a102f 100%);
    --surface-glass: rgba(255, 255, 255, 0.05);
    --border-neon-cyan: rgba(0, 240, 255, 0.15);
    --border-neon-hover: rgba(0, 240, 255, 0.4);
    --neon-cyan: #00f0ff;
    --neon-magenta: #ff007f;
    --text-white: #f8fafc;
    --text-silver: #cbd5e1;
    --font-display: 'Geist', sans-serif;
    --font-body: 'Inter', sans-serif;
}

.stApp {
    background: var(--bg-gradient) !important;
    color: var(--text-silver);
    font-family: var(--font-body);
}

.stApp::before {
    content: '';
    position: fixed;
    top: -15vw;
    left: -15vw;
    width: 55vw;
    height: 55vw;
    background: radial-gradient(circle, rgba(0, 240, 255, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
}

.stApp::after {
    content: '';
    position: fixed;
    bottom: -15vw;
    right: -15vw;
    width: 55vw;
    height: 55vw;
    background: radial-gradient(circle, rgba(255, 0, 127, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
}

section[data-testid="stSidebar"] {
    background: rgba(11, 15, 25, 0.75) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-right: 1px solid var(--border-neon-cyan) !important;
}

.glass-card {
    background: var(--surface-glass);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border-neon-cyan);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: all 0.3s ease;
}

.glass-card:hover {
    border-color: var(--border-neon-hover);
    box-shadow: 0 12px 40px 0 rgba(0, 240, 255, 0.15);
}

.stButton > button {
    background: linear-gradient(135deg, var(--neon-cyan) 0%, var(--neon-magenta) 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(0, 240, 255, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(255, 0, 127, 0.5) !important;
}

.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid var(--border-neon-cyan) !important;
    border-radius: 10px !important;
    color: var(--text-white) !important;
    padding: 12px 16px !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--neon-cyan) !important;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.3) !important;
}

div[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.04) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid var(--border-neon-cyan) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
}

div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
    background: rgba(255, 0, 127, 0.08) !important;
    border-color: rgba(255, 0, 127, 0.25) !important;
}

.hero-title {
    font-family: var(--font-display);
    font-size: 34px;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #00f0ff 50%, #ff007f 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
}

a[href*="youtube.com/watch"] {
    color: var(--neon-cyan) !important;
    background: rgba(0, 240, 255, 0.1) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    border: 1px solid rgba(0, 240, 255, 0.3) !important;
    text-decoration: none !important;
    font-family: 'JetBrains Mono', monospace !important;
}

a[href*="youtube.com/watch"]:hover {
    background: rgba(0, 240, 255, 0.25) !important;
    color: #ffffff !important;
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.4) !important;
}
</style>
"""
st.markdown(GLASSMORPHISM_CSS, unsafe_allow_html=True)


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
    model_name: str = "gemini-3.5-flash",
    chat_history: list = None
) -> str:
    """Executes Copilot Query with Direct Video Metadata & Description Injection."""
    meta = fetch_youtube_metadata(video_url)

    if retrieved_chunks:
        context_text = "\n\n".join([f"[{doc.metadata.get('formatted_time', '00:00')}] {doc.page_content}" for doc in retrieved_chunks])
    else:
        context_text = "No spoken transcript captions available for this video."

    system_prompt = f"""You are YouTube Copilot, an AI video assistant (powered by Gemini 3.5 Flash).
Your task is to answer ANY type of question asked about this video like YouTube's "Ask Gemini" feature.

=== VIDEO METADATA & DESCRIPTION ===
Title: {meta['title']}
Channel: {meta['channel']}
Full Description:
{meta['description'] if meta['description'] else "No description provided."}

=== TRANSCRIPT CONTEXT ===
{context_text}

=== STRICT RESPONSE RULES ===
1. ANSWER ANY QUESTION: Provide direct, thorough, comprehensive, and high-intelligence answers to ANY question asked about this video's content, concepts, arguments, code, speakers, or topics.
2. CLICKABLE TIMESTAMPS: Always include clickable Markdown timestamp links using format: [MM:SS](https://www.youtube.com/watch?v={extract_video_id(video_url)}&t=Xs) whenever referencing key events, timestamps, quotes, or chapters.
3. MUSIC MIXES / TRACKLISTS: Inspect the FULL DESCRIPTION field first for tracklists. If no tracklist exists in the description or captions, state: "No written tracklist was found in the video metadata." DO NOT invent fake song names.
4. NO HALLUCINATIONS: If the question answer is not present in either the description or transcript, explicitly state: "The video description and captions do not contain this information."
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
    
    if "1.5" in model_name or "2.0" in model_name or "2.5" in model_name:
        model_name = "gemini-3.5-flash"

    llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=0.1)
    chain = prompt | llm

    response = chain.invoke({"input": user_query})
    return response.content


def generate_executive_summary(
    video_url: str,
    transcript_items: List[Dict[str, Any]],
    api_key: str,
    model_name: str = "gemini-3.5-flash"
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

    system_prompt = f"""You are YouTube Copilot, an expert AI video analyst.

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

If this is a music mix with no spoken captions, inspect the FULL DESCRIPTION first for a written tracklist. If no tracklist exists in the description or captions, explicitly state: "No written tracklist was found in the video metadata." DO NOT invent fake song titles.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Generate Executive Summary for this video.")
    ])

    if "1.5" in model_name or "2.0" in model_name or "2.5" in model_name:
        model_name = "gemini-3.5-flash"

    llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=0.2)
    chain = prompt | llm

    return chain.invoke({}).content


# -----------------------------------------------------------------------------
# 4. SIDEBAR CONFIGURATION (SECURE BACKEND API KEY)
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
    st.markdown('<div class="hero-title" style="font-size:24px;">⚙️ Model Preferences</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    chat_model = st.selectbox(
        "Gemini AI Model Selection",
        options=["gemini-3.5-flash", "gemini-flash-latest", "gemini-3.1-pro-preview"],
        index=0
    )
    
    top_k = st.slider("Retrieval Top-K Chunks", min_value=2, max_value=10, value=4, step=1)
    chunk_size = st.slider("Chunk Size", min_value=500, max_value=1500, value=800, step=50)
    chunk_overlap = st.slider("Chunk Overlap", min_value=0, max_value=300, value=120, step=10)
    
    st.markdown("---")
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
# 5. DASHBOARD & CONVERSATIONAL UI
# -----------------------------------------------------------------------------

st.markdown('<h1 class="hero-title">⚡ YouTube Copilot</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: var(--text-silver); margin-bottom: 20px;">Universal YouTube Intelligence • Ask ANY Question About ANY Video (Powered by Gemini 3.5 Flash)</p>', unsafe_allow_html=True)

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

    col_left, col_right = st.columns([5, 7], gap="large")

    # LEFT COLUMN: EMBEDDED VIDEO PLAYER & METADATA
    with col_left:
        st.markdown('### 🎥 Embedded Video Player')
        st.video(video_watch_url)
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.04); padding: 14px 16px; border-radius: 12px; border: 1px solid rgba(0,240,255,0.15); margin-bottom: 20px;">
            <div style="font-weight:700; font-size:16px; color:#ffffff; margin-bottom:4px;">{meta['title']}</div>
            <div style="color: var(--neon-cyan); font-size:13px; margin-bottom:10px;">Channel: {meta['channel']}</div>
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
                <span class="pill-badge pill-cyan">ID: {current_video_id}</span>
                <span class="pill-badge pill-indigo">Captions: {len(transcript_items)} Chunks</span>
                <span class="pill-badge pill-purple"><a href="{video_watch_url}" target="_blank" style="color:inherit;text-decoration:none;">Open YouTube ↗</a></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if meta.get('description'):
            with st.expander("📄 View Video Description & Tracklist", expanded=False):
                st.caption(meta['description'])

        st.markdown("### 📝 Executive Summary Engine")
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
            with st.expander("📝 Executive Summary", expanded=True):
                st.markdown(st.session_state.summary)

    # RIGHT COLUMN: CONVERSATIONAL RAG CHAT
    with col_right:
        st.markdown('### 💬 Universal Intelligence Copilot (Ask Gemini)')
        st.caption(f"Ask ANY question about video `{current_video_id}`.")

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

        user_query = st.chat_input("Ask ANY question about this video...")

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
