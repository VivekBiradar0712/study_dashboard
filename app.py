"""
Study Monitoring Dashboard - Streamlit Application
Live time tracking dashboard for students with real-time study session monitoring
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, date, timedelta, time
import time as time_module
import base64
import os
import uuid
from database import StudyDatabase, StudySession, Subject, StudyGoal

# Page configuration
st.set_page_config(
    page_title="Study Monitor Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# THEME & STYLING SYSTEM
# =============================================================================

# Initialize theme in session state
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Theme configurations
THEMES = {
    "light": {
        "bg_primary": "#f8fafc",
        "bg_secondary": "#ffffff",
        "bg_tertiary": "#f1f5f9",
        "text_primary": "#0f172a",
        "text_secondary": "#475569",
        "text_muted": "#94a3b8",
        "border": "#e2e8f0",
        "border_light": "#f1f5f9",
        "accent": "#2a78d6",
        "accent_hover": "#1e5bb8",
        "accent_light": "#dbeafe",
        "success": "#0ca30c",
        "success_light": "#dcfce7",
        "warning": "#fab219",
        "warning_light": "#fef9c3",
        "danger": "#e03131",
        "danger_light": "#fee2e2",
        "shadow": "0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.06)",
        "shadow_hover": "0 10px 25px rgba(0,0,0,0.1), 0 5px 10px rgba(0,0,0,0.04)",
        "card_bg": "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)",
        "sidebar_bg": "#f8fafc",
        "input_bg": "#ffffff",
        "input_border": "#e2e8f0",
        "timer_bg": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        "timer_text": "#f8fafc",
        "timer_accent": "#60a5fa",
    },
    "dark": {
        "bg_primary": "#0f172a",
        "bg_secondary": "#1e293b",
        "bg_tertiary": "#334155",
        "text_primary": "#f8fafc",
        "text_secondary": "#cbd5e1",
        "text_muted": "#64748b",
        "border": "#334155",
        "border_light": "#1e293b",
        "accent": "#60a5fa",
        "accent_hover": "#93c5fd",
        "accent_light": "#1e3a5f",
        "success": "#4ade80",
        "success_light": "#064e3b",
        "warning": "#fbbf24",
        "warning_light": "#78350f",
        "danger": "#f87171",
        "danger_light": "#7f1d1d",
        "shadow": "0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)",
        "shadow_hover": "0 10px 25px rgba(0,0,0,0.4), 0 5px 10px rgba(0,0,0,0.2)",
        "card_bg": "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
        "sidebar_bg": "#0f172a",
        "input_bg": "#1e293b",
        "input_border": "#334155",
        "timer_bg": "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
        "timer_text": "#0f172a",
        "timer_accent": "#2a78d6",
    }
}

def get_theme():
    return THEMES[st.session_state.theme]

def inject_theme_css():
    theme = get_theme()
    st.markdown(f"""
