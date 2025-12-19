@echo off
title Application Blockchain IoT - Demarrage
color 0A

echo.
echo ========================================
echo    LANCEMENT DE L'APPLICATION
echo ========================================
echo.

cd /d "%~dp0"

echo Demarrage de Streamlit...
echo.
echo L'application va s'ouvrir dans votre navigateur.
echo.
echo URLs disponibles:
echo   - http://localhost:8501
echo   - http://192.168.1.90:8501
echo.
echo IMPORTANT: Gardez cette fenetre ouverte !
echo.

:: Ouvrir le navigateur après 5 secondes
start /min cmd /c "timeout /t 5 /nobreak >nul && start http://localhost:8501"

:: Lancer Streamlit
streamlit run dashboard.py

pause
