from search import tf_idf_search
import pickle

str = ""
with open('inverted_index_simple.pkl', 'rb') as f:
    inverted_index = pickle.load(f)
    
with open('recipes_dict.pkl', 'rb') as f:
    recipes_dict = pickle.load(f)
print("Loaded")
while True:
    str = input(": ")
    if str == "q!":
        break
    results = tf_idf_search(str, inverted_index_file='inverted_index_simple.pkl', top_k=10, inverted_index=inverted_index)
    # Print the ranked document IDs and their scores.
    for doc_id, score in results:
        print(f"Document {doc_id} : {recipes_dict[doc_id]['title']} - Score: {score:.4f}")
    