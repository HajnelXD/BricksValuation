/* eslint-disable @typescript-eslint/no-explicit-any */
import axios from 'axios';

const baseURL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000/api';
const timeout = parseInt((import.meta.env.VITE_API_TIMEOUT as string) || '30000', 10);

/**
 * Configured API client instance
 * Uses environment variables: VITE_API_URL, VITE_API_TIMEOUT
 * Note: VITE_API_URL contains base URL with /api (e.g., http://localhost:8000/api)
 * Version prefix (e.g., /v1, /v2) should be included in individual endpoint calls
 */
const client: any = axios.create({
  baseURL,
  timeout,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default client;
