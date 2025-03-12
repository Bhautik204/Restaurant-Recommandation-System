import streamlit as st

def about_project():
    st.title("📌 About the Project")
    
    st.markdown("""
    ## 🍽️ Restaurant Recommendation System
    **Objective:**  
    This project is designed to help users discover the best restaurants based on their preferences, such as location, cuisine type, and budget.  
    Using machine learning, we provide smart recommendations to enhance the dining experience.

    ## 🚀 Features
    - 📍 **Location-based Filtering**: Find restaurants in your preferred country and city.
    - 🍜 **Cuisine Preferences**: Search for restaurants serving your favorite cuisines.
    - 💰 **Budget Constraint**: Get recommendations that match your spending range.
    - ⭐ **Ratings & Reviews**: View restaurant ratings to make informed choices.
    - 📌 **Map Integration**: Visualize restaurant locations using interactive maps.
    
    ## 🛠️ Technologies Used
    - **Python Libraries:** `pandas`, `numpy`, `joblib`, `streamlit`, `folium`
    - **Machine Learning:** Trained recommendation model (`restaurant_recommendation_model.pkl`)
    - **Web Framework:** `Streamlit` for user interface

   
    """)

# To use this in your Streamlit app, call `about_project()` inside a tab or navigation logic.
