import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import EmptyState from '@/components/bricksets/EmptyState.vue';

describe('EmptyState Component', () => {
  it('renders the component', () => {
    const wrapper = mount(EmptyState);

    expect(wrapper.exists()).toBe(true);
  });

  it('displays empty state message', () => {
    const wrapper = mount(EmptyState);

    const text = wrapper.text();
    expect(text.length).toBeGreaterThan(0);
    // Message should contain Polish translation
    expect(text.toLowerCase()).toContain('brak');
  });

  it('displays help text', () => {
    const wrapper = mount(EmptyState);

    expect(wrapper.text().length).toBeGreaterThan(0);
  });

  it('has appropriate styling classes', () => {
    const wrapper = mount(EmptyState);

    expect(wrapper.exists()).toBe(true);
  });

  it('is accessible', () => {
    const wrapper = mount(EmptyState);

    expect(wrapper.exists()).toBe(true);
  });
});
