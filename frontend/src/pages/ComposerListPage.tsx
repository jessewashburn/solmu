import { useState, useEffect, useCallback } from 'react';
import api from '../lib/api';
import { ComposerListItem } from '../types';
import { useDebounce } from '../hooks/useDebounce';
import { useInstrumentations } from '../hooks/useInstrumentations';
import { useCountries } from '../hooks/useCountries';
import { useSort } from '../hooks/useSort';
import { useFilters } from '../hooks/useFilters';
import Pagination from '../components/ui/Pagination';
import SearchBar from '../components/ui/SearchBar';
import AdvancedFilters from '../components/ui/AdvancedFilters';
import ExpandableComposerRow from '../components/features/composers/ExpandableComposerRow';
import '../styles/shared/ListPage.css';

// Work type for composer's works list (minimal fields)
interface ComposerWork {
  id: number;
  title: string;
  instrumentation_category: {
    id: number;
    name: string;
  } | null;
}

export default function ComposerListPage() {
  const [composers, setComposers] = useState<ComposerListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortLoading, setSortLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [backendOrderField, setBackendOrderField] = useState<string>('last_name,first_name');
  const [backendOrderDirection, setBackendOrderDirection] = useState<'asc' | 'desc'>('asc');
  const { sortColumn, sortDirection, handleSort } = useSort<'name' | 'country' | 'birth_year' | 'work_count'>();
  const {
    yearRange: birthYearRange,
    setYearRange: setBirthYearRange,
    selectedInstrumentation,
    setSelectedInstrumentation,
    selectedCountry,
    setSelectedCountry,
    clearFilters,
  } = useFilters();
  const instrumentations = useInstrumentations();
  const countries = useCountries();
  const debouncedSearch = useDebounce(searchQuery, 150);
  const debouncedYearRange = useDebounce(birthYearRange, 300);

  // Cache loaded works to prevent unnecessary API calls
  const [loadedWorksCache, setLoadedWorksCache] = useState<Record<number, ComposerWork[]>>({});
  
  const pageSize = 50;

  // Unified sort handler for all columns
  const handleColumnSort = (column: 'name' | 'country' | 'birth_year' | 'work_count') => {
    handleSort(column);
    const newDirection = sortColumn === column && sortDirection === 'asc' ? 'desc' : 'asc';
    
    // Map column to backend field
    const fieldMap: Record<typeof column, string> = {
      name: 'last_name,first_name',
      country: 'country__name',
      birth_year: 'birth_year',
      work_count: 'work_count'
    };
    
    setBackendOrderField(fieldMap[column]);
    setBackendOrderDirection(newDirection);
    
    // Reset to first page when sorting
    setCurrentPage(1);
  };

  const fetchComposers = useCallback(async () => {
    // Use sortLoading for sorting operations to keep table visible
    if (sortColumn) {
      setSortLoading(true);
    } else {
      setLoading(true);
    }
    
    setError(null);
    
    try {
      // Use server-side search with database indexes (fast!)
      const params: Record<string, string | number> = {
        page: currentPage,
        page_size: pageSize,
      };
      
      // Apply backend ordering - allow manual sorting to override search relevance
      if (debouncedSearch && !sortColumn) {
        // When searching without manual sort, use relevance (no ordering parameter)
      } else {
        // When browsing OR when user manually sorted during search, use column ordering
        params.ordering = backendOrderDirection === 'asc' ? backendOrderField : `-${backendOrderField}`;
      }
      
      // Add search query if present
      if (debouncedSearch) {
        params.search = debouncedSearch;
      }
      
      // Add instrumentation filter if selected
      if (selectedInstrumentation) {
        params.instrumentation = selectedInstrumentation;
      }
      
      // Add country filter if selected
      if (selectedCountry) {
        params.country_name = selectedCountry;
      }
      
      // Add birth year filters if either end has been adjusted
      if (debouncedYearRange[0] !== 1400 || debouncedYearRange[1] !== 2025) {
        params.birth_year_min = debouncedYearRange[0];
        params.birth_year_max = debouncedYearRange[1];
      }

      const response = await api.get('/composers/', { params });
      setComposers(response.data.results || response.data);
      setTotalCount(response.data.count || response.data.length);
    } catch (err) {
      console.error('Error fetching composers:', err);
      setError('Failed to load composers. Please try again.');
    } finally {
      setLoading(false);
      setSortLoading(false);
    }
  }, [currentPage, pageSize, debouncedSearch, selectedInstrumentation, selectedCountry, debouncedYearRange, backendOrderField, backendOrderDirection, sortColumn]);

  useEffect(() => {
    fetchComposers();
  }, [fetchComposers]);

  // All sorting handled by backend for consistent UX with loading overlay

  const loadComposerWorks = async (composerId: number): Promise<ComposerWork[]> => {
    // Return cached works if already loaded
    if (loadedWorksCache[composerId]) {
      return loadedWorksCache[composerId];
    }
    
    try {
      const response = await api.get(`/composers/${composerId}/works/`);
      // Handle both paginated and non-paginated responses
      const works = response.data.results || response.data;
      
      // Cache the results
      setLoadedWorksCache(prev => ({
        ...prev,
        [composerId]: works
      }));
      
      return works;
    } catch (error) {
      console.error('Error loading composer works:', error);
      return [];
    }
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="list-page">
      <header className="page-header">
        <h1>Composers</h1>
      </header>

      <SearchBar
        value={searchQuery}
        onChange={(value) => {
          setSearchQuery(value);
          setCurrentPage(1);
        }}
        placeholder="Search for composers..."
      />

      <AdvancedFilters
        yearRangeLabel="Birth Year Range"
        yearRange={birthYearRange}
        onYearRangeChange={setBirthYearRange}
        selectedInstrumentation={selectedInstrumentation}
        onInstrumentationChange={(value) => {
          setSelectedInstrumentation(value);
          setCurrentPage(1);
        }}
        instrumentations={instrumentations}
        selectedCountry={selectedCountry}
        onCountryChange={(value) => {
          setSelectedCountry(value);
          setCurrentPage(1);
        }}
        countries={countries}
        onClearFilters={clearFilters}
      />

      {/* Error State */}
      <div className="content-area">
        {error && (
          <div className="error-state">
            <p>{error}</p>
            <button className="btn btn-primary" onClick={fetchComposers}>
              Retry
            </button>
          </div>
        )}

        {/* Composers List */}
        {!error && !loading && (
        <>
          <div className="composers-table-container" style={{ position: 'relative' }}>
            {sortLoading && (
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(255, 255, 255, 0.7)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 10,
                pointerEvents: 'none'
              }}>
                <div className="spinner" style={{ width: '24px', height: '24px' }}></div>
              </div>
            )}
            <table className="composers-table">
              <thead>
                <tr>
                  <th 
                    className="sortable"
                    onClick={() => handleColumnSort('name')}
                  >
                    Name {sortColumn === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className="sortable"
                    onClick={() => handleColumnSort('country')}
                  >
                    Country {sortColumn === 'country' && (sortDirection === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className="sortable align-center years-column"
                    onClick={() => handleColumnSort('birth_year')}
                  >
                    Years {sortColumn === 'birth_year' && (sortDirection === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className="sortable align-center works-column"
                    onClick={() => handleColumnSort('work_count')}
                  >
                    Works {sortColumn === 'work_count' && (sortDirection === 'asc' ? '↑' : '↓')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {composers.map((composer) => (
                  <ExpandableComposerRow
                    key={composer.id}
                    composer={composer}
                    onLoadWorks={loadComposerWorks}
                  />
                ))}
              </tbody>
            </table>
          </div>

          {composers.length > 0 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              totalCount={totalCount}
              onPageChange={setCurrentPage}
              itemName="composers"
            />
          )}
        </>
        )}

        {/* Loading State */}
        {loading && (
          <div className="loading-state">
            <p>Loading composers...</p>
          </div>
        )}

        {/* No Results */}
        {!loading && !error && composers.length === 0 && (
          <div className="empty-state">
            <p>No composers found. Try adjusting your search.</p>
          </div>
        )}
      </div>
    </div>
  );
}
