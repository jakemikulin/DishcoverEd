import pickle
import math
from collections import defaultdict
import time
from data_processing import preprocess, build_simple_inverted_index_titles, load_dataset, build_simple_inverted_index, save_recipes_as_dict_pkl
import numpy as np

ALL_TOKENS = None

def load_indices():
    df = load_dataset('recipes_test_data.csv')
    save_recipes_as_dict_pkl(df, 'backend/recipes_with_labels.csv')
    # build_simple_inverted_index(df)
    # build_simple_inverted_index_titles(df)

def get_all_tokens(inverted_index, inverted_index_titles):
    """Compute all tokens from both indices only once."""
    global ALL_TOKENS
    if ALL_TOKENS is None:
        print("Computing all_tokens...")
        ALL_TOKENS = set(inverted_index.keys()).union(inverted_index_titles.keys()) if inverted_index_titles else set(inverted_index.keys())
    return ALL_TOKENS

def levenshtein_distance(s, t):
    """
    Compute the Levenshtein edit distance between strings s and t.
    """
    m, n = len(s), len(t)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1):
        dp[i][0] = i
    for j in range(n+1):
        dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if s[i-1] == t[j-1] else 1
            dp[i][j] = min(dp[i-1][j] + 1,      # deletion
                           dp[i][j-1] + 1,      # insertion
                           dp[i-1][j-1] + cost) # substitution
    return dp[m][n]

def get_fuzzy_match(token, token_set, max_distance=1):
    """
    Given a token and a set of tokens, return the token from token_set 
    with the smallest edit distance (if within max_distance), or (None, None)
    if no such token is found.
    """
    best_match = None
    best_distance = None
    for cand in token_set:
        d = levenshtein_distance(token, cand)
        if d <= max_distance:
            if best_distance is None or d < best_distance:
                best_distance = d
                best_match = cand
    return best_match, best_distance

def tf_idf_search_fuzzy(query,
                  cuisines=None,
                  categories=None,
                  inverted_index_file='inverted_index_simple.pkl',
                  top_k=100,
                  inverted_index=None,
                  return_all=False,
                  inverted_index_titles=None,
                  recipes_dict=None):
    """
    Perform a TF-IDF search over documents using the inverted index.
    
    If a query token doesn't have any exact matches in either index but is within a
    small edit distance of a token that is in an index, it contributes to the score
    with a reduced weighting.
    """

    if cuisines is None:
        cuisines = {'southern_us', 'russian', 'chinese', 'italian', 'mexican', 'french',
                    'british', 'cajun_creole', 'filipino', 'indian', 'irish', 'moroccan',
                    'jamaican', 'spanish', 'japanese', 'greek', 'vietnamese', 'korean',
                    'brazilian', 'thai'}
    if categories is None:
        categories = set()

    # Preprocess the query to obtain tokens.
    query_tokens = preprocess(query)
    print("Query tokens:", query_tokens)
    
    # Load inverted index if not provided.
    if inverted_index is None:
        with open(inverted_index_file, 'rb') as f:
            inverted_index = pickle.load(f)
    
    # Determine the total number of documents.
    total_docs = max(max(postings.keys()) for postings in inverted_index.values())
    print("Total documents:", total_docs)
    
    # Prepare required categories (filter out empty strings if undesired).
    # required_categories = {cat for cat in categories if cat}
    required_categories = categories.union({''})
    
    # Create a set of all tokens from both indices.
    # all_tokens = set(inverted_index.keys()).union(set(inverted_index_titles.keys()))
    all_tokens = get_all_tokens(inverted_index, inverted_index_titles)
    
    # A dictionary to accumulate TF-IDF scores for each document.
    scores = defaultdict(float)
    
    # Define parameters for fuzzy matching.
    reduced_weight_factor = 0.5
    max_edit_distance = 1  # maximum allowed edit distance for fuzzy matching
    
    # Process each token in the query.
    for token in query_tokens:
        print("\nToken:", token)
        weight_factor = 1.0  # default weight for exact matches
        
        # If token is not found exactly in either index, try fuzzy matching.
        if token not in inverted_index and token not in inverted_index_titles:
            candidate, distance = get_fuzzy_match(token, all_tokens, max_distance=max_edit_distance)
            if candidate is None:
                continue  # skip token if no fuzzy match is found
            else:
                print(f"Token '{token}' fuzzy matched with '{candidate}' (distance {distance}).")
                token = candidate  # use the candidate token for scoring
                weight_factor = reduced_weight_factor
        
        # Retrieve postings from both indices.
        postings = inverted_index.get(token, {})
        title_postings = inverted_index_titles.get(token, {})
        
        # Compute document frequency.
        doc_freq = len(postings) + len(title_postings)
        if doc_freq == 0:
            continue
        print(f"Document frequency: {doc_freq}")
        idf = math.log(total_docs / doc_freq)
        
        # Process postings from the regular index.
        for doc_id, positions in postings.items():
            recipe = recipes_dict.get(doc_id)
            
            if recipe is None:
                continue
            if recipe['cuisine'] not in cuisines:
                continue
            recipe_categories = recipe['categories']
            required_categories_list = list(required_categories)

            # if '' not in recipe_categories:
            #     recipe_categories.append('')

            # print("Recipe categories:", recipe_categories)
            # print("Required categories:", required_categories_list)

            # Check that every category in required_categories_list is in recipe_categories_list.
            if any(cat not in recipe_categories for cat in required_categories_list):
                continue
            # else:
            #     print("Categories match!")
            tf = len(positions) / math.log(1 + len(recipe['NER']))
            scores[doc_id] += weight_factor * tf * idf
        
        # Process postings from the title index.
        for doc_id, positions in title_postings.items():
            recipe = recipes_dict.get(doc_id)
            if recipe is None:
                continue
            if recipe['cuisine'] not in cuisines:
                continue
            recipe_categories = recipe['categories']
            required_categories_list = list(required_categories)

            if '' not in recipe_categories:
                recipe_categories.append('')

            # print("Titles Recipe categories:", recipe_categories)
            # print("Titles Required categories:", required_categories_list)

            # Check that every category in required_categories_list is in recipe_categories_list.
            if any(cat not in recipe_categories for cat in required_categories_list):
                continue
            # else:
            #     print("Categories match!")
            tf = len(positions) / math.log(1 + len(recipe['title']))
            scores[doc_id] += weight_factor * tf * idf

    # Sort documents by their cumulative TF-IDF score.
    ranked_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    print("Number of results:", len(ranked_results))
    
    if return_all:
        return ranked_results
    return ranked_results[:top_k]

