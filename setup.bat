@echo off
echo ============================================
echo  QUICK SETUP - SHL Assessment System
echo ============================================

echo Step 1: Creating virtual environment...
python -m venv shl_env

echo Step 2: Activating environment...
call shl_env\Scripts\activate.bat

echo Step 3: Installing required packages...
pip install fastapi uvicorn scikit-learn faiss-cpu pandas numpy google-generativeai streamlit requests openpyxl

echo Step 4: Creating sample data file...
python -c "
import pandas as pd
sample_data = [
    {'name': 'SHL Java Test', 'url': 'https://shl.com/java', 'description': 'Java programming assessment'},
    {'name': 'SHL Python Test', 'url': 'https://shl.com/python', 'description': 'Python programming test'},
    {'name': 'SHL SQL Test', 'url': 'https://shl.com/sql', 'description': 'SQL database skills'},
    {'name': 'SHL Communication Test', 'url': 'https://shl.com/communication', 'description': 'Communication skills assessment'},
    {'name': 'SHL Personality Test', 'url': 'https://shl.com/personality', 'description': 'Personality assessment'},
]
df = pd.DataFrame(sample_data)
df.to_csv('shl_assessments.csv', index=False)
print('Created shl_assessments.csv with 5 sample assessments')
"

echo.
echo ============================================
echo  SETUP COMPLETE!
echo ============================================
echo.
echo To run the system:
echo 1. First terminal: python app.py
echo 2. Second terminal: streamlit run streamlit_app.py
echo.
echo API will be at: http://localhost:8000
echo Frontend will be at: http://localhost:8501
echo.
pause