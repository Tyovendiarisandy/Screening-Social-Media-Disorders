import streamlit as st
from services.sheets_service import store_response
from services.gemini_service import analyze_response

st.set_page_config(page_title="SMDS-27 Screening", page_icon="🧠", layout="wide")

def main():
    st.title("🧠 Social Media Disorder Scale (SMDS-27) Screening")
    st.markdown("""
    This tool allows you to self-screen for social media addiction using the standardized SMDS-27 instrument.
    Your responses will be analyzed to provide personalized, scientifically-backed insights.
    """)
    
    # Initialize session state for steps
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    if st.session_state.step == 1:
        render_profile_form()
    elif st.session_state.step == 2:
        render_questionnaire()
    elif st.session_state.step == 3:
        render_results()

def render_profile_form():
    st.header("Step 1: Personal Profile")
    
    with st.form("profile_form"):
        alias = st.text_input("Name Alias (Pseudonym)")
        age = st.number_input("Age", min_value=10, max_value=100, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
        occupation = st.text_input("Occupation")
        
        submitted = st.form_submit_button("Next")
        
        if submitted:
            if alias and occupation:
                st.session_state.profile = {
                    "alias": alias,
                    "age": age,
                    "gender": gender,
                    "occupation": occupation
                }
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Please fill in all fields.")

def render_questionnaire():
    st.header("Step 2: SMDS-27 Questionnaire")
    st.info("Please answer the following 27 questions honestly based on your experience over the past year.")
    
    questions = [
        # Preoccupation
        "1. During the past year, have you often found it difficult not to look at messages on social media when you were doing something else (e.g., school work)?",
        "2. During the past year, have you regularly found that you can't think of anything else but the moment that you will be able to use social media again?",
        "3. During the past year, have you often sat waiting until something happens on social media again?",
        
        # Tolerance
        "4. During the past year, have you regularly felt dissatisfied because you wanted to spend more time on social media?",
        "5. During the past year, have you regularly felt that you needed to spend more and more time on social media to get the same feeling of satisfaction?",
        "6. During the past year, have you regularly experienced that a satisfied feeling from using social media only lasted for a short time and you quickly wanted to use it again?",
        
        # Withdrawal
        "7. During the past year, have you often felt bad when you could not use social media?",
        "8. During the past year, have you often felt restless, irritated, or unhappy when you could not use social media?",
        "9. During the past year, have you regularly experienced that you felt a strong urge to use social media when you couldn't?",
        
        # Persistence
        "10. During the past year, have you tried to spend less time on social media, but failed?",
        "11. During the past year, have you regularly failed to reduce your social media use even after others told you to use it less?",
        "12. During the past year, have you regularly found it difficult to cut down on social media use, even when you really wanted to?",
        
        # Displacement
        "13. During the past year, have you regularly neglected other activities (e.g., hobbies, sports, homework) because you wanted to use social media?",
        "14. During the past year, have you regularly spent less time on important activities because you preferred to use social media?",
        "15. During the past year, have you often chosen to use social media instead of meeting friends or engaging in other activities?",
        
        # Problems
        "16. During the past year, have you regularly had arguments with others because of your social media use?",
        "17. During the past year, have you regularly experienced problems at school, work, or with your friends/family because of your social media use?",
        "18. During the past year, have you often felt negative consequences (e.g., poor grades, reprimands) due to your social media use?",
        
        # Deception
        "19. During the past year, have you regularly lied to your parents or friends about the amount of time you spend on social media?",
        "20. During the past year, have you often concealed how much time you spent on social media from others?",
        "21. During the past year, have you often downplayed your social media use to avoid criticism from others?",
        
        # Escape
        "22. During the past year, have you often used social media to escape from negative feelings?",
        "23. During the past year, have you regularly used social media to forget about personal problems or to relieve negative feelings such as guilt or anxiety?",
        "24. During the past year, have you often turned to social media when you felt sad, anxious, or bored?",
        
        # Conflict
        "25. During the past year, have you had serious conflict with your parents, brother(s), or sister(s) (friends, relationships, etc.) because of your social media use?",
        "26. During the past year, have you regularly put important relationships at risk because of your social media use?",
        "27. During the past year, have you often jeopardized educational or career opportunities because of your social media use?"
    ]
    
    with st.form("smds_form"):
        responses = {}
        
        for i, question in enumerate(questions):
            st.markdown(f"**{question}**")
            # Use a unique key for each slider
            responses[f"Q{i+1}"] = st.slider(
                "Your Answer", 
                min_value=1, 
                max_value=5, 
                value=3, 
                key=f"q{i+1}",
                help="1=Strongly Disagree, 5=Strongly Agree",
                label_visibility="collapsed"
            )
            st.divider()
            
        submitted = st.form_submit_button("Submit & Analyze")
        
        if submitted:
            st.session_state.responses = responses
            st.session_state.step = 3
            st.rerun()

def render_results():
    st.header("Step 3: Analysis Results")
    
    with st.spinner("Analyzing your responses..."):
        # 1. Store Data
        if 'stored' not in st.session_state:
            success = store_response(st.session_state.profile, st.session_state.responses)
            if success:
                st.success("Data successfully stored.")
            else:
                st.warning("Could not store data (check secrets configuration). Proceeding with analysis...")
            st.session_state.stored = True
            
        # 2. Analyze with Gemini
        if 'analysis' not in st.session_state:
            analysis = analyze_response(st.session_state.profile, st.session_state.responses)
            st.session_state.analysis = analysis
            
        st.markdown(st.session_state.analysis)
        
    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()

if __name__ == "__main__":
    main()
