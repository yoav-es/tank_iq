// ui/src/services/api-service.ts
import {
  FuelEntryDB,
  FuelEntryInput,
  EntryListResponse,
  DetailedStats,
} from '../types/fuel-entry'; // make sure the filename matches exactly

const BASE_URL = 'http://localhost:8000';

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
  const response = await fetch(`${BASE_URL}/entries/`);
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
  const response = await fetch(`${BASE_URL}/stats/`);
  return handleResponse<DetailedStats>(response);
};