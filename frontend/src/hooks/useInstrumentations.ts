import { useState, useEffect } from 'react';
import api from '../lib/api';

/**
 * Custom hook to fetch instrumentation categories.
 * The API returns curated categories, so no additional filtering is needed.
 */
export function useInstrumentations() {
  const [instrumentations, setInstrumentations] = useState<string[]>([]);

  useEffect(() => {
    const fetchInstrumentations = async () => {
      try {
        const response = await api.get('/instrumentations/', {
          params: { page_size: 100 }
        });
        const categories = response.data.results || response.data;
        
        // Extract names from the curated API response
        const instrumentationNames = categories.map((cat: any) => cat.name);
        
        setInstrumentations(instrumentationNames);
      } catch (err) {
        console.error('Error fetching instrumentations:', err);
      }
    };
    
    fetchInstrumentations();
  }, []);

  return instrumentations;
}
