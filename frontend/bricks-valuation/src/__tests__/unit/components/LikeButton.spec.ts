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
        isLiked: false,
      },
    });

    expect(wrapper.text()).toContain('10');
  });

  it('displays filled heart emoji when isLiked is true', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: false,
        isLiked: true,
      },
    });

    expect(wrapper.text()).toContain('❤️');
  });

  it('displays outline heart emoji when isLiked is false', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: false,
        isLiked: false,
      },
    });

    expect(wrapper.text()).toContain('🤍');
  });

  it('emits like event when clicked and not disabled', async () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: false,
        isLiked: false,
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
        isLiked: false,
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
        isLiked: false,
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
        isLiked: false,
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
        isLiked: false,
      },
    });

    const button = wrapper.find('button');
    expect(button.classes()).toContain('bg-gray-700');
    expect(button.classes()).toContain('cursor-not-allowed');
  });

  it('applies red styles when liked and enabled', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: false,
        isLiked: true,
      },
    });

    const button = wrapper.find('button');
    expect(button.classes()).toContain('text-red-600');
    expect(button.classes()).toContain('hover:bg-red-100');
  });

  it('applies gray styles when not liked and enabled', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: false,
        isLiked: false,
      },
    });

    const button = wrapper.find('button');
    expect(button.classes()).toContain('bg-gray-200');
    expect(button.classes()).toContain('text-gray-700');
  });

  it('has correct aria-busy attribute when loading', () => {
    const wrapper = mount(LikeButton, {
      props: {
        likesCount: 5,
        disabled: false,
        loading: true,
        isLiked: false,
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
        isLiked: false,
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
        isLiked: false,
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
        isLiked: false,
      },
    });

    expect(wrapper.text()).toContain('0');
  });
});
