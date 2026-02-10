import { useState, useEffect } from 'react';
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
  
  const pageSize = 200;

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
  };

  useEffect(() => {
    fetchComposers();
  }, [debouncedSearch, currentPage, birthYearRange, selectedInstrumentation, selectedCountry, backendOrderField, backendOrderDirection]);

  const fetchComposers = async () => {
    // Use sortLoading for sorting operations to keep table visible
    if (sortColumn) {
      setSortLoading(true);
    } else {
      setLoading(true);
    }
    
    setError(null);
    
    try {
      // Use server-side search with database indexes (fast!)
      const params: any = {
        page: currentPage,
        page_size: pageSize,
      };
      
      // Apply backend ordering
      params.ordering = backendOrderDirection === 'asc' ? backendOrderField : `-${backendOrderField}`;
      
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
      
      // Add birth year filters if set
      if (birthYearRange[0] > 1400) {
        params.birth_year_min = birthYearRange[0];
      }
      if (birthYearRange[1] < 2025) {
        params.birth_year_max = birthYearRange[1];
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
  };

  // All sorting handled by backend for consistent UX with loading overlay

  const loadComposerWorks = async (composerId: number): Promise<ComposerWork[]> => {
    try {
      const response = await api.get(`/composers/${composerId}/works/`);
      return response.data.results || response.data;
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
        <p>Browse 15,000+ guitar composers</p>
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
  );
}
