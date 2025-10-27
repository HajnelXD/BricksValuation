import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import { createPinia } from 'pinia';
import { createI18n } from 'vue-i18n';
import UserMenu from '@/components/navigation/UserMenu.vue';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';

describe('UserMenu', () => {
  let wrapper: ReturnType<typeof mount>;
  let authStore: ReturnType<typeof useAuthStore>;
  let notificationStore: ReturnType<typeof useNotificationStore>;
  let router: ReturnType<typeof createRouter>;
  let pinia: ReturnType<typeof createPinia>;
  let i18n: ReturnType<typeof createI18n>;

  beforeEach(() => {
    // Setup i18n
    i18n = createI18n({
      legacy: false,
      locale: 'pl',
      messages: {
        pl: {},
      },
    });

    // Setup Pinia
    pinia = createPinia();

    // Setup Router
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/profile', name: 'profile', component: { template: '<div>Profile</div>' } },
        { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
      ],
    });

    // Mount component
    wrapper = mount(UserMenu, {
      global: {
        plugins: [pinia, router, i18n],
      },
    });

    authStore = useAuthStore();
    notificationStore = useNotificationStore();

    // Set a test user
    authStore.user = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
    };
  });

  describe('Avatar Display', () => {
    it('should display user initials in avatar', async () => {
      await wrapper.vm.$nextTick();
      // User: "testuser" - should be "T" (first letter of word, not "TU")
      // The implementation takes first letter of each word, so "testuser" = "T"
      expect(wrapper.vm.userInitials).toBe('T');
    });

    it('should handle single word username', async () => {
      authStore.user.username = 'alice';
      await wrapper.vm.$nextTick();
      expect(wrapper.vm.userInitials).toBe('A');
    });

    it('should display ? when no username', async () => {
      authStore.user = null;
      await wrapper.vm.$nextTick();
      expect(wrapper.vm.userInitials).toBe('?');
    });

    it('should render avatar button', () => {
      expect(wrapper.find('button').exists()).toBe(true);
    });
  });

  describe('Dropdown Menu', () => {
    it('should toggle menu on avatar click', async () => {
      expect(wrapper.vm.isOpen).toBe(false);

      await wrapper.find('button').trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.isOpen).toBe(true);

      await wrapper.find('button').trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.isOpen).toBe(false);
    });

    it('should display user info in menu when open', async () => {
      wrapper.vm.isOpen = true;
      await wrapper.vm.$nextTick();

      expect(wrapper.text()).toContain('testuser');
      expect(wrapper.text()).toContain('test@example.com');
    });

    it('should display profile and logout options', async () => {
      wrapper.vm.isOpen = true;
      await wrapper.vm.$nextTick();

      expect(wrapper.text()).toContain('Profil');
      expect(wrapper.text()).toContain('Wyloguj');
    });

    it('should close menu on Escape key', async () => {
      wrapper.vm.isOpen = true;
      await wrapper.vm.$nextTick();

      const event = new KeyboardEvent('keydown', { key: 'Escape' });
      wrapper.vm.handleKeyPress(event);

      expect(wrapper.vm.isOpen).toBe(false);
    });

    it('should close menu when clicking outside', async () => {
      wrapper.vm.isOpen = true;
      await wrapper.vm.$nextTick();

      const event = new MouseEvent('click');
      wrapper.vm.handleClickOutside(event);

      expect(wrapper.vm.isOpen).toBe(false);
    });
  });

  describe('Profile Navigation', () => {
    it('should navigate to profile page', async () => {
      const routerPushSpy = vi.spyOn(router, 'push');

      wrapper.vm.goToProfile();

      expect(routerPushSpy).toHaveBeenCalledWith({ name: 'profile' });
    });

    it('should close menu after profile click', async () => {
      wrapper.vm.isOpen = true;
      await wrapper.vm.$nextTick();

      wrapper.vm.goToProfile();
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.isOpen).toBe(false);
    });
  });

  describe('Logout', () => {
    it('should call authStore.logout', async () => {
      const logoutSpy = vi.spyOn(authStore, 'logout').mockResolvedValue(undefined);

      await wrapper.vm.handleLogout();

      expect(logoutSpy).toHaveBeenCalled();
    });

    it('should show success notification on logout', async () => {
      const successSpy = vi.spyOn(notificationStore, 'success');
      vi.spyOn(authStore, 'logout').mockResolvedValue(undefined);

      await wrapper.vm.handleLogout();

      expect(successSpy).toHaveBeenCalledWith('Wylogowano pomyślnie');
    });

    it('should redirect to home after logout', async () => {
      const routerPushSpy = vi.spyOn(router, 'push');
      vi.spyOn(authStore, 'logout').mockResolvedValue(undefined);

      await wrapper.vm.handleLogout();

      expect(routerPushSpy).toHaveBeenCalledWith('/');
    });

    it('should close menu after logout', async () => {
      wrapper.vm.isOpen = true;
      vi.spyOn(authStore, 'logout').mockResolvedValue(undefined);

      await wrapper.vm.handleLogout();
      await wrapper.vm.$nextTick();

      expect(wrapper.vm.isOpen).toBe(false);
    });

    it('should set isLoggingOut to true during logout', async () => {
      vi.spyOn(authStore, 'logout').mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 50))
      );

      const logoutPromise = wrapper.vm.handleLogout();
      expect(wrapper.vm.isLoggingOut).toBe(true);

      await logoutPromise;

      expect(wrapper.vm.isLoggingOut).toBe(false);
    });

    it('should show error notification on logout failure', async () => {
      const errorSpy = vi.spyOn(notificationStore, 'error');
      const logoutError = new Error('Logout failed');
      vi.spyOn(authStore, 'logout').mockRejectedValue(logoutError);

      await wrapper.vm.handleLogout();

      expect(errorSpy).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper aria labels on avatar button', async () => {
      const button = wrapper.find('button');
      expect(button.attributes('aria-label')).toContain('testuser');
    });

    it('should set aria-expanded based on menu state', async () => {
      let button = wrapper.find('button');
      expect(button.attributes('aria-expanded')).toBe('false');

      wrapper.vm.isOpen = true;
      await wrapper.vm.$nextTick();

      button = wrapper.find('button');
      expect(button.attributes('aria-expanded')).toBe('true');
    });

    it('should have role menu on dropdown', async () => {
      wrapper.vm.isOpen = true;
      await wrapper.vm.$nextTick();

      expect(wrapper.find('[role="menu"]').exists()).toBe(true);
    });
  });
});
