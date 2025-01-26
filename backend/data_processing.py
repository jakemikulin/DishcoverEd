import pandas as pd
import numpy as np
import regex as re
import Stemmer
import ast
from collections import defaultdict

def load_dataset(file_path):
    df = pd.read_csv(file_path)
    print("Loaded dataset")
    return df

def preprocess(text):
    tokens = tokenise(text)

    preprocessed = stem(tokens)

    return preprocessed

    
def tokenise(raw_text):
    # store measurements/quantities together (eg. 1 c. and 1 1/2 lb.)
    raw_text = raw_text.lower()
    match = re.findall('[a-zA-Z0-9/]+(?: [0-9/]+)?(?: [a-zA-Z]+\.)?', raw_text)

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

# ----------------------------
# Inverted Index Building
# ----------------------------


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
    
    return inverted_index


def format_inverted_index(inverted_index):
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
    
    return '\n'.join(formatted_inverted_index)



def main():
    dataset_file = 'recipes_data.csv'
    df = load_dataset(dataset_file)
    inverted_index = build_inverted_index_with_ingredient_ids(df)
    formatted_index = format_inverted_index(inverted_index)
    # print(formatted_index)

    with open('inverted_index.txt', 'w') as f:
        f.write(formatted_index)


if __name__ == '__main__':
    main()
    