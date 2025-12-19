@echo off
title Verification Application
color 0E

echo.
echo ========================================
echo   VERIFICATION DE L'APPLICATION
echo ========================================
echo.

:: Vérifier si Streamlit est en cours
echo [1/4] Verification du processus Streamlit...
tasklist | findstr /i "streamlit" >nul
if %errorlevel% equ 0 (
    echo [OK] Streamlit est en cours d'execution
) else (
    echo [ERREUR] Streamlit n'est PAS en cours
    echo.
    echo Pour demarrer: Double-cliquez sur START.bat
    goto end
)

echo.
echo [2/4] Verification du port 8501...
netstat -ano | findstr ":8501" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo [OK] Le port 8501 est en ecoute
) else (
    echo [ERREUR] Le port 8501 n'est PAS en ecoute
    goto end
)

echo.
echo [3/4] Test de connexion HTTP...
curl -s -o nul -w "HTTP %%{http_code}" http://localhost:8501 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] L'application repond
) else (
    echo [ATTENTION] L'application ne repond pas encore
    echo Attendez quelques secondes...
)

echo.
echo [4/4] Ouverture du navigateur...
start http://localhost:8501

echo.
echo ========================================
echo   RESULTAT
echo ========================================
echo.
echo Si vous voyez l'application dans votre navigateur:
echo   [OK] TOUT FONCTIONNE !
echo.
echo Si vous voyez une erreur:
echo   - Verifiez que la fenetre noire de START.bat est ouverte
echo   - Attendez 15 secondes et actualisez (F5)
echo.
:end
pause
