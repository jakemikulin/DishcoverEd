from flask import Flask, request, jsonify
from flask_cors import CORS
from search import tf_idf_search, tf_idf_search_fuzzy, tf_idf_search_fuzzy2
from load_synonyms import load_synonyms
import pickle
import random
import json
import ast
from symspellpy import SymSpell, Verbosity

with open('inverted_index_simple.pkl', 'rb') as f:
    inverted_index = pickle.load(f)

with open('inverted_index_simple_titles.pkl', 'rb') as f:
    inverted_index_titles = pickle.load(f)

with open('recipes_dict.pkl', 'rb') as f:
    recipes_dict = pickle.load(f)

with open('top_5000_terms.pkl', 'rb') as f:
    top_5000 = pickle.load(f)

total_docs = max(max(postings.keys()) for postings in inverted_index.values())
load_synonyms()

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
    print(f"Query: {query}")
    
    # corrected_tokens = []
    # for token in query.split(" "):
    #     token = spell_correct(token)
    #     corrected_tokens.append(token)

    # query = " ".join(corrected_tokens)

    # print(f"Corrected Query: {query}")

    if query == "surprise":
        print("Feeling hungry!")
        total = len(recipes_dict)
        random_recipe_index = random.randint(0, total)
        print(f"Random recipe index: {random_recipe_index}")
        try:
            return jsonify([[recipes_dict[random_recipe_index], 1.0]])
        except:
            return jsonify({"error": "Invalid request"}), 400

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
        tf_idf_results = tf_idf_search_fuzzy2(query=query, total_docs=total_docs, top_5000=top_5000, inverted_index_file='', top_k=10, inverted_index=inverted_index, inverted_index_titles=inverted_index_titles, recipes_dict=recipes_dict, categories=selected_categories, cuisines=selected_cuisines)
        results = []
        for doc_id, score in tf_idf_results:
            results.append([recipes_dict[doc_id],score])
        return jsonify(results)
    except:
        return jsonify({"error":"Invalid request"}), 400

def spell_correct(token):
    suggestions = sym_spell.lookup(token, Verbosity.CLOSEST, max_edit_distance=2, include_unknown=True)
    return suggestions[0].term if suggestions else token

# @app.route("/api/search?query=feelinghungry")
# def imfeelinghungry():
#     total = len(recipes_dict)
#     random_recipe_index = random.randint(0, total)
#     return jsonify(recipes_dict[random_recipe_index])

if __name__ == "__main__":
    print("Starting Flask server...")
    
    # # Dummy search
    # dummy_query = "chicken soup"
    # try:
    #     tf_idf_search_fuzzy2(query=dummy_query, total_docs=total_docs, inverted_index_file='', top_k=10, inverted_index=inverted_index, inverted_index_titles=inverted_index_titles, recipes_dict=recipes_dict)
    # except Exception as e:
    #     print(f"Warm-up query failed: {e}")
    
    print("Flask server is ready.")
    app.run(debug=True)
