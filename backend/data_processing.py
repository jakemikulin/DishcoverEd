import pandas as pd
import numpy as np
import regex as re
import Stemmer
import ast
import pickle
from collections import defaultdict
from synonym_search import SYNONYM_MAP

# Libary of functions that are useful for building the data to be searched through using the backend.

def load_dataset(file_path):
    print("Loading dataset")
    df = pd.read_csv(file_path)
    print("Loaded dataset")
    return df


def save_recipes_as_dict_pkl(df, output_file="recipes_dict.pkl"):
    print("Saving recipes as dictionary")

    # Ensure 'doc_id' starts from 1
    df = df.reset_index(drop=True)  # Reset index without keeping old index
    df["doc_id"] = df.index + 1  # Assign doc_id starting from 1

    # Create dictionary with {doc_id: recipe_data}
    recipes_dict = df.set_index("doc_id").to_dict(orient="index")

    # Save dictionary as a pickle file
    with open(output_file, "wb") as f:
        pickle.dump(recipes_dict, f)

    print(f"Saved recipes dictionary to {output_file}")
    return recipes_dict

def normalize_text(text):
    """Replace multi-word and hyphenated synonyms before tokenising."""
    for synonym, canonical in SYNONYM_MAP.items():
        text = re.sub(r'\b' + re.escape(synonym) + r'\b', canonical, text, flags=re.IGNORECASE)
    return text

def preprocess_title(text):
    try:
        text = normalize_text(text)
        tokens = tokenise(text)
        preprocessed = stem(tokens)
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        preprocessed = []

    return preprocessed

def preprocess(text):
    try:
        text = normalize_text(text)
        tokens = tokenise_title(text)
        preprocessed = stem(tokens)
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        preprocessed = []

    return preprocessed

    
def tokenise(raw_text):
    # store measurements/quantities together (eg. 1 c. and 1 1/2 lb.)
    raw_text = raw_text.lower()
    match = re.findall('[a-zA-Z0-9/]+(?: [0-9/]+)?(?: [a-zA-Z]+\.)?', raw_text)

    return match

def tokenise_title(raw_text):
    raw_text = raw_text.lower()
    match = re.findall('[a-zA-Z0-9]+', raw_text)

    return match

def remove_stop_words(word_array):
    # Change stop_words_path if required.
    stop_words_path = 'englishST.txt'
    lines = []
    with open(stop_words_path, 'r') as f:
        stop_words = set(f.read().splitlines())
    
    filtered = [word for word in word_array if word not in stop_words]
    return filtered

def stem(word_array):
    stemmer = Stemmer.Stemmer('english')
    stemmed = []
    for word in word_array:
        word = stemmer.stemWord(word)
        stemmed.append(word)
    return stemmed

# 
# Inverted Index for Ingredients with Quantities
# 

def build_inverted_index_with_ingredient_ids(df):
    # Inverted index structure: {term: {doc_id: {ingredient_id: [positions]}}}
    inverted_index = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    total = len(df["ingredients"])
    # Iterate through each row in the DataFrame
    for doc_id, ingredients_string in enumerate(df["ingredients"], start=1):
        if doc_id % 100000 == 0:
            print(f"At document {doc_id} / {total}")
        # Convert ingredients string into a list of ingredients
        ingredients_array = ast.literal_eval(ingredients_string)

        # Process each ingredient in the recipe
        for ingredient_id, ingredient in enumerate(ingredients_array, start=1):
            tokens = preprocess(ingredient)

            # Add each token to the inverted index with positions
            for pos, term in enumerate(tokens):
                inverted_index[term][doc_id][ingredient_id].append(pos + 1)
    print("Built inverted index!")
    
    # Can't pickle defaultdict objects.
    def convert_to_regular_dict(d):
        if isinstance(d, defaultdict):
            return {k: convert_to_regular_dict(v) for k, v in d.items()}
        return d
    
    inverted_index = convert_to_regular_dict(inverted_index)
    
    output_file = 'inverted_index_ingredient_ids.pkl'
    print("Pickle dumping inverted index")
    with open(output_file, 'wb') as f:
        pickle.dump(inverted_index, f)
    print(f"Saved inverted index to {output_file}")
        

    return inverted_index

def format_inverted_index(inverted_index):
    print("Formatting inverted index to write.")
    # Format the inverted index for easier visualization
    formatted_inverted_index = []

    for term, doc_info in inverted_index.items():
        df = len(doc_info)
        formatted_inverted_index.append(f"{term}:{df}")

        for doc_id, ingredients in doc_info.items():
            formatted_inverted_index.append(f"\t{doc_id}:")
            for ingredient_id, positions in ingredients.items():
                pos_str = ','.join(map(str, positions))
                formatted_inverted_index.append(f"\t\t{ingredient_id}:{pos_str}")
    
    print("Finished formatting.")
    return '\n'.join(formatted_inverted_index)


