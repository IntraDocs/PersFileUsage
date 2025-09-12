import streamlit as st

# Configureer de pagina
st.set_page_config(page_title="Hello World Test App", layout="wide")

# Titel en welkomstbericht
st.title("Hello World Test App")
st.header("Welkom bij deze test app!")

# Voeg wat basis interactie toe
st.write("Deze app is bedoeld om te testen of Streamlit Cloud correct werkt.")

# Voeg een eenvoudige interactie toe
name = st.text_input("Voer uw naam in:", "Gast")
st.write(f"Hallo, {name}!")

# Voeg wat basis UI elementen toe
if st.button("Klik hier"):
    st.balloons()
    st.success("Gefeliciteerd! De app werkt correct.")

# Toon wat basis informatie over de omgeving
st.subheader("App Informatie")
st.info("Deze app is ontworpen als een minimale test voor Streamlit Cloud deployment.")