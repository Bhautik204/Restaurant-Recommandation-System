""" from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load dataset
restaurants_df = pd.read_csv('Dataset.csv')

# Content-Based Filtering
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(restaurants_df['Cuisines'].fillna(''))
content_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

@app.route('/recommend', methods=['POST'])
def recommend_restaurants():  
    logging.info("Received a request for restaurant recommendations.")
    data = request.json
    country_code = data.get("country_code")
    city = data.get("city")
    cuisines = data.get("cuisines")
    avg_cost = data.get("avg_cost")
    
    filtered_df = restaurants_df.copy()
    if country_code:
        filtered_df = filtered_df[filtered_df['Country Code'] == int(country_code)]
    if city:
        filtered_df = filtered_df[filtered_df['City'].str.contains(city, case=False, na=False)]
    if cuisines:
        filtered_df = filtered_df[filtered_df['Cuisines'].str.contains(cuisines, case=False, na=False)]
    if avg_cost:
        filtered_df = filtered_df[filtered_df['Average Cost for two'] <= int(avg_cost)]
    
    if filtered_df.empty:  
        logging.warning("No recommendations found for the given filters.")
        return jsonify([])
    
    recommendations = filtered_df[['Restaurant Name', 'City', 'Cuisines', 'Average Cost for two', 'Aggregate rating']].head(10)
    
    result = [
        {
            "name": row['Restaurant Name'],
            "city": row['City'],
            "cuisines": row['Cuisines'],
            "cost": row['Average Cost for two'],
            "rating": row['Aggregate rating']
        }
        for _, row in recommendations.iterrows()
    ]
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
 """


from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import folium
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load dataset
restaurants_df = pd.read_csv('Dataset_Updated.csv')

# Extract unique country and city values
country_mapping = restaurants_df[['Country Code', 'Country']].drop_duplicates()

# Content-Based Filtering
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(restaurants_df['Cuisines'].fillna(''))
content_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

@app.route('/get_countries', methods=['GET'])
def get_countries():
    """Returns a list of unique countries for dropdown."""
    countries = country_mapping.to_dict(orient='records')
    return jsonify(countries)

@app.route('/get_cities', methods=['GET'])
def get_cities():
    """Returns unique cities for a given country."""
    country_code = request.args.get('country_code')

    if not country_code:
        return jsonify({"error": "Please provide a country code"}), 400

    filtered_cities = restaurants_df[restaurants_df['Country Code'] == int(country_code)]['City'].unique().tolist()
    return jsonify(filtered_cities)

@app.route('/recommend', methods=['POST'])
def recommend_restaurants():  
    """Recommends restaurants based on user filters."""
    logging.info("Received a request for restaurant recommendations.")
    data = request.json
    country_code = data.get("country_code")
    city = data.get("city")
    cuisines = data.get("cuisines")
    avg_cost = data.get("avg_cost")
    
    filtered_df = restaurants_df.copy()
    if country_code:
        filtered_df = filtered_df[filtered_df['Country Code'] == int(country_code)]
    if city:
        filtered_df = filtered_df[filtered_df['City'].str.contains(city, case=False, na=False)]
    if cuisines:
        filtered_df = filtered_df[filtered_df['Cuisines'].str.contains(cuisines, case=False, na=False)]
    if avg_cost:
        filtered_df = filtered_df[filtered_df['Average Cost for two'] <= int(avg_cost)]
    
    if filtered_df.empty:  
        logging.warning("No recommendations found for the given filters.")
        return jsonify({"message": "No restaurants found."})

    # Select top 10 restaurants
    recommendations = filtered_df[['Restaurant Name', 'City', 'Cuisines', 'Average Cost for two', 'Aggregate rating', 'Latitude', 'Longitude']].head(10)

    # Generate a map with restaurant locations
    map_center = [filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()]
    restaurant_map = folium.Map(location=map_center, zoom_start=12)

    for _, row in recommendations.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Restaurant Name']} ({row['Cuisines']}) - Rating: {row['Aggregate rating']}",
            tooltip=row['Restaurant Name']
        ).add_to(restaurant_map)

    # Save map as an HTML file
    map_path = "templates/restaurant_map.html"
    restaurant_map.save(map_path)

    # Convert recommendations to JSON format
    result = {
        "restaurants": [
            {
                "name": row['Restaurant Name'],
                "city": row['City'],
                "cuisines": row['Cuisines'],
                "cost": row['Average Cost for two'],
                "rating": row['Aggregate rating'],
                "latitude": row['Latitude'],
                "longitude": row['Longitude']
            }
            for _, row in recommendations.iterrows()
        ],
        "map_url": "/map"  # Endpoint to render the map
    }
    
    return jsonify(result)

@app.route('/map')
def show_map():
    """Displays the generated restaurant map."""
    return render_template("restaurant_map.html")

if __name__ == '__main__':
    # Ensure templates folder exists
    os.makedirs("templates", exist_ok=True)
    app.run(debug=True)
