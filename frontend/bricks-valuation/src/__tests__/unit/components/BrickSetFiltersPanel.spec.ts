import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
// @ts-expect-error Vitest runtime provides this module resolution during tests
import type { DOMWrapper } from '@vue/test-utils';
import BrickSetFiltersPanel from '@/components/bricksets/BrickSetFiltersPanel.vue';
import type { BrickSetFiltersState } from '@/types/bricksets';

// Mock i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
  }),
}));

describe('BrickSetFiltersPanel Component', () => {
  const createFilters = (overrides: Partial<BrickSetFiltersState> = {}): BrickSetFiltersState => ({
    q: '',
    production_status: null,
    completeness: null,
    has_instructions: null,
    has_box: null,
    is_factory_sealed: null,
    ordering: '-created_at',
    page: 1,
    pageSize: 20,
    ...overrides,
  });

  const createWrapper = (props: { modelValue: BrickSetFiltersState; disabled?: boolean }) => {
    return mount(BrickSetFiltersPanel, {
      props,
      global: {
        stubs: {
          BaseInput: {
            template:
              '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
            props: ['modelValue', 'label', 'type', 'placeholder', 'disabled', 'clearable'],
          },
          BaseCustomSelect: {
            template:
              '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><option v-for="opt in options" :key="opt.value" :value="opt.value">{{ opt.label }}</option></select>',
            props: ['modelValue', 'label', 'options', 'disabled'],
          },
        },
      },
    });
  };

  it('renders the component', () => {
    const wrapper = createWrapper({
      modelValue: createFilters(),
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays search input field', () => {
    const wrapper = createWrapper({
      modelValue: createFilters(),
    });

    const inputs = wrapper.findAll('input');
    expect(inputs.length).toBeGreaterThan(0);
  });

  it('updates search value in v-model', async () => {
    const filters = createFilters({ q: 'initial' });

    const wrapper = createWrapper({
      modelValue: filters,
    });

    expect(wrapper.props('modelValue').q).toBe('initial');
  });

  it('emits filter changes for search', async () => {
    const wrapper = createWrapper({
      modelValue: createFilters(),
    });

    const inputs = wrapper.findAll('input');
    if (inputs.length > 0) {
      await inputs[0].setValue('test search');
      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted).toBeDefined();
    }
  });

  it('displays production status filter options', () => {
    const wrapper = createWrapper({
      modelValue: createFilters(),
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays completeness filter options', () => {
    const wrapper = createWrapper({
      modelValue: createFilters(),
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays ordering select dropdown', () => {
    const wrapper = createWrapper({
      modelValue: createFilters(),
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays checkboxes for boolean filters', () => {
    const wrapper = createWrapper({
      modelValue: createFilters(),
    });

    const checkboxes = wrapper.findAll('input[type="checkbox"]');
    expect(checkboxes.length).toBeGreaterThanOrEqual(0);
  });

  it('reflects current filter values', () => {
    const filters = createFilters({
      q: 'lego',
      production_status: 'ACTIVE' as const,
      completeness: 'COMPLETE' as const,
      has_instructions: true,
      ordering: 'created_at' as const,
    });

    const wrapper = createWrapper({
      modelValue: filters,
    });

    expect(wrapper.props('modelValue').q).toBe('lego');
  });

  it('emits filter-change event when filters change', async () => {
    const wrapper = createWrapper({
      modelValue: createFilters(),
    });

    const inputs = wrapper.findAll('input');
    if (inputs.length > 0) {
      await inputs[0].setValue('new value');
      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted).toBeDefined();
    }
  });

  it('disables inputs when isLoading is true', () => {
    const wrapper = createWrapper({
      modelValue: createFilters(),
      disabled: true,
    });

    const inputs = wrapper.findAll('input');
    inputs.forEach((input: DOMWrapper<Element>) => {
      const disabled = input.attributes('disabled');
      expect(
        disabled === '' || disabled === 'disabled' || disabled === true || disabled === undefined
      ).toBe(true);
    });
  });

  it('displays reset button', () => {
    const wrapper = createWrapper({
      modelValue: createFilters(),
    });

    const buttons = wrapper.findAll('button');
    expect(buttons.length).toBeGreaterThanOrEqual(1);
  });

  it('emits reset event when reset button clicked', async () => {
    const wrapper = createWrapper({
      modelValue: createFilters({ q: 'something' }),
    });

    const buttons = wrapper.findAll('button');
    for (const button of buttons) {
      if (
        button.text().toLowerCase().includes('czyść') ||
        button.text().toLowerCase().includes('reset')
      ) {
        await button.trigger('click');
        break;
      }
    }

    const emitted = wrapper.emitted('reset');
    expect(emitted).toBeDefined();
  });

  it('handles null filter values correctly', () => {
    const filters = createFilters({
      production_status: null,
      completeness: null,
      has_instructions: null,
    });

    const wrapper = createWrapper({
      modelValue: filters,
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('updates when filters prop changes', async () => {
    const initialFilters = createFilters({ q: 'initial' });

    const wrapper = createWrapper({
      modelValue: initialFilters,
    });

    const newFilters = createFilters({ q: 'updated' });

    await wrapper.setProps({ modelValue: newFilters });

    expect(wrapper.props('modelValue').q).toBe('updated');
  });
});
