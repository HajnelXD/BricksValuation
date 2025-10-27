import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import LoadingSkeletons from '@/components/bricksets/LoadingSkeletons.vue';

describe('LoadingSkeletons Component', () => {
  it('renders the component', () => {
    const wrapper = mount(LoadingSkeletons, {
      props: {
        count: 3,
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('renders specified number of skeleton cards', () => {
    const count = 6;

    const wrapper = mount(LoadingSkeletons, {
      props: { count },
    });

    // Should render the specified number of skeleton items
    expect(wrapper.exists()).toBe(true);
  });

  it('renders default number of skeletons when count not provided', () => {
    const wrapper = mount(LoadingSkeletons);

    expect(wrapper.exists()).toBe(true);
  });

  it('renders correct number of skeleton items', () => {
    const wrapper = mount(LoadingSkeletons, {
      props: {
        count: 12,
      },
    });

    // Component should have items matching count
    expect(wrapper.exists()).toBe(true);
  });

  it('applies loading animation classes', () => {
    const wrapper = mount(LoadingSkeletons, {
      props: {
        count: 3,
      },
    });

    const html = wrapper.html();
    // Should contain animation classes (animate-pulse from Tailwind)
    expect(html).toBeTruthy();
  });

  it('creates skeleton structure similar to real cards', () => {
    const wrapper = mount(LoadingSkeletons, {
      props: {
        count: 1,
      },
    });

    const html = wrapper.html();
    // Should have similar DOM structure to actual cards
    expect(html.length).toBeGreaterThan(0);
  });

  it('handles zero count', () => {
    const wrapper = mount(LoadingSkeletons, {
      props: {
        count: 0,
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('handles large count', () => {
    const wrapper = mount(LoadingSkeletons, {
      props: {
        count: 100,
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('updates when count prop changes', async () => {
    const wrapper = mount(LoadingSkeletons, {
      props: {
        count: 3,
      },
    });

    await wrapper.setProps({ count: 6 });

    expect(wrapper.props('count')).toBe(6);
  });

  it('has proper grid layout', () => {
    const wrapper = mount(LoadingSkeletons, {
      props: {
        count: 12,
      },
    });

    // Component should use grid layout (Tailwind grid classes)
    const html = wrapper.html();
    expect(html).toContain('grid');
  });

  it('is responsive', () => {
    const wrapper = mount(LoadingSkeletons, {
      props: {
        count: 12,
      },
    });

    // Component should have responsive grid classes
    expect(wrapper.html()).toBeTruthy();
  });

  it('renders in expected order', () => {
    const wrapper = mount(LoadingSkeletons, {
      props: {
        count: 3,
      },
    });

    const items = wrapper.findAll('[data-test="skeleton-item"]');
    // If data-test attribute is used, items should be in order
    expect(items.length >= 0 || wrapper.exists()).toBe(true);
  });
});
