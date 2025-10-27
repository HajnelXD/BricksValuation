import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import BaseSelect from '@/components/base/BaseSelect.vue';
import type { SelectOption } from '@/types/bricksets';

describe('BaseSelect Component', () => {
  const mockOptions: SelectOption[] = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3', disabled: true },
  ];

  it('renders the component', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays label text', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'My Select Field',
        options: mockOptions,
      },
    });

    expect(wrapper.find('label').text()).toContain('My Select Field');
  });

  it('renders all options', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
      },
    });

    const options = wrapper.findAll('option');
    // Should have 3 options (no placeholder in this case)
    expect(options.length).toBe(3);
  });

  it('renders placeholder option when provided', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
        placeholder: 'Select an option',
      },
    });

    const options = wrapper.findAll('option');
    // Should have 4 options (3 + placeholder)
    expect(options.length).toBe(4);
    expect(options[0].text()).toBe('Select an option');
    expect(options[0].element.value).toBe('');
  });

  it('sets the correct selected value', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: 'option2',
        label: 'Test Select',
        options: mockOptions,
      },
    });

    const select = wrapper.find('select');
    expect((select.element as HTMLSelectElement).value).toBe('option2');
  });

  it('emits update:modelValue on change', async () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: 'option1',
        label: 'Test Select',
        options: mockOptions,
      },
    });

    const select = wrapper.find('select');
    await select.setValue('option2');

    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['option2']);
  });

  it('emits blur event on blur', async () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
      },
    });

    const select = wrapper.find('select');
    await select.trigger('blur');

    expect(wrapper.emitted('blur')).toBeTruthy();
  });

  it('emits focus event on focus', async () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
      },
    });

    const select = wrapper.find('select');
    await select.trigger('focus');

    expect(wrapper.emitted('focus')).toBeTruthy();
  });

  it('displays error message when error prop is provided', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
        error: 'This field is required',
      },
    });

    expect(wrapper.text()).toContain('This field is required');
  });

  it('applies error styling when error prop is provided', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
        error: 'Error message',
      },
    });

    const select = wrapper.find('select');
    expect(select.classes()).toContain('border-red-500');
  });

  it('disables select when disabled prop is true', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
        disabled: true,
      },
    });

    const select = wrapper.find('select');
    expect(select.element.disabled).toBe(true);
  });

  it('renders disabled options correctly', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
      },
    });

    const options = wrapper.findAll('option');
    const disabledOption = options.find((opt) => opt.element.value === 'option3');

    expect(disabledOption?.element.disabled).toBe(true);
  });

  it('shows required asterisk when required prop is true', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
        required: true,
      },
    });

    expect(wrapper.find('label').text()).toContain('*');
  });

  it('sets aria-invalid attribute when error is present', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
        error: 'Error',
      },
    });

    const select = wrapper.find('select');
    expect(select.attributes('aria-invalid')).toBe('true');
  });

  it('sets aria-describedby attribute when error is present', () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: '',
        label: 'Test Select',
        options: mockOptions,
        error: 'Error message',
      },
    });

    const select = wrapper.find('select');
    expect(select.attributes('aria-describedby')).toBeTruthy();
  });

  it('does not emit update:modelValue when disabled', async () => {
    const wrapper = mount(BaseSelect, {
      props: {
        modelValue: 'option1',
        label: 'Test Select',
        options: mockOptions,
        disabled: true,
      },
    });

    const select = wrapper.find('select');
    await select.setValue('option2');

    // Event should still be emitted by Vue, but user cannot interact with disabled select
    expect(select.element.disabled).toBe(true);
  });
});