def tf_idf_search_fuzzy2(query, total_docs,
                        cuisines={'southern_us', 'russian', 'chinese',
                                  'italian', 'mexican', 'french',
                                  'british', 'cajun_creole', 'filipino',
                                  'indian', 'irish', 'moroccan',
                                  'jamaican', 'spanish', 'japanese',
                                  'greek', 'vietnamese', 'korean',
                                  'brazilian', 'thai'},
                        categories={},
                        inverted_index_file='inverted_index_simple.pkl',
                        top_k=100,
                        inverted_index=None,
                        return_all=False,
                        inverted_index_titles=None,
                        recipes_dict=None):
    """
    Perform a TF-IDF search over documents using the inverted index.
    
    For each query token, if there is no exact match in either index, the top 3 closest
    tokens (by edit distance) are used. Their contributions are weighted with an exponential 
    decay factor (0.5 ** edit_distance).
    """
    start_time = time.time()
    # Preprocess the query to obtain tokens.
    query_tokens = preprocess(query)
    print("Query tokens:", query_tokens)

    print("Time to preprocess query:", time.time() - start_time)
    
    # It is assumed that inverted_index_titles is already provided.
    # Determine the total number of documents.
    print("Total documents:", total_docs)
    print("time to get total docs:", time.time() - start_time)
    
    # Prepare required categories (filter out empty strings if undesired).
    required_categories = {cat for cat in categories if cat}.union({''})

    print("time to prepare required categories:", time.time() - start_time)
    
    # Create a collection of all tokens from both indices.
    # (Assuming both indices use similar tokens.)
    all_tokens = set(inverted_index.keys()).union(set(inverted_index_titles.keys()))
    
    # Dictionary to accumulate TF-IDF scores.
    scores = defaultdict(float)

    print("time to load all tokens:", time.time() - start_time)
    
    # Process each token in the query.
    for token in query_tokens:
        print("\nProcessing token:", token)
        # If the token has an exact match in either index, process normally.
        if token in inverted_index or token in inverted_index_titles:
            weight_factor = 1.0
            tokens_to_process = [(token, weight_factor)]
        else:
            # No exact match: compute edit distances for all tokens.
            candidate_distances = []
            for cand in all_tokens:
                d = levenshtein_distance(token, cand)
                candidate_distances.append((cand, d))
            # Sort by edit distance.
            candidate_distances.sort(key=lambda x: x[1])
            # Select the top 3 closest tokens.
            top_candidates = candidate_distances[:3]
            # Create a list of tokens to process, with weight decaying exponentially with distance.
            tokens_to_process = []
            for candidate, distance in top_candidates:
                # Use weight_factor = 0.5 ** distance
                weight = 0.75 ** distance
                print(f"Token '{token}' fuzzy matched with '{candidate}' (distance {distance}, weight {weight}).")
                tokens_to_process.append((candidate, weight))
        
        # Process each candidate token (either exact or fuzzy).
        for candidate_token, weight_factor in tokens_to_process:
            candidate_time = time.time()
            print(f"Processing candidate token '{candidate_token}'")
            postings = inverted_index.get(candidate_token, {})
            title_postings = inverted_index_titles.get(candidate_token, {})
            # doc_freq = len(postings) + len(title_postings)
            all_postings = set(postings.keys()).union(set(title_postings.keys()))
            doc_freq = len(all_postings)
            if doc_freq == 0:
                continue
            print(f"Candidate token '{candidate_token}' document frequency: {doc_freq}")
            idf = math.log(total_docs / doc_freq)

            print("time to get postings:", time.time() - candidate_time)
                  
            # Process postings from the regular index.
            for doc_id, positions in postings.items():
                recipe = recipes_dict.get(doc_id)
                if recipe is None:
                    continue
                if recipe['cuisine'] not in cuisines:
                    continue
                recipe_categories = recipe['categories']
                required_categories_list = list(required_categories)
                if '' not in recipe_categories:
                    recipe_categories.append('')
                if any(cat not in recipe_categories for cat in required_categories_list):
                    continue
                tf = len(positions) / math.log(1 + len(recipe['NER']))
                scores[doc_id] += weight_factor * tf * idf

            print("time to process regular postings:", time.time() - candidate_time)
            
            # Process postings from the title index.
            for doc_id, positions in title_postings.items():
                recipe = recipes_dict.get(doc_id)
                if recipe is None:
                    continue
                if recipe['cuisine'] not in cuisines:
                    continue
                recipe_categories = recipe['categories']
                required_categories_list = list(required_categories)
                if '' not in recipe_categories:
                    recipe_categories.append('')
                if any(cat not in recipe_categories for cat in required_categories_list):
                    continue
                tf = len(positions) / math.log(1 + len(recipe['title']))
                scores[doc_id] += weight_factor * tf * idf

            print("time to process title postings:", time.time() - candidate_time)

    print("time to process tokens:", time.time() - start_time)
    # Sort the documents by their cumulative TF-IDF scores.
    ranked_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    print("Number of results:", len(ranked_results))
    print("time to complete search:", time.time() - start_time)
    if return_all:
        return ranked_results
    return ranked_results[:top_k]

