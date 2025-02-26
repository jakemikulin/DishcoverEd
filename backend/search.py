import pickle
import math
from collections import defaultdict
from data_processing import preprocess, build_simple_inverted_index_titles, load_dataset, build_simple_inverted_index, save_recipes_as_dict_pkl
import numpy as np

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

    # Preprocess the query to obtain tokens.
    # Make sure your preprocess function is defined/imported.
    query_tokens = preprocess(query)
    print("Query tokens:", query_tokens)
    
    # If not already provided, load the inverted index.
    if inverted_index is None:
        with open(inverted_index_file, 'rb') as f:
            inverted_index = pickle.load(f)
    
    # It is assumed that inverted_index_titles is already provided.
    # Determine the total number of documents.
    total_docs = max(max(postings.keys()) for postings in inverted_index.values())
    print("Total documents:", total_docs)
    
    # Prepare a set of required categories, filtering out empty strings.
    required_categories = {cat for cat in categories if cat}
    
    # A dictionary to accumulate TF-IDF scores for each document.
    scores = defaultdict(float)
    
    # Process each token in the query.
    for token in query_tokens:
        print("\nToken:", token)

        FUZZY_TOKEN_AMOUNT = 3
        fuzzy_tokens = sort_by_edit_distance(token, inverted_index.keys())[:FUZZY_TOKEN_AMOUNT] # An array with tuples (token, edit_distance)

        token_edit_distance = [(token, 0)] + fuzzy_tokens

        for token, edit_distance in token_edit_distance:
            
            if token not in inverted_index and token not in inverted_index_titles:
                continue

            # Get postings; use .get() in case the token isn't in one of the indices.
            postings = inverted_index.get(token, {})
            title_postings = inverted_index_titles.get(token, {})
            
            # Number of documents that contain the token.
            doc_freq = len(postings) + len(title_postings)
            if doc_freq == 0:
                continue

            print(f"Document frequency: {doc_freq}")
            idf = math.log(total_docs / doc_freq)

            # Scale IDF by edit distance
            idf = idf / (2**edit_distance) 
            
            # Process regular postings.
            for doc_id, positions in postings.items():
                recipe = recipes_dict.get(doc_id)
                if recipe is None:
                    continue
                # Check that the cuisine is allowed.
                if recipe['cuisine'] not in cuisines:
                    continue
                # Check that all required categories are present.
                # Here, recipe['categories'] is assumed to be iterable (list, set, etc.).
                recipe_categories = set(recipe.get('categories', []))
                if not required_categories.issubset(recipe_categories):
                    continue
                # Compute term frequency adjusted by document length.
                tf = len(positions) / math.log(1 + len(recipe['NER']))
                scores[doc_id] += tf * idf
            
            # Process title postings.
            for doc_id, positions in title_postings.items():
                recipe = recipes_dict.get(doc_id)
                if recipe is None:
                    continue
                if recipe['cuisine'] not in cuisines:
                    continue
                recipe_categories = set(recipe.get('categories', []))
                if not required_categories.issubset(recipe_categories):
                    continue
                tf = len(positions) / math.log(1 + len(recipe['title']))
                scores[doc_id] += tf * idf

    # Sort the documents by their cumulative TF-IDF scores in descending order.
    ranked_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    print("Number of results:", len(ranked_results))
    
    if return_all:
        return ranked_results
    return ranked_results[:top_k]

def edit_distance(token, target):
    m = len(token)
    n = len(target)

    # Initialize the DP table
    dp = np.zeros((m + 1, n + 1))

    # Base cases: filling in the first row and first column
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Fill the rest of the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # If characters are the same, no edit is needed
            if token[i - 1] == target[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                # If characters are different, take the minimum of:
                # 1. Insertion: dp[i][j-1] + 1
                # 2. Deletion: dp[i-1][j] + 1
                # 3. Substitution: dp[i-1][j-1] + 1
                dp[i][j] = min(dp[i - 1][j - 1] + 1,    # substitution
                               dp[i][j - 1] + 1,        # insertion
                               dp[i - 1][j] + 1)        # deletion

    return int(dp[m][n])

def sort_by_edit_distance(token, candidates):
    edit_dict = {}
    for candidate in candidates:
        edit_dict[candidate] = edit_distance(token, candidate)
    return sorted(edit_dict.items(), key=lambda x: x[1])
    

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
        
