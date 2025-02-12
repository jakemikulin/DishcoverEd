import { useState } from 'react';
import './Modal.css';

const cuisinesList = [
  'Southern US', 'Russian', 'Chinese', 'Italian', 'Mexican',
  'French', 'British', 'Cajun Creole', 'Filipino', 'Indian',
  'Irish', 'Jamaican', 'Moroccan', 'Spanish', 'Japanese',
  'Greek', 'Vietnamese', 'Korean', 'Brazilian', 'Thai'
];

const categoriesList = [
  'Additive', 'Bakery', 'Beverage', 'Beverage Alcoholic', 'Dairy',
  'Essential Oil', 'Fish', 'Flower', 'Fruit', 'Fungus', 'Herb',
  'Legume', 'Maize', 'Meat', 'Nuts & Seed', 'Plant', 'Seafood',
  'Spice', 'Vegetable'
];


function Modal({ onClose, onApplyFilters }) {
  const [selectedCuisines, setSelectedCuisines] = useState({});
  const [selectedCategories, setSelectedCategories] = useState({});

  // Handle toggle of cuisine
  const handleCuisineToggle = (cuisine) => {
    setSelectedCuisines(prevState => ({
      ...prevState,
      [cuisine]: !prevState[cuisine]
    }));
  };

  // Handle toggle of category
  const handleCategoryToggle = (category) => {
    setSelectedCategories(prevState => ({
      ...prevState,
      [category]: !prevState[category]
    }));
  };

  // Handle applying the filters
  const handleApplyFilters = () => {
    onApplyFilters({ cuisines: selectedCuisines, categories: selectedCategories });
    onClose();  // Close the modal after applying filters
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="close-btn" onClick={onClose}>X</button>
        <h2>Filters</h2>
        
        {/* Cuisines Section */}
        <h3>Cuisines</h3>
        <div className="cuisines-grid">
          {cuisinesList.map((cuisine) => (
            <label key={cuisine} className="cuisine-checkbox">
              <input
                type="checkbox"
                checked={selectedCuisines[cuisine] || false}
                onChange={() => handleCuisineToggle(cuisine)}
              />
              {cuisine}
            </label>
          ))}
        </div>

        {/* Categories Section */}
        <h3>Categories</h3>
        <div className="categories-grid">
          {categoriesList.map((category) => (
            <label key={category} className="category-checkbox">
              <input
                type="checkbox"
                checked={selectedCategories[category] || false}
                onChange={() => handleCategoryToggle(category)}
              />
              {category}
            </label>
          ))}
        </div>

        <button className="apply-filters-btn" onClick={handleApplyFilters}>
          Apply Filters
        </button>
      </div>
    </div>
  );
}

export default Modal;
