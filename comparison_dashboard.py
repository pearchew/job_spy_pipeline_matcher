import streamlit as st
import pandas as pd
import os
import glob

# Expand the page to fit comfortably
st.set_page_config(layout="wide", page_title="Job Match Dashboard")

st.title("Job Match Evaluation Dashboard")

# ==========================================
# GLOBAL CSS STYLES
# ==========================================
st.markdown("""
<style>
    /* Tab 1: Scrollable Description Box */
    .scrollable-desc {
        height: 350px; 
        overflow-y: auto; 
        padding: 10px; 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 5px; 
        font-size: 14px;
    }
    
    /* Tab 2: Fixed Sidebar Panel */
    .fixed-side-panel {
        position: fixed; 
        top: 90px; 
        right: 2vw; 
        width: 30vw; 
        background-color: var(--background-color, #ffffff); 
        color: var(--text-color, #31333f); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 0.5rem; 
        padding: 1.5rem; 
        height: calc(100vh - 120px); 
        overflow-y: auto; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); 
        z-index: 999;
    }
    
    /* Tab 2: Empty State Sidebar Panel */
    .fixed-empty-panel {
        position: fixed; 
        top: 90px; 
        right: 2vw; 
        width: 30vw; 
        background-color: var(--secondary-background-color, #f8f9fa); 
        color: var(--text-color, #31333f); 
        border: 1px dashed rgba(128, 128, 128, 0.3); 
        border-radius: 0.5rem; 
        padding: 2rem; 
        text-align: center; 
        height: max-content; 
        z-index: 999;
    }
    
    /* Explicit Dark Mode Overrides */
    @media (prefers-color-scheme: dark) {
        .fixed-side-panel {
            background-color: var(--background-color, #0e1117);
            color: var(--text-color, #fafafa);
        }
        .fixed-empty-panel {
            background-color: var(--secondary-background-color, #262730);
            color: var(--text-color, #fafafa);
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 1. Load Data ---
output_dir = "output"
files = glob.glob(os.path.join(output_dir, "matched_master_*.csv"))

if not files:
    st.error(f"No files found in the '{output_dir}' directory matching 'matched_master_*.csv'.")
    st.stop()

def get_model_name(filepath):
    basename = os.path.basename(filepath)
    return basename.replace("matched_master_", "").replace(".csv", "")

model_names = [get_model_name(f) for f in files]

correct_cols = [
    'processed_date', 'keyword', 'company', 'title', 'date_posted', 
    'match_score', 'matched_skills', 'gaps_in_skill', 'job_url', 'description', 'location'
]

@st.cache_data
def load_all_data(files_list, col_names):
    data = {}
    for f in files_list:
        model = get_model_name(f)
        data[model] = pd.read_csv(f, names=col_names, header=0)
    return data

dataframes = load_all_data(files, correct_cols)

# Initialize session state for the side panel job description
if 'selected_job_title' not in st.session_state:
    st.session_state.selected_job_title = None
if 'selected_job_company' not in st.session_state:
    st.session_state.selected_job_company = None
if 'selected_job_location' not in st.session_state:
    st.session_state.selected_job_location = None
if 'selected_job_date' not in st.session_state:
    st.session_state.selected_job_date = None
if 'selected_job_desc' not in st.session_state:
    st.session_state.selected_job_desc = None

# --- Helper Functions ---
def create_pills(skill_string, pill_type="match"):
    if pd.isna(skill_string) or str(skill_string).strip() == "":
        return "<i>None</i>"
    
    skills = [s.strip() for s in str(skill_string).split(',') if s.strip()]
    
    if pill_type == "match":
        bg_color, text_color, border_color = "#E8F5E9", "#2E7D32", "#C8E6C9"
    else:
        bg_color, text_color, border_color = "#FFEBEE", "#C62828", "#FFCDD2"
        
    pills_html = ""
    for skill in skills:
        pills_html += f'<span style="background-color: {bg_color}; color: {text_color}; padding: 4px 10px; border-radius: 12px; font-size: 13px; margin: 0px 4px 6px 0px; display: inline-block; border: 1px solid {border_color};">{skill}</span>'
    return pills_html

# --- 2. Create Tabs ---
tab1, tab2 = st.tabs(["📊 Model Comparison", "📋 Job Board View"])

# ==========================================
# TAB 1: MODEL COMPARISON
# ==========================================
with tab1:
    st.header("Select Models to Compare")
    col1, col2 = st.columns(2)
    with col1:
        model1 = st.selectbox("Select Model 1", options=model_names, index=0, key="comp_m1")
    with col2:
        default_idx_2 = 1 if len(model_names) > 1 else 0
        model2 = st.selectbox("Select Model 2", options=model_names, index=default_idx_2, key="comp_m2")

    if model1 and model2:
        df1 = dataframes[model1]
        df2 = dataframes[model2]
        common_cols = ['job_url', 'title', 'company']
        
        df1_eval = df1[common_cols + ['description', 'location', 'date_posted', 'match_score', 'matched_skills', 'gaps_in_skill']].copy()
        df2_eval = df2[common_cols + ['match_score', 'matched_skills', 'gaps_in_skill']].copy()
        
        df1_eval = df1_eval.rename(columns={'match_score': 'match_score_1', 'matched_skills': 'matched_skills_1', 'gaps_in_skill': 'gaps_in_skill_1'})
        df2_eval = df2_eval.rename(columns={'match_score': 'match_score_2', 'matched_skills': 'matched_skills_2', 'gaps_in_skill': 'gaps_in_skill_2'})
        
        merged_df = pd.merge(df1_eval, df2_eval, on=common_cols, how='inner')
        st.success(f"Found {len(merged_df)} common jobs evaluated by both **{model1}** and **{model2}**.")
        
        for idx, row in merged_df.iterrows():
            st.markdown("---") 
            c1, c2, c3, c4 = st.columns([1, 1.5, 1, 1])
            with c1:
                st.subheader(row['title'])
                loc_str = row['location'] if pd.notna(row['location']) else "Unknown Location"
                date_str = row['date_posted'] if pd.notna(row['date_posted']) else "Unknown Date"
                st.markdown(f"**🏢 {row['company']}** <br> 📍 {loc_str} <br> 📅 {date_str}", unsafe_allow_html=True)
                
                if pd.notna(row['job_url']):
                    st.markdown(f"🔗 [Link to Job Post]({row['job_url']})")
            with c2:
                st.subheader("Job Description")
                desc_html = str(row['description']).replace('\n', '<br>')
                st.markdown(f'<div class="scrollable-desc">{desc_html}</div>', unsafe_allow_html=True)
            with c3:
                st.subheader(f"Model: {model1}")
                st.metric("Match Score", row['match_score_1'])
                st.markdown("**✅ Matched Skills:**")
                st.markdown(create_pills(row['matched_skills_1'], 'match'), unsafe_allow_html=True)
                st.markdown("**❌ Gaps in Skills:**")
                st.markdown(create_pills(row['gaps_in_skill_1'], 'gap'), unsafe_allow_html=True)
            with c4:
                st.subheader(f"Model: {model2}")
                st.metric("Match Score", row['match_score_2'])
                st.markdown("**✅ Matched Skills:**")
                st.markdown(create_pills(row['matched_skills_2'], 'match'), unsafe_allow_html=True)
                st.markdown("**❌ Gaps in Skills:**")
                st.markdown(create_pills(row['gaps_in_skill_2'], 'gap'), unsafe_allow_html=True)


# ==========================================
# TAB 2: JOB BOARD VIEW
# ==========================================
with tab2:
    # Set up the 2/3 and 1/3 split immediately
    main_col, side_col = st.columns([2, 1])
    
    with main_col:
        # Move the header, select box, and filters INSIDE the 2/3 column
        st.header("Job Board")
        board_model = st.selectbox("Select Model Results to View", options=model_names, index=0, key="board_model")
        df_board = dataframes[board_model].copy()
        
        # --- EXCLUSION FILTERS ---
        st.markdown("##### Exclude Results")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            all_locations = sorted([loc for loc in df_board['location'].unique() if pd.notna(loc)])
            selected_locations = st.multiselect("Select Locations to Exclude", options=all_locations, default=[])
            
        with filter_col2:
            all_companies = sorted([comp for comp in df_board['company'].unique() if pd.notna(comp)])
            selected_companies = st.multiselect("Select Companies to Exclude", options=all_companies, default=[])
            
        with filter_col3:
            all_dates = sorted([str(d) for d in df_board['date_posted'].unique() if pd.notna(d)], reverse=True)
            selected_dates = st.multiselect("Select Dates to Exclude", options=all_dates, default=[])
            
        # Apply the exclusion filters
        if selected_locations:
            df_board = df_board[~df_board['location'].isin(selected_locations)]
        if selected_companies:
            df_board = df_board[~df_board['company'].isin(selected_companies)]
        if selected_dates:
            df_board = df_board[~df_board['date_posted'].astype(str).isin(selected_dates)]
            
        st.write(f"Showing **{len(df_board)}** jobs.")
        st.divider()
        # ---------------
        
        # Sort by match score
        df_board['match_score_num'] = pd.to_numeric(df_board['match_score'], errors='coerce')
        df_board = df_board.sort_values(by='match_score_num', ascending=False, na_position='last').reset_index(drop=True)
        
        # Display the job cards (also inside the 2/3 column)
        for i in range(0, len(df_board), 2):
            card_cols = st.columns(2)
            
            for j in range(2):
                if i + j < len(df_board):
                    row = df_board.iloc[i + j]
                    
                    with card_cols[j]:
                        with st.container(border=True):
                            st.subheader(row['title'])
                            loc_str = row['location'] if pd.notna(row['location']) else "Unknown Location"
                            date_str = row['date_posted'] if pd.notna(row['date_posted']) else "Unknown Date"
                            st.markdown(f"**🏢 {row['company']}** <br> 📍 {loc_str} <br> 📅 {date_str}", unsafe_allow_html=True)
                            
                            score_html = f"""
                            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px; margin-top: 10px;">
                                <span style="font-size: 13px; color: #666;">Match Score</span><br>
                                <span style="font-size: 22px; font-weight: bold; color: #333;">{row['match_score']}</span>
                            </div>
                            """
                            st.markdown(score_html, unsafe_allow_html=True)
                            
                            st.markdown("**(✅) Matched Skills**")
                            st.markdown(create_pills(row['matched_skills'], 'match'), unsafe_allow_html=True)
                            st.write("") 
                            st.markdown("**(❌) Skill Gaps**")
                            st.markdown(create_pills(row['gaps_in_skill'], 'gap'), unsafe_allow_html=True)
                            st.write("") 
                            
                            btn_col1, btn_col2 = st.columns(2)
                            with btn_col1:
                                if st.button("📄 View Description", key=f"desc_btn_{board_model}_{i}_{j}", use_container_width=True):
                                    st.session_state.selected_job_title = row['title']
                                    st.session_state.selected_job_company = row['company']
                                    st.session_state.selected_job_location = loc_str
                                    st.session_state.selected_job_date = date_str
                                    st.session_state.selected_job_desc = row['description']
                                    
                            with btn_col2:
                                if pd.notna(row['job_url']):
                                    st.link_button("🔗 Job Posting", row['job_url'], use_container_width=True)

    with side_col:
        # The fixed panel remains exclusively in its 1/3 column
        if st.session_state.selected_job_desc:
            desc_html = str(st.session_state.selected_job_desc).replace('\n', '<br>')
            
            fixed_panel_html = f"""
            <div class="fixed-side-panel">
                <h3 style="margin-top: 0; padding-top: 0;">{st.session_state.selected_job_title}</h3>
                <p style="font-size: 16px; margin-bottom: 5px;"><strong>🏢 {st.session_state.selected_job_company}</strong></p>
                <p style="font-size: 14px; margin-top: 0; margin-bottom: 2px; color: gray;">📍 {st.session_state.selected_job_location}</p>
                <p style="font-size: 14px; margin-top: 0; margin-bottom: 15px; color: gray;">📅 {st.session_state.selected_job_date}</p>
                <hr style="border: 0; height: 1px; background: rgba(128, 128, 128, 0.2); margin: 0 0 15px 0;">
                <div style="font-size: 14.5px; line-height: 1.6;">
                    {desc_html}
                </div>
            </div>
            """
            st.markdown(fixed_panel_html, unsafe_allow_html=True)
        else:
            empty_panel_html = """
            <div class="fixed-empty-panel">
                <h3 style="margin-top: 0;">Job Description</h3>
                <p>👈 Click <strong>'📄 View Description'</strong> on any job card to read the full description here.</p>
            </div>
            """
            st.markdown(empty_panel_html, unsafe_allow_html=True)