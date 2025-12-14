# log_stream.py - Gestionnaire de logs pour l'UI Streamlit

import collections

# Stocke les 50 derniers logs en mémoire (pour l'affichage temps réel)
_log_buffer = collections.deque(maxlen=50)

def add_log(level, source, message):
    """Ajoute un log au buffer circulaire."""
    _log_buffer.append({
        "level": level,
        "source": source,
        "message": message,
        "timestamp": None # On pourrait mettre un timestamp ici si besoin
    })

def get_logs():
    """Récupère tous les logs actuels."""
    return list(_log_buffer)

def clear_logs():
    """Vide les logs."""
    _log_buffer.clear()
