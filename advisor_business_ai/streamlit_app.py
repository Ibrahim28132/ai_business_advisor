import streamlit as st
import json
import time
from pathlib import Path
from graphs.business_advisor import BusinessAdvisorGraph
from utils.config import config
from utils.logging import logger

# Set page config
st.set_page_config(
    page_title="StartSmart AI Business Advisor",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .stTextArea > div > div > textarea {
        font-size: 16px;
    }
    .stButton button {
        width: 100%;
        padding: 10px;
        font-size: 16px;
        background-color: #4CAF50;
        color: white;
    }
    .stDownloadButton button {
        width: 100%;
        padding: 10px;
        font-size: 16px;
    }
    .success-box {
        background-color: #e6f7e6;
        border-radius: 5px;
        padding: 20px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.title("🚀 StartSmart AI Business Advisor")
    st.markdown("""
    Validate your business idea, conduct market research, analyze competition, and generate a professional business plan.
    """)

    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'business_plan' not in st.session_state:
        st.session_state.business_plan = None

    # Sidebar for additional context
    with st.sidebar:
        st.header("Business Context")
        industry = st.text_input("Industry/Sector")
        target_market = st.text_input("Target Market")
        budget = st.selectbox("Budget Range",
                              ["Under $10K", "$10K-$50K", "$50K-$100K", "$100K+"])
        timeline = st.selectbox("Timeline",
                                ["0-3 months", "3-6 months", "6-12 months", "1+ years"])

        st.markdown("---")
        st.markdown("### Settings")
        model_version = st.selectbox(
            "AI Model Version",
            ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            index=0
        )
        config.MODEL_NAME = model_version

    # Main form
    with st.form("business_idea_form"):
        st.subheader("Describe Your Business Idea")
        business_idea = st.text_area(
            "Explain your business idea in detail:",
            placeholder="e.g., 'I want to create an AI-powered personal shopping assistant for busy professionals...'",
            height=150
        )

        submitted = st.form_submit_button("Generate Business Plan")

    if submitted and business_idea:
        # Prepare business context
        business_context = {
            "industry": industry,
            "target_market": target_market,
            "budget": budget,
            "timeline": timeline
        }

        # Initialize and run the business advisor
        with st.spinner("Analyzing your business idea..."):
            advisor = BusinessAdvisorGraph()

            # Setup progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(step, total_steps=6):
                progress = int((step / total_steps) * 100)
                progress_bar.progress(progress)
                steps = [
                    "Planning workflow...",
                    "Conducting market research...",
                    "Analyzing data...",
                    "Developing strategies...",
                    "Creating business plan...",
                    "Reviewing final plan..."
                ]
                status_text.text(f"Status: {steps[step - 1]}")

            # Mock progress updates (in a real app, you'd hook into actual progress)
            for i in range(1, 7):
                time.sleep(1)
                update_progress(i)

            result = advisor.run(business_idea, business_context)
            st.session_state.results = result

        # Display results
        if st.session_state.results.get("status") == "success":
            st.session_state.business_plan = st.session_state.results["business_plan"]

            st.markdown("---")
            st.success("🎉 Business Plan Created Successfully!")

            # Display PDF download button
            with open(st.session_state.business_plan["pdf_path"], "rb") as f:
                st.download_button(
                    label="📄 Download Business Plan (PDF)",
                    data=f,
                    file_name=Path(st.session_state.business_plan["pdf_path"]).name,
                    mime="application/pdf"
                )

            # Display review summary
            with st.expander("🔍 Plan Review Summary", expanded=True):
                st.markdown(f"""
                <div class="success-box">
                    <h4>⭐ Plan Rating: {st.session_state.results['review']['rating']}/10</h4>
                    <p>{st.session_state.results['review']['feedback']}</p>
                </div>
                """, unsafe_allow_html=True)

            # Display business plan sections
            st.subheader("Business Plan Preview")
            plan_sections = st.session_state.business_plan["business_plan"].split("\n\n")

            tab1, tab2, tab3, tab4 = st.tabs(["Executive Summary", "Market Analysis", "Strategy", "Financials"])

            with tab1:
                st.write("\n\n".join([s for s in plan_sections if s.startswith("1.")]))

            with tab2:
                st.write("\n\n".join([s for s in plan_sections if s.startswith("2.") or s.startswith("3.")]))

            with tab3:
                st.write("\n\n".join([s for s in plan_sections if s.startswith("4.") or s.startswith("5.")]))

            with tab4:
                st.write("\n\n".join([s for s in plan_sections if s.startswith("6.")]))

        else:
            st.error("❌ Failed to create business plan:")
            st.error(st.session_state.results.get("error", "Unknown error"))


if __name__ == "__main__":
    main()