import streamlit as st
import requests
import pandas as pd
from typing import List, Dict


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🎯",
    layout="wide"
)


# --------------------------------------------------
# Custom Styling (CSS)
# --------------------------------------------------

st.markdown(
    """
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E3A8A;
            text-align: center;
            margin-bottom: 2rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #374151;
            margin-top: 1.5rem;
        }
        .recommendation-card {
            background-color: #F3F4F6;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 5px solid #3B82F6;
        }
        .test-type-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.8rem;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .duration-badge {
            background-color: #10B981;
            color: white;
        }
        .adaptive-badge {
            background-color: #8B5CF6;
            color: white;
        }
        .remote-badge {
            background-color: #F59E0B;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Page Header
# --------------------------------------------------

st.markdown(
    '<h1 class="main-header">🎯 SHL Assessment Recommendation System</h1>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="text-align: center; color: #6B7280; margin-bottom: 2rem;">
        AI-powered assessment recommendations for hiring managers and recruiters
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Sidebar Configuration
# --------------------------------------------------

with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    # Backend API URL
    api_url = st.text_input(
        "API Base URL",
        value="http://localhost:8000",
        help="FastAPI backend URL"
    )

    # Example queries for quick testing
    st.markdown("## 💡 Example Queries")

    example_queries = [
        "I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment that can be completed in 40 minutes.",
        "Looking to hire mid-level professionals proficient in Python, SQL and JavaScript. Need an assessment package that can test all skills with max duration of 60 minutes.",
        "I want to hire customer support executives who are proficient in English communication.",
        "Find me a 1-hour assessment for a QA Engineer role with Java and Selenium skills."
    ]

    # Populate text area when example is clicked
    for idx, query in enumerate(example_queries):
        if st.button(f"Example {idx + 1}", key=f"example_{idx}"):
            st.session_state.query_text = query

    # About section
    st.markdown("---")
    st.markdown("### 📊 About")
    st.markdown(
        """
        This system uses a **RAG (Retrieval-Augmented Generation)** approach:
        - TF-IDF (baseline) for semantic retrieval (uses Sentence Transformers when available)
        - FAISS for fast vector search (optional)
        - Google Gemini for intelligent re-ranking (optional)
        - SHL assessment catalog as the knowledge base
        """
    )


# --------------------------------------------------
# Main Layout
# --------------------------------------------------

left_col, right_col = st.columns([2, 1])

with left_col:
    # Query input box
    query_text = st.text_area(
        "📄 **Enter Job Description or Hiring Query**",
        value=st.session_state.get("query_text", ""),
        height=150,
        placeholder=(
            "Example: I need to hire a Senior Data Analyst with expertise in "
            "SQL, Excel, and Python. The assessment should be 1–2 hours long."
        ),
        help="Provide as much detail as possible for better recommendations"
    )

    # Optional advanced filters (UI-only for now)
    with st.expander("⚡ Advanced Filters"):
        col_a, col_b = st.columns(2)

        with col_a:
            max_duration = st.selectbox(
                "Max Duration (minutes)",
                options=["Any", "30", "45", "60", "90", "120"],
                index=0
            )

        with col_b:
            test_type_preferences = st.multiselect(
                "Preferred Test Types",
                options=[
                    "Ability & Aptitude",
                    "Knowledge & Skills",
                    "Personality & Behavior",
                    "Simulations",
                    "Competencies",
                    "Assessment Exercises"
                ],
                default=[]
            )

with right_col:
    st.markdown("### 📋 Quick Tips")
    st.info(
        """
        **For best results:**
        1. Clearly mention technical skills
        2. Specify job level (junior / mid / senior)
        3. Include desired test duration
        4. Mention soft skills if needed
        5. Add domain or industry context
        """
    )
    st.caption("Relevance score shown next to each result (0 = not related, 1 = highly relevant)")


# --------------------------------------------------
# Recommendation Action
# --------------------------------------------------

if st.button("🚀 Get Recommendations", type="primary", use_container_width=True):

    if not query_text.strip():
        st.warning("Please enter a job description or query.")
    else:
        with st.spinner("🔍 Analyzing query and fetching assessments..."):
            try:
                # Check backend health
                health_response = requests.get(
                    f"{api_url}/health",
                    timeout=5
                )

                if health_response.status_code != 200:
                    st.error("Backend API is not healthy.")
                    st.stop()

                # Call recommendation endpoint with filters
                payload = {
                    "query": query_text,
                    "max_duration": None if max_duration == "Any" else int(max_duration),
                    "preferred_test_types": test_type_preferences
                }

                response = requests.post(
                    f"{api_url}/recommend",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    recommendations = data.get(
                        "recommended_assessments", []
                    )

                    if recommendations:
                        st.success(
                            f"✅ Found {len(recommendations)} matching assessments"
                        )

                        # Split into high and low relevance lists
                        high_recs = [r for r in recommendations if not r.get('low_relevance')]
                        low_recs = [r for r in recommendations if r.get('low_relevance')]

                        # Display high relevance items first
                        for idx, rec in enumerate(high_recs, start=1):
                            types = rec.get('test_type', [])
                            if isinstance(types, str):
                                types = [types]
                            score = rec.get('score') or 0.0
                            score_text = f"{score:.3f}"
                            bar_width = min(max(int(score * 100), 1), 100)

                            st.markdown(
                                f"""
                                <div class="recommendation-card" style="opacity: 1.0;">
                                    <div style="display:flex;justify-content:space-between;align-items:center;">
                                        <h3 style="margin:0">{idx}. {rec['name']}</h3>
                                        <div style="text-align:right;color:#6B7280;font-size:0.9rem;">
                                            <div style="font-weight:600">Relevance</div>
                                            <div style="width:120px;background:#E5E7EB;border-radius:6px;overflow:hidden;">
                                                <div style="width:{bar_width}%;background:#10B981;height:8px;"></div>
                                            </div>
                                            <div style="font-size:0.8rem">{score_text}</div>
                                        </div>
                                    </div>

                                    <p style="margin-top:0.5rem;color:#374151">{rec.get('description','')}</p>

                                    <div style="margin-bottom: 1rem;">
                                        <span class="test-type-badge duration-badge">
                                            ⏱️ {rec.get('duration', '')} min
                                        </span>
                                        <span class="test-type-badge adaptive-badge">
                                            🔄 {rec.get('adaptive_support', '')}
                                        </span>
                                        <span class="test-type-badge remote-badge">
                                            🌐 {rec.get('remote_support', '')}
                                        </span>
                                    </div>

                                    <strong>Test Types:</strong><br>
                                    {', '.join(types)}<br><br>

                                    <a href="{rec.get('url','')}" target="_blank"
                                       style="background-color:#3B82F6;color:white;
                                              padding:0.5rem 1rem;border-radius:5px;
                                              text-decoration:none;">
                                        View Assessment →
                                    </a>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        # Low relevance items in a collapsed section to reduce noise
                        if low_recs:
                            with st.expander(f"Low relevance results ({len(low_recs)}) — Show / Hide"):
                                for idx_off, rec in enumerate(low_recs, start=len(high_recs)+1):
                                    types = rec.get('test_type', [])
                                    if isinstance(types, str):
                                        types = [types]
                                    score = rec.get('score') or 0.0
                                    score_text = f"{score:.3f}"
                                    bar_width = min(max(int(score * 100), 1), 100)

                                    st.markdown(
                                        f"""
                                        <div class="recommendation-card" style="opacity: 0.6;">
                                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                                <h4 style="margin:0">{idx_off}. {rec['name']}</h4>
                                                <div style="text-align:right;color:#6B7280;font-size:0.85rem;">
                                                    <div style="font-weight:600">Relevance</div>
                                                    <div style="width:120px;background:#E5E7EB;border-radius:6px;overflow:hidden;">
                                                        <div style="width:{bar_width}%;background:#10B981;height:8px;"></div>
                                                    </div>
                                                    <div style="font-size:0.8rem">{score_text}</div>
                                                </div>
                                            </div>

                                            <p style="margin-top:0.5rem;color:#374151">{rec.get('description','')}</p>

                                            <div style="margin-bottom: 1rem;">
                                                <span class="test-type-badge duration-badge">
                                                    ⏱️ {rec.get('duration', '')} min
                                                </span>
                                                <span class="test-type-badge adaptive-badge">
                                                    🔄 {rec.get('adaptive_support', '')}
                                                </span>
                                                <span class="test-type-badge remote-badge">
                                                    🌐 {rec.get('remote_support', '')}
                                                </span>
                                            </div>

                                            <strong>Test Types:</strong><br>
                                            {', '.join(types)}<br><br>

                                            <a href="{rec.get('url','')}" target="_blank"
                                               style="background-color:#3B82F6;color:white;
                                                      padding:0.5rem 1rem;border-radius:5px;
                                                      text-decoration:none;">
                                                View Assessment →
                                            </a>

                                            <div style="color:#9CA3AF;margin-top:0.5rem;font-size:0.9rem;">Low relevance — try a more detailed query.</div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

                        # CSV download option
                        df = pd.DataFrame(recommendations)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=df.to_csv(index=False),
                            file_name="shl_recommendations.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                    else:
                        st.warning(
                            "No recommendations found. Try a more detailed query."
                        )

                else:
                    st.error(
                        f"API Error {response.status_code}: {response.text}"
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot connect to backend. "
                    "Ensure FastAPI server is running."
                )
                st.info("Run backend using: `python app.py`")

            except requests.exceptions.Timeout:
                st.error("⏰ Request timed out. Please try again.")

            except Exception as error:
                st.error(f"❌ Unexpected error: {error}")


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6B7280;">
        <p>Built with ❤️ using RAG (TF-IDF baseline); FAISS & Gemini are optional</p>
        <p>This is a demo system. Add validation & security for production use.</p>
    </div>
    """,
    unsafe_allow_html=True
)
