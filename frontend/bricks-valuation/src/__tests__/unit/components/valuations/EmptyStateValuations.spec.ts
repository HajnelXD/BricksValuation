/**
 * Tests for EmptyState Component (Valuations)
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import EmptyState from '@/components/valuations/EmptyState.vue';

describe('EmptyState Component (Valuations)', () => {
  it('should render empty state message', () => {
    const wrapper = mount(EmptyState, {
      global: {
        stubs: {
          RouterLink: {
            name: 'RouterLink',
            props: ['to'],
            template: '<a :href="to"><slot /></a>',
          },
        },
      },
    });

    expect(wrapper.text()).toContain('Nie dodałeś jeszcze żadnych wycen');
  });

  it('should render description text', () => {
    const wrapper = mount(EmptyState);

    expect(wrapper.text()).toContain('Przeglądaj zestawy i dodawaj swoje wyceny');
  });

  it('should display emoji icon', () => {
    const wrapper = mount(EmptyState);

    expect(wrapper.text()).toContain('📝');
  });

  it('should have link button to bricksets', () => {
    const wrapper = mount(EmptyState);

    // Check that the link/button text is displayed
    expect(wrapper.text()).toContain('Przejdź do zestawów');
  });

  it('should display action button text', () => {
    const wrapper = mount(EmptyState);

    expect(wrapper.text()).toContain('Przejdź do zestawów');
  });

  it('should have proper styling classes', () => {
    const wrapper = mount(EmptyState);

    const container = wrapper.find('[class*="text-center"]');
    expect(container.exists()).toBe(true);
  });

  it('should have heading element', () => {
    const wrapper = mount(EmptyState);

    const heading = wrapper.find('h3');
    expect(heading.exists()).toBe(true);
    expect(heading.classes()).toContain('text-2xl');
    expect(heading.classes()).toContain('font-bold');
  });

  it('should render centered layout', () => {
    const wrapper = mount(EmptyState);

    const mainDiv = wrapper.find('.text-center');
    expect(mainDiv.exists()).toBe(true);
  });
});