<style>
    :root {{
        --bg-primary: {theme['bg_primary']};
        --bg-secondary: {theme['bg_secondary']};
        --bg-tertiary: {theme['bg_tertiary']};
        --text-primary: {theme['text_primary']};
        --text-secondary: {theme['text_secondary']};
        --text-muted: {theme['text_muted']};
        --border: {theme['border']};
        --border-light: {theme['border_light']};
        --accent: {theme['accent']};
        --accent-hover: {theme['accent_hover']};
        --accent-light: {theme['accent_light']};
        --success: {theme['success']};
        --success-light: {theme['success_light']};
        --warning: {theme['warning']};
        --warning-light: {theme['warning_light']};
        --danger: {theme['danger']};
        --danger-light: {theme['danger_light']};
        --shadow: {theme['shadow']};
        --shadow-hover: {theme['shadow_hover']};
        --card-bg: {theme['card_bg']};
        --sidebar-bg: {theme['sidebar_bg']};
        --input-bg: {theme['input_bg']};
        --input-border: {theme['input_border']};
        --timer-bg: {theme['timer_bg']};
        --timer-text: {theme['timer_text']};
        --timer-accent: {theme['timer_accent']};
    }}

    /* Global Styles */
    .stApp {{
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }}

    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border);
    }}

    section[data-testid="stSidebar"] .stMarkdown {{
        color: var(--text-primary) !important;
    }}

    /* Custom Components */
    .metric-card {{
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
    }}
    .metric-card:hover {{
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }}
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }}
    .metric-label {{
        font-size: 0.875rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }}

    .timer-display {{
        font-size: 5rem;
        font-weight: 800;
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Mono', monospace;
        color: var(--timer-text);
        text-align: center;
        font-variant-numeric: tabular-nums;
        text-shadow: 0 4px 20px rgba(0,0,0,0.15);
        letter-spacing: -0.02em;
    }}
    .timer-label {{
        font-size: 1.125rem;
        color: var(--text-muted);
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 500;
    }}
    .timer-container {{
        background: var(--timer-bg);
        border-radius: 24px;
        padding: 3rem 2rem;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
    }}
    .timer-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent), var(--success), var(--warning), var(--accent));
        background-size: 200% 100%;
        animation: gradientShift 3s ease infinite;
    }}
    @keyframes gradientShift {{
        0%, 100% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
    }}

    .subject-card {{
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }}
    .subject-card:hover {{
        box-shadow: var(--shadow-hover);
        transform: translateX(4px);
    }}

    .stButton > button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 0.9375rem !important;
    }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%) !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(42, 120, 214, 0.3) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 6px 20px rgba(42, 120, 214, 0.4) !important;
        transform: translateY(-1px) !important;
    }}
    .stButton > button[kind="secondary"] {{
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
    }}
    .stButton > button[kind="secondary"]:hover {{
        background: var(--border) !important;
        transform: translateY(-1px) !important;
    }}
    .stButton > button:disabled {{
        opacity: 0.5 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }}

    .session-row {{
        padding: 1rem;
        border-radius: 12px;
        background: var(--bg-secondary);
        margin: 0.5rem 0;
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }}
    .session-row:hover {{
        box-shadow: var(--shadow-hover);
        border-color: var(--accent);
    }}
    .status-active {{ border-left: 4px solid var(--success); }}
    .status-paused {{ border-left: 4px solid var(--warning); }}
    .status-completed {{ border-left: 4px solid var(--accent); }}

    div[data-testid="stMetric"] {{
        background: var(--bg-secondary) !important;
        padding: 1.25rem !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        box-shadow: var(--shadow) !important;
    }}
    div[data-testid="stMetric"] label {{
        color: var(--text-muted) !important;
        font-size: 0.8125rem !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: var(--text-primary) !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }}

    .chart-container {{
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--border);
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow);
    }}

    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {{
        background: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-light) !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: var(--bg-tertiary);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid var(--border);
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: var(--bg-secondary) !important;
        color: var(--accent) !important;
        box-shadow: var(--shadow) !important;
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }}
    .streamlit-expanderContent {{
        background: var(--bg-primary) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }}

    /* Dataframe */
    .stDataFrame {{
        background: var(--bg-secondary) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
    }}

    /* Progress bar */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, var(--accent), var(--success)) !important;
        border-radius: 8px !important;
    }}
    .stProgress > div > div > div {{
        background: var(--bg-tertiary) !important;
        border-radius: 8px !important;
    }}

    /* Color picker */
    .stColorPicker > div > div {{
        border-radius: 10px !important;
        border: 2px solid var(--border) !important;
    }}

    /* File uploader */
    .stFileUploader > div {{
        background: var(--bg-secondary) !important;
        border: 2px dashed var(--border) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
    }}
    .stFileUploader > div:hover {{
        border-color: var(--accent) !important;
        background: var(--accent-light) !important;
    }}

    /* Radio */
    .stRadio > div {{
        gap: 0.5rem !important;
    }}
    .stRadio label {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s ease !important;
    }}
    .stRadio label:hover {{
        border-color: var(--accent) !important;
        background: var(--accent-light) !important;
    }}
    .stRadio [data-testid="stMarkdownContainer"] p {{
        font-weight: 500 !important;
        color: var(--text-primary) !important;
    }}

    /* Divider */
    hr {{
        border-color: var(--border) !important;
        margin: 2rem 0 !important;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--bg-primary);
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border);
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--text-muted);
    }}

    /* Animations */
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    .animate-pulse {{
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}

    @keyframes spin {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    .animate-spin {{
        animation: spin 1s linear infinite;
    }}

    /* Badge */
    .badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .badge-success {{
        background: var(--success-light);
        color: var(--success);
    }}
    .badge-warning {{
        background: var(--warning-light);
        color: var(--warning);
    }}
    .badge-info {{
        background: var(--accent-light);
        color: var(--accent);
    }}

    /* Note/File Card */
    .note-card {{
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
    }}
    .note-card-header {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border);
    }}
    .note-card-content {{
        color: var(--text-secondary);
        line-height: 1.6;
        white-space: pre-wrap;
    }}
    .file-link {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: var(--accent-light);
        color: var(--accent);
        border-radius: 8px;
        font-weight: 500;
        text-decoration: none;
        transition: all 0.2s ease;
    }}
    .file-link:hover {{
        background: var(--accent);
        color: white;
    }}

    /* Live indicator */
    .live-indicator {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: var(--success-light);
        color: var(--success);
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.875rem;
    }}
    .live-indicator::before {{
        content: '';
        width: 8px;
        height: 8px;
        background: var(--success);
        border-radius: 50%;
        animation: pulse 1.5s ease-in-out infinite;
    }}

    /* Date/Time display */
    .datetime-display {{
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Mono', monospace;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
    }}
    .datetime-label {{
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }}

    /* Subject progress ring */
    .progress-ring {{
        transform: rotate(-90deg);
    }}

    /* Footer */
    .footer {{
        text-align: center;
        padding: 2rem;
        color: var(--text-muted);
        font-size: 0.875rem;
        border-top: 1px solid var(--border);
        margin-top: 3rem;
    }}
