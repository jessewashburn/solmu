import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import { WorkListItem } from '../types';
import { useDebounce } from '../hooks/useDebounce';
import { useInstrumentations } from '../hooks/useInstrumentations';
import { useCountries } from '../hooks/useCountries';
import { useSort } from '../hooks/useSort';
import { useFilters } from '../hooks/useFilters';
import DataTable, { Column } from '../components/ui/DataTable';
import Pagination from '../components/ui/Pagination';
import SearchBar from '../components/ui/SearchBar';
import AdvancedFilters from '../components/ui/AdvancedFilters';
import SuggestionButton from '../components/features/SuggestionButton';
import '../styles/shared/ListPage.css';

export default function WorkListPage() {
  const [works, setWorks] = useState<WorkListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortLoading, setSortLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [backendOrderField, setBackendOrderField] = useState<string>('title_sort_key'); // Track backend ordering
  const [backendOrderDirection, setBackendOrderDirection] = useState<'asc' | 'desc'>('asc');
  const [manualSortActive, setManualSortActive] = useState(false); // Track if user explicitly sorted
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
  const debouncedYearRange = useDebounce(compositionYearRange, 300);

  const pageSize = 50;

  // Reset manual sort when search query changes to use relevance ordering
  useEffect(() => {
    if (debouncedSearch) {
      setManualSortActive(false);
    }
  }, [debouncedSearch]);

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
    setManualSortActive(true); // User explicitly sorted
    
    // Reset to first page when sorting
    setCurrentPage(1);
  };

  const columns: Column<WorkListItem>[] = [
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
        <>
          <Link to={`/works/${work.id}`} state={{ from: 'works' }} className="link-primary">
            {work.title}
          </Link>
          {' '}
          <SuggestionButton itemType="work" itemData={work} />
        </>
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
      const params: Record<string, string | number> = {
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

      // Add composer birth year filters if either end has been adjusted
      if (debouncedYearRange[0] !== 1400 || debouncedYearRange[1] !== 2025) {
        params.composer_birth_year_min = debouncedYearRange[0];
        params.composer_birth_year_max = debouncedYearRange[1];
      }

      // Apply backend ordering - allow manual sorting to override search relevance
      if (debouncedSearch && !manualSortActive) {
        // When searching without manual sort, use relevance (no ordering parameter)
      } else {
        // When browsing OR when user manually sorted during search, use column ordering
        params.ordering = backendOrderDirection === 'asc' ? backendOrderField : `-${backendOrderField}`;
      }

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
  }, [currentPage, pageSize, debouncedSearch, selectedInstrumentation, selectedCountry, debouncedYearRange, backendOrderField, backendOrderDirection, manualSortActive, sortColumn, loading]);

  useEffect(() => {
    fetchWorks();
  }, [fetchWorks]);

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="list-page">
      <header className="page-header">
        <h1>Works</h1>
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
        yearRangeLabel="Composer Dates Range"
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
      <div className="content-area">
        {error && (
          <div className="error-state">
            <p>{error}</p>
            <button className="btn btn-primary" onClick={fetchWorks}>
              Retry
            </button>
          </div>
        )}

        {/* Works Table */}
        {!error && !loading && (
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

        {/* Loading State */}
        {loading && (
          <div className="loading-state">
            <p>Loading works...</p>
          </div>
        )}

      </div>
    </div>
  );
}
