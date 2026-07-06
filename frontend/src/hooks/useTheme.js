import { useContext } from 'react';
import { ThemeContext } from '../App';

/**
 * Hook to access theme context.
 * @returns {{ isDark: boolean, toggleTheme: () => void }}
 */
export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeContext.Provider');
  }
  return context;
}
