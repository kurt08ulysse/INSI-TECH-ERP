@echo off
title Systeme de Gestion Municipale - Blockchain IoT
color 0A

echo.
echo ========================================
echo   SYSTEME DE GESTION MUNICIPALE
echo   Blockchain IoT - Dashboard
echo ========================================
echo.

:: Se placer dans le bon répertoire
cd /d "%~dp0"

:: Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Telechargez Python depuis : https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Verification de Python...
python --version
echo.

:: Vérifier si Streamlit est installé
echo [2/5] Verification de Streamlit...
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ATTENTION] Streamlit n'est pas installe
    echo Installation en cours...
    pip install streamlit
)
echo [OK] Streamlit installe
echo.

:: Vérifier et installer toutes les dépendances
echo [3/5] Verification des dependances...
echo Installation/mise a jour des packages requis...
pip install -q paho-mqtt python-dotenv plotly pandas streamlit-autorefresh scikit-learn fpdf hedera-sdk-py mysql-connector-python
if %errorlevel% neq 0 (
    echo [ATTENTION] Certaines dependances n'ont pas pu etre installees
    echo Continuons quand meme...
) else (
    echo [OK] Toutes les dependances sont installees
)
echo.

:: Vérifier que le fichier dashboard.py existe
echo [4/5] Verification du fichier dashboard.py...
if not exist "dashboard.py" (
    echo [ERREUR] Le fichier dashboard.py est introuvable !
    echo Verifiez que vous etes dans le bon repertoire.
    pause
    exit /b 1
)
echo [OK] dashboard.py trouve
echo.

:: Vérifier que WampServer MySQL est démarré (optionnel)
echo [5/5] Verification de la base de donnees...
tasklist /FI "IMAGENAME eq mysqld.exe" 2>NUL | find /I /N "mysqld.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] MySQL est demarre (WampServer actif)
) else (
    echo [INFO] MySQL n'est pas detecte
    echo L'application utilisera SQLite (mairie.db)
)
echo.

echo ========================================
echo   LANCEMENT DE L'APPLICATION
echo ========================================
echo.
echo L'application va demarrer dans votre navigateur...
echo.
echo URLs d'acces :
echo   - Local  : http://localhost:8501
echo   - Reseau : http://192.168.1.90:8501
echo.
echo IMPORTANT :
echo   - LAISSEZ CETTE FENETRE OUVERTE
echo   - Pour arreter : Appuyez sur Ctrl+C
echo   - Ou fermez simplement cette fenetre
echo.
echo ========================================
echo.

:: Attendre 3 secondes
timeout /t 3 /nobreak >nul

:: Lancer Streamlit
echo Demarrage de Streamlit...
echo.

streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0 --server.headless=false

:: Si l'application s'arrête
echo.
echo ========================================
echo Application arretee.
echo ========================================
pause
