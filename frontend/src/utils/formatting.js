/**
 * Formatting utilities for display values.
 */

/**
 * Format a probability (0-1) as a percentage string.
 * @param {number} prob - Probability value
 * @returns {string} Formatted percentage (e.g., "72.3%")
 */
export function formatProbability(prob) {
  return `${(prob * 100).toFixed(1)}%`;
}

/**
 * Format a decimal as a percentage.
 * @param {number} value - Decimal value
 * @returns {string} Formatted percentage
 */
export function formatPercent(value) {
  return `${(value * 100).toFixed(1)}%`;
}

/**
 * Format a large number with commas.
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export function formatNumber(num) {
  return num.toLocaleString();
}

/**
 * Format a date string to locale date format.
 * @param {string} dateStr - ISO date string
 * @returns {string} Formatted date
 */
export function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format a datetime string to locale datetime format.
 * @param {string} dateTimeStr - ISO datetime string
 * @returns {string} Formatted datetime
 */
export function formatDateTime(dateTimeStr) {
  return new Date(dateTimeStr).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Get a human-readable label for a feature name.
 * @param {string} featureName - Internal feature name
 * @returns {string} Human-readable label
 */
export function featureLabel(featureName) {
  const labels = {
    'Month': 'Month of Year',
    'DayofMonth': 'Day of Month',
    'DayOfWeek': 'Day of Week',
    'Airline': 'Airline',
    'Origin': 'Origin Airport',
    'Dest': 'Destination Airport',
    'Distance': 'Route Distance',
    'DepHour': 'Departure Hour',
    'ArrHour': 'Arrival Hour',
  };
  return labels[featureName] || featureName;
}
