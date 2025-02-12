from flask import Flask, request, jsonify
from search import tf_idf_search
import pickle


with open('inverted_index_simple.pkl', 'rb') as f:
    inverted_index = pickle.load(f)

with open('inverted_index_simple_titles.pkl', 'rb') as f:
    inverted_index_titles = pickle.load(f)

with open('recipes_dict.pkl', 'rb') as f:
    recipes_dict = pickle.load(f)

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/api/search")
def search():
    query = request.args.get("query")
    type = request.args.get("type")
    
    if not query:
        return jsonify({"error": "Query paramater required."})
        # can change top k later.
    if not type or type == 'ingredients':
        print("Ingredient query")
        tf_idf_results = tf_idf_search(query=query, inverted_index_file='', top_k=10, inverted_index=inverted_index)
        results = []
        for doc_id, score in tf_idf_results:
            results.append([recipes_dict[doc_id],score])

        return jsonify(results)
    
    elif type == 'titles':
        print("Title query")
        tf_idf_results = tf_idf_search(query=query, inverted_index_file='', top_k=10, inverted_index=inverted_index_titles)
        results = []
        for doc_id, score in tf_idf_results:
            results.append([recipes_dict[doc_id],score])

        return jsonify(results)

    return jsonify({"error":"Invalid request"})

if __name__ == "__main__":
    app.run(debug=True)