def tf_idf_search_fuzzy4(query,
                        cuisines=None,
                        categories=None,
                        inverted_index_file='inverted_index_simple.pkl',
                        top_k=100,
                        inverted_index=None,
                        return_all=False,
                        inverted_index_titles=None,
                        recipes_dict=None):
    """
    Perform a TF-IDF search over documents using the inverted index.
    Uses fuzzy matching **only when necessary**.
    """
    start_time = time.time()

    if cuisines is None:
        cuisines = {'southern_us', 'russian', 'chinese', 'italian', 'mexican', 'french',
                    'british', 'cajun_creole', 'filipino', 'indian', 'irish', 'moroccan',
                    'jamaican', 'spanish', 'japanese', 'greek', 'vietnamese', 'korean',
                    'brazilian', 'thai'}
    if categories is None:
        categories = set()

    if inverted_index is None:
        with open(inverted_index_file, 'rb') as f:
            inverted_index = pickle.load(f)

    # Preprocess the query to obtain tokens
    query_tokens = preprocess(query)
    print("Query tokens:", query_tokens)

    # Compute all tokens only once**
    all_tokens = get_all_tokens(inverted_index, inverted_index_titles)

    # Determine total number of documents
    total_docs = max(max(postings.keys()) for postings in inverted_index.values())

    required_categories = categories.union({''})

    scores = defaultdict(float)

    for token in query_tokens:
        print("\nProcessing token:", token)

        if token in inverted_index or token in inverted_index_titles:
            # Skip fuzzy search if exact match exists
            tokens_to_process = [(token, 1.0)]
        else:
            candidate_distances = []
            for cand in all_tokens:
                d = levenshtein_distance(token, cand)
                candidate_distances.append((cand, d))
            candidate_distances.sort(key=lambda x: x[1])
            top_candidates = candidate_distances[:3]
            tokens_to_process = [(candidate, 0.75 ** distance) for candidate, distance in top_candidates]
            print(f"Token '{token}' fuzzy matched with {top_candidates}")

        # Process each token (either exact or fuzzy match)
        for candidate_token, weight_factor in tokens_to_process:
            postings = inverted_index.get(candidate_token, {})
            title_postings = inverted_index_titles.get(candidate_token, {})

            doc_freq = len(postings) + len(title_postings)
            if doc_freq == 0:
                continue

            idf = math.log(total_docs / doc_freq)

            # Process postings from the regular index
            for doc_id, positions in postings.items():
                recipe = recipes_dict.get(doc_id)
                if not recipe or recipe['cuisine'] not in cuisines or not required_categories.issubset(recipe['categories']):
                    continue
                tf = len(positions) / math.log(1 + len(recipe['NER']))
                scores[doc_id] += weight_factor * tf * idf

            # Process postings from the title index
            for doc_id, positions in title_postings.items():
                recipe = recipes_dict.get(doc_id)
                if not recipe or recipe['cuisine'] not in cuisines or not required_categories.issubset(recipe['categories']):
                    continue
                tf = len(positions) / math.log(1 + len(recipe['title']))
                scores[doc_id] += weight_factor * tf * idf

    # Sort and return results
    ranked_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    print("Number of results:", len(ranked_results))
    print("Time to complete search:", time.time() - start_time)

    return ranked_results if return_all else ranked_results[:top_k]


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
        
