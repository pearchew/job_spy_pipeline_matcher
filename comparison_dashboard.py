import streamlit as st
import pandas as pd
import os
import glob

# Expand the page to fit 4 columns comfortably
st.set_page_config(layout="wide", page_title="Job Match Dashboard")

st.title("Job Match Evaluation Dashboard")

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

# The fixed columns to prevent Pandas data shifting
correct_cols = [
    'processed_date', 'keyword', 'company', 'title', 'date_posted', 
    'match_score', 'matched_skills', 'gaps_in_skill', 'job_url', 'description', 'location'
]

# Load all datasets into a dictionary upfront so we don't have to keep reading them
@st.cache_data
def load_all_data(files_list, col_names):
    data = {}
    for f in files_list:
        model = get_model_name(f)
        data[model] = pd.read_csv(f, names=col_names, header=0)
    return data

dataframes = load_all_data(files, correct_cols)

# --- Helper Function for Creating HTML Pills ---
def create_pills(skill_string, pill_type="match"):
    """Converts a comma-separated string into HTML styled pills."""
    if pd.isna(skill_string) or str(skill_string).strip() == "":
        return "<i>None</i>"
    
    skills = [s.strip() for s in str(skill_string).split(',') if s.strip()]
    
    if pill_type == "match":
        bg_color = "#d4edda"  # Light green
        text_color = "#155724"
    else:
        bg_color = "#f8d7da"  # Light red
        text_color = "#721c24"
        
    pills_html = ""
    for skill in skills:
        pills_html += f'<span style="background-color: {bg_color}; color: {text_color}; padding: 4px 10px; border-radius: 15px; font-size: 12px; margin: 0px 4px 6px 0px; display: inline-block; border: 1px solid {"#c3e6cb" if pill_type=="match" else "#f5c6cb"};">{skill}</span>'
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
        
        df1_eval = df1[common_cols + ['description', 'match_score', 'matched_skills', 'gaps_in_skill']].copy()
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
                st.markdown(f"**🏢 Company:** {row['company']}")
                if pd.notna(row['job_url']):
                    st.markdown(f"🔗 [Link to Job Post]({row['job_url']})")
                
            with c2:
                st.subheader("Job Description")
                desc_html = str(row['description']).replace('\n', '<br>')
                st.markdown(
                    f'''
                    <div style="height: 350px; overflow-y: auto; padding: 10px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 5px; font-size: 14px;">
                        {desc_html}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
                    
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
    st.header("Job Board")
    
    # Select which model's results to view on the board
    board_model = st.selectbox("Select Model Results to View", options=model_names, index=0, key="board_model")
    
    df_board = dataframes[board_model]
    
    # We will iterate through the rows and chunk them into groups of 3
    for i in range(0, len(df_board), 3):
        cols = st.columns(3)
        
        for j in range(3):
            # Ensure we don't go out of bounds on the last row
            if i + j < len(df_board):
                row = df_board.iloc[i + j]
                
                with cols[j]:
                    # Create the Card UI using HTML/CSS
                    card_html = f"""
                    <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; background-color: #ffffff; box-shadow: 0px 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; min-height: 400px; display: flex; flex-direction: column;">
                        <h4 style="margin-top: 0; margin-bottom: 5px; color: #1f1f1f;">{row['title']}</h4>
                        <p style="color: #666; font-weight: 500; margin-top: 0; margin-bottom: 15px;">🏢 {row['company']}</p>
                        
                        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                            <span style="font-size: 14px; color: #555;">Match Score</span><br>
                            <span style="font-size: 24px; font-weight: bold; color: #0056b3;">{row['match_score']}</span>
                        </div>
                        
                        <div style="flex-grow: 1;">
                            <p style="margin-bottom: 5px; font-size: 14px;"><strong>✅ Matched Skills</strong></p>
                            <div style="margin-bottom: 15px;">
                                {create_pills(row['matched_skills'], 'match')}
                            </div>
                            
                            <p style="margin-bottom: 5px; font-size: 14px;"><strong>❌ Skill Gaps</strong></p>
                            <div style="margin-bottom: 20px;">
                                {create_pills(row['gaps_in_skill'], 'gap')}
                            </div>
                        </div>
                        
                        <a href="{row['job_url']}" target="_blank" style="text-decoration: none; color: white; background-color: #212529; padding: 10px; border-radius: 6px; text-align: center; font-weight: bold; display: block; font-size: 14px;">View Job Posting</a>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)