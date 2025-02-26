from flask import Flask, request, jsonify
from flask_cors import CORS
from search import tf_idf_search, tf_idf_search_fuzzy
import pickle
import random
import json
import ast


with open('inverted_index_simple.pkl', 'rb') as f:
    inverted_index = pickle.load(f)

with open('inverted_index_simple_titles.pkl', 'rb') as f:
    inverted_index_titles = pickle.load(f)

with open('recipes_dict.pkl', 'rb') as f:
    recipes_dict = pickle.load(f)

app = Flask(__name__)
cors = CORS(app, origins="*")
# CORS(app, origins="http://localhost:5173")
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/api/search")
def search():
    query = request.args.get("query")
    categories = request.args.get("categories")
    cuisines = request.args.get("cuisines")

    categories_dict = json.loads(categories) if categories else {}
    selected_categories = {key for key, value in categories_dict.items() if value}
    print(f"Selected categories: {selected_categories}")
    print(f"Category Type: {type(selected_categories)}")
    
    cuisines_dict = json.loads(cuisines) if cuisines else {}
    selected_cuisines = [key.lower().replace(" ", "_") for key, value in cuisines_dict.items() if value]
    if selected_cuisines == []:
        selected_cuisines = ['southern_us', 'russian', 'chinese',
                            'italian', 'mexican', 'french',
                            'british', 'cajun_creole', 'filipino',
                            'indian', 'irish', 'moroccan',
                            'jamaican', 'spanish', 'japanese',
                            'greek', 'vietnamese', 'korean',
                            'brazilian', 'thai']
    print(f"Selected cuisines: {selected_cuisines}")
    print(f"Cuisine Type: {type(selected_cuisines)}")


    print(f"Query: {query}")
    print(f"Categories: {categories}")
    print(f"Cuisines: {cuisines}")
    
    if not query:
        return jsonify({"error": "Query parameter required."})
        # can change top k later.
    try:
        print(f"Selected cuisines in search: {selected_cuisines}")
        tf_idf_results = tf_idf_search_fuzzy(query=query, inverted_index_file='', top_k=10, inverted_index=inverted_index, inverted_index_titles=inverted_index_titles, recipes_dict=recipes_dict, categories=selected_categories, cuisines=selected_cuisines)
        results = []
        for doc_id, score in tf_idf_results:
            results.append([recipes_dict[doc_id],score])
        return jsonify(results)
    except:
        return jsonify({"error":"Invalid request"}), 400

@app.route("/api/feelinghungry")
def imfeelinghungry():
    total = len(recipes_dict)
    random_recipe_index = random.randint(0, total)
    return jsonify(recipes_dict[random_recipe_index])

if __name__ == "__main__":
    app.run(debug=True)