def generate_inverted_index_incl_quantities():
    dataset_file = 'recipes_with_labels.csv'
    df = load_dataset(dataset_file)
    inverted_index = build_inverted_index_with_ingredient_ids(df)
    formatted_index = format_inverted_index(inverted_index)

    print("Writing index to inverted_index.txt")
    with open('inverted_index.txt', 'w') as f:
        f.write(formatted_index)
    f.close()
    print("Finished.")

# 
# Simple Inverted Index for Ingredients
# 
    
def build_simple_inverted_index(df):
    # Inverted index structure: {term: {doc_id: [positions]}}
    inverted_index = defaultdict(lambda: defaultdict(list))
    recipe_lengths = {}
    
    total = len(df["NER"])

    # Iterate through each row in the DataFrame
    for doc_id, ingredients_string in enumerate(df["NER"], start=1):
        if doc_id % 100000 == 0:
            print(f"At document {doc_id} / {total}")
        tokens = preprocess(ingredients_string)
        recipe_lengths[doc_id] = len(tokens)
        # Add each token to the inverted index with positions
        for pos, term in enumerate(tokens):
            inverted_index[term][doc_id].append(pos + 1)
    
    print("Built inverted index!")
    
    # Can't pickle defaultdict objects.
    def convert_to_regular_dict(d):
        if isinstance(d, defaultdict):
            return {k: convert_to_regular_dict(v) for k, v in d.items()}
        return d
    
    inverted_index = convert_to_regular_dict(inverted_index)
    
    inverted_index_output_file = 'inverted_index_simple.pkl'
    print("Pickle dumping inverted index")
    with open(inverted_index_output_file, 'wb') as f:
        pickle.dump(inverted_index, f)

    recipe_lengths_output_file = 'recipe_lengths.pkl'
    print("Pickle dumping recipe lengths")
    with open(recipe_lengths_output_file, 'wb') as f:
        pickle.dump(recipe_lengths, f)
    
    print(f"Saved inverted index to {inverted_index_output_file} and recipe lengths to {recipe_lengths_output_file}")
    
    return inverted_index

def format_inverted_index_simple(inverted_index):
    print("Formatting inverted index to write.")
    # Format the inverted index for easier visualization
    formatted_inverted_index = []

    for term, doc_info in inverted_index.items():
        df = len(doc_info)
        formatted_inverted_index.append(f"{term}:{df}")

        for doc_id in doc_info.keys():
            formatted_inverted_index.append(f"\t{doc_id}:")
            positions = doc_info[doc_id]
            pos_str = ','.join(map(str, positions))
            formatted_inverted_index.append(f"\t\t{pos_str}")
    
    print("Finished formatting.")
    return '\n'.join(formatted_inverted_index)

def generate_inverted_index_simple():
    dataset_file = 'recipes_with_labels.csv'
    df = load_dataset(dataset_file)
    inverted_index = build_simple_inverted_index(df)
    formatted_index = format_inverted_index_simple(inverted_index)

    print("Writing index to inverted_index_simple.txt")
    with open('inverted_index_simple.txt', 'w') as f:
        f.write(formatted_index)
    f.close()
    print("Finished.")

# 
# Inverted Index for Recipe Titles
# 

def generated_inverted_index_simple_titles():
    dataset_file = 'recipes_with_labels.csv'
    df = load_dataset(dataset_file)
    inverted_index = build_simple_inverted_index_titles(df)
    formatted_index = format_inverted_index_simple(inverted_index)

    print("Writing index to inverted_index_simple_titles.txt")
    with open('inverted_index_simple_titles.txt', 'w') as f:
        f.write(formatted_index)
    f.close()
    print("Finished.")
    
    
def build_simple_inverted_index_titles(df):
    # Inverted index structure: {term: {doc_id: [positions]}}
    inverted_index = defaultdict(lambda: defaultdict(list))
    total = len(df["title"])
    # Iterate through each row in the DataFrame
    for doc_id, ingredients_string in enumerate(df["title"], start=1):
        if doc_id % 100000 == 0:
            print(f"At document {doc_id} / {total}")
        tokens = preprocess_title(ingredients_string)
        # Add each token to the inverted index with positions
        for pos, term in enumerate(tokens):
            inverted_index[term][doc_id].append(pos + 1)
    
    print("Built inverted index!")
    
    # Can't pickle defaultdict objects.
    def convert_to_regular_dict(d):
        if isinstance(d, defaultdict):
            return {k: convert_to_regular_dict(v) for k, v in d.items()}
        return d
    
    inverted_index = convert_to_regular_dict(inverted_index)
    
    output_file = 'inverted_index_simple_titles.pkl'
    print("Pickle dumping inverted index")
    with open(output_file, 'wb') as f:
        pickle.dump(inverted_index, f)
    print(f"Saved inverted index to {output_file}")
    
    return inverted_index
    
