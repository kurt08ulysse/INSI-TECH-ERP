@echo off
REM ================================================================================
REM     Script pour pousser le projet sur GitHub
REM ================================================================================

echo.
echo ================================================================================
echo            PREPARATION DU DEPLOIEMENT SUR GITHUB
echo ================================================================================
echo.

REM Vérifier si Git est installé
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Git n'est pas installe!
    echo Telechargez Git sur: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [OK] Git est installe
echo.

REM Afficher l'aide
echo AVANT DE CONTINUER, vous devez:
echo.
echo 1. Creer un repository sur GitHub:
echo    https://github.com/new
echo.
echo 2. Copier l'URL du repository (exemple):
echo    https://github.com/VOTRE_USERNAME/VOTRE_REPO.git
echo.
echo ================================================================================
echo.

REM Demander l'URL du repository
set /p REPO_URL="Collez l'URL de votre repository GitHub: "

if "%REPO_URL%"=="" (
    echo [ERREUR] URL vide!
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                         ETAPE 1: Ajout des fichiers
echo ================================================================================
echo.

git add .
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Echec de git add
    pause
    exit /b 1
)

echo [OK] Fichiers ajoutes
echo.

echo ================================================================================
echo                         ETAPE 2: Creation du commit
echo ================================================================================
echo.

git commit -m "Preparation pour deploiement Streamlit Cloud - Systeme de Gestion Municipale"
if %ERRORLEVEL% NEQ 0 (
    echo [AVERTISSEMENT] Aucun changement a commiter ou erreur
    echo.
)

echo [OK] Commit cree
echo.

echo ================================================================================
echo                     ETAPE 3: Configuration du remote
echo ================================================================================
echo.

REM Supprimer l'ancien remote s'il existe
git remote remove origin 2>nul

REM Ajouter le nouveau remote
git remote add origin %REPO_URL%
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Echec de l'ajout du remote
    pause
    exit /b 1
)

echo [OK] Remote configure: %REPO_URL%
echo.

echo ================================================================================
echo                         ETAPE 4: Push vers GitHub
echo ================================================================================
echo.

git branch -M main
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] Echec du push vers GitHub
    echo.
    echo Causes possibles:
    echo - Vous n'etes pas authentifie
    echo - Le repository n'existe pas
    echo - L'URL est incorrecte
    echo.
    echo Solutions:
    echo 1. Verifiez l'URL du repository
    echo 2. Authentifiez-vous avec: gh auth login
    echo    (ou utilisez GitHub Desktop)
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                           SUCCES!
echo ================================================================================
echo.
echo [OK] Code pousse sur GitHub avec succes!
echo.
echo Repository: %REPO_URL%
echo.
echo ================================================================================
echo                     PROCHAINES ETAPES
echo ================================================================================
echo.
echo 1. Allez sur: https://share.streamlit.io/
echo.
echo 2. Connectez-vous avec GitHub
echo.
echo 3. Cliquez sur "New app"
echo.
echo 4. Selectionnez:
echo    - Repository: Votre repository
echo    - Branch: main
echo    - Main file: Projet-Blockchain-et-IoT-Suivi-intelligent-des-stocks-avec-RFID-et-Hashgraph-master/dashboard.py
echo.
echo 5. Cliquez sur "Deploy!"
echo.
echo 6. Configurez les secrets (Settings ^> Secrets)
echo    Copiez le contenu de .streamlit/secrets.toml.example
echo.
echo ================================================================================
echo.
echo Pour plus de details, consultez:
echo - DEPLOIEMENT_RAPIDE.txt
echo - DEPLOIEMENT_STREAMLIT_CLOUD.md
echo.
echo ================================================================================
echo.

pause
