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
from database import StudyDatabase, StudySession, Subject, StudyGoal

# Page configuration
st.set_page_config(
    page_title="Study Monitor Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    .timer-display {
        font-size: 4rem;
        font-weight: 700;
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Mono', monospace;
        color: #0f172a;
        text-align: center;
        font-variant-numeric: tabular-nums;
    }
    .timer-label {
        font-size: 1rem;
        color: #64748b;
        text-align: center;
        margin-top: 0.5rem;
    }
    .subject-card {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .progress-ring {
        transform: rotate(-90deg);
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2a78d6 0%, #1e5bb8 100%);
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1e5bb8 0%, #1a4a9a 100%);
        box-shadow: 0 4px 12px rgba(42, 120, 214, 0.3);
    }
    .session-row {
        padding: 0.75rem;
        border-radius: 8px;
        background: #f8fafc;
        margin: 0.25rem 0;
        border: 1px solid #e2e8f0;
    }
    .status-active { border-left: 4px solid #0ca30c; }
    .status-paused { border-left: 4px solid #fab219; }
    .status-completed { border-left: 4px solid #2a78d6; }
    .sidebar .sidebar-content {
        background: #f8fafc;
    }
    div[data-testid="stMetric"] {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
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

# Helper functions
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
    """Calculate current elapsed time for active session"""
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
    elif paused:
        st.session_state.paused_session = paused
        st.session_state.accumulated_seconds = paused.duration_seconds

# Load session on startup
if st.session_state.active_session is None and st.session_state.paused_session is None:
    load_active_session()

# Sidebar Navigation
with st.sidebar:
    st.markdown("## 📚 Study Monitor")
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
    weekly_stats = db.get_weekly_stats(date.today() - timedelta(days=date.today().weekday()))
    streak = db.get_streak_days()

    st.metric("Today", f"{today_stats['total_minutes']} min")
    st.metric("This Week", f"{weekly_stats['total_minutes']} min")
    st.metric("Streak", f"{streak} days")

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
        st.markdown("<div class='timer-display' id='timer'>00:00:00</div>", unsafe_allow_html=True)
        st.markdown("<div class='timer-label'>Current Session</div>", unsafe_allow_html=True)

        # Subject selector for new session
        subjects = db.get_all_subjects()
        subject_options = {s.name: s.id for s in subjects}

        if not current_session:
            selected_subject = st.selectbox(
                "Select Subject",
                options=list(subject_options.keys()),
                index=0
            )

        # Session Controls
        control_cols = st.columns(4)

        if not current_session:
            # No active session - show Start button
            with control_cols[1]:
                if st.button("▶️ Start Session", type="primary", use_container_width=True):
                    subject_id = subject_options[selected_subject]
                    new_session = db.create_session(subject_id)
                    st.session_state.active_session = new_session
                    st.session_state.timer_start_time = time_module.time()
                    st.session_state.accumulated_seconds = 0
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
                if st.button("⏸️ Pause", use_container_width=True):
                    session = st.session_state.active_session
                    current_duration = get_current_session_time()
                    db.update_session_status(session.id, "PAUSED", current_duration)
                    st.session_state.active_session = None
                    st.session_state.paused_session = session
                    st.session_state.paused_session.duration_seconds = current_duration
                    st.session_state.timer_start_time = None
                    st.rerun()
            with control_cols[2]:
                if st.button("⏹️ Stop", type="primary", use_container_width=True):
                    session = st.session_state.active_session
                    current_duration = get_current_session_time()
                    db.complete_session(session.id, current_duration)
                    st.session_state.active_session = None
                    st.session_state.timer_start_time = None
                    st.session_state.accumulated_seconds = 0
                    st.success(f"Session completed! Duration: {format_duration(current_duration)}")
                    st.rerun()
            with control_cols[3]:
                st.write("")

        elif st.session_state.paused_session:
            # Paused session - show Resume and Stop
            with control_cols[0]:
                st.button("▶️ Start", disabled=True, use_container_width=True)
            with control_cols[1]:
                if st.button("▶️ Resume", type="primary", use_container_width=True):
                    session = st.session_state.paused_session
                    st.session_state.active_session = session
                    st.session_state.paused_session = None
                    st.session_state.timer_start_time = time_module.time()
                    st.rerun()
            with control_cols[2]:
                if st.button("⏹️ Stop", use_container_width=True):
                    session = st.session_state.paused_session
                    db.complete_session(session.id, session.duration_seconds)
                    st.session_state.paused_session = None
                    st.session_state.accumulated_seconds = 0
                    st.success(f"Session completed! Duration: {format_duration(session.duration_seconds)}")
                    st.rerun()
            with control_cols[3]:
                st.write("")

        # Current session info
        if current_session:
            session = st.session_state.active_session or st.session_state.paused_session
            status = "🟢 ACTIVE" if st.session_state.active_session else "🟡 PAUSED"
            st.markdown(f"""
            <div class='subject-card' style='border-left-color: {session.subject_color}; margin-top: 1rem;'>
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

    # Progress bars
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
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=0, b=0, l=0, r=0),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    # Auto-refresh for live timer
    if st.session_state.active_session and st.session_state.auto_refresh:
        time_module.sleep(1)
        st.rerun()

# =============================================================================
# PAGE 2: ANALYTICS
# =============================================================================
elif page == "📊 Analytics":
    st.title("📊 Study Analytics")
    st.markdown("Deep dive into your study patterns and progress")

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
            fig.update_traces(texttemplate='%{text} min', textposition='outside')
            fig.update_layout(showlegend=False, height=350, yaxis_title="Minutes")
            st.plotly_chart(fig, use_container_width=True)

            # Table view
            st.dataframe(
                df[["Subject", "Minutes"]].rename(columns={"Minutes": "Time (min)"}),
                use_container_width=True,
                hide_index=True
            )

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
            fig.update_traces(texttemplate='%{text} min', textposition='outside')
            fig.update_layout(showlegend=False, height=350, yaxis_title="Minutes")
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
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=350, showlegend=True)
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
            fig.update_traces(texttemplate='%{text} min', textposition='top center')
            fig.update_layout(height=350, yaxis_title="Minutes")
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
            fig.update_traces(texttemplate='%{text} min', textposition='outside')
            fig.update_layout(showlegend=False, height=350, yaxis_title="Minutes")
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

        if st.button("Save Goals", type="primary"):
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
            new_name = st.text_input("Subject Name")
            new_color = st.color_picker("Color", value="#4338ca")
            new_weekly_target = st.number_input("Weekly Target (minutes)", min_value=0, value=0, step=30)

            if st.button("Add Subject"):
                if new_name:
                    try:
                        db.add_subject(new_name, new_color, new_weekly_target)
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
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                with col1:
                    st.markdown(f"<span style='color:{subj.color}; font-weight:bold;'>{subj.name}</span>", unsafe_allow_html=True)

                with col2:
                    if target > 0:
                        st.progress(progress / 100)
                        st.caption(f"{actual} / {target} min this week")
                    else:
                        st.caption(f"{actual} min this week (no target set)")

                with col3:
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

                with col4:
                    if st.button("🗑️", key=f"del_{subj.id}"):
                        db.delete_subject(subj.id)
                        st.success(f"Deleted {subj.name}")
                        st.rerun()

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

        # Session list
        for session in sessions:
            dt = datetime.fromisoformat(session.start_time)
            duration_str = format_duration(session.duration_seconds)

            status_class = "status-completed"
            status_icon = "✅"

            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

                with col1:
                    st.markdown(f"""
                    <div class='session-row {status_class}'>
                        <strong>{session.subject_name}</strong><br>
                        <small>{dt.strftime('%B %d, %Y at %I:%M %p')}</small>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class='session-row {status_class}'>
                        <span style='color:{session.subject_color}; font-weight:bold;'>{duration_str}</span><br>
                        <small>{status_icon} Completed</small>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"<div class='session-row {status_class}' style='text-align:center;'>{dt.strftime('%a')}</div>", unsafe_allow_html=True)

                with col4:
                    st.markdown(f"<div class='session-row {status_class}' style='text-align:center;'>Session #{session.id[:8]}</div>", unsafe_allow_html=True)
    else:
        st.info("No sessions found for the selected filters. Start studying to see your history!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#64748b; font-size:0.875rem;'>"
    "📚 Study Monitor Dashboard • Built with Streamlit • Data stored locally in SQLite"
    "</div>",
    unsafe_allow_html=True
)