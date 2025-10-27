import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ValidationErrorList from '@/components/base/ValidationErrorList.vue';

describe('ValidationErrorList Component', () => {
  it('renders the component', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error 1'],
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays single error message', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['This field is required'],
      },
    });

    expect(wrapper.text()).toContain('This field is required');
  });

  it('displays multiple error messages', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error 1', 'Error 2', 'Error 3'],
      },
    });

    expect(wrapper.text()).toContain('Error 1');
    expect(wrapper.text()).toContain('Error 2');
    expect(wrapper.text()).toContain('Error 3');
  });

  it('renders errors in a list', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error 1', 'Error 2'],
      },
    });

    const listItems = wrapper.findAll('li');
    expect(listItems.length).toBe(2);
  });

  it('does not render when errors array is empty', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: [],
      },
    });

    expect(wrapper.find('[role="alert"]').exists()).toBe(false);
  });

  it('applies error type styling by default', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error message'],
      },
    });

    const alert = wrapper.find('[role="alert"]');
    expect(alert.classes()).toContain('bg-red-50');
    expect(alert.classes()).toContain('border-red-400');
  });

  it('applies warning type styling', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Warning message'],
        type: 'warning',
      },
    });

    const alert = wrapper.find('[role="alert"]');
    expect(alert.classes()).toContain('bg-yellow-50');
    expect(alert.classes()).toContain('border-yellow-400');
  });

  it('applies info type styling', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Info message'],
        type: 'info',
      },
    });

    const alert = wrapper.find('[role="alert"]');
    expect(alert.classes()).toContain('bg-blue-50');
    expect(alert.classes()).toContain('border-blue-400');
  });

  it('displays dismiss button when isDismissible is true', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error message'],
        isDismissible: true,
      },
    });

    const dismissButton = wrapper.find('button');
    expect(dismissButton.exists()).toBe(true);
  });

  it('does not display dismiss button when isDismissible is false', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error message'],
        isDismissible: false,
      },
    });

    const dismissButton = wrapper.find('button');
    expect(dismissButton.exists()).toBe(false);
  });

  it('hides component when dismiss button is clicked', async () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error message'],
        isDismissible: true,
      },
    });

    const dismissButton = wrapper.find('button');
    await dismissButton.trigger('click');

    // Component should be hidden after dismiss
    await wrapper.vm.$nextTick();
    expect(wrapper.find('[role="alert"]').exists()).toBe(false);
  });

  it('has proper ARIA attributes', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error message'],
      },
    });

    const alert = wrapper.find('[role="alert"]');
    expect(alert.attributes('role')).toBe('alert');
    expect(alert.attributes('aria-live')).toBe('assertive');
    expect(alert.attributes('aria-atomic')).toBe('true');
  });

  it('displays error icon for error type', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error message'],
        type: 'error',
      },
    });

    expect(wrapper.text()).toContain('❌');
  });

  it('displays warning icon for warning type', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Warning message'],
        type: 'warning',
      },
    });

    expect(wrapper.text()).toContain('⚠️');
  });

  it('displays info icon for info type', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Info message'],
        type: 'info',
      },
    });

    expect(wrapper.text()).toContain('ℹ️');
  });

  it('dismiss button has proper aria-label', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error message'],
        isDismissible: true,
      },
    });

    const dismissButton = wrapper.find('button');
    expect(dismissButton.attributes('aria-label')).toBe('Zamknij powiadomienie o błędzie');
  });

  it('renders with proper styling for dark mode', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error message'],
        type: 'error',
      },
    });

    const alert = wrapper.find('[role="alert"]');
    // Check that dark mode classes are present
    expect(alert.classes()).toContain('dark:bg-red-900/20');
  });

  it('each error has a bullet point', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['Error 1', 'Error 2'],
      },
    });

    const bullets = wrapper.findAll('.rounded-full');
    expect(bullets.length).toBe(2);
  });

  it('handles empty string in errors array', () => {
    const wrapper = mount(ValidationErrorList, {
      props: {
        errors: ['', 'Valid error'],
      },
    });

    const listItems = wrapper.findAll('li');
    expect(listItems.length).toBe(2);
  });
});
