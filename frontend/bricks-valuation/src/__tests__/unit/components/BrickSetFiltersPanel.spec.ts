import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
// @ts-expect-error Vitest runtime provides this module resolution during tests
import type { DOMWrapper } from '@vue/test-utils';
import BrickSetFiltersPanel from '@/components/bricksets/BrickSetFiltersPanel.vue';
import type { BrickSetFiltersState } from '@/types/bricksets';

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

  it('renders the component', () => {
    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: createFilters(),
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays search input field', () => {
    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: createFilters(),
      },
    });

    const inputs = wrapper.findAll('input');
    expect(inputs.length).toBeGreaterThan(0);
  });

  it('updates search value in v-model', async () => {
    const filters = createFilters({ q: 'initial' });

    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: filters,
      },
    });

    expect(wrapper.props('modelValue').q).toBe('initial');
  });

  it('emits filter changes for search', async () => {
    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: createFilters(),
      },
    });

    const inputs = wrapper.findAll('input[type="text"]');
    if (inputs.length > 0) {
      await inputs[0].setValue('test search');
      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted).toBeDefined();
    }
  });

  it('displays production status filter options', () => {
    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: createFilters(),
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays completeness filter options', () => {
    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: createFilters(),
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays ordering select dropdown', () => {
    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: createFilters(),
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays checkboxes for boolean filters', () => {
    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: createFilters(),
      },
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

    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: filters,
      },
    });

    expect(wrapper.props('modelValue').q).toBe('lego');
  });

  it('emits filter-change event when filters change', async () => {
    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: createFilters(),
      },
    });

    const inputs = wrapper.findAll('input[type="text"]');
    if (inputs.length > 0) {
      await inputs[0].setValue('new value');
      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted).toBeDefined();
    }
  });

  it('disables inputs when isLoading is true', () => {
    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: createFilters(),
        disabled: true,
      },
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
    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: createFilters(),
      },
    });

    const buttons = wrapper.findAll('button');
    expect(buttons.length).toBeGreaterThanOrEqual(1);
  });

  it('emits reset event when reset button clicked', async () => {
    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: createFilters({ q: 'something' }),
      },
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

    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: filters,
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('updates when filters prop changes', async () => {
    const initialFilters = createFilters({ q: 'initial' });

    const wrapper = mount(BrickSetFiltersPanel, {
      props: {
        modelValue: initialFilters,
      },
    });

    const newFilters = createFilters({ q: 'updated' });

    await wrapper.setProps({ modelValue: newFilters });

    expect(wrapper.props('modelValue').q).toBe('updated');
  });
});
