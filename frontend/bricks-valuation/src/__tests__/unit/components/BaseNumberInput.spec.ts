import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import BaseNumberInput from '@/components/base/BaseNumberInput.vue';

describe('BaseNumberInput Component', () => {
  it('renders the component', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays label text', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Valuation Value',
      },
    });

    expect(wrapper.find('label').text()).toContain('Valuation Value');
  });

  it('displays required indicator when required prop is true', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test',
        required: true,
      },
    });

    const requiredSpan = wrapper.find('span[aria-label="required"]');
    expect(requiredSpan.exists()).toBe(true);
    expect(requiredSpan.text()).toBe('*');
  });

  it('does not display required indicator when required prop is false', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test',
        required: false,
      },
    });

    const requiredSpan = wrapper.find('span[aria-label="required"]');
    expect(requiredSpan.exists()).toBe(false);
  });

  it('renders number input field', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input[type="number"]');
    expect(input.exists()).toBe(true);
  });

  it('displays placeholder text', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        placeholder: 'Enter a value',
      },
    });

    const input = wrapper.find('input');
    expect(input.attributes('placeholder')).toBe('Enter a value');
  });

  it('displays currency code as suffix', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        currencyCode: 'PLN',
      },
    });

    expect(wrapper.text()).toContain('PLN');
  });

  it('does not display currency suffix when not provided', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const currencySpan = wrapper.find('span[aria-hidden="true"]');
    expect(currencySpan.exists()).toBe(false);
  });

  it('displays value in input when modelValue is set', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: 5000,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    expect(input.element.value).toBe('5000');
  });

  it('shows empty input when modelValue is null', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    expect(input.element.value).toBe('');
  });

  it('emits update:modelValue with number when input changes', async () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    await input.setValue('5000');

    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([5000]);
  });

  it('emits update:modelValue with null when input is cleared', async () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: 5000,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    await input.setValue('');

    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([null]);
  });

  it('emits blur event when input loses focus', async () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    await input.trigger('blur');

    expect(wrapper.emitted('blur')).toBeTruthy();
  });

  it('emits focus event when input gains focus', async () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    await input.trigger('focus');

    expect(wrapper.emitted('focus')).toBeTruthy();
  });

  it('displays error message when error prop is provided', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        error: 'This field is required',
      },
    });

    expect(wrapper.text()).toContain('This field is required');
  });

  it('does not display error message when error prop is not provided', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const errorDiv = wrapper.find('[role="alert"]');
    expect(errorDiv.exists()).toBe(false);
  });

  it('displays error icon when error is present', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        error: 'Error message',
      },
    });

    const errorDiv = wrapper.find('[role="alert"]');
    expect(errorDiv.exists()).toBe(true);
    expect(errorDiv.text()).toContain('⚠️');
  });

  it('sets aria-invalid when error is present', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        error: 'Error message',
      },
    });

    const input = wrapper.find('input');
    expect(input.attributes('aria-invalid')).toBe('true');
  });

  it('does not set aria-invalid when error is not present', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    expect(input.attributes('aria-invalid')).toBe('false');
  });

  it('sets aria-describedby when error is present', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        error: 'Error message',
      },
    });

    const input = wrapper.find('input');
    expect(input.attributes('aria-describedby')).toBeTruthy();
  });

  it('does not set aria-describedby when error is not present', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    expect(input.attributes('aria-describedby')).toBeUndefined();
  });

  it('disables input when disabled prop is true', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        disabled: true,
      },
    });

    const input = wrapper.find('input');
    expect(input.element.disabled).toBe(true);
  });

  it('enables input when disabled prop is false', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        disabled: false,
      },
    });

    const input = wrapper.find('input');
    expect(input.element.disabled).toBe(false);
  });

  it('sets min attribute on input', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        min: 1,
      },
    });

    const input = wrapper.find('input');
    expect(input.attributes('min')).toBe('1');
  });

  it('sets max attribute on input', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        max: 999999,
      },
    });

    const input = wrapper.find('input');
    expect(input.attributes('max')).toBe('999999');
  });

  it('sets step attribute on input when provided', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        step: 0.01,
      },
    });

    const input = wrapper.find('input');
    expect(input.attributes('step')).toBe('0.01');
  });

  it('sets aria-required when required prop is true', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        required: true,
      },
    });

    const input = wrapper.find('input');
    expect(input.attributes('aria-required')).toBe('true');
  });

  it('sets aria-required as false when required prop is false', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        required: false,
      },
    });

    const input = wrapper.find('input');
    expect(input.attributes('aria-required')).toBe('false');
  });

  it('applies error styling when error is present', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        error: 'Error message',
      },
    });

    const input = wrapper.find('input');
    expect(input.classes()).toContain('border-red-500');
  });

  it('applies normal styling when error is not present', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    expect(input.classes()).toContain('border-gray-300');
  });

  it('applies disabled styling when disabled', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        disabled: true,
      },
    });

    const input = wrapper.find('input');
    expect(input.classes()).toContain('opacity-60');
    expect(input.classes()).toContain('cursor-not-allowed');
  });

  it('handles decimal input correctly', async () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    await input.setValue('1500.5');

    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([1500.5]);
  });

  it('parses float value from string input', async () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    await input.setValue('123.456');

    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([123.456]);
  });

  it('updates input value when modelValue prop changes', async () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: 100,
        label: 'Test Number',
      },
    });

    let input = wrapper.find('input');
    expect(input.element.value).toBe('100');

    await wrapper.setProps({ modelValue: 500 });

    input = wrapper.find('input');
    expect(input.element.value).toBe('500');
  });

  it('applies dark mode classes', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
      },
    });

    const input = wrapper.find('input');
    expect(input.classes()).toContain('dark:bg-gray-800');
    expect(input.classes()).toContain('dark:text-white');
  });

  it('applies currency code suffix styling correctly', () => {
    const wrapper = mount(BaseNumberInput, {
      props: {
        modelValue: null,
        label: 'Test Number',
        currencyCode: 'PLN',
      },
    });

    const input = wrapper.find('input');
    expect(input.classes()).toContain('pr-14'); // Padding for currency

    const currencySpan = wrapper.find('span[aria-hidden="true"]');
    expect(currencySpan.exists()).toBe(true);
    expect(currencySpan.classes()).toContain('pointer-events-none');
  });
});
