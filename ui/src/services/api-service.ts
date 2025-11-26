// ui/src/services/api-service.ts
import {
  FuelEntryDB,
  FuelEntryInput,
  EntryListResponse,
  DetailedStats,
} from '../types/fuel-entry'; // make sure the filename matches exactly

const BASE_URL = 'http://localhost:8000';

// CHANGE: keep controllers per endpoint to cancel overlapping requests
let entriesController: AbortController | null = null;   // CHANGE: new
let statsController: AbortController | null = null;     // CHANGE: new

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: 'Unknown API error' }));
    throw new Error(errorBody.detail || response.statusText);
  }
  return response.json() as Promise<T>;
};

export const createEntry = async (entry: FuelEntryInput): Promise<FuelEntryDB> => {
  const response = await fetch(`${BASE_URL}/entries/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  });
  return handleResponse<FuelEntryDB>(response);
};

export const getEntries = async (): Promise<EntryListResponse> => {
  // CHANGE: cancel previous request if still running
  if (entriesController) entriesController.abort();      // CHANGE
  entriesController = new AbortController();             // CHANGE

  const response = await fetch(`${BASE_URL}/entries/`, {
    signal: entriesController.signal,                    // CHANGE
  });
  return handleResponse<EntryListResponse>(response);
};

export const updateEntry = async (id: number, entry: FuelEntryInput): Promise<FuelEntryDB> => {
  const response = await fetch(`${BASE_URL}/entries/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  });
  return handleResponse<FuelEntryDB>(response);
};

export const deleteEntry = async (id: number): Promise<void> => {
  const response = await fetch(`${BASE_URL}/entries/${id}`, { method: 'DELETE' });
  if (!response.ok) {
    throw new Error(`Failed to delete entry ${id}. Status: ${response.status}`);
  }
};

export const getDetailedStats = async (): Promise<DetailedStats> => {
  // CHANGE: cancel previous stats request if still running
  if (statsController) statsController.abort();          // CHANGE
  statsController = new AbortController();               // CHANGE

  const response = await fetch(`${BASE_URL}/stats/`, {
    signal: statsController.signal,                      // CHANGE
  });
  return handleResponse<DetailedStats>(response);
};

// api-service.ts
export async function purgeEntries(): Promise<void> {
  const res = await fetch(`${BASE_URL}/entries/`, { method: 'DELETE' }); // use BASE_URL
  if (!res.ok) throw new Error('Failed to purge entries');
}

export async function exportEntriesCsv(): Promise<string> {
  const res = await fetch(`${BASE_URL}/entries/export`, { method: 'GET' }); // use BASE_URL
  if (!res.ok) throw new Error('Failed to export CSV');
  return await res.text();
}

