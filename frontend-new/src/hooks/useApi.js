import { useState, useCallback } from 'react';

const API_BASE = ''; // Same origin as backend

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const request = useCallback(async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
          ...options.headers,
          // Authorization headers can be added here if session management is shared
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Internal Server Error');
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { request, loading, error };
};
