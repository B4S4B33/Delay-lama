import { useState, useEffect } from 'react';

/**
 * Hook to persist state in sessionStorage with JSON serialization.
 * 
 * @param {string} key - Storage key
 * @param {*} initialValue - Default value
 * @returns {[*, (value: *) => void]} State and setter
 */
export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = sessionStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading sessionStorage key "${key}":`, error);
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      sessionStorage.setItem(key, JSON.stringify(storedValue));
    } catch (error) {
      console.warn(`Error writing sessionStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setStoredValue];
}
