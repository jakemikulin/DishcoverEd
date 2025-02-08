import pickle
import math
from collections import defaultdict
from data_processing import preprocess

def tf_idf_search(query, inverted_index_file='inverted_index_simple.pkl', top_k=10, inverted_index = None):
    """
    Perform a TF-IDF search over documents using the inverted index.

    Parameters:
      query (str): The search query.
      inverted_index_file (str): The path to the pickled inverted index.
      top_k (int): Number of top documents to return.

    Returns:
      List of tuples (doc_id, score) sorted by descending score.
    """
    if inverted_index == None:
    # Load the inverted index from the pickle file.
        with open(inverted_index_file, 'rb') as f:
            inverted_index = pickle.load(f)
    

    # Preprocess the query to obtain tokens.
    # Make sure your `preprocess` function is defined/imported.
    query_tokens = preprocess(query)

    print("Query tokens:", query_tokens)
    
    # Determine the total number of documents.
    # Assuming that document IDs are positive integers starting from 1,
    # we compute total_docs as the maximum doc_id found in the index.
    
    # total_docs = 10000
    total_docs = max(max(postings.keys()) for postings in inverted_index.values())
    print(total_docs)
    
    # A dictionary to accumulate TF-IDF scores for each document.
    scores = defaultdict(float)

    # Process each token in the query.
    for token in query_tokens:
        print("\nToken:", token)
        # Skip tokens not in the index.
        if token not in inverted_index:
            continue

        # Get the posting list for the token: {doc_id: [positions]}.
        postings = inverted_index[token]
        # Number of documents that contain the token.
        doc_freq = len(postings)
        if doc_freq == 0:
            continue

        print(f"Document frequency: {doc_freq}")

        # Compute the inverse document frequency (IDF) for this term.
        idf = math.log(total_docs / doc_freq)

        # For each document containing the token, add the TF-IDF contribution.
        
        for doc_id, positions in postings.items():
            # Term frequency is the number of occurrences (length of positions list).
            tf = len(positions)
            # Add the tf-idf score; if the term appears multiple times, its contributions add up.
            scores[doc_id] += tf * idf

    # Sort the documents by their score in descending order.
    ranked_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Return the top_k results.
    return ranked_results[:top_k]

# Example usage:
if __name__ == '__main__':
    # Example query string.
    query = "chicken garlic lemon"
    print("Query:", query)
    with open('queries.txt', 'a') as f:
        f.write(query + '\n')
    # Call the search function.


    results = tf_idf_search(query, inverted_index_file='inverted_index_simple.pkl', top_k=10, inverted_index=None)
    # Print the ranked document IDs and their scores.
    for doc_id, score in results:
        print(f"Document {doc_id} - Score: {score:.4f}")
