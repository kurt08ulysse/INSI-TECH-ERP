# launcher.py - Point d'entrée pour l'exécutable
import subprocess
import webbrowser
import time
import sys
import os

# Obtenir le chemin du dossier où se trouve l'exécutable
if getattr(sys, 'frozen', False):
    # Si on est dans un .exe PyInstaller
    base_path = sys._MEIPASS
else:
    # Si on est en mode développement
    base_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(base_path)

print("🚀 Démarrage de INSI-TECH...")
print("📂 Dossier:", base_path)

# Lancer Streamlit en arrière-plan
process = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "dashboard.py", "--server.headless=true", "--server.port=8501"],
    cwd=base_path
)

# Attendre que le serveur démarre
time.sleep(4)

# Ouvrir le navigateur automatiquement
webbrowser.open("http://localhost:8501")

print("✅ Application lancée ! Ouvrez http://localhost:8501 si le navigateur ne s'ouvre pas.")
print("❌ Fermez cette fenêtre pour arrêter l'application.")

# Garder le processus actif
process.wait()