</style>
""", unsafe_allow_html=True)

inject_theme_css()

# =============================================================================
# DATABASE & SESSION STATE
# =============================================================================

@st.cache_resource
def get_database():
    return StudyDatabase()

db = get_database()

# Session state initialization
if "active_session" not in st.session_state:
    st.session_state.active_session = None
if "paused_session" not in st.session_state:
    st.session_state.paused_session = None
if "timer_start_time" not in st.session_state:
    st.session_state.timer_start_time = None
if "accumulated_seconds" not in st.session_state:
    st.session_state.accumulated_seconds = 0
if "last_update" not in st.session_state:
    st.session_state.last_update = time_module.time()
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "session_notes" not in st.session_state:
    st.session_state.session_notes = ""
if "session_file" not in st.session_state:
    st.session_state.session_file = None

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_duration(seconds: int) -> str:
    """Format seconds as HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_duration_short(seconds: int) -> str:
    """Format seconds as Hh Mm or Mm Ss"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m {seconds % 60}s"

def get_current_session_time() -> int:
    """Calculate current elapsed time for active session - synced with system time"""
    if st.session_state.active_session and st.session_state.timer_start_time:
        elapsed = int(time_module.time() - st.session_state.timer_start_time)
        return st.session_state.accumulated_seconds + elapsed
    return st.session_state.accumulated_seconds

def load_active_session():
    """Load active or paused session from database"""
    active = db.get_active_session()
    paused = db.get_paused_session()

    if active:
        st.session_state.active_session = active
        start_dt = datetime.fromisoformat(active.start_time)
        st.session_state.timer_start_time = start_dt.timestamp()
        st.session_state.accumulated_seconds = active.duration_seconds
        st.session_state.session_notes = active.notes or ""
    elif paused:
        st.session_state.paused_session = paused
        st.session_state.accumulated_seconds = paused.duration_seconds
        st.session_state.session_notes = paused.notes or ""

def save_uploaded_file(uploaded_file, prefix="study"):
    """Save uploaded file and return path"""
    if uploaded_file is None:
        return "", "", ""
    os.makedirs("uploads", exist_ok=True)
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    file_name = f"{prefix}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = os.path.join("uploads", file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path, uploaded_file.name, file_ext

def get_file_icon(file_type: str) -> str:
    """Get icon for file type"""
    if file_type.lower() in ['.pdf']:
        return "📄"
    elif file_type.lower() in ['.doc', '.docx']:
        return "📝"
    elif file_type.lower() in ['.txt', '.md']:
        return "📃"
    elif file_type.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        return "🖼️"
    else:
        return "📎"

def create_download_link(file_path: str, file_name: str) -> str:
    """Create download link for file"""
    if not file_path or not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}" class="file-link">{get_file_icon(os.path.splitext(file_name)[1])} {file_name}</a>'

def display_note_card(notes: str, file_path: str, file_name: str, file_type: str, title: str = "Notes"):
    """Display notes and file attachment card"""
    if not notes and not file_path:
        return
    st.markdown(f"""
    <div class="note-card">
        <div class="note-card-header">
            <span style="font-weight: 600; color: var(--text-primary);">{title}</span>
        </div>
        <div class="note-card-content">
    """, unsafe_allow_html=True)
    if notes:
        st.markdown(f"<div style='margin-bottom: 0.75rem;'>{notes}</div>", unsafe_allow_html=True)
    if file_path:
        st.markdown(create_download_link(file_path, file_name), unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# Load session on startup
if st.session_state.active_session is None and st.session_state.paused_session is None:
    load_active_session()

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

with st.sidebar:
    # Theme Toggle at top
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("## 📚 Study Monitor")
    with col2:
        if st.button("🌙" if st.session_state.theme == "light" else "☀️",
                     key="theme_toggle",
                     help="Toggle dark/light mode",
                     use_container_width=True):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()

    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["🏠 Live Dashboard", "📊 Analytics", "🎯 Goals & Subjects", "📝 Session History"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### Quick Stats")

    # Quick stats in sidebar
    today_stats = db.get_daily_stats(date.today())
    week_start = date.today() - timedelta(days=date.today().weekday())
    weekly_stats = db.get_weekly_stats(week_start)
    streak = db.get_streak_days()

    st.metric("Today", f"{today_stats['total_minutes']} min")
    st.metric("This Week", f"{weekly_stats['total_minutes']} min")
    st.metric("Streak", f"{streak} days")

    st.markdown("---")

    # Live date/time display
    now = datetime.now()
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: var(--bg-secondary); border-radius: 12px; border: 1px solid var(--border);">
        <div class="datetime-label">Current Time</div>
        <div class="datetime-display">{now.strftime('%I:%M:%S %p')}</div>
        <div class="datetime-label" style="margin-top: 0.5rem;">{now.strftime('%A, %B %d, %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("💡 Tip: Use the Live Dashboard to start tracking your study sessions!")

# =============================================================================
# PAGE 1: LIVE DASHBOARD
# =============================================================================

if page == "🏠 Live Dashboard":
    st.title("🏠 Live Study Dashboard")
    st.markdown("Track your study time in real-time with live session monitoring")

    # Check for active/paused session
    current_session = st.session_state.active_session or st.session_state.paused_session

    # Main Timer Display
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Timer container with animated border
        current_time = get_current_session_time()
        status = "🟢 ACTIVE" if st.session_state.active_session else ("🟡 PAUSED" if st.session_state.paused_session else "⚪ IDLE")

        st.markdown(f"""
        <div class="timer-container">
            <div class="timer-display" id="timer">{format_duration(current_time)}</div>
            <div class="timer-label">Current Session • {status}</div>
        </div>
        """, unsafe_allow_html=True)

        # Subject selector for new session
        subjects = db.get_all_subjects()
        subject_options = {s.name: s.id for s in subjects}

        if not current_session:
            selected_subject_name = st.selectbox(
                "Select Subject",
                options=list(subject_options.keys()),
                index=0,
                key="subject_selector"
            )
            selected_subject = db.get_subject(subject_options[selected_subject_name])

            # Show subject notes if any
            if selected_subject and (selected_subject.notes or selected_subject.note_file_path):
                with st.expander("📋 Subject Notes & Files", expanded=True):
                    display_note_card(
                        selected_subject.notes,
                        selected_subject.note_file_path,
                        selected_subject.note_file_name,
                        selected_subject.note_file_type,
                        f"{selected_subject.name} Notes"
                    )

        # Session Controls
        control_cols = st.columns(4)

        if not current_session:
            # No active session - show Start button
            with control_cols[0]:
                st.button("▶️ Start", disabled=True, use_container_width=True)
            with control_cols[1]:
                if st.button("▶️ Start Session", type="primary", use_container_width=True, key="start_btn"):
                    subject_id = subject_options[selected_subject_name]
                    new_session = db.create_session(subject_id)
                    st.session_state.active_session = new_session
                    st.session_state.timer_start_time = time_module.time()
                    st.session_state.accumulated_seconds = 0
                    st.session_state.session_notes = ""
                    st.session_state.session_file = None
                    st.rerun()
            with control_cols[2]:
                st.button("⏸️ Pause", disabled=True, use_container_width=True)
            with control_cols[3]:
                st.button("⏹️ Stop", disabled=True, use_container_width=True)

        elif st.session_state.active_session:
            # Active session - show Pause and Stop
            with control_cols[0]:
                st.button("▶️ Start", disabled=True, use_container_width=True)
            with control_cols[1]:
                if st.button("⏸️ Pause", use_container_width=True, key="pause_btn"):
                    session = st.session_state.active_session
                    current_duration = get_current_session_time()
                    db.update_session_status(session.id, "PAUSED", current_duration)
                    st.session_state.active_session = None
                    st.session_state.paused_session = session
                    st.session_state.paused_session.duration_seconds = current_duration
                    st.session_state.timer_start_time = None
                    st.rerun()
            with control_cols[2]:
                if st.button("⏹️ Stop", type="primary", use_container_width=True, key="stop_active_btn"):
                    session = st.session_state.active_session
                    current_duration = get_current_session_time()
                    db.complete_session(session.id, current_duration, st.session_state.session_notes, "", "", "")
                    st.session_state.active_session = None
                    st.session_state.timer_start_time = None
                    st.session_state.accumulated_seconds = 0
                    st.session_state.session_notes = ""
                    st.session_state.session_file = None
                    st.success(f"Session completed! Duration: {format_duration(current_duration)}")
                    st.rerun()
            with control_cols[3]:
                st.write("")

        elif st.session_state.paused_session:
            # Paused session - show Resume and Stop
            with control_cols[0]:
                st.button("▶️ Start", disabled=True, use_container_width=True)
            with control_cols[1]:
                if st.button("▶️ Resume", type="primary", use_container_width=True, key="resume_btn"):
                    session = st.session_state.paused_session
                    st.session_state.active_session = session
                    st.session_state.paused_session = None
                    st.session_state.timer_start_time = time_module.time()
                    st.rerun()
            with control_cols[2]:
                if st.button("⏹️ Stop", use_container_width=True, key="stop_paused_btn"):
                    session = st.session_state.paused_session
                    db.complete_session(session.id, session.duration_seconds, st.session_state.session_notes, "", "", "")
                    st.session_state.paused_session = None
                    st.session_state.accumulated_seconds = 0
                    st.session_state.session_notes = ""
                    st.session_state.session_file = None
                    st.success(f"Session completed! Duration: {format_duration(session.duration_seconds)}")
                    st.rerun()
            with control_cols[3]:
                st.write("")

        # Session Notes & File Upload (for active/paused sessions)
        if current_session:
            st.markdown("---")
            st.markdown("### 📝 Session Notes & Attachments")

            # Notes text area
            session_notes = st.text_area(
                "Notes for this session",
                value=st.session_state.session_notes,
                placeholder="Add notes about what you studied, key concepts, questions...",
                height=100,
                key="session_notes_input"
            )
            st.session_state.session_notes = session_notes

            # File uploader
            uploaded_file = st.file_uploader(
                "Attach file (PDF, DOC, TXT, images)",
                type=['pdf', 'doc', 'docx', 'txt', 'md', 'png', 'jpg', 'jpeg', 'gif', 'webp'],
                key="session_file_uploader"
            )
            if uploaded_file:
                st.session_state.session_file = uploaded_file
                file_path, file_name, file_type = save_uploaded_file(uploaded_file, "session")
                st.success(f"File attached: {file_name}")

            # Show subject info
            session = st.session_state.active_session or st.session_state.paused_session
            status_class = "status-active" if st.session_state.active_session else "status-paused"
            st.markdown(f"""
            <div class='subject-card {status_class}' style='border-left-color: {session.subject_color}; margin-top: 1rem;'>
                <strong>{session.subject_name}</strong> • {status}
            </div>
            """, unsafe_allow_html=True)

    # Today's Progress Overview
    st.markdown("---")
    st.subheader("📈 Today's Progress")

    goals = db.get_goals()
    today_stats = db.get_daily_stats(date.today())

    # Progress metrics
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)

    daily_progress = min(today_stats['total_minutes'] / goals.daily_target_minutes * 100, 100) if goals.daily_target_minutes > 0 else 0

    with mcol1:
        st.metric(
            "Study Time Today",
            f"{today_stats['total_minutes']} min",
            f"{today_stats['session_count']} sessions"
        )
    with mcol2:
        st.metric(
            "Daily Goal",
            f"{goals.daily_target_minutes} min",
            f"{daily_progress:.0f}% complete"
        )
    with mcol3:
        weekly_progress = min(weekly_stats['total_minutes'] / goals.weekly_target_minutes * 100, 100) if goals.weekly_target_minutes > 0 else 0
        st.metric(
            "Weekly Progress",
            f"{weekly_stats['total_minutes']} min",
            f"{weekly_progress:.0f}% of {goals.weekly_target_minutes} min"
        )
    with mcol4:
        st.metric(
            "Current Streak",
            f"{streak} days",
            "🔥" if streak > 0 else "Start today!"
        )

    # Progress bars with modern styling
    pcol1, pcol2 = st.columns(2)

    with pcol1:
        st.markdown("**Daily Goal Progress**")
        st.progress(daily_progress / 100)
        st.caption(f"{today_stats['total_minutes']} / {goals.daily_target_minutes} minutes")

    with pcol2:
        st.markdown("**Weekly Goal Progress**")
        st.progress(weekly_progress / 100)
        st.caption(f"{weekly_stats['total_minutes']} / {goals.weekly_target_minutes} minutes")

    # Today's Subject Breakdown
    if today_stats['by_subject']:
        st.markdown("### Today's Subject Breakdown")

        # Create pie chart for today's subjects
        fig = px.pie(
            values=[v['seconds']/60 for v in today_stats['by_subject'].values()],
            names=list(today_stats['by_subject'].keys()),
            color=list(today_stats['by_subject'].keys()),
            color_discrete_map={k: v['color'] for k, v in today_stats['by_subject'].items()},
            hole=0.5
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=12,
            hovertemplate='<b>%{label}</b><br>%{value} min (%{percent})<extra></extra>',
            marker=dict(line=dict(color='#ffffff', width=2))
        )
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=11)),
            margin=dict(t=0, b=0, l=0, r=0),
            height=320,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=get_theme()['text_primary'])
        )
        st.plotly_chart(fig, use_container_width=True)

    # Auto-refresh for live timer
    if st.session_state.active_session and st.session_state.auto_refresh:
        time_module.sleep(0.5)
        st.rerun()

# =============================================================================
# PAGE 2: ANALYTICS
# =============================================================================

elif page == "📊 Analytics":
    st.title("📊 Study Analytics")
    st.markdown("Deep dive into your study patterns and progress")

    theme = get_theme()

    # Time range selector
    tab1, tab2, tab3 = st.tabs(["📅 Daily View", "📆 Weekly View", "📈 Monthly View"])

    with tab1:
        selected_date = st.date_input("Select Date", value=date.today(), key="daily_date")
        daily_stats = db.get_daily_stats(selected_date)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Time", f"{daily_stats['total_minutes']} min")
        col2.metric("Sessions", daily_stats['session_count'])
        col3.metric("Subjects", len(daily_stats['by_subject']))

        if daily_stats['by_subject']:
            st.markdown("### Subject Breakdown")
            df = pd.DataFrame([
                {"Subject": k, "Minutes": v['seconds']//60, "Color": v['color']}
                for k, v in daily_stats['by_subject'].items()
            ])

            fig = px.bar(
                df, x="Subject", y="Minutes", color="Subject",
                color_discrete_map={row.Subject: row.Color for _, row in df.iterrows()},
                text="Minutes"
            )
            fig.update_traces(texttemplate='%{text} min', textposition='outside', textfont_size=12)
            fig.update_layout(
                showlegend=False,
                height=380,
                yaxis_title="Minutes",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=theme['text_primary']),
                xaxis=dict(gridcolor=theme['border']),
                yaxis=dict(gridcolor=theme['border'])
            )
            st.plotly_chart(fig, use_container_width=True)

            # Sessions detail table
            sessions = db.get_sessions_for_date(selected_date)
            if sessions:
                st.markdown("### Session Details")
                session_data = []
                for s in sessions:
                    dt = datetime.fromisoformat(s.start_time)
                    session_data.append({
                        "Time": dt.strftime('%I:%M %p'),
                        "Subject": s.subject_name,
                        "Duration": format_duration_short(s.duration_seconds),
                        "Notes": s.notes[:50] + "..." if s.notes and len(s.notes) > 50 else (s.notes or "—"),
                        "File": "📎" if s.note_file_path else "—"
                    })
                st.dataframe(pd.DataFrame(session_data), use_container_width=True, hide_index=True)

    with tab2:
        week_start = st.date_input(
            "Week Starting",
            value=date.today() - timedelta(days=date.today().weekday()),
            key="weekly_date"
        )
        weekly_stats = db.get_weekly_stats(week_start)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Time", f"{weekly_stats['total_minutes']} min")
        col2.metric("Sessions", weekly_stats['session_count'])
        col3.metric("Avg/Day", f"{weekly_stats['total_minutes']//7 if weekly_stats['total_minutes'] > 0 else 0} min")

        # Daily trend chart
        if weekly_stats['by_day']:
            st.markdown("### Daily Trend")
            days_order = [(week_start + timedelta(days=i)).isoformat() for i in range(7)]
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

            trend_data = []
            for i, day_key in enumerate(days_order):
                minutes = weekly_stats['by_day'].get(day_key, 0) // 60
                trend_data.append({"Day": day_names[i], "Minutes": minutes, "Date": day_key})

            df_trend = pd.DataFrame(trend_data)

            fig = px.bar(
                df_trend, x="Day", y="Minutes",
                text="Minutes", color="Minutes",
                color_continuous_scale="Blues"
            )
            fig.update_traces(texttemplate='%{text} min', textposition='outside', textfont_size=12)
            fig.update_layout(
                showlegend=False,
                height=350,
                yaxis_title="Minutes",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=theme['text_primary']),
                xaxis=dict(gridcolor=theme['border']),
                yaxis=dict(gridcolor=theme['border']),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)

        # Subject breakdown for week
        if weekly_stats['by_subject']:
            st.markdown("### Weekly Subject Distribution")
            df_week = pd.DataFrame([
                {"Subject": k, "Minutes": v['seconds']//60, "Color": v['color']}
                for k, v in weekly_stats['by_subject'].items()
            ])

            fig = px.pie(
                df_week, values="Minutes", names="Subject",
                color="Subject",
                color_discrete_map={row.Subject: row.Color for _, row in df_week.iterrows()},
                hole=0.5
            )
            fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
            fig.update_layout(
                height=350,
                showlegend=True,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=theme['text_primary']),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox("Year", range(2024, 2030), index=date.today().year - 2024)
        with col2:
            month = st.selectbox("Month", range(1, 13), index=date.today().month - 1)

        monthly_stats = db.get_monthly_stats(year, month)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Time", f"{monthly_stats['total_minutes']} min")
        col2.metric("Sessions", monthly_stats['session_count'])
        col3.metric("Avg/Week", f"{monthly_stats['total_minutes']//4 if monthly_stats['total_minutes'] > 0 else 0} min")

        # Weekly trend for month
        if monthly_stats['by_week']:
            st.markdown("### Weekly Trend")
            week_data = []
            for week_start_str, seconds in sorted(monthly_stats['by_week'].items()):
                week_data.append({
                    "Week": f"Week of {week_start_str}",
                    "Minutes": seconds // 60
                })

            df_month = pd.DataFrame(week_data)
            fig = px.line(
                df_month, x="Week", y="Minutes",
                markers=True, text="Minutes"
            )
            fig.update_traces(
                texttemplate='%{text} min',
                textposition='top center',
                line=dict(width=3, color=theme['accent']),
                marker=dict(size=8, color=theme['accent'])
            )
            fig.update_layout(
                height=350,
                yaxis_title="Minutes",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=theme['text_primary']),
                xaxis=dict(gridcolor=theme['border']),
                yaxis=dict(gridcolor=theme['border'])
            )
            st.plotly_chart(fig, use_container_width=True)

        # Subject breakdown for month
        if monthly_stats['by_subject']:
            st.markdown("### Monthly Subject Distribution")
            df_month_subj = pd.DataFrame([
                {"Subject": k, "Minutes": v['seconds']//60, "Color": v['color']}
                for k, v in monthly_stats['by_subject'].items()
            ])

            fig = px.bar(
                df_month_subj, x="Subject", y="Minutes", color="Subject",
                color_discrete_map={row.Subject: row.Color for _, row in df_month_subj.iterrows()},
                text="Minutes"
            )
            fig.update_traces(texttemplate='%{text} min', textposition='outside', textfont_size=12)
            fig.update_layout(
                showlegend=False,
                height=350,
                yaxis_title="Minutes",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=theme['text_primary']),
                xaxis=dict(gridcolor=theme['border']),
                yaxis=dict(gridcolor=theme['border'])
            )
            st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# PAGE 3: GOALS & SUBJECTS
# =============================================================================

elif page == "🎯 Goals & Subjects":
    st.title("🎯 Goals & Subjects Management")

    tab1, tab2 = st.tabs(["🎯 Study Goals", "📚 Subjects"])

    with tab1:
        st.subheader("Study Targets")
        goals = db.get_goals()

        col1, col2 = st.columns(2)
        with col1:
            new_daily = st.number_input(
                "Daily Target (minutes)",
                min_value=0, max_value=1440,
                value=goals.daily_target_minutes,
                step=15
            )
        with col2:
            new_weekly = st.number_input(
                "Weekly Target (minutes)",
                min_value=0, max_value=10080,
                value=goals.weekly_target_minutes,
                step=60
            )

        if st.button("Save Goals", type="primary", use_container_width=True):
            db.update_goals(new_daily, new_weekly)
            st.success("Goals updated successfully!")
            st.rerun()

        st.markdown("---")
        st.subheader("Current Progress")

        today_stats = db.get_daily_stats(date.today())
        weekly_stats = db.get_weekly_stats(date.today() - timedelta(days=date.today().weekday()))

        daily_pct = min(today_stats['total_minutes'] / new_daily * 100, 100) if new_daily > 0 else 0
        weekly_pct = min(weekly_stats['total_minutes'] / new_weekly * 100, 100) if new_weekly > 0 else 0

        st.markdown("**Daily Goal**")
        st.progress(daily_pct / 100)
        st.caption(f"{today_stats['total_minutes']} / {new_daily} minutes ({daily_pct:.0f}%)")

        st.markdown("**Weekly Goal**")
        st.progress(weekly_pct / 100)
        st.caption(f"{weekly_stats['total_minutes']} / {new_weekly} minutes ({weekly_pct:.0f}%)")

    with tab2:
        st.subheader("Manage Subjects")

        # Add new subject
        with st.expander("➕ Add New Subject", expanded=False):
            new_name = st.text_input("Subject Name", placeholder="e.g., Data Structures")
            new_color = st.color_picker("Color", value="#4338ca")
            new_weekly_target = st.number_input("Weekly Target (minutes)", min_value=0, value=0, step=30)

            st.markdown("**Notes**")
            new_notes = st.text_area("Subject notes", placeholder="Add description, resources, key topics...", height=80)

            st.markdown("**Attach File**")
            new_file = st.file_uploader(
                "Upload reference material (PDF, DOC, etc.)",
                type=['pdf', 'doc', 'docx', 'txt', 'md'],
                key="subject_file_upload"
            )

            if st.button("Add Subject", type="primary", use_container_width=True):
                if new_name:
                    file_path, file_name, file_type = save_uploaded_file(new_file, "subject") if new_file else ("", "", "")
                    try:
                        db.add_subject(new_name, new_color, new_weekly_target, new_notes, file_path, file_name, file_type)
                        st.success(f"Added subject: {new_name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please enter a subject name")

        # List existing subjects
        st.markdown("### Current Subjects")
        subjects = db.get_all_subjects()
        week_start = date.today() - timedelta(days=date.today().weekday())

        for subj in subjects:
            actual, target = db.get_subject_weekly_progress(subj.id, week_start)
            progress = min(actual / target * 100, 100) if target > 0 else 0

            with st.container():
                # Subject header with color indicator
                st.markdown(f"""
                <div class="subject-card" style="border-left-color: {subj.color}; margin: 1rem 0;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <span style="font-size: 1.125rem; font-weight: 600; color: var(--text-primary);">{subj.name}</span>
                            <span style="margin-left: 0.75rem; font-size: 0.875rem; color: var(--text-muted);">Target: {target} min/week</span>
                        </div>
                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                            <span style="font-size: 2rem;">{subj.color} ●</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                with col1:
                    if target > 0:
                        st.progress(progress / 100)
                        st.caption(f"{actual} / {target} min this week ({progress:.0f}%)")
                    else:
                        st.caption(f"{actual} min this week (no target set)")

                with col2:
                    new_target = st.number_input(
                        "Weekly Target",
                        min_value=0, max_value=10080,
                        value=subj.weekly_target_minutes,
                        step=30,
                        key=f"target_{subj.id}",
                        label_visibility="collapsed"
                    )
                    if new_target != subj.weekly_target_minutes:
                        db.update_subject_target(subj.id, new_target)
                        st.rerun()

                with col3:
                    # Edit notes/files
                    if st.button("📝 Edit Notes", key=f"edit_{subj.id}", use_container_width=True):
                        st.session_state[f"editing_{subj.id}"] = True
                        st.rerun()

                with col4:
                    if st.button("🗑️", key=f"del_{subj.id}", help="Delete subject"):
                        db.delete_subject(subj.id)
                        st.success(f"Deleted {subj.name}")
                        st.rerun()

                # Inline edit form for notes
                if st.session_state.get(f"editing_{subj.id}", False):
                    with st.form(f"edit_form_{subj.id}"):
                        st.markdown("**Edit Notes & Files**")
                        edit_notes = st.text_area("Notes", value=subj.notes, height=100)
                        edit_file = st.file_uploader("Replace file", type=['pdf', 'doc', 'docx', 'txt', 'md'], key=f"edit_file_{subj.id}")

                        c1, c2 = st.columns(2)
                        with c1:
                            if st.form_submit_button("Save", type="primary", use_container_width=True):
                                file_path, file_name, file_type = save_uploaded_file(edit_file, "subject") if edit_file else (subj.note_file_path, subj.note_file_name, subj.note_file_type)
                                db.update_subject_notes(subj.id, edit_notes, file_path, file_name, file_type)
                                st.session_state[f"editing_{subj.id}"] = False
                                st.success("Updated!")
                                st.rerun()
                        with c2:
                            if st.form_submit_button("Cancel", use_container_width=True):
                                st.session_state[f"editing_{subj.id}"] = False
                                st.rerun()

                    # Show existing notes/files
                    if subj.notes or subj.note_file_path:
                        st.markdown("**Current Notes & Files:**")
                        display_note_card(subj.notes, subj.note_file_path, subj.note_file_name, subj.note_file_type)

