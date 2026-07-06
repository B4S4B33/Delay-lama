import { API_URL } from '../constants/config';

/**
 * Base fetch wrapper with error handling.
 * 
 * @param {string} endpoint - API endpoint path
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Response data
 */
export async function apiFetch(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };
  
  const response = await fetch(url, { ...defaultOptions, ...options });
  
  if (!response.ok) {
    let errorDetail;
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || `Request failed (${response.status})`;
    } catch {
      errorDetail = `Request failed (${response.status})`;
    }
    throw new Error(errorDetail);
  }
  
  return response.json();
}

/**
 * POST request helper.
 */
export function apiPost(endpoint, data) {
  return apiFetch(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * GET request helper.
 */
export function apiGet(endpoint) {
  return apiFetch(endpoint, { method: 'GET' });
}

/**
 * Upload file via multipart/form-data.
 */
export async function apiUpload(endpoint, file) {
  const url = `${API_URL}${endpoint}`;
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(url, {
    method: 'POST',
    body: formData,
    // Don't set Content-Type header - browser sets it with boundary
  });
  
  if (!response.ok) {
    let errorDetail;
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || `Upload failed (${response.status})`;
    } catch {
      errorDetail = `Upload failed (${response.status})`;
    }
    throw new Error(errorDetail);
  }
  
  return response.json();
}
