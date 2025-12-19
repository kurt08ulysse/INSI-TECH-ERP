"""
Helper pour accéder aux variables de configuration
Compatible avec .env local ET Streamlit Cloud secrets
"""
import os
from typing import Any, Optional

# Charger .env si disponible (développement local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv non installé, c'est OK

# Détecter si on est sur Streamlit Cloud
_is_streamlit = False
try:
    import streamlit as st
    _is_streamlit = hasattr(st, 'secrets')
except ImportError:
    pass


def get_config(key: str, section: Optional[str] = None, default: Any = None) -> Any:
    """
    Récupère une valeur de configuration.

    Essaie dans cet ordre:
    1. st.secrets (si sur Streamlit Cloud)
    2. os.getenv (variables d'environnement)
    3. valeur par défaut

    Args:
        key: Nom de la clé
        section: Section dans st.secrets (ex: "database", "email")
        default: Valeur par défaut si non trouvée

    Returns:
        La valeur trouvée ou la valeur par défaut

    Examples:
        >>> get_config("DB_TYPE", "database", "sqlite")
        >>> get_config("EMAIL_FROM", "email", "")
    """
    # 1. Essayer Streamlit secrets (si disponible)
    if _is_streamlit:
        try:
            import streamlit as st
            if section:
                # Accès par section: st.secrets["database"]["DB_TYPE"]
                if section in st.secrets and key in st.secrets[section]:
                    return st.secrets[section][key]
            else:
                # Accès direct: st.secrets["DB_TYPE"]
                if key in st.secrets:
                    return st.secrets[key]
        except Exception:
            pass  # Secrets non configurés, continuer

    # 2. Essayer variable d'environnement
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value

    # 3. Retourner valeur par défaut
    return default


# Raccourcis pour accès rapide aux configurations courantes

def get_db_config():
    """Retourne la configuration de la base de données."""
    return {
        'type': get_config('DB_TYPE', 'database', 'sqlite'),
        'host': get_config('DB_HOST', 'database', 'localhost'),
        'database': get_config('DB_NAME', 'database', 'mairie_db'),
        'user': get_config('DB_USER', 'database', 'root'),
        'password': get_config('DB_PASSWORD', 'database', ''),
        'port': get_config('DB_PORT', 'database', '3306'),
    }


def get_email_config():
    """Retourne la configuration email."""
    return {
        'from': get_config('EMAIL_FROM', 'email', ''),
        'password': get_config('EMAIL_PASSWORD', 'email', ''),
        'to': get_config('EMAIL_TO', 'email', ''),
    }


def get_mqtt_config():
    """Retourne la configuration MQTT."""
    return {
        'broker': get_config('MQTT_BROKER', 'mqtt', ''),
        'port': int(get_config('MQTT_PORT', 'mqtt', '8883')),
        'username': get_config('MQTT_USERNAME', 'mqtt', ''),
        'password': get_config('MQTT_PASSWORD', 'mqtt', ''),
    }


def get_hedera_config():
    """Retourne la configuration Hedera Hashgraph."""
    return {
        'operator_id': get_config('OPERATOR_ID', 'hedera', ''),
        'operator_key': get_config('OPERATOR_KEY', 'hedera', ''),
        'topic_id': get_config('TOPIC_ID', 'hedera', ''),
        'supplier_account_id': get_config('SUPPLIER_ACCOUNT_ID', 'hedera', ''),
    }


def is_streamlit_cloud():
    """Retourne True si l'application tourne sur Streamlit Cloud."""
    return _is_streamlit and hasattr(st, 'secrets')


def is_local():
    """Retourne True si l'application tourne en local."""
    return not is_streamlit_cloud()


# Test du module (si exécuté directement)
if __name__ == "__main__":
    print("=== Test du config_helper ===")
    print(f"Sur Streamlit Cloud: {is_streamlit_cloud()}")
    print(f"En local: {is_local()}")
    print("\nConfiguration base de données:")
    print(get_db_config())
    print("\nConfiguration email:")
    print(get_email_config())
    print("\nConfiguration MQTT:")
    print(get_mqtt_config())
    print("\nConfiguration Hedera:")
    print(get_hedera_config())
