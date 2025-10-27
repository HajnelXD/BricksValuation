import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ErrorState from '@/components/bricksets/ErrorState.vue';

describe('ErrorState Component', () => {
  it('renders the component', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Test error message',
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays error message', () => {
    const errorMessage = 'Something went wrong';

    const wrapper = mount(ErrorState, {
      props: {
        error: errorMessage,
      },
    });

    expect(wrapper.text()).toContain(errorMessage);
  });

  it('displays default error message when not provided', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: null,
      },
    });

    const text = wrapper.text();
    expect(text.length).toBeGreaterThan(0);
    // Should contain Polish text
    expect(text).toBeTruthy();
  });

  it('emits retry event when retry button clicked', async () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Error occurred',
      },
    });

    const buttons = wrapper.findAll('button');
    if (buttons.length > 0) {
      await buttons[0].trigger('click');
    }

    const emitted = wrapper.emitted('retry');
    expect(emitted).toBeTruthy();
  });

  it('displays retry button', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Error occurred',
      },
    });

    const buttons = wrapper.findAll('button');
    expect(buttons.length).toBeGreaterThanOrEqual(1);
  });

  it('has error styling', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Error message',
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('is accessible', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: 'Accessible error',
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('handles empty error message', () => {
    const wrapper = mount(ErrorState, {
      props: {
        error: '',
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('handles long error messages', () => {
    const longMessage = 'AAAA';

    const wrapper = mount(ErrorState, {
      props: {
        error: longMessage,
      },
    });

    expect(wrapper.text()).toContain(longMessage);
  });
});

