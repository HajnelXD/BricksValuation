/**
 * Tests for PaginationControls Component
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import PaginationControls from '@/components/valuations/PaginationControls.vue';

describe('PaginationControls Component', () => {
  it('should display current page and total pages', () => {
    const wrapper = mount(PaginationControls, {
      props: {
        currentPage: 2,
        totalPages: 5,
        totalCount: 100,
        isLoading: false,
        hasNextPage: true,
        hasPreviousPage: true,
      },
    });

    expect(wrapper.text()).toContain('Strona 2 z 5');
    expect(wrapper.text()).toContain('100 wycen');
  });

  it('should display total count', () => {
    const wrapper = mount(PaginationControls, {
      props: {
        currentPage: 1,
        totalPages: 1,
        totalCount: 25,
        isLoading: false,
        hasNextPage: false,
        hasPreviousPage: false,
      },
    });

    expect(wrapper.text()).toContain('25 wycen');
  });

  it('should disable previous button on first page', () => {
    const wrapper = mount(PaginationControls, {
      props: {
        currentPage: 1,
        totalPages: 5,
        totalCount: 100,
        isLoading: false,
        hasNextPage: true,
        hasPreviousPage: false,
      },
    });

    const buttons = wrapper.findAll('button');
    const previousButton = buttons[0];
    expect(previousButton.attributes('disabled')).toBeDefined();
  });

  it('should disable next button on last page', () => {
    const wrapper = mount(PaginationControls, {
      props: {
        currentPage: 5,
        totalPages: 5,
        totalCount: 100,
        isLoading: false,
        hasNextPage: false,
        hasPreviousPage: true,
      },
    });

    const buttons = wrapper.findAll('button');
    const nextButton = buttons[1];
    expect(nextButton.attributes('disabled')).toBeDefined();
  });

  it('should disable both buttons on single page', () => {
    const wrapper = mount(PaginationControls, {
      props: {
        currentPage: 1,
        totalPages: 1,
        totalCount: 10,
        isLoading: false,
        hasNextPage: false,
        hasPreviousPage: false,
      },
    });

    const buttons = wrapper.findAll('button');
    expect(buttons[0].attributes('disabled')).toBeDefined();
    expect(buttons[1].attributes('disabled')).toBeDefined();
  });

  it('should disable buttons when loading', () => {
    const wrapper = mount(PaginationControls, {
      props: {
        currentPage: 2,
        totalPages: 5,
        totalCount: 100,
        isLoading: true,
        hasNextPage: true,
        hasPreviousPage: true,
      },
    });

    const buttons = wrapper.findAll('button');
    expect(buttons[0].attributes('disabled')).toBeDefined();
    expect(buttons[1].attributes('disabled')).toBeDefined();
  });

  it('should emit page-change event on previous button click', async () => {
    const wrapper = mount(PaginationControls, {
      props: {
        currentPage: 2,
        totalPages: 5,
        totalCount: 100,
        isLoading: false,
        hasNextPage: true,
        hasPreviousPage: true,
      },
    });

    const buttons = wrapper.findAll('button');
    await buttons[0].trigger('click');

    expect(wrapper.emitted('page-change')).toBeTruthy();
    expect(wrapper.emitted('page-change')?.[0]).toEqual([1]);
  });

  it('should emit page-change event on next button click', async () => {
    const wrapper = mount(PaginationControls, {
      props: {
        currentPage: 2,
        totalPages: 5,
        totalCount: 100,
        isLoading: false,
        hasNextPage: true,
        hasPreviousPage: true,
      },
    });

    const buttons = wrapper.findAll('button');
    await buttons[1].trigger('click');

    expect(wrapper.emitted('page-change')).toBeTruthy();
    expect(wrapper.emitted('page-change')?.[0]).toEqual([3]);
  });

  it('should display correct button labels', () => {
    const wrapper = mount(PaginationControls, {
      props: {
        currentPage: 1,
        totalPages: 5,
        totalCount: 100,
        isLoading: false,
        hasNextPage: true,
        hasPreviousPage: false,
      },
      global: {
        mocks: {
          $t: (key: string) => {
            const translations: Record<string, string> = {
              'common.previous': 'Poprzednia',
              'common.next': 'Następna',
            };
            return translations[key] || key;
          },
        },
      },
    });

    const buttons = wrapper.findAll('button');
    expect(buttons[0].text()).toContain('Poprzednia');
    expect(buttons[1].text()).toContain('Następna');
  });

  it('should have proper button styling classes', () => {
    const wrapper = mount(PaginationControls, {
      props: {
        currentPage: 1,
        totalPages: 5,
        totalCount: 100,
        isLoading: false,
        hasNextPage: true,
        hasPreviousPage: false,
      },
    });

    const buttons = wrapper.findAll('button');
    buttons.forEach((button) => {
      expect(button.classes()).toContain('px-4');
      expect(button.classes()).toContain('py-2');
      expect(button.classes()).toContain('rounded-lg');
      expect(button.classes()).toContain('border');
    });
  });
});
