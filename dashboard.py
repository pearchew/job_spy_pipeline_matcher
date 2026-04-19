import streamlit as st
import pandas as pd
from pathlib import Path
import math

# Set wide layout
st.set_page_config(page_title="Job Board Dashboard", layout="wide")

# Custom CSS for strict styling rules
custom_css = """
<style>
    /* Force main app background to light gray */
    .stApp {
        background-color: #f4f5f7 !important;
    }
    
    /* Target cards for custom styling */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #94a3b8 !important;
        border-top: 5px solid #8ab4f8 !important;
        transition: box-shadow 0.3s ease-in-out;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }

    /* Force high-contrast text for headers */
    h3 {
        color: #0f172a !important;
        margin-bottom: 0.2rem;
        font-size: 1.1rem;
    }
    
    /* Meta info styling */
    .meta-info {
        color: #1e293b !important;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    /* Skill Pill Badges */
    .skill-pill {
        display: inline-block;
        color: #0f172a !important;
        border: 1px solid #94a3b8;
        border-radius: 20px;
        padding: 2px 8px;
        margin: 2px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .skill-matched {
        background-color: #dcfce7; /* Light green */
    }
    .skill-gap {
        background-color: #fee2e2; /* Light red */
    }

    /* Expander styling */
    [data-testid="stExpander"] summary p, 
    [data-testid="stExpander"] summary span {
        color: #0f172a !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpander"] summary svg {
        fill: #0f172a !important;
        color: #0f172a !important;
    }
    .expander-content {
        color: #334155 !important;
        font-size: 0.85rem;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

st.title("Modern Job Board")

@st.cache_data
def load_data():
    file_path = Path("output") / "matched_master.csv"
    if file_path.exists():
        df = pd.read_csv(file_path)
        # Ensure match_score is treated as numeric, fill blanks with 0, and sort descending
        if 'match_score' in df.columns:
            df['match_score'] = pd.to_numeric(df['match_score'], errors='coerce').fillna(0)
            df = df.sort_values(by='match_score', ascending=False).reset_index(drop=True)
        return df
    else:
        st.error(f"File not found: {file_path.absolute()}")
        return pd.DataFrame()

df = load_data()

def render_skills(skills_str, pill_class):
    if pd.isna(skills_str) or str(skills_str).strip().lower() in ['n/a', '', 'nan']:
        return ""
    skills = [s.strip() for s in str(skills_str).split(",") if s.strip()]
    if not skills:
        return ""
    
    html = ""
    for skill in skills:
        html += f"<span class='skill-pill {pill_class}'>{skill}</span>"
    return html

if not df.empty:
    # Changed to exactly 3 cards per row
    cards_per_row = 3
    for i in range(0, len(df), cards_per_row):
        cols = st.columns(cards_per_row)
        for j in range(cards_per_row):
            if i + j < len(df):
                row = df.iloc[i + j]
                with cols[j]:
                    with st.container(border=True, height=450):
                        
                        # Match score formatting
                        try:
                            score = float(row.get('match_score', 0))
                        except:
                            score = 0
                            
                        score_color = "red" if score < 75 else "green"
                        
                        # Render Title & Match Score
                        title = row.get('title', 'Unknown Title')
                        st.markdown(
                            f"<h3>{title} <span style='color: {score_color}; font-size: 0.9rem;'>[{int(score)}%]</span></h3>", 
                            unsafe_allow_html=True
                        )
                        
                        # Render Meta Info
                        company = row.get('company', 'N/A')
                        date_posted = row.get('date_posted', 'N/A')
                        processed_date = row.get('processed_date', 'N/A')
                        
                        st.markdown(
                            f"""
                            <div class="meta-info">
                                <b>Company:</b> {company}<br>
                                <b>Date Posted:</b> {date_posted}<br>
                                <b>Processed On:</b> {processed_date}
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                        # Render Skill Tags
                        matched_html = render_skills(row.get('matched_skills', ''), 'skill-matched')
                        gaps_html = render_skills(row.get('gaps_in_skill', ''), 'skill-gap')
                        
                        total_skills_html = matched_html + gaps_html
                        if not total_skills_html:
                            # Crucial Edge Case
                            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                        else:
                            # Render all combined skills
                            st.markdown(f"<div style='margin-bottom: 10px; min-height: 28px;'>{total_skills_html}</div>", unsafe_allow_html=True)
                        
                        # Render Link Button
                        job_url = str(row.get('job_url', '#'))
                        if pd.isna(job_url) or job_url.lower() == 'nan':
                            job_url = "#"
                        st.link_button("Apply / View Listing", url=job_url, use_container_width=True)
                        
                        # Expander for Description
                        with st.expander("View Job Description"):
                            desc = str(row.get('description', 'No description provided.'))
                            if pd.isna(desc) or desc.lower() == 'nan':
                                desc = "No description provided."
                            st.markdown(f"<div class='expander-content'>{desc}</div>", unsafe_allow_html=True)