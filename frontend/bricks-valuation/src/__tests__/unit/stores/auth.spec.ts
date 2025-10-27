import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from '@/stores/auth';
import client from '@/config/axios';

// Mock axios
vi.mock('@/config/axios');

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('login', () => {
    it('should login successfully with correct credentials', async () => {
      const store = useAuthStore();
      const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (client.post as any).mockResolvedValue({
        data: { user: mockUser },
      });

      const result = await store.login({
        username: 'testuser',
        password: 'password123',
      });

      expect(result).toEqual(mockUser);
      expect(store.user).toEqual(mockUser);
      expect(store.isAuthenticated).toBe(true);
      expect(store.error).toBeNull();
    });

    it('should handle validation error (400)', async () => {
      const store = useAuthStore();
      const error = new Error('Validation error');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (error as any).response = {
        status: 400,
        data: { error_code: 'VALIDATION_ERROR' },
      };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (client.post as any).mockRejectedValue(error);

      try {
        await store.login({
          username: '',
          password: 'password123',
        });
      } catch {
        // Expected to throw
      }

      expect(store.error).toContain('Wypełnij wszystkie pola');
      expect(store.isAuthenticated).toBe(false);
    });

    it('should handle invalid credentials error (401)', async () => {
      const store = useAuthStore();
      const error = new Error('Invalid credentials');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (error as any).response = {
        status: 401,
        data: { error_code: 'INVALID_CREDENTIALS' },
      };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (client.post as any).mockRejectedValue(error);

      try {
        await store.login({
          username: 'testuser',
          password: 'wrongpassword',
        });
      } catch {
        // Expected to throw
      }

      expect(store.error).toContain('Nieprawidłowe dane logowania');
      expect(store.isAuthenticated).toBe(false);
    });

    it('should handle server error (500)', async () => {
      const store = useAuthStore();
      const error = new Error('Server error');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (error as any).response = {
        status: 500,
        data: { error_code: 'INTERNAL_ERROR' },
      };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (client.post as any).mockRejectedValue(error);

      try {
        await store.login({
          username: 'testuser',
          password: 'password123',
        });
      } catch {
        // Expected to throw
      }

      expect(store.error).toContain('nieoczekiwany błąd');
    });

    it('should set isLoading during login', async () => {
      const store = useAuthStore();
      const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (client.post as any).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ data: { user: mockUser } }), 50))
      );

      const loginPromise = store.login({
        username: 'testuser',
        password: 'password123',
      });

      expect(store.isLoading).toBe(true);

      await loginPromise;

      expect(store.isLoading).toBe(false);
    });
  });

  describe('logout', () => {
    it('should logout successfully', async () => {
      const store = useAuthStore();
      store.user = { id: 1, username: 'testuser', email: 'test@example.com' };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (client.post as any).mockResolvedValue({ status: 204 });

      await store.logout();

      expect(store.user).toBeNull();
      expect(store.isAuthenticated).toBe(false);
      expect(store.error).toBeNull();
    });

    it('should handle 401 error gracefully', async () => {
      const store = useAuthStore();
      store.user = { id: 1, username: 'testuser', email: 'test@example.com' };

      const error = new Error('Not authenticated');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (error as any).response = {
        status: 401,
        data: { error_code: 'NOT_AUTHENTICATED' },
      };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (client.post as any).mockRejectedValue(error);

      // Should not throw, should still clear user
      await store.logout();

      expect(store.user).toBeNull();
      expect(store.isAuthenticated).toBe(false);
    });

    it('should clear error on logout', async () => {
      const store = useAuthStore();
      store.error = 'Some error';
      store.user = { id: 1, username: 'testuser', email: 'test@example.com' };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (client.post as any).mockResolvedValue({ status: 204 });

      await store.logout();

      expect(store.error).toBeNull();
    });
  });

  describe('fetchProfile', () => {
    it('should fetch and restore user profile', async () => {
      const store = useAuthStore();
      const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (client.get as any).mockResolvedValue({ data: mockUser });

      const result = await store.fetchProfile();

      expect(result).toEqual(mockUser);
      expect(store.user).toEqual(mockUser);
      expect(store.error).toBeNull();
    });

    it('should handle 401 error and clear user', async () => {
      const store = useAuthStore();

      const error = new Error('Not authenticated');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (error as any).response = {
        status: 401,
      };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (client.get as any).mockRejectedValue(error);

      const result = await store.fetchProfile();

      expect(result).toBeNull();
      expect(store.user).toBeNull();
    });

    it('should set isLoading during fetch', async () => {
      const store = useAuthStore();
      const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (client.get as any).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ data: mockUser }), 50))
      );

      const fetchPromise = store.fetchProfile();

      expect(store.isLoading).toBe(true);

      await fetchPromise;

      expect(store.isLoading).toBe(false);
    });
  });

  describe('Computed Properties', () => {
    it('should compute isAuthenticated based on user state', () => {
      const store = useAuthStore();

      expect(store.isAuthenticated).toBe(false);

      store.user = { id: 1, username: 'testuser', email: 'test@example.com' };

      expect(store.isAuthenticated).toBe(true);

      store.user = null;

      expect(store.isAuthenticated).toBe(false);
    });
  });
});
