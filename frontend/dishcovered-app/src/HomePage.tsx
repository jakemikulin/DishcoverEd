import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import dishcoveredLogo from './assets/dishcovered-logo-green.png';

function HomePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

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
    <div className="App">

      <img src={dishcoveredLogo} alt="DishcoverEd Logo" className="home-logo" />


      <h1 className="logo">Dishcover<span className="highlight">Ed</span></h1>
      <div className="search-container" style={{ width: '600px', margin: '0 auto', display: 'flex', alignItems: 'center', gap: '10px', marginTop: '20px' }}>
        {/* Search box wrapper to keep clear button inside */}
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
        
        {/* Search button is fully separate */}
        <button className="search-btn" onClick={handleSearch} style={{ flexShrink: 0 }}>🔍</button>
      </div>
    </div>
  );
}

export default HomePage;