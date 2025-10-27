import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import BaseCheckbox from '@/components/base/BaseCheckbox.vue';

describe('BaseCheckbox Component', () => {
  it('renders the component', () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays label text', () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Accept Terms',
      },
    });

    expect(wrapper.find('label').text()).toContain('Accept Terms');
  });

  it('renders checkbox as unchecked by default', () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
      },
    });

    const checkbox = wrapper.find('input[type="checkbox"]');
    expect((checkbox.element as HTMLInputElement).checked).toBe(false);
  });

  it('renders checkbox as checked when modelValue is true', () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: true,
        label: 'Test Checkbox',
      },
    });

    const checkbox = wrapper.find('input[type="checkbox"]');
    expect((checkbox.element as HTMLInputElement).checked).toBe(true);
  });

  it('emits update:modelValue with true when checkbox is checked', async () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
      },
    });

    const checkbox = wrapper.find('input[type="checkbox"]');
    await checkbox.setValue(true);

    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([true]);
  });

  it('emits update:modelValue with false when checkbox is unchecked', async () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: true,
        label: 'Test Checkbox',
      },
    });

    const checkbox = wrapper.find('input[type="checkbox"]');
    await checkbox.setValue(false);

    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false]);
  });

  it('emits blur event on blur', async () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
      },
    });

    const checkbox = wrapper.find('input[type="checkbox"]');
    await checkbox.trigger('blur');

    expect(wrapper.emitted('blur')).toBeTruthy();
  });

  it('emits focus event on focus', async () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
      },
    });

    const checkbox = wrapper.find('input[type="checkbox"]');
    await checkbox.trigger('focus');

    expect(wrapper.emitted('focus')).toBeTruthy();
  });

  it('displays description when provided', () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
        description: 'This is a helpful description',
      },
    });

    expect(wrapper.text()).toContain('This is a helpful description');
  });

  it('displays hint when provided', () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
        hint: 'Additional hint text',
      },
    });

    expect(wrapper.text()).toContain('Additional hint text');
  });

  it('disables checkbox when disabled prop is true', () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
        disabled: true,
      },
    });

    const checkbox = wrapper.find('input[type="checkbox"]');
    expect(checkbox.element.disabled).toBe(true);
  });

  it('applies disabled styling when disabled', () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
        disabled: true,
      },
    });

    const checkbox = wrapper.find('input[type="checkbox"]');
    expect(checkbox.classes()).toContain('cursor-not-allowed');
  });

  it('does not display description when not provided', () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
      },
    });

    const descriptions = wrapper.findAll('p');
    expect(descriptions.length).toBe(0);
  });

  it('does not display hint when not provided', () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
      },
    });

    // Should not have hint paragraph
    const paragraphs = wrapper.findAll('p');
    const hintExists = paragraphs.some((p) => p.classes().includes('ml-7'));
    expect(hintExists).toBe(false);
  });

  it('can toggle checkbox multiple times', async () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
      },
    });

    const checkbox = wrapper.find('input[type="checkbox"]');

    // First toggle
    await checkbox.setValue(true);
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([true]);

    // Second toggle
    await checkbox.setValue(false);
    expect(wrapper.emitted('update:modelValue')?.[1]).toEqual([false]);

    // Third toggle
    await checkbox.setValue(true);
    expect(wrapper.emitted('update:modelValue')?.[2]).toEqual([true]);
  });

  it('has proper cursor pointer class when enabled', () => {
    const wrapper = mount(BaseCheckbox, {
      props: {
        modelValue: false,
        label: 'Test Checkbox',
        disabled: false,
      },
    });

    const checkbox = wrapper.find('input[type="checkbox"]');
    expect(checkbox.classes()).toContain('cursor-pointer');
  });
});
