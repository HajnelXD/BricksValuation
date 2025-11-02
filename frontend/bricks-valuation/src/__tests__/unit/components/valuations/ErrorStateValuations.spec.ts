/**
 * Tests for ErrorState Component (Valuations)
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ErrorState from '@/components/valuations/ErrorState.vue';

describe('ErrorState Component (Valuations)', () => {
  it('should render error message', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Błąd połączenia z serwerem',
        isLoading: false,
      },
    });

    expect(wrapper.text()).toContain('Błąd połączenia z serwerem');
  });

  it('should display error title', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Test error',
        isLoading: false,
      },
    });

    expect(wrapper.text()).toContain('Coś poszło nie tak');
  });

  it('should display warning emoji', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Test error',
        isLoading: false,
      },
    });

    expect(wrapper.text()).toContain('⚠️');
  });

  it('should emit retry event on button click', async () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Test error',
        isLoading: false,
      },
    });

    const button = wrapper.find('button');
    await button.trigger('click');

    expect(wrapper.emitted('retry')).toBeTruthy();
  });

  it('should display retry button text when not loading', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Test error',
        isLoading: false,
      },
      global: {
        mocks: {
          $t: (key: string) => {
            const translations: Record<string, string> = {
              'common.retry': 'Spróbuj ponownie',
            };
            return translations[key] || key;
          },
        },
      },
    });

    expect(wrapper.text()).toContain('Spróbuj ponownie');
  });

  it('should display loading text when loading', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Test error',
        isLoading: true,
      },
    });

    expect(wrapper.text()).toContain('Ładowanie...');
  });

  it('should disable button when loading', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Test error',
        isLoading: true,
      },
    });

    const button = wrapper.find('button');
    expect(button.attributes('disabled')).toBeDefined();
  });

  it('should enable button when not loading', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Test error',
        isLoading: false,
      },
    });

    const button = wrapper.find('button');
    expect(button.attributes('disabled')).toBeUndefined();
  });

  it('should display different error messages', () => {
    const errors = [
      'Błąd serwera. Spróbuj później.',
      'Brak połączenia z serwerem. Sprawdź internet.',
      'Żądanie przekroczyło limit czasu.',
    ];

    errors.forEach((errorMessage) => {
      const wrapper = mount(ErrorState, {
        props: {
          error: errorMessage,
          isLoading: false,
        },
      });

      expect(wrapper.text()).toContain(errorMessage);
    });
  });

  it('should have proper styling classes', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Test error',
        isLoading: false,
      },
    });

    const container = wrapper.find('.text-center');
    expect(container.exists()).toBe(true);

    const button = wrapper.find('button');
    expect(button.classes()).toContain('bg-blue-600');
    expect(button.classes()).toContain('text-white');
    expect(button.classes()).toContain('rounded-lg');
  });

  it('should have centered layout', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Test error',
        isLoading: false,
      },
    });

    const mainDiv = wrapper.find('.text-center');
    expect(mainDiv.exists()).toBe(true);
    expect(mainDiv.classes()).toContain('py-16');
  });

  it('should display heading element', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Test error',
        isLoading: false,
      },
    });

    const heading = wrapper.find('h3');
    expect(heading.exists()).toBe(true);
    expect(heading.classes()).toContain('text-2xl');
    expect(heading.classes()).toContain('font-bold');
  });
});
