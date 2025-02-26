import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './HomePage';
import ResultsPage from './ResultsPage';
import './App.css';
import { FilterProvider } from './FilterContext';

function App() {
  return (
    <FilterProvider> {/* Wrap your entire app or the relevant part of your app */}
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<ResultsPage />} />
        </Routes>
      </Router>
    </FilterProvider>
  );
}

export default App;
