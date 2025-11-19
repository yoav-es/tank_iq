// ui/src/services/apiService.ts

import {
  FuelEntryDB,
  FuelEntryInput,
  EntryListResponse,
  DetailedStats,
} from '../types/fuel-entry.js';

const BASE_URL = 'http://localhost:8000';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: 'Unknown API error' }));
    throw new Error(errorBody.detail || response.statusText);
  }
  return response.json() as Promise<T>;
}

export async function createEntry(entry: FuelEntryInput): Promise<FuelEntryDB> {
  const response = await fetch(`${BASE_URL}/entries/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  });
  return handleResponse<FuelEntryDB>(response);
}

export async function getEntries(): Promise<EntryListResponse> {
  const response = await fetch(`${BASE_URL}/entries/`);
  return handleResponse<EntryListResponse>(response);
}

export async function getEntryById(id: number): Promise<FuelEntryDB> {
  const response = await fetch(`${BASE_URL}/entries/${id}`);
  return handleResponse<FuelEntryDB>(response);
}

export async function updateEntry(id: number, entry: FuelEntryInput): Promise<FuelEntryDB> {
  const response = await fetch(`${BASE_URL}/entries/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  });
  return handleResponse<FuelEntryDB>(response);
}

export async function deleteEntry(id: number): Promise<void> {
  const response = await fetch(`${BASE_URL}/entries/${id}`, { method: 'DELETE' });
  if (!response.ok) {
    throw new Error(`Failed to delete entry ${id}. Status: ${response.status}`);
  }
}

export async function getDetailedStats(): Promise<DetailedStats> {
  const response = await fetch(`${BASE_URL}/stats/`);
  return handleResponse<DetailedStats>(response);
}