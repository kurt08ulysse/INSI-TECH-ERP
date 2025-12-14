
import sys
try:
    import streamlit_autorefresh
    print("SUCCESS: streamlit_autorefresh is installed.")
    print(f"Location: {streamlit_autorefresh.__file__}")
except ImportError as e:
    print(f"FAILURE: {e}")
except Exception as e:
    print(f"ERROR: {e}")

print(f"Python Executable: {sys.executable}")
