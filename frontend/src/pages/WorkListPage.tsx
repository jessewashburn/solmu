import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import { useDebounce } from '../hooks/useDebounce';
import { useInstrumentations } from '../hooks/useInstrumentations';
import { useCountries } from '../hooks/useCountries';
import { useSort } from '../hooks/useSort';
import { useFilters } from '../hooks/useFilters';
import DataTable, { Column } from '../components/ui/DataTable';
import Pagination from '../components/ui/Pagination';
import SearchBar from '../components/ui/SearchBar';
import AdvancedFilters from '../components/ui/AdvancedFilters';
import '../styles/shared/ListPage.css';

interface Work {
  id: number;
  title: string;
  composer: {
    id: number;
    full_name: string;
  } | null;
  instrumentation_category: {
    id: number;
    name: string;
  } | null;
  difficulty_level: number | null;
  composition_year: number | null;
}

export default function WorkListPage() {
  const [works, setWorks] = useState<Work[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortLoading, setSortLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [backendOrderField, setBackendOrderField] = useState<string>('title_sort_key'); // Track backend ordering
  const [backendOrderDirection, setBackendOrderDirection] = useState<'asc' | 'desc'>('asc');
  const { sortColumn, sortDirection, handleSort } = useSort<'title' | 'composer' | 'instrumentation'>('title');
  const {
    yearRange: compositionYearRange,
    setYearRange: setCompositionYearRange,
    selectedInstrumentation,
    setSelectedInstrumentation,
    selectedCountry,
    setSelectedCountry,
    clearFilters,
  } = useFilters();
  const instrumentations = useInstrumentations();
  const countries = useCountries();
  const debouncedSearch = useDebounce(searchQuery, 500); // Increased from 300ms to reduce API calls
  
  const pageSize = 200;

  // All sorting handled by backend for consistent UX with loading overlay

  // Unified sort handler for all columns
  const handleColumnSort = (column: 'title' | 'composer' | 'instrumentation') => {
    handleSort(column);
    const newDirection = sortColumn === column && sortDirection === 'asc' ? 'desc' : 'asc';
    
    // Map column to backend field
    const fieldMap = {
      title: 'title_sort_key',
      composer: 'composer__full_name',
      instrumentation: 'instrumentation_category__name'
    };
    
    setBackendOrderField(fieldMap[column]);
    setBackendOrderDirection(newDirection);
  };

  const columns: Column<Work>[] = [
    {
      header: (
        <span 
          onClick={() => handleColumnSort('title')} 
          className="sort-header"
        >
          Work Title {sortColumn === 'title' && (sortDirection === 'asc' ? '↑' : '↓')}
        </span>
      ),
      accessor: (work) => (
        <Link to={`/works/${work.id}`} state={{ from: 'works' }} className="link-primary">
          {work.title}
        </Link>
      ),
    },
    {
      header: (
        <span 
          onClick={() => handleColumnSort('composer')} 
          className="sort-header"
        >
          Composer {sortColumn === 'composer' && (sortDirection === 'asc' ? '↑' : '↓')}
        </span>
      ),
      accessor: (work) =>
        work.composer ? (
          <Link to={`/composers/${work.composer.id}`} className="link-secondary">
            {work.composer.full_name}
          </Link>
        ) : (
          '-'
        ),
    },
    {
      header: (
        <span 
          onClick={() => handleColumnSort('instrumentation')} 
          className="sort-header"
        >
          Instrumentation {sortColumn === 'instrumentation' && (sortDirection === 'asc' ? '↑' : '↓')}
        </span>
      ),
      accessor: (work) => work.instrumentation_category?.name || '-',
    },
  ];

  const fetchWorks = useCallback(async () => {
    // Use sortLoading for all sorting operations to keep table visible
    // Only use main loading on initial mount or page change
    const isSortOperation = currentPage === 1 && !loading;
    
    if (isSortOperation || sortColumn) {
      setSortLoading(true);
    } else {
      setLoading(true);
    }
    
    setError(null);
    
    try {
      const params: any = {
        page: currentPage,
        page_size: pageSize,
      };

      if (debouncedSearch) {
        params.search = debouncedSearch;
      }

      // Add instrumentation filter if selected
      if (selectedInstrumentation) {
        params.instrumentation = selectedInstrumentation;
      }

      // Add country filter if selected
      if (selectedCountry) {
        params.composer_country = selectedCountry;
      }

      // Add composition year filters if set
      if (compositionYearRange[0] > 1400) {
        params.composition_year_min = compositionYearRange[0];
      }
      if (compositionYearRange[1] < 2025) {
        params.composition_year_max = compositionYearRange[1];
      }

      // Apply backend ordering for all columns with consistent loading overlay
      params.ordering = backendOrderDirection === 'asc' ? backendOrderField : `-${backendOrderField}`;

      const response = await api.get('/works/', { params });
      setWorks(response.data.results || response.data);
      setTotalCount(response.data.count || response.data.length);
    } catch (err) {
      console.error('Error fetching works:', err);
      setError('Failed to load works. Please try again.');
    } finally {
      setLoading(false);
      setSortLoading(false);
    }
  }, [currentPage, pageSize, debouncedSearch, selectedInstrumentation, selectedCountry, compositionYearRange, backendOrderField, backendOrderDirection, sortColumn, loading]);

  useEffect(() => {
    fetchWorks();
  }, [fetchWorks]);

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="list-page">
      <header className="page-header">
        <h1>Works</h1>
        <p>Browse {loading && totalCount === 0 ? '...' : (totalCount || 0).toLocaleString()} guitar works</p>
      </header>

      <SearchBar
        value={searchQuery}
        onChange={(value) => {
          setSearchQuery(value);
          setCurrentPage(1);
        }}
        placeholder="Search for works or composers..."
      />

      <AdvancedFilters
        yearRangeLabel="Composition Year Range"
        yearRange={compositionYearRange}
        onYearRangeChange={setCompositionYearRange}
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
          <button className="btn btn-primary" onClick={fetchWorks}>
            Retry
          </button>
        </div>
      )}

      {/* Works List */}
      {!error && (
        <>
          <div style={{ position: 'relative' }}>
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
            <DataTable
              data={works}
              columns={columns}
              getRowKey={(work) => work.id}
              loading={loading}
              emptyMessage="No works found. Try adjusting your search."
            />
          </div>

          {!loading && works.length > 0 && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              totalCount={totalCount}
              onPageChange={setCurrentPage}
              itemName="total works"
            />
          )}
        </>
      )}
    </div>
  );
}
