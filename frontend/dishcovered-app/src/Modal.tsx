import { useState, useEffect } from 'react';
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

interface Filters {
  cuisines: Record<string, boolean>;
  categories: Record<string, boolean>;
}

interface ModalProps {
  filters: Filters;
  onClose: () => void;
  onApplyFilters: (filters: Filters) => void;
}

function Modal({ filters, onClose, onApplyFilters }: ModalProps) {
  const [selectedCuisines, setSelectedCuisines] = useState<Record<string, boolean>>({});
  const [selectedCategories, setSelectedCategories] = useState<Record<string, boolean>>({});

  // Initialize state with the filters passed as props
  useEffect(() => {
    setSelectedCuisines(filters.cuisines || {});
    setSelectedCategories(filters.categories || {});
  }, [filters]);

  // Handle toggle of cuisine
  const handleCuisineToggle = (cuisine: string) => {
    setSelectedCuisines(prevState => ({
      ...prevState,
      [cuisine]: !prevState[cuisine]
    }));
  };

  // Handle toggle of category
  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prevState => ({
      ...prevState,
      [category]: !prevState[category]
    }));
  };

  // Handle applying the filters
  const handleApply = () => {
    onApplyFilters({
      cuisines: selectedCuisines,
      categories: selectedCategories,
    });
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button className="close-btn" onClick={onClose}>X</button>
        <h2>Filters</h2>
        
        <button className="apply-filters-btn" onClick={handleApply}>
          Apply Filters
        </button>
        
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
      </div>
    </div>
  );
}

export default Modal;
