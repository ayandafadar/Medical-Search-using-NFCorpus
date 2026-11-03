const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const API_V1_PREFIX = '/api/v1';

async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (typeof errorData.detail === 'object') {
          errorMessage = JSON.stringify(errorData.detail);
        }
      }
    } catch (e) {
      // Ignore JSON parse error on non-JSON response
    }
    throw new Error(errorMessage);
  }
  return await response.json();
}

export async function fetchHealth(signal) {
  const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/health`, { signal });
  return await handleResponse(response);
}

export async function fetchModels(signal) {
  const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/models`, { signal });
  return await handleResponse(response);
}

export async function executeSearch(payload, signal) {
  const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
    signal,
  });
  return await handleResponse(response);
}

export async function fetchEvaluationResults(split = 'test', signal) {
  const response = await fetch(`${API_BASE_URL}${API_V1_PREFIX}/evaluation/results?split=${split}`, { signal });
  return await handleResponse(response);
}
