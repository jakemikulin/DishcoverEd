import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
import dishcoveredLogo from './assets/dishcovered-logo-green.png';
import Modal from './Modal';
import { useFilters } from './FilterContext';

const highlightText = (text: string, query: string) => {
  return text
  if (!query) return text;

  // Convert query into an array of words, escaping special regex characters
  const queryWords = query.split(/\s+/).map(word => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

  if (queryWords.length === 0) return text;

  // Create a regex to match any of the query words
  const regex = new RegExp(`(${queryWords.join("|")})`, "gi");

  // Split the text into parts and render them
  return text.split(regex).map((part, idx) =>
    regex.test(part) ? <strong key={idx}>{part}</strong> : part
  );
};

function ResultsPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('query')?.toLowerCase() || '';
  const [recipes, setRecipes] = useState([]);
  const [searchTerm, setSearchTerm] = useState(query);
  const navigate = useNavigate();
  const [searchTime, setSearchTime] = useState<number | null>(null);
  const { filters, setFilters } = useFilters();

  const defaultFilters = {
    cuisines: {},
    categories: {}
  };

  const parseStringArray = (str: string) => {
    try {
      return JSON.parse(str.replace(/'/g, '"')); // Convert to valid JSON format and parse
    } catch (error) {
      console.warn("Failed to parse string array:", str); // Debugging
      return []; // Return empty array if parsing fails
    }
  };

  useEffect(() => {
    if (!query) return;
    const fetchRecipes = async () => {
      const startTime = performance.now(); // Start time
      
      // Construct the filters to send with the request
      const filterParams = new URLSearchParams();

      if (filters.cuisines && Object.keys(filters.cuisines).length > 0) {
        filterParams.append('cuisines', JSON.stringify(filters.cuisines));
      }
      if (filters.categories && Object.keys(filters.categories).length > 0) {
        filterParams.append('categories', JSON.stringify(filters.categories));
      }
      
      // try {
      //   const response = await fetch(`http://127.0.0.1:5000/api/search?query=${encodeURIComponent(query)}`, 
      //   {
      //     method: 'GET', 
      //     headers: {'Content-Type': 'application/json'}, 
      //     mode: 'cors'},);

      try {
        const response = await fetch(`http://127.0.0.1:5000/api/search?query=${encodeURIComponent(query)}&${filterParams.toString()}`, {
          method: 'GET', 
          headers: { 'Content-Type': 'application/json' }, 
          mode: 'cors'
        });

        const data = await response.json();
        console.log(data);

        if (Array.isArray(data)) {
          // Transform API response to match frontend
          const formattedRecipes = data.map(([recipe, score]) => ({
            title: recipe.title,
            ingredients: parseStringArray(recipe.ingredients),
            instructions: parseStringArray(recipe.directions), 
            link: recipe.link, 
            cuisine: recipe.cuisine,
            tags: parseStringArray(recipe.categories || []),
          }));
          setRecipes(formattedRecipes);
        } else {
          setRecipes([]);
        }
      } catch (error) {
        console.error("Error fetching recipes:", error);
        setRecipes([]);
      }
      const endTime = performance.now(); // End time
      setSearchTime(parseFloat(((endTime - startTime) / 1000).toFixed(8)));
    };
    fetchRecipes();
  }, [query, filters]);

  const handleSearch = () => {
    if (searchTerm.trim()) {
      navigate(`/search?query=${encodeURIComponent(searchTerm)}`);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  // ----------------------- DYLAN'S CODE ---------------------------

  // Modal state and filter data
  const [isModalOpen, setIsModalOpen] = useState(false);
  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleApplyFilters = (filters: any) => {
    setFilters(filters);
    setIsModalOpen(false);
  };

// DYLAN YOU NEED TO FIX SEARCH WITH FILTERS - LIASE WITH BACKEND AND MAYBE USE THE ABOVE USEEFFECT

  // useEffect(() => {
  //   const startTime = performance.now();

  //   // Filter recipes based on search query and filters
  //   let filteredRecipes = sampleRecipes.filter(recipe =>
  //     recipe.title.toLowerCase().includes(query) || 
  //     recipe.ingredients.some(ingredient => ingredient.toLowerCase().includes(query))
  //   );

  //   // Apply additional filters to the recipe list
  //   if (selectedFilters.tags) {
  //     filteredRecipes = filteredRecipes.filter(recipe =>
  //       recipe.tags.some(tag => selectedFilters.tags.includes(tag))
  //     );
  //   }

  //   setRecipes(filteredRecipes);

  //   const endTime = performance.now();
  //   setSearchTime(parseFloat(((endTime - startTime) / 1000).toFixed(8)));
  // }, [query, selectedFilters]);


  // State to track checked ingredients
  const [checkedIngredients, setCheckedIngredients] = useState<{ [key: string]: boolean }>({});

  // Handle toggle checkbox state
  const handleCheckboxChange = (ingredient: string) => {
    setCheckedIngredients((prev) => ({
      ...prev,
      [ingredient]: !prev[ingredient],
    }));
  };

// ----------------------- PAGE FORMATTING ---------------------------

    return (
    <div className="page-container">
      <header className="header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px', height: '80px' }}>
        {/* Logo on the right*/}
        <img src={dishcoveredLogo} alt="DishcoverEd Logo" className="header-logo" />
      <h1 className="logo">
        <Link to="/" className="logo-link">
        Dishcover<span className="highlight">Ed</span>
        </Link>
        </h1>        
        <div className="search-container" style={{ width: '600px', margin: '0 auto', display: 'flex', alignItems: 'center', gap: '10px', marginTop: '20px', marginLeft: '20px' }}>
          <div style={{ position: 'relative', flex: 1, display: 'flex' }}>
            <input
              type="text"
              placeholder="Search for a recipe..."
              className="search-box"
              style={{ width: '100%', paddingRight: '40px' }}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            {searchTerm && (
              <button
                className="clear-btn"
                onClick={() => setSearchTerm('')}
                aria-label="Clear search"
              >
              ×
              </button>
            )}
          </div>
          <button className="search-btn" onClick={handleSearch} style={{ flexShrink: 0 }}>🔍</button>
          <button className="filter-btn" onClick={handleOpenModal}></button>
        </div>

      </header>
      
      <main className="results-container">
        <div className="results-info">
          <h2 className="results-text">Results for "{query}"</h2>
          {searchTime !== null && <span className="search-time">({searchTime} seconds)</span>}
          {/* Modal for filter */}
          {isModalOpen && (
        <Modal
          filters={filters || defaultFilters}  // Pass filters, default to empty filters if undefined
          onClose={handleCloseModal}
          onApplyFilters={handleApplyFilters}
        />
      )}
        </div>
        <div className="recipe-list">
          {recipes.length > 0 ? (
            recipes.map((recipe, index) => (
              <div key={index} className="recipe-card">
                <div className="recipe-header">
                    <h2>{recipe.title.replace(/\b\w/g, char => char.toUpperCase())}</h2>
                    <p className="recipe-cuisine">{recipe.cuisine.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase())}</p>
                  <div className="recipe-tags">
                    {recipe.tags.map((tag, idx) => <span key={idx} className="recipe-tag">{tag}</span>)}
                  </div>
                </div>
                <div className="recipe-body">
                  <div className="recipe-ingredients recipe-section scrollable-container">
                    <h3>Ingredients</h3>
                    <ul>
                      {recipe.ingredients.map((ingredient, idx) => (
                        <li key={idx} style={{ display: 'flex', alignItems: 'center' }}>
                          <input
                            type="checkbox"
                            checked={checkedIngredients[ingredient] || false}
                            onChange={() => handleCheckboxChange(ingredient)}
                            style={{ marginRight: '10px' }}
                          />
                          {highlightText(ingredient, query)}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="recipe-instructions recipe-section scrollable-container">
                    <h3>Instructions</h3>
                    <ol>{recipe.instructions.map((step, idx) => <li key={idx}>{step}</li>)}</ol>
                  </div>
                  <div className="recipe-link">
                    <a href={recipe.link} target="_blank" rel="noopener noreferrer">View Full Recipe</a>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p>No recipes found. Try searching for something else!</p>
          )}
        </div>
      </main>
    </div>
  );
}

export default ResultsPage;