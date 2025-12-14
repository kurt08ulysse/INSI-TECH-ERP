@echo off
echo Installing dependencies... > install.log
pip install -r requirements.txt >> install.log 2>&1
if %errorlevel% neq 0 (
    echo "pip install failed" >> install.log
    exit /b %errorlevel%
)
echo Starting Streamlit... > app.log
python -m streamlit run dashboard.py >> app.log 2>&1
