import React, { createContext, useState, useContext, ReactNode } from 'react';

// Define a type for the filters object
interface Filters {
  cuisines: { [key: string]: boolean };
  categories: { [key: string]: boolean };
}

// Define the context type, including the filters and setFilters function
interface FilterContextType {
  filters: Filters;
  setFilters: (filters: Filters) => void;
}

// Create the context with a default value of undefined
const FilterContext = createContext<FilterContextType | undefined>(undefined);

// Define the FilterProvider component
export const FilterProvider = ({ children }: { children: ReactNode }) => {
  // Initialize the filters state with default values
  const [filters, setFilters] = useState<Filters>({
    cuisines: {},
    categories: {},
  });

  return (
    <FilterContext.Provider value={{ filters, setFilters }}>
      {children}
    </FilterContext.Provider>
  );
};

// Custom hook to access the filters context
export const useFilters = (): FilterContextType => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};
