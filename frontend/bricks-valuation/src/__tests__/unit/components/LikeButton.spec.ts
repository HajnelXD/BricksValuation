import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import LikeButton from '@/components/bricksets/LikeButton.vue';

describe('LikeButton Component', () => {
  it('renders with likes count', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 10,
        disabled: false,
        loading: false,
      },
    });

    expect(wrapper.text()).toContain('10');
  });

  it('emits like event when clicked and not disabled', async () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: false,
      },
    });

    await wrapper.find('button').trigger('click');

    expect(wrapper.emitted('like')).toBeTruthy();
    expect(wrapper.emitted('like')).toHaveLength(1);
  });

  it('does not emit like event when disabled', async () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: true,
        loading: false,
      },
    });

    await wrapper.find('button').trigger('click');

    expect(wrapper.emitted('like')).toBeFalsy();
  });

  it('does not emit like event when loading', async () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: true,
      },
    });

    await wrapper.find('button').trigger('click');

    expect(wrapper.emitted('like')).toBeFalsy();
  });

  it('shows loading spinner when loading', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: true,
      },
    });

    expect(wrapper.find('svg').exists()).toBe(true);
  });

  it('applies disabled styles when disabled', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: true,
        loading: false,
      },
    });

    const button = wrapper.find('button');
    expect(button.classes()).toContain('bg-gray-700');
    expect(button.classes()).toContain('cursor-not-allowed');
  });

  it('applies active styles when enabled', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: false,
      },
    });

    const button = wrapper.find('button');
    expect(button.classes()).toContain('bg-blue-600');
  });

  it('has correct aria-busy attribute when loading', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: true,
      },
    });

    const button = wrapper.find('button');
    expect(button.attributes('aria-busy')).toBe('true');
  });

  it('is disabled in DOM when disabled prop is true', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: true,
        loading: false,
      },
    });

    const button = wrapper.find('button');
    expect(button.element.disabled).toBe(true);
  });

  it('is disabled in DOM when loading', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: true,
      },
    });

    const button = wrapper.find('button');
    expect(button.element.disabled).toBe(true);
  });

  it('displays zero likes correctly', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 0,
        disabled: false,
        loading: false,
      },
    });

    expect(wrapper.text()).toContain('0');
  });
});
