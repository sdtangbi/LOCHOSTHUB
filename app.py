import streamlit as st
st.set_page_config(page_title="LOCHOSTHUB", layout="wide")
st.title("LOCHOSTHUB - Offline AI Research Platform")
st.sidebar.title("Navigation")
option = st.sidebar.selectbox("Choose a feature", ["Home", "Chat with PDF", "Literature Review", "AI Writer"])
if option == "Home":
    st.write("Welcome to LOCHOSTHUB!")
elif option == "Chat with PDF":
    st.write("Chat with PDF module placeholder.")
elif option == "Literature Review":
    st.write("Literature Review module placeholder.")
elif option == "AI Writer":
    st.write("AI Writer module placeholder.")
