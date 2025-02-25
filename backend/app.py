from flask import Flask, request, jsonify
from flask_cors import CORS
from search import tf_idf_search
import pickle


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
    categories = request.args.getlist("categories")
    
    if not query:
        return jsonify({"error": "Query parameter required."})
        # can change top k later.
    try:
        if not categories:
            tf_idf_results = tf_idf_search(query=query, inverted_index_file='', top_k=10, inverted_index=inverted_index, inverted_index_titles=inverted_index_titles, recipes_dict=recipes_dict)
        else:
            tf_idf_results = tf_idf_search(query=query, inverted_index_file='', top_k=10, inverted_index=inverted_index, inverted_index_titles=inverted_index_titles, recipes_dict=recipes_dict, categories=categories)
        results = []
        for doc_id, score in tf_idf_results:
            results.append([recipes_dict[doc_id],score])
        return jsonify(results)
    except:
        return jsonify({"error":"Invalid request"}), 400

if __name__ == "__main__":
    app.run(debug=True)
