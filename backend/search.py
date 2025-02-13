import pickle
import math
from collections import defaultdict
from data_processing import preprocess, build_simple_inverted_index_titles, load_dataset, build_simple_inverted_index, save_recipes_as_dict_pkl

def load_indices():
    df = load_dataset('recipes_test_data.csv')
    save_recipes_as_dict_pkl(df, 'backend/recipes_with_labels.csv')
    # build_simple_inverted_index(df)
    # build_simple_inverted_index_titles(df)

def get_synonyms(word, word_vectors, top_n=3):
    """Retrieve top N similar words using Word2Vec/FastText."""
    try:
        similar_words = word_vectors.most_similar(word, topn=top_n)
        return [w for w, _ in similar_words]
    except KeyError:
        return []  # Return empty if word is not in the model

def expand_token(token, idf,word_vectors, top_n=3, idf_threshold=2.0):

    if idf >= idf_threshold:
        expanded_tokens = [preprocess(exp) for exp in get_synonyms(token)]
    expanded_tokens.append(token)
    return set(expanded_tokens)
        
        

def tf_idf_search(query, cuisines={'southern_us', 'russian', 'chinese',
                                  'italian', 'mexican', 'french',
                                  'british', 'cajun_creole', 'filipino',
                                  'indian', 'irish', 'moroccan',
                                  'jamaican', 'spanish', 'japanese',
                                  'greek', 'vietnamese', 'korean',
                                  'brazilian', 'thai'},
                    categories={'', 'Additive', 'Bakery', # Should the empty string be included?
                                'Beverage', 'Beverage Alcoholic', 'Dairy',
                                'Essential Oil', 'Fish', 'Flower', 'Fruit',
                                'Fungus', 'Herb', 'Legume', 'Maize', 'Meat',
                                'Nuts & Seed', 'Plant', 'Seafood', 'Spice',
                                'Vegetable'}, inverted_index_file='inverted_index_simple.pkl', top_k=100, inverted_index = None, return_all=False, inverted_index_titles = None, recipes_dict = None ):
    """
    Perform a TF-IDF search over documents using the inverted index.

    Parameters:
      query (str): The search query.
      inverted_index_file (str): The path to the pickled inverted index.
      top_k (int): Number of top documents to return.

    Returns:
      List of tuples (doc_id, score) sorted by descending score.
    """

    # Preprocess the query to obtain tokens.
    # Make sure your `preprocess` function is defined/imported.
    query_tokens = preprocess(query)

    print("Query tokens:", query_tokens)
    
    # Determine the total number of documents.
    # Assuming that document IDs are positive integers starting from 1,
    # we compute total_docs as the maximum doc_id found in the index.
    
    # total_docs = 10000
    total_docs = max(max(postings.keys()) for postings in inverted_index.values())
    print("Total documents:", total_docs)
    
    # A dictionary to accumulate TF-IDF scores for each document.
    scores = defaultdict(float)

    # Process each token in the query.
    for token in query_tokens:
        print("\nToken:", token)
        # Skip tokens not in the index.
        if token not in inverted_index and token not in inverted_index_titles:
            continue

        # Get the posting list for the token: {doc_id: [positions]}.
        postings = inverted_index[token]
        title_postings = inverted_index_titles[token]
        # Number of documents that contain the token.
        doc_freq = len(postings) + len(title_postings)
        if doc_freq == 0:
            continue

        print(f"Document frequency: {doc_freq}")

        # Compute the inverse document frequency (IDF) for this term.
        idf = math.log(total_docs / doc_freq)

        # For each document containing the token, add the TF-IDF contribution.
        
        for doc_id, positions in postings.items():
            if recipes_dict[doc_id]['cuisine'] in cuisines:
                # valid_category = False
                # for catetory in recipes_dict[doc_id]['categories']:
                #     if catetory in categories:
                #         valid_category = True
                #         break
                # if not valid_category:
                #     continue
                # Term frequency is the number of occurrences (length of positions list).
                tf = len(positions) / math.log(1 + len(recipes_dict[doc_id]['NER']))
                # Add the tf-idf score; if the term appears multiple times, its contributions add up.
                scores[doc_id] += tf * idf
            else:
                continue

        for doc_id, positions in title_postings.items():
            if recipes_dict[doc_id]['cuisine'] in cuisines:
                # valid_category = False
                # for catetory in recipes_dict[doc_id]['categories']:
                #     if catetory in categories:
                #         valid_category = True
                #         break
                # if not valid_category:
                #     continue
                # Term frequency is the number of occurrences (length of positions list).
                # tf = len(positions) / (len(recipes_dict[doc_id]['title']))
                tf = len(positions) / math.log(1 + len(recipes_dict[doc_id]['title']))

                # Add the tf-idf score; if the term appears multiple times, its contributions add up.
                scores[doc_id] += tf * idf
            else:
                continue

    # Sort the documents by their score in descending order.
    ranked_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    print("Number of results:", len(ranked_results))

    if return_all:
        return ranked_results
    # Return the top_k results.
    return ranked_results[:top_k]

# Example usage:
if __name__ == '__main__':
    load_indices()

    # # Example query string.
    # query = "chicken garlic lemon"
    # print("Query:", query)
    # with open('queries.txt', 'a') as f:
    #     f.write(query + '\n')
    # # Call the search function.


    # results = tf_idf_search(query, inverted_index_file='inverted_index_simple.pkl', top_k=10, inverted_index=None)
    # # Print the ranked document IDs and their scores.
    # for doc_id, score in results:
    #     print(f"Document {doc_id} - Score: {score:.4f}")
        
