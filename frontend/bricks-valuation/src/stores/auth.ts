/**
 * Auth Store
 * Manages authentication state and API calls for auth operations
 * Uses Pinia store with setup syntax
 *
 * Features:
 * - User authentication state management
 * - Login/logout functionality
 * - Session validation with fetchProfile()
 * - Error handling with proper HTTP status mapping
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type {
  RegisterRequestDTO,
  RegisterResponseDTO,
  LoginRequestDTO,
  UserDTO,
} from '@/types/auth';
import { env } from '@/config/env';
import client from '@/config/axios';

const API_BASE_URL = `/v${env.api.version}/auth`;

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserDTO | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => user.value !== null);

  /**
   * Login with username/email and password
   * Sets HttpOnly JWT cookie on success
   * @throws Error with response data if login fails
   */
  async function login(credentials: LoginRequestDTO): Promise<UserDTO> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = (await client.post(`${API_BASE_URL}/login`, credentials, {
        withCredentials: true,
      })) as { data: { user: UserDTO } };

      user.value = response.data.user;
      return response.data.user;
    } catch (err: unknown) {
      // Map API errors to user-friendly messages
      const errorResponse = err as { response?: { status: number } };
      if (errorResponse.response?.status === 400) {
        error.value = 'Wypełnij wszystkie pola';
      } else if (errorResponse.response?.status === 401) {
        error.value = 'Nieprawidłowe dane logowania';
      } else if (errorResponse.response?.status && errorResponse.response.status >= 500) {
        error.value = 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie później';
      } else {
        error.value = 'Błąd logowania. Spróbuj ponownie';
      }
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Logout - invalidates session on server and clears local state
   * Handles expired sessions gracefully (ignores 401 errors)
   */
  async function logout(): Promise<void> {
    isLoading.value = true;

    try {
      await client.post(`${API_BASE_URL}/logout`, {}, { withCredentials: true });
    } catch (err: unknown) {
      // Ignore 401 (session already expired) - clear state locally anyway
      const errorResponse = err as { response?: { status: number } };
      if (errorResponse.response?.status !== 401) {
        console.error('Logout error:', err);
      }
    } finally {
      // Always clear user state
      user.value = null;
      error.value = null;
      isLoading.value = false;
    }
  }

  /**
   * Fetch current user profile - validates session and restores user state
   * Used on app initialization to check if user is still logged in
   * @returns User data if authenticated, null if not
   */
  /**
   * Fetch current user profile - validates session and restores user state
   * Used on app initialization to check if user is still logged in
   * @returns User data if authenticated, null if not
   */
  async function fetchProfile(): Promise<UserDTO | null> {
    isLoading.value = true;

    try {
      const response = (await client.get(`${API_BASE_URL}/me`, {
        withCredentials: true,
      })) as { data: UserDTO };
      user.value = response.data;
      error.value = null;
      return response.data;
    } catch (err: unknown) {
      const errorResponse = err as { response?: { status: number } };
      if (errorResponse.response?.status === 401) {
        user.value = null;
      }
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Register a new user
   * @throws Error with response data if registration fails
   */
  async function register(data: RegisterRequestDTO): Promise<RegisterResponseDTO> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = (await client.post(`${API_BASE_URL}/register`, data, {
        withCredentials: true,
      })) as { data: RegisterResponseDTO };

      return response.data;
    } catch (err) {
      error.value = (err as Error).message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    fetchProfile,
    register,
  };
});
