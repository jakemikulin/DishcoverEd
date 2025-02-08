from data_processing import load_dataset
from data_processing import save_recipes_as_dict_pkl
from data_processing import build_simple_inverted_index
from data_processing import build_inverted_index_with_ingredient_ids
from data_processing import build_simple_inverted_index_titles

# Run this to build all needed pkl files. 
def main():
    df = load_dataset('recipes_data.csv')
    save_recipes_as_dict_pkl(df)
    build_simple_inverted_index(df)
    # build_inverted_index_with_ingredient_ids(df)
    build_simple_inverted_index_titles(df)
    
if __name__ == "__main__":
    main()