# =============================================================================
# PAGE 4: SESSION HISTORY
# =============================================================================

elif page == "📝 Session History":
    st.title("📝 Session History")
    st.markdown("View and manage your complete study session history")

    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_type = st.selectbox("Time Range", ["Last 10 Sessions", "Today", "This Week", "This Month", "All Time"])
    with col2:
        subjects = db.get_all_subjects()
        subject_filter = st.selectbox("Filter by Subject", ["All Subjects"] + [s.name for s in subjects])
    with col3:
        sort_order = st.selectbox("Sort By", ["Newest First", "Oldest First", "Duration (Longest)", "Duration (Shortest)"])

    # Fetch sessions based on filter
    if filter_type == "Last 10 Sessions":
        sessions = db.get_recent_sessions(10)
    elif filter_type == "Today":
        sessions = db.get_sessions_for_date(date.today())
    elif filter_type == "This Week":
        week_start = date.today() - timedelta(days=date.today().weekday())
        sessions = db.get_sessions_for_week(week_start)
    elif filter_type == "This Month":
        sessions = db.get_sessions_for_month(date.today().year, date.today().month)
    else:
        sessions = db.get_all_completed_sessions()

    # Apply subject filter
    if subject_filter != "All Subjects":
        sessions = [s for s in sessions if s.subject_name == subject_filter]

    # Apply sort
    if sort_order == "Oldest First":
        sessions = sorted(sessions, key=lambda x: x.start_time)
    elif sort_order == "Duration (Longest)":
        sessions = sorted(sessions, key=lambda x: x.duration_seconds, reverse=True)
    elif sort_order == "Duration (Shortest)":
        sessions = sorted(sessions, key=lambda x: x.duration_seconds)

    # Display sessions
    if sessions:
        st.markdown(f"### {len(sessions)} Sessions Found")

        # Summary stats
        total_min = sum(s.duration_seconds for s in sessions) // 60
        avg_min = total_min // len(sessions) if sessions else 0
        st.markdown(f"**Total: {total_min} min** • **Average: {avg_min} min/session**")

        st.markdown("---")

        # Session list with expandable details
        for session in sessions:
            dt = datetime.fromisoformat(session.start_time)
            duration_str = format_duration(session.duration_seconds)

            with st.expander(f"{session.subject_name} • {dt.strftime('%B %d, %Y at %I:%M %p')} • {duration_str}", expanded=False):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"""
                    <div class="session-row status-completed">
                        <strong style="font-size: 1.125rem;">{session.subject_name}</strong><br>
                        <span style="color: var(--text-muted);">{dt.strftime('%A, %B %d, %Y at %I:%M %p')}</span><br>
                        <span style="font-size: 1.25rem; font-weight: 700; color: var(--accent); font-family: monospace;">{duration_str}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    display_note_card(session.notes, session.note_file_path, session.note_file_name, session.note_file_type, "Session Notes")

                with col2:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; background: var(--bg-secondary); border-radius: 12px; border: 1px solid var(--border);">
                        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em;">Subject</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: {session.subject_color};">{session.subject_name}</div>
                        <div style="margin-top: 1rem; font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em;">Day</div>
                        <div style="font-size: 1.5rem; font-weight: 700;">{dt.strftime('%a')}</div>
                        <div style="margin-top: 1rem; font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em;">Session ID</div>
                        <div style="font-family: monospace; font-size: 0.875rem;">#{session.id[:8]}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No sessions found for the selected filters. Start studying to see your history!")

# Footer
st.markdown("""
<div class="footer">
    📚 Study Monitor Dashboard • Built with Streamlit • Data stored locally in SQLite
</div>
""", unsafe_allow_html=True)