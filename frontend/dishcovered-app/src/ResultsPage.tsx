import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
import dishcoveredLogo from './assets/dishcovered-logo-green.png';

const sampleRecipes = [
  {
    title: 'Vegan Apple Cinnamon Oatmeal',
    author: 'Freshman Latsmalane',
    ingredients: ['1 cup oats', '1 cup oat milk', '1 tsp cinnamon', '1/2 apple, chopped', '1 tbsp chopped pecans', '1 tbsp maple syrup'],
    instructions: ['Boil oat milk in a saucepan.', 'Add oats and stir for 3-5 minutes.', 'Mix in cinnamon, apples, and pecans.', 'Drizzle with maple syrup before serving.'],
    nutrition: { calories: 210, fiber: '3.4g', protein: '5g' },
    times: { prep: 5, cook: 10, total: 15 },
    tags: ['Vegan', 'Gluten Free', 'Breakfast'],
  },
  {
    title: 'Some Other Cool Oatmeal',
    author: 'FirstName LastName',
    ingredients: ['1 cup rolled oats', '1 large apple', '1/2 tsp ground cinnamon', 'Pinch of Ground Nutmeg', '1/4 cup chopped pecans'],
    instructions: ['Heat coconut oil in a medium-sized saucepan over medium heat.', 'Add in the apples and sauté for 2-3 minutes. Stir in the cinnamon and nutmeg.'],
    nutrition: { calories: 80, fiber: '1.8g', protein: '3.4g' },
    times: { prep: 5, cook: 10, total: 15 },
    tags: ['Vegan', 'Gluten Free', 'Breakfast'],
  },
  {
    title: 'Blueberry Almond Overnight Oats',
    author: 'Chef HealthyBites',
    ingredients: ['1/2 cup rolled oats', '1/2 cup almond milk', '1/4 cup fresh blueberries', '1 tbsp chia seeds', '1 tbsp honey', '1 tbsp sliced almonds'],
    instructions: ['In a jar, combine oats, almond milk, and chia seeds. Stir well.', 'Add honey and mix to combine.', 'Top with fresh blueberries and sliced almonds.', 'Cover and refrigerate overnight.', 'Stir before eating and enjoy!'],
    nutrition: { calories: 260, fiber: '6g', protein: '7g' },
    times: { prep: 5, cook: 0, total: 5 },
    tags: ['Vegetarian', 'Healthy', 'Breakfast'],
  },
  {
    title: 'Spicy Chickpea Avocado Toast',
    author: 'Foodie Fiesta',
    ingredients: ['1 slice whole-grain bread', '1/2 ripe avocado', '1/4 cup canned chickpeas', '1/2 tsp red chili flakes', '1/4 tsp garlic powder', '1 tbsp lemon juice', 'Salt & pepper to taste'],
    instructions: ['Toast the whole-grain bread until golden and crispy.', 'In a bowl, mash the avocado with lemon juice, salt, and pepper.', 'Mash chickpeas slightly and mix with garlic powder and red chili flakes.', 'Spread mashed avocado over the toast.', 'Top with spicy chickpea mixture and enjoy!'],
    nutrition: { calories: 320, fiber: '8g', protein: '9g' },
    times: { prep: 5, cook: 2, total: 7 },
    tags: ['Vegan', 'Spicy', 'Lunch'],
  }
];

function ResultsPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('query')?.toLowerCase() || '';
  const [recipes, setRecipes] = useState<typeof sampleRecipes>([]);
  const [searchTerm, setSearchTerm] = useState(query);
  const navigate = useNavigate();
  const [searchTime, setSearchTime] = useState<number | null>(null);

  useEffect(() => {
    const startTime = performance.now(); // Start time

    // Filter recipes based on search query logic here [PLACEHOLDER]
    if (query) {
      const filteredRecipes = sampleRecipes.filter(recipe =>
        recipe.title.toLowerCase().includes(query) || 
        recipe.ingredients.some(ingredient => ingredient.toLowerCase().includes(query))
      );
      setRecipes(filteredRecipes);
    }

    const endTime = performance.now(); // End time
    setSearchTime(parseFloat(((endTime - startTime) / 1000).toFixed(8)));
    
  }, [query]);

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
        </div>

      </header>
      
      <main className="results-container">
        <div className="results-info">
          <h2 className="results-text">Results for "{query}"</h2>
          {searchTime !== null && <span className="search-time">({searchTime} seconds)</span>}
        </div>
        <div className="recipe-list">
          {recipes.length > 0 ? (
            recipes.map((recipe, index) => (
              <div key={index} className="recipe-card">
                <div className="recipe-header">
                  <h2>{recipe.title}</h2>
                  <p className="recipe-author">by {recipe.author}</p>
                  <div className="recipe-tags">
                    {recipe.tags.map((tag, idx) => <span key={idx} className="recipe-tag">{tag}</span>)}
                  </div>
                </div>
                <div className="recipe-body">
                  <div className="recipe-ingredients">
                    <h3>Ingredients</h3>
                    <ul>{recipe.ingredients.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
                  </div>
                  <div className="recipe-instructions">
                    <h3>Instructions</h3>
                    <ol>{recipe.instructions.map((step, idx) => <li key={idx}>{step}</li>)}</ol>
                  </div>
                  <div className="recipe-nutrition">
                    <h3>Nutritional Information</h3>
                    <p>Calories: {recipe.nutrition.calories}</p>
                    <p>Fiber: {recipe.nutrition.fiber}</p>
                    <p>Protein: {recipe.nutrition.protein}</p>
                  </div>
                  <div className="recipe-time">
                    <h3>Time</h3>
                    <p><strong>Prep Time:</strong> {recipe.times.prep} minutes</p>
                    <p><strong>Cook Time:</strong> {recipe.times.cook} minutes</p>
                    <p><strong>Total Time:</strong> {recipe.times.total} minutes</p>
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
