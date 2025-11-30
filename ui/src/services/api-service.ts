// ui/src/services/api-service.ts
import {
  FuelEntryDB,
  FuelEntryInput,
  EntryListResponse,
  DetailedStats,
} from '../types/FuelEntry';

/**
 * Base URL for API requests.
 * Should be configured via environment variable for flexibility.
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Handle API responses consistently.
 *
 * @param response - Fetch API response object
 * @returns Parsed JSON body of type T
 * @throws Error if response is not ok
 */
const handleJsonResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: 'Unknown API error' }));
    throw new Error(errorBody.detail || response.statusText);
  }
  return response.json() as Promise<T>;
};

/**
 * Handle text responses (e.g. CSV export).
 *
 * @param response - Fetch API response object
 * @returns Response body as plain text
 * @throws Error if response is not ok
 */
const handleTextResponse = async (response: Response): Promise<string> => {
  if (!response.ok) {
    const errorBody = await response.text().catch(() => 'Unknown API error');
    throw new Error(errorBody || response.statusText);
  }
  return response.text();
};

/**
 * Create a new fuel entry.
 */
export const createEntry = async (entry: FuelEntryInput): Promise<FuelEntryDB> => {
  const response = await fetch(`${BASE_URL}/entries/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  });
  return handleJsonResponse<FuelEntryDB>(response);
};

/**
 * Fetch all fuel entries.
 * Each call uses its own AbortController to prevent overlap.
 */
export const getEntries = async (signal?: AbortSignal): Promise<EntryListResponse> => {
  const controller = new AbortController();
  const response = await fetch(`${BASE_URL}/entries/`, {
    signal: signal ?? controller.signal,
  });
  return handleJsonResponse<EntryListResponse>(response);
};

/**
 * Update an existing fuel entry.
 */
export const updateEntry = async (id: number, entry: FuelEntryInput): Promise<FuelEntryDB> => {
  const response = await fetch(`${BASE_URL}/entries/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  });
  return handleJsonResponse<FuelEntryDB>(response);
};

/**
 * Delete a fuel entry by ID.
 */
export const deleteEntry = async (id: number): Promise<void> => {
  const response = await fetch(`${BASE_URL}/entries/${id}`, { method: 'DELETE' });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: 'Unknown API error' }));
    throw new Error(errorBody.detail || `Failed to delete entry ${id}. Status: ${response.status}`);
  }
};

/**
 * Fetch detailed statistics.
 * Each call uses its own AbortController to prevent overlap.
 */
export const getDetailedStats = async (signal?: AbortSignal): Promise<DetailedStats> => {
  const controller = new AbortController();
  const response = await fetch(`${BASE_URL}/stats/`, {
    signal: signal ?? controller.signal,
  });
  return handleJsonResponse<DetailedStats>(response);
};

/**
 * Purge all fuel entries.
 */
export async function purgeEntries(): Promise<void> {
  const response = await fetch(`${BASE_URL}/entries/`, { method: 'DELETE' });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: 'Unknown API error' }));
    throw new Error(errorBody.detail || 'Failed to purge entries');
  }
}

/**
 * Export all fuel entries as CSV.
 */
export async function exportEntriesCsv(): Promise<string> {
  const response = await fetch(`${BASE_URL}/entries/export`, { method: 'GET' });
  return handleTextResponse(response);
}
