import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import folium_static

from about import about_project

# Load the trained model
model = joblib.load("restaurant_recommendation_model.pkl")

# Load dataset
restaurants_df = pd.read_csv("Dataset_Updated.csv")

# Streamlit Page Configuration
st.set_page_config(page_title="Restaurant Recommander", layout="wide")

# Custom CSS for professional styling
st.markdown("""
    <style>
        /* General Styles */
        body { font-family: 'Arial', sans-serif; background-color: #f5f5f5; }
        
        /* Header */
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 30px;
            background-color: #2E7D32;
            color: white;
            border-radius: 10px;
        }
        .header-title {
            font-size: 28px;
            font-weight: bold;
        }
        .menu {
            display: flex;
            gap: 20px;
        }
        .menu a {
            color: white;
            text-decoration: none;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        }
        .menu a:hover {
            background-color: #1B5E20;
            border-radius: 5px;
        }
        
        /* Footer */
        .footer {
            background-color: #2E7D32;
            text-align: center;
            padding: 20px;
            margin-top: 30px;
            font-size: 14px;
            color: white;
            border-radius: 10px;
        }
        /* Cards */
        .card {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

# Navigation Menu using Streamlit tabs
tab1, tab2, tab3 = st.tabs(["🍽️ Restaurants", "📍 Locations", "📖 About Project"])

with tab3:
    about_project()
    
# Sidebar Inputs
with st.sidebar:
    st.header("🔍 Find Your Ideal Restaurant")
    country = st.selectbox("🌍 Select Country", restaurants_df["Country"].unique())
    city_options = restaurants_df[restaurants_df["Country"] == country]["City"].unique()
    city = st.selectbox("🏙️ Select City", city_options)
    cuisines = st.text_input("🍜 Enter Preferred Cuisines (e.g., Chinese, Italian)")
    budget = st.number_input("💰 Enter Budget for Two (₹)", min_value=100, step=100)
    
    # Button to trigger search
    find_button = st.button("🔍 Find Restaurants")

# Recommendation Function
def recommend_restaurants(country, city, cuisines, budget):
    filtered_df = restaurants_df[
        (restaurants_df["Country"] == country) &
        (restaurants_df["City"] == city) &
        (restaurants_df["Cuisines"].str.contains(cuisines, case=False, na=False))
    ]
    
    if filtered_df.empty:
        return None

    # Budget Difference Calculation
    filtered_df["Budget Difference"] = abs(filtered_df["Average Cost for two"] - budget)
    sorted_df = filtered_df.sort_values(by=["Budget Difference", "Aggregate rating"], ascending=[True, False])

    return sorted_df.head(10)

# Show results only when button is clicked
if find_button:
    recommendations = recommend_restaurants(country, city, cuisines, budget)

    if recommendations is None:
        with tab1:
            st.warning("⚠️ No matching restaurants found. Try different filters.")
    else:
      # Display Restaurant Cards under "Restaurants" tab
        with tab1:
            st.subheader(f"🎯 Top Restaurant Recommendations in {city}")
            
            # Ensure consistent two-column layout
            cols = st.columns(2)  
        
            for index, row in enumerate(recommendations.iterrows()):
                i, row_data = row
                with cols[index % 2]:  # Ensures alternate placement
                    st.markdown(f"""
                        <div class="card">
                            <h3>🍽 {row_data['Restaurant Name']}</h3>
                            <p>📍 <b>City:</b> {row_data['City']}</p>
                            <p>🏠 <b>Address:</b> {row_data['Address']}</p>
                            <p>🍜 <b>Cuisine Type:</b> {row_data['Cuisines']}</p>
                            <p>💰 <b>Average Cost for Two:</b> ₹{row_data['Average Cost for two']}</p>
                            <p>⭐ <b>Rating:</b> {row_data['Aggregate rating']} ⭐ – {row_data['Rating text']}</p>
                            <p>🛵 <b>Online Delivery:</b> { "Available" if row_data['Has Online delivery'] == 1 else "Not Available" }</p>
                            <p>🪑 <b>Table Booking:</b> { "Available" if row_data['Has Table booking'] == 1 else "Not Available" }</p>
                        </div>
                    """, unsafe_allow_html=True)
     

        # Display Locations under "📍 Locations" tab
        with tab2:
            st.subheader("🗺️ Restaurant Locations on Map")
            map_center = [recommendations["Latitude"].mean(), recommendations["Longitude"].mean()]
            m = folium.Map(location=map_center, zoom_start=12)

            for _, row in recommendations.iterrows():
                popup_content = f"""
                <b>{row['Restaurant Name']}</b><br>
                📍 {row['Address']}<br>
                🍜 {row['Cuisines']}<br>
                💰 Cost for Two: ₹{row['Average Cost for two']}<br>
                ⭐ Rating: {row['Aggregate rating']} ⭐
                """
                folium.Marker(
                    location=[row["Latitude"], row["Longitude"]],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=row["Restaurant Name"],
                    icon=folium.Icon(color="red", icon="cutlery", prefix="fa")
                ).add_to(m)

            # Display map in Streamlit
            folium_static(m)

# Footer
st.markdown("<div class='footer'>© 2025 Restaurant Finder | Built with ❤️ using Streamlit</div>", unsafe_allow_html=True)
