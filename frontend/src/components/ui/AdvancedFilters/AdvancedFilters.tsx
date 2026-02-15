import { useState, useRef, useEffect } from 'react';
import '../../../styles/shared/ListPage.css';

interface AdvancedFiltersProps {
  yearRangeLabel: string;
  yearRange: [number, number];
  onYearRangeChange: (range: [number, number]) => void;
  selectedInstrumentation: string;
  onInstrumentationChange: (value: string) => void;
  instrumentations: string[];
  selectedCountry: string;
  onCountryChange: (value: string) => void;
  countries: string[];
  onClearFilters: () => void;
}

export default function AdvancedFilters({
  yearRangeLabel,
  yearRange,
  onYearRangeChange,
  selectedInstrumentation,
  onInstrumentationChange,
  instrumentations,
  selectedCountry,
  onCountryChange,
  countries,
  onClearFilters,
}: AdvancedFiltersProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [showInstrumentationDropdown, setShowInstrumentationDropdown] = useState(false);
  const [showCountryDropdown, setShowCountryDropdown] = useState(false);
  const instrumentationRef = useRef<HTMLDivElement>(null);
  const countryRef = useRef<HTMLDivElement>(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (instrumentationRef.current && !instrumentationRef.current.contains(event.target as Node)) {
        setShowInstrumentationDropdown(false);
      }
      if (countryRef.current && !countryRef.current.contains(event.target as Node)) {
        setShowCountryDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <>
      {/* Advanced Filters Toggle */}
      <div className="advanced-filters-toggle">
        <button
          className="toggle-button"
          onClick={() => setShowFilters(!showFilters)}
        >
          {showFilters ? '▲' : '▼'} Advanced Filters
        </button>
      </div>

      {/* Advanced Filters Panel */}
      {showFilters && (
        <div className="advanced-filters-panel">
          {/* Year Range Slider */}
          <div className="filter-group">
            <label className="filter-label">
              {yearRangeLabel}: {yearRange[0]} - {yearRange[1]}
            </label>
            <div className="slider-container">
              <input
                type="range"
                className="range-slider"
                min="1400"
                max="2025"
                value={yearRange[0]}
                onChange={(e) => {
                  const val = parseInt(e.target.value);
                  onYearRangeChange([Math.min(val, yearRange[1]), yearRange[1]]);
                }}
              />
              <input
                type="range"
                className="range-slider"
                min="1400"
                max="2025"
                value={yearRange[1]}
                onChange={(e) => {
                  const val = parseInt(e.target.value);
                  onYearRangeChange([yearRange[0], Math.max(val, yearRange[0])]);
                }}
              />
            </div>
          </div>

          {/* Instrumentation Dropdown */}
          <div className="filter-group" ref={instrumentationRef}>
            <label className="filter-label">Instrumentation</label>
            <div className="custom-dropdown">
              <button
                className="filter-select dropdown-button"
                onClick={() => setShowInstrumentationDropdown(!showInstrumentationDropdown)}
                type="button"
              >
                {selectedInstrumentation || 'All Instrumentations'}
                <span className="dropdown-arrow">{showInstrumentationDropdown ? '▲' : '▼'}</span>
              </button>
              {showInstrumentationDropdown && (
                <div className="dropdown-menu">
                  <div
                    className={`dropdown-option ${!selectedInstrumentation ? 'selected' : ''}`}
                    onClick={() => {
                      onInstrumentationChange('');
                      setShowInstrumentationDropdown(false);
                    }}
                  >
                    All Instrumentations
                  </div>
                  {instrumentations.map((inst) => (
                    <div
                      key={inst}
                      className={`dropdown-option ${selectedInstrumentation === inst ? 'selected' : ''}`}
                      onClick={() => {
                        onInstrumentationChange(inst);
                        setShowInstrumentationDropdown(false);
                      }}
                    >
                      {inst}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Country Dropdown */}
          <div className="filter-group" ref={countryRef}>
            <label className="filter-label">
              {yearRangeLabel.includes('Birth') ? 'Country' : 'Composer Country'}
            </label>
            <div className="custom-dropdown">
              <button
                className="filter-select dropdown-button"
                onClick={() => setShowCountryDropdown(!showCountryDropdown)}
                type="button"
              >
                {selectedCountry || 'All Countries'}
                <span className="dropdown-arrow">{showCountryDropdown ? '▲' : '▼'}</span>
              </button>
              {showCountryDropdown && (
                <div className="dropdown-menu">
                  <div
                    className={`dropdown-option ${!selectedCountry ? 'selected' : ''}`}
                    onClick={() => {
                      onCountryChange('');
                      setShowCountryDropdown(false);
                    }}
                  >
                    All Countries
                  </div>
                  {countries.map((country) => (
                    <div
                      key={country}
                      className={`dropdown-option ${selectedCountry === country ? 'selected' : ''}`}
                      onClick={() => {
                        onCountryChange(country);
                        setShowCountryDropdown(false);
                      }}
                    >
                      {country}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Clear Filters Button */}
          <button className="clear-filters-button" onClick={onClearFilters}>
            Clear Filters
          </button>
        </div>
      )}
    </>
  );
}
