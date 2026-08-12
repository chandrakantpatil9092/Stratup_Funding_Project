        )import streamlit as st
import pandas as pd

from resume_parser import extract_text_from_pdf
from recommender import (
    extract_skills,
    calculate_score,
    recommend_jobs
)

from database import (
    save_analysis,
    get_all_analysis
)


# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# -----------------------------
# LOAD JOB DATA
# -----------------------------

@st.cache_data
def load_jobs():

    return pd.read_csv("data/jobs.csv")


jobs_df = load_jobs()


# -----------------------------
# HEADER
# -----------------------------

st.title("🤖 AI Resume Analyzer & Job Recommendation System")

st.write(
    "Upload your resume and get skill analysis, "
    "resume score and suitable job recommendations."
)


st.divider()


# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Resume Analyzer",
        "Admin Dashboard"
    ]
)


# =====================================================
# RESUME ANALYZER
# =====================================================

if page == "Resume Analyzer":

    st.header("📄 Resume Analyzer")

    col1, col2 = st.columns(2)

    with col1:

        candidate_name = st.text_input(
            "Candidate Name"
        )

    with col2:

        email = st.text_input(
            "Email"
        )


    uploaded_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"]
    )


    if uploaded_file:

        st.success(
            "Resume uploaded successfully!"
        )


        if st.button(
            "🔍 Analyze Resume",
            type="primary"
        ):

            with st.spinner(
                "Analyzing your resume..."
            ):

                # Extract text
                resume_text = extract_text_from_pdf(
                    uploaded_file
                )


                # Check text
                if not resume_text.strip():

                    st.error(
                        "Could not extract text from this PDF."
                    )

                    st.stop()


                # Extract skills
                resume_skills = extract_skills(
                    resume_text
                )


                # -----------------------------------
                # OVERALL SKILLS
                # -----------------------------------

                all_skills = set()

                for skills in jobs_df["skills"]:

                    for skill in skills.split(","):

                        all_skills.add(
                            skill.strip().lower()
                        )


                matched_skills = []

                missing_skills = []


                for skill in all_skills:

                    if skill in resume_skills:

                        matched_skills.append(skill)

                    else:

                        missing_skills.append(skill)


                # -----------------------------------
                # RESUME SCORE
                # -----------------------------------

                if all_skills:

                    resume_score = (
                        len(matched_skills)
                        /
                        len(all_skills)
                    ) * 100

                else:

                    resume_score = 0


                resume_score = round(
                    resume_score,
                    2
                )


                # -----------------------------------
                # JOB RECOMMENDATION
                # -----------------------------------

                recommendations = recommend_jobs(
                    resume_text,
                    jobs_df
                )


                recommended_jobs = (
                    recommendations["title"]
                    .tolist()
                )


                # -----------------------------------
                # SAVE TO DATABASE
                # -----------------------------------

                try:

                    save_analysis(
                        candidate_name,
                        email,
                        resume_score,
                        matched_skills,
                        missing_skills,
                        recommended_jobs
                    )

                    database_status = True

                except Exception as e:

                    database_status = False

                    st.warning(
                        f"Database error: {e}"
                    )


            # =====================================
            # RESULTS
            # =====================================

            st.divider()

            st.header("📊 Resume Analysis Result")


            # Score
            score_col1, score_col2, score_col3 = st.columns(3)


            with score_col1:

                st.metric(
                    "Resume Score",
                    f"{resume_score}%"
                )


            with score_col2:

                st.metric(
                    "Skills Found",
                    len(resume_skills)
                )


            with score_col3:

                st.metric(
                    "Recommended Jobs",
                    len(recommendations)
                )


            # -----------------------------------
            # MATCHED SKILLS
            # -----------------------------------

            st.subheader(
                "✅ Detected Skills"
            )

            if resume_skills:

                st.write(
                    ", ".join(
                        sorted(resume_skills)
                    )
                )

            else:

                st.warning(
                    "No predefined skills detected."
                )


            # -----------------------------------
            # MISSING SKILLS
            # -----------------------------------

            st.subheader(
                "📚 Skills You Can Learn"
            )

            if missing_skills:

                st.write(
                    ", ".join(
                        sorted(missing_skills)
                    )
                )


            # -----------------------------------
            # JOB RECOMMENDATIONS
            # -----------------------------------

            st.subheader(
                "💼 Recommended Jobs"
            )


            display_df = recommendations[
                [
                    "title",
                    "skills",
                    "match_score"
                ]
            ].copy()


            display_df.columns = [
                "Job Role",
                "Required Skills",
                "Match %"
            ]


            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )


            # -----------------------------------
            # TOP JOB
            # -----------------------------------

            if len(recommendations) > 0:

                top_job = recommendations.iloc[0]

                st.success(
                    f"🎯 Best Match: "
                    f"{top_job['title']} "
                    f"({top_job['match_score']}%)"
                )


            if database_status:

                st.info(
                    "Analysis saved successfully in MySQL."
                )


# =====================================================
# ADMIN DASHBOARD
# =====================================================

elif page == "Admin Dashboard":

    st.header("📊 Admin Dashboard")


    try:

        data = get_all_analysis()


        if not data:

            st.info(
                "No analysis records available."
            )

        else:

            df = pd.DataFrame(data)


            # -----------------------------------
            # METRICS
            # -----------------------------------

            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Total Candidates",
                    len(df)
                )


            with col2:

                st.metric(
                    "Average Resume Score",
                    f"{df['resume_score'].mean():.2f}%"
                )


            with col3:

                st.metric(
                    "Highest Score",
                    f"{df['resume_score'].max():.2f}%"
                )


            st.divider()


            # -----------------------------------
            # TABLE
            # -----------------------------------

            st.subheader(
                "Candidate Analysis"
            )


            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )


            # -----------------------------------
            # CHART
            # -----------------------------------

            st.subheader(
                "Resume Score Analysis"
            )


            chart_df = df[
                [
                    "candidate_name",
                    "resume_score"
                ]
            ].set_index(
                "candidate_name"
            )


            st.bar_chart(
                chart_df
            )


    except Exception as e:

        st.error(
            f"Could not load dashboard: {e}"
