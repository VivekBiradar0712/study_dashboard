# Study Monitor Dashboard

A live study time tracking dashboard built with **Streamlit** and **Python**. Track your study sessions in real-time with beautiful visualizations and analytics.

## Features

### 🏠 Live Dashboard
- **Real-time timer** with HH:MM:SS display
- **Session controls**: Start, Pause, Resume, Stop
- **Subject selection** with color-coded categories
- **Daily/Weekly progress** with progress bars
- **Today's subject breakdown** (pie chart)
- **Auto-refresh** for live timer updates

### 📊 Analytics
- **Daily view**: Hour-by-hour breakdown with bar charts
- **Weekly view**: 7-day trend with daily totals + subject distribution
- **Monthly view**: Week-by-week trend + monthly subject breakdown
- Interactive Plotly charts with hover tooltips

### 🎯 Goals & Subjects
- **Customizable daily/weekly targets**
- **Subject management**: Add, edit, delete subjects with custom colors
- **Weekly targets per subject** with progress tracking
- Visual progress bars for goals

### 📝 Session History
- Filter by time range (Today, Week, Month, All Time)
- Filter by subject
- Sort by date or duration
- Summary statistics

## Quick Start

### 1. Install Dependencies
```bash
cd study_dashboard
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

## Usage

### Starting a Study Session
1. Go to **Live Dashboard**
2. Select a subject from the dropdown
3. Click **▶️ Start Session**
4. The timer starts counting in real-time
5. Use **⏸️ Pause** to pause, **▶️ Resume** to continue
6. Click **⏹️ Stop** to complete and save the session

### Setting Goals
1. Go to **Goals & Subjects** → **Study Goals**
2. Set your daily and weekly target minutes
3. Click **Save Goals**
3. Progress bars on the Live Dashboard will show your progress

### Managing Subjects
1. Go to **Goals & Subjects** → **Subjects**
3. Click **➕ Add New Subject** to create custom subjects
4. Set weekly targets per subject
5. Delete subjects you no longer need

### Viewing Analytics
- **Daily View**: Select any date to see that day's breakdown
- **Weekly View**: See 7-day trend and subject distribution
- **Monthly View**: Track weekly trends over the month

## Data Storage

All data is stored locally in **SQLite** (`study_data.db`):
- Subjects and their colors/targets
- Study sessions with timestamps and durations
- Study goals (daily/weekly targets)
- No cloud dependency - fully offline!

## Tech Stack

- **Streamlit** - Web app framework
- **Plotly** - Interactive charts
- **Pandas** - Data manipulation
- **SQLite** - Local database
- **Python standard library** - datetime, uuid, threading

## Keyboard Shortcuts (when timer is running)

The timer auto-refreshes every second when a session is active. The page will rerun to update the display.

## Customization

Edit `.streamlit/config.toml` to customize:
- Theme colors
- Port number
- Server settings

## Project Structure

```
study_dashboard/
├── app.py              # Main Streamlit application
├── database.py         # SQLite database layer
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── .streamlit/
    └── config.toml     # Streamlit configuration
```

## License

MIT License - Feel free to use and modify!