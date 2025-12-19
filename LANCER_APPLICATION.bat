@echo off
echo ========================================
echo LANCEMENT DE L'APPLICATION
echo Systeme de Gestion Municipale
echo ========================================
echo.
echo L'application va demarrer dans votre navigateur...
echo URL: http://localhost:8501
echo.
echo Pour acceder depuis un autre appareil sur le reseau:
echo URL: http://192.168.1.90:8501
echo.
echo IMPORTANT: Laissez cette fenetre ouverte
echo Appuyez sur Ctrl+C pour arreter l'application
echo.
echo ========================================
echo.

cd /d "%~dp0"
streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0

pause
