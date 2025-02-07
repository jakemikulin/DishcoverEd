from data_processing import load_dataset
from data_processing import save_recipes_as_dict_pkl
from data_processing import build_simple_inverted_index
df = load_dataset('recipes_data.csv')
save_recipes_as_dict_pkl(df)
inverted_index = build_simple_inverted_index(df)
