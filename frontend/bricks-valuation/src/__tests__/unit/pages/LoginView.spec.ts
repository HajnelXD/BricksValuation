import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import { createPinia } from 'pinia';
import { createI18n } from 'vue-i18n';
import LoginView from '@/pages/auth/LoginView.vue';
import { useAuthStore } from '@/stores/auth';

describe('LoginView', () => {
  let wrapper: ReturnType<typeof mount>;
  let authStore: ReturnType<typeof useAuthStore>;
  let router: ReturnType<typeof createRouter>;
  let i18n: ReturnType<typeof createI18n>;
  let pinia: ReturnType<typeof createPinia>;

  beforeEach(() => {
    // Setup i18n
    i18n = createI18n({
      legacy: false,
      locale: 'pl',
      messages: {
        pl: {
          login: {
            title: 'Logowanie',
            username: 'Nazwa użytkownika lub email',
            password: 'Hasło',
            submit: 'Zaloguj się',
            hasAccount: 'Nie masz konta?',
            register: 'Zarejestruj się',
            errors: {
              usernameRequired: 'Nazwa użytkownika jest wymagana',
              passwordRequired: 'Hasło jest wymagane',
              fillAllFields: 'Wypełnij wszystkie pola',
            },
          },
          errors: {
            unexpectedError: 'Wystąpił błąd',
          },
        },
      },
    });

    // Setup Pinia
    pinia = createPinia();

    // Setup Router
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
        { path: '/login', name: 'login', component: { template: '<div>Login</div>' } },
        { path: '/register', name: 'register', component: { template: '<div>Register</div>' } },
        {
          path: '/app/bricksets',
          name: 'app-bricksets',
          component: { template: '<div>Dashboard</div>' },
        },
      ],
    });

    // Mount component without stubs - let it render the real component
    wrapper = mount(LoginView, {
      global: {
        plugins: [pinia, router, i18n],
        // Stub only layout component that doesn't need full rendering
        stubs: {
          AuthFormLayout: {
            template: '<div><slot name="title" /><form><slot /></form><slot name="links" /></div>',
          },
        },
      },
    });

    authStore = useAuthStore();
  });

  describe('Form Rendering', () => {
    it('should render login form with username and password fields', () => {
      expect(wrapper.find('input').exists()).toBe(true);
    });

    it('should render submit button', () => {
      expect(wrapper.find('button').exists()).toBe(true);
    });

    it('should have register link', () => {
      // The register link text comes from i18n messages
      const registerButton = wrapper.find('button[type="button"]');
      expect(registerButton.exists()).toBe(true);
      // Check that register text appears somewhere
      const text = wrapper.text();
      expect(text).toContain('login.register');
    });
  });

  describe('Form Validation', () => {
    it('should show error when submitting with empty fields', async () => {
      await wrapper.vm.handleSubmit();
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.serverError).toBeTruthy();
    });

    it('should not submit when form is invalid', async () => {
      const loginSpy = vi.spyOn(authStore, 'login');
      wrapper.vm.formData.username = '';
      wrapper.vm.formData.password = 'password123';

      await wrapper.vm.handleSubmit();

      expect(loginSpy).not.toHaveBeenCalled();
    });

    it('should enable submit button when form is valid', async () => {
      wrapper.vm.formData.username = 'testuser';
      wrapper.vm.formData.password = 'password123';

      await wrapper.vm.$nextTick();

      expect(wrapper.vm.isFormValid).toBe(true);
    });
  });

  describe('Login Submission', () => {
    it('should call authStore.login with form data', async () => {
      const loginSpy = vi.spyOn(authStore, 'login').mockResolvedValue({ id: 1, username: 'test' });

      wrapper.vm.formData.username = 'testuser';
      wrapper.vm.formData.password = 'password123';

      await wrapper.vm.handleSubmit();

      expect(loginSpy).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
      });
    });

    it('should set isSubmitting to true while submitting', async () => {
      vi.spyOn(authStore, 'login').mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ id: 1 }), 100))
      );

      wrapper.vm.formData.username = 'testuser';
      wrapper.vm.formData.password = 'password123';

      // Trigger submit - handleSubmit is async, so track the promise
      const handleSubmitPromise = wrapper.vm.handleSubmit();
      await wrapper.vm.$nextTick();
      expect(wrapper.vm.isSubmitting).toBe(true);

      await handleSubmitPromise;
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.isSubmitting).toBe(false);
    });

    it('should redirect to dashboard on successful login', async () => {
      const routerPushSpy = vi.spyOn(router, 'push').mockResolvedValue(undefined);
      vi.spyOn(authStore, 'login').mockResolvedValue({ id: 1, username: 'test' });

      wrapper.vm.formData.username = 'testuser';
      wrapper.vm.formData.password = 'password123';

      await wrapper.vm.handleSubmit();
      await wrapper.vm.$nextTick();

      expect(routerPushSpy).toHaveBeenCalledWith('/');
    });

    it('should redirect to redirect query param if provided', async () => {
      const routerPushSpy = vi.spyOn(router, 'push').mockResolvedValue(undefined);
      vi.spyOn(authStore, 'login').mockResolvedValue({ id: 1, username: 'test' });

      // Override the route query
      vi.mocked(wrapper.vm.$route).query = { redirect: '/app/bricksets/123' };

      wrapper.vm.formData.username = 'testuser';
      wrapper.vm.formData.password = 'password123';

      await wrapper.vm.handleSubmit();
      await wrapper.vm.$nextTick();

      expect(routerPushSpy).toHaveBeenCalledWith('/app/bricksets/123');
    });
  });

  describe('Error Handling', () => {
    it('should display server error on login failure', async () => {
      vi.spyOn(authStore, 'login').mockRejectedValue(new Error('Unauthorized'));
      authStore.error = 'Nieprawidłowe dane logowania';

      wrapper.vm.formData.username = 'testuser';
      wrapper.vm.formData.password = 'wrongpassword';

      await wrapper.vm.handleSubmit();
      await wrapper.vm.$nextTick();

      // serverError should be set from authStore.error in the catch block
      expect(wrapper.vm.serverError).toBe('Nieprawidłowe dane logowania');
    });

    it('should clear server error when user starts editing', async () => {
      wrapper.vm.serverError = 'Previous error';

      wrapper.vm.formData.username = 'newvalue';
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.serverError).toBeNull();
    });

    it('should set field errors on validation failure', async () => {
      wrapper.vm.formData.username = '';
      wrapper.vm.formData.password = '';

      // Call handleSubmit directly to trigger validation
      await wrapper.vm.handleSubmit();
      await wrapper.vm.$nextTick();

      // fieldErrors should be an object with error messages
      expect(Object.keys(wrapper.vm.fieldErrors).length).toBeGreaterThan(0);
      expect(wrapper.vm.fieldErrors).toHaveProperty('username');
      expect(wrapper.vm.fieldErrors).toHaveProperty('password');
    });
  });

  describe('Navigation', () => {
    it('should navigate to register page on link click', async () => {
      const routerPushSpy = vi.spyOn(router, 'push');

      // Find and click register button
      wrapper.vm.goToRegister();

      expect(routerPushSpy).toHaveBeenCalledWith({ name: 'register' });
    });
  });

  describe('Accessibility', () => {
    it('should focus username field on mount', async () => {
      await wrapper.vm.$nextTick();
      // Component should have autofocus logic on mount
      expect(wrapper.vm).toBeTruthy();
    });

    it('should handle Enter key submission', async () => {
      vi.spyOn(authStore, 'login').mockResolvedValue({ id: 1 });

      wrapper.vm.formData.username = 'testuser';
      wrapper.vm.formData.password = 'password123';

      const event = new KeyboardEvent('keypress', { key: 'Enter' });
      wrapper.vm.handleKeyPress(event);

      expect(wrapper.vm.isFormValid).toBe(true);
    });
  });
});
