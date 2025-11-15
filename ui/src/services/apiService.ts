// ui/src/services/apiService.ts

import { 
  FuelEntryDB, 
  FuelEntryInput, 
  EntryListResponse, 
  DetailedStats 
} from '../types/fuelEntry';

// BASE_URL should match your FastAPI server's host and port
// Assumes FastAPI is running on default port 8000
const BASE_URL = 'http://localhost:8000'; 

// --- CRUD Operations ---

// CREATE: POST /entries/
export async function createEntry(entry: FuelEntryInput): Promise<FuelEntryDB> {
  const response = await fetch(`${BASE_URL}/entries/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: 'Unknown API error' }));
    throw new Error(`Failed to create entry: ${errorBody.detail || response.statusText}`);
  }

  // API returns the full FuelEntryDB object with 'id' and calculated fields
  return response.json();
}

// READ ALL: GET /entries/
// Returns the EntryListResponse which contains the array of entries and overall stats
export async function getEntries(): Promise<EntryListResponse> {
  const response = await fetch(`${BASE_URL}/entries/`);

  if (!response.ok) {
    throw new Error(`Failed to fetch entries. Status: ${response.status}`);
  }

  return response.json();
}

// READ SINGLE: GET /entries/{entry_id}
export async function getEntryById(id: number): Promise<FuelEntryDB> {
  const response = await fetch(`${BASE_URL}/entries/${id}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch entry ID ${id}. Status: ${response.status}`);
  }

  return response.json();
}

// UPDATE: PUT /entries/{entry_id}
export async function updateEntry(id: number, entry: FuelEntryInput): Promise<FuelEntryDB> {
  const response = await fetch(`${BASE_URL}/entries/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entry),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: 'Unknown API error' }));
    throw new Error(`Failed to update entry ${id}: ${errorBody.detail || response.statusText}`);
  }

  return response.json();
}

// DELETE: DELETE /entries/{entry_id} (Expected 204 No Content response)
export async function deleteEntry(id: number): Promise<void> {
  const response = await fetch(`${BASE_URL}/entries/${id}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`Failed to delete entry ${id}. Status: ${response.status}`);
  }
}

// --- Stats Operation ---

// READ DETAILED STATS: GET /stats/
export async function getDetailedStats(): Promise<DetailedStats> {
  const response = await fetch(`${BASE_URL}/stats/`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch detailed statistics. Status: ${response.status}`);
  }

  return response.json();
}