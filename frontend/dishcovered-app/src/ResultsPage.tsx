import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

const sampleRecipes = [
  {
    title: 'Vegan Apple Cinnamon Oatmeal',
    author: 'Freshman Latsmalane',
    ingredients: ['1 cup oats', '1 cup oat milk', '1 tsp cinnamon', '1/2 apple, chopped', '1 tbsp chopped pecans', '1 tbsp maple syrup'],
    instructions: ['Boil oat milk in a saucepan.', 'Add oats and stir for 3-5 minutes.', 'Mix in cinnamon, apples, and pecans.', 'Drizzle with maple syrup before serving.'],
    nutrition: { calories: 210, fiber: '3.4g', protein: '5g' },
    times: { prep: 5, cook: 10, total: 15 },
  },
];

function ResultsPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('query')?.toLowerCase() || '';
  const [recipes, setRecipes] = useState<typeof sampleRecipes>([]);

  useEffect(() => {
    console.log("Query received:", query);

    if (query) {
      // Filter recipes based on query matching title or ingredients
      const filteredRecipes = sampleRecipes.filter(recipe =>
        recipe.title.toLowerCase().includes(query) || 
        recipe.ingredients.some(ingredient => ingredient.toLowerCase().includes(query))
      );

      setRecipes(filteredRecipes);
      console.log("Filtered Recipes:", filteredRecipes);
    }
  }, [query]);

  return (
    <div className="results-container">
      <h1>Results for "{query}"</h1>
      
      {recipes.length > 0 ? (
        recipes.map((recipe, index) => (
          <div key={index} className="recipe-card">
            <h2>{recipe.title}</h2>
            <p>by {recipe.author}</p>
            <h3>Ingredients</h3>
            <ul>{recipe.ingredients.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
            <h3>Instructions</h3>
            <ol>{recipe.instructions.map((step, idx) => <li key={idx}>{step}</li>)}</ol>
            <h3>Nutritional Information</h3>
            <p>Calories: {recipe.nutrition.calories}</p>
            <p>Fiber: {recipe.nutrition.fiber}</p>
            <p>Protein: {recipe.nutrition.protein}</p>
            <h3>Time</h3>
            <p>Prep Time: {recipe.times.prep} min</p>
            <p>Cook Time: {recipe.times.cook} min</p>
            <p>Total Time: {recipe.times.total} min</p>
          </div>
        ))
      ) : (
        <p>No recipes found. Try searching for something else!</p>
      )}
    </div>
  );
}

export default ResultsPage;