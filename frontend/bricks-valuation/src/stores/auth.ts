/**
 * Auth Store
 * Manages authentication state and API calls for auth operations
 * Uses Pinia store with setup syntax
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { RegisterRequestDTO, RegisterResponseDTO } from '@/types/auth';
import { env } from '@/config/env';

const API_BASE_URL = `${env.api.baseUrl}/${env.api.version}`;

export const useAuthStore = defineStore('auth', () => {
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Register a new user
   * @throws Error with response data if registration fails
   */
  async function register(data: RegisterRequestDTO): Promise<RegisterResponseDTO> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const responseData = (await response.json()) as RegisterResponseDTO | Record<string, unknown>;

      if (!response.ok) {
        // Create error with response data for easier handling in components
        const error = new Error('Registration failed') as Error & {
          response?: { status: number; data: unknown };
        };
        error.response = {
          status: response.status,
          data: responseData,
        };
        throw error;
      }

      return responseData as RegisterResponseDTO;
    } catch (err) {
      error.value = (err as Error).message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    isLoading,
    error,
    register,
  };
});
