import streamlit as st
import sys
import os

# Try importing required packages
try:
    import polars
    polars_version = polars.__version__
except ImportError:
    polars_version = "Not installed"

try:
    import altair
    altair_version = altair.__version__
except ImportError:
    altair_version = "Not installed"

st.set_page_config(page_title="Debug App", layout="wide")
st.title("Debug App")
st.write("If you can see this, the app is working correctly!")

# Display system info
st.subheader("System Information")
st.code(f"""
Python version: {sys.version}
Streamlit version: {st.__version__}
Polars version: {polars_version}
Altair version: {altair_version}
""")

# Try to list files in the out directory
import os
st.subheader("Files in 'out' directory")
try:
    files = os.listdir("out")
    st.write(files)
except Exception as e:
    st.error(f"Error listing files: {e}")