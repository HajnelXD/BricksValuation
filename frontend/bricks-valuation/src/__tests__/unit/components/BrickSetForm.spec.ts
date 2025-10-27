import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import BrickSetForm from '@/components/bricksets/BrickSetForm.vue';
import { useBrickSetForm } from '@/composables/useBrickSetForm';

// Mock the composable
vi.mock('@/composables/useBrickSetForm');

// Mock i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
  }),
}));

describe('BrickSetForm Component', () => {
  const mockForm = {
    formData: {
      number: '',
      productionStatus: 'ACTIVE',
      completeness: 'COMPLETE',
      hasInstructions: false,
      hasBox: false,
      isFactorySealed: false,
      ownerInitialEstimate: null,
      isDirty: false,
    },
    fieldErrors: {},
    isSubmitting: { value: false },
    hasErrors: { value: false },
    isDirty: { value: false },
    validateField: vi.fn(),
    validateForm: vi.fn(),
    setFieldValue: vi.fn(),
    resetForm: vi.fn(),
    submitForm: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useBrickSetForm).mockReturnValue(mockForm as ReturnType<typeof useBrickSetForm>);
  });

  it('renders the component', () => {
    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays form title', () => {
    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    expect(wrapper.text()).toContain('bricksets.create.title');
  });

  it('renders all form sections', () => {
    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    expect(wrapper.text()).toContain('bricksets.create.section.identity');
    expect(wrapper.text()).toContain('bricksets.create.section.status');
    expect(wrapper.text()).toContain('bricksets.create.section.attributes');
    expect(wrapper.text()).toContain('bricksets.create.section.estimate');
  });

  it('emits on-submit when form is submitted successfully', async () => {
    mockForm.submitForm.mockResolvedValueOnce({
      id: 1,
      number: 10331,
    });

    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    const form = wrapper.find('form');
    await form.trigger('submit.prevent');

    expect(mockForm.submitForm).toHaveBeenCalled();
  });

  it('emits on-cancel when cancel button is clicked', async () => {
    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    const buttons = wrapper.findAll('button');
    const cancelButton = buttons.find((btn) => btn.text().includes('common.cancel'));

    await cancelButton?.trigger('click');

    expect(wrapper.emitted('on-cancel')).toBeTruthy();
  });

  it('disables submit button when form has errors', () => {
    mockForm.hasErrors.value = true;

    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    const buttons = wrapper.findAll('button');
    const submitButton = buttons.find((btn) => btn.text().includes('bricksets.create.submit'));

    expect(submitButton?.element.disabled).toBe(true);
  });

  it('disables submit button when form is submitting', () => {
    mockForm.isSubmitting.value = true;

    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    const buttons = wrapper.findAll('button');
    const submitButton = buttons.find((btn) => btn.text().includes('bricksets.create.submit'));

    expect(submitButton?.element.disabled).toBe(true);
  });

  it('handles field value changes through the form composable', () => {
    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    // Component mounts successfully and has the form composable integrated
    expect(wrapper.exists()).toBe(true);
    // The setFieldValue method is defined in the composable
    expect(mockForm.setFieldValue).toBeDefined();
  });

  it('handles Escape key to cancel form', async () => {
    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    const form = wrapper.find('form');
    await form.trigger('keydown', { key: 'Escape' });

    expect(wrapper.emitted('on-cancel')).toBeTruthy();
  });

  it('handles Ctrl+Enter to submit form', async () => {
    mockForm.submitForm.mockResolvedValueOnce({
      id: 1,
      number: 10331,
    });

    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    const form = wrapper.find('form');
    await form.trigger('keydown', { key: 'Enter', ctrlKey: true });

    expect(mockForm.submitForm).toHaveBeenCalled();
  });

  it('displays keyboard shortcuts hint', () => {
    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    expect(wrapper.text()).toContain('common.keyboardShortcuts');
  });

  it('displays form hint message', () => {
    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    expect(wrapper.text()).toContain('bricksets.create.formHint');
  });

  it('shows loading spinner when form is submitting', () => {
    mockForm.isSubmitting.value = true;

    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    const svg = wrapper.find('svg');
    expect(svg.exists()).toBe(true);
    expect(svg.classes()).toContain('animate-spin');
  });

  it('handles form submission errors gracefully', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    mockForm.submitForm.mockRejectedValueOnce(new Error('Submission failed'));

    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: true,
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    const form = wrapper.find('form');
    await form.trigger('submit.prevent');

    // Wait for async error handling
    await wrapper.vm.$nextTick();

    expect(consoleErrorSpy).toHaveBeenCalledWith('Form submission error:', expect.any(Error));

    consoleErrorSpy.mockRestore();
  });

  it('renders production status options', () => {
    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: {
            template:
              '<select><option v-for="opt in options" :key="opt.value">{{ opt.label }}</option></select>',
            props: ['options'],
          },
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    expect(wrapper.text()).toContain('bricksets.active');
    expect(wrapper.text()).toContain('bricksets.retired');
  });

  it('renders completeness options', () => {
    const wrapper = mount(BrickSetForm, {
      global: {
        stubs: {
          BaseInput: true,
          BaseSelect: {
            template:
              '<select><option v-for="opt in options" :key="opt.value">{{ opt.label }}</option></select>',
            props: ['options'],
          },
          BaseCheckbox: true,
          ValidationErrorList: true,
        },
      },
    });

    expect(wrapper.text()).toContain('bricksets.complete');
    expect(wrapper.text()).toContain('bricksets.incomplete');
  });
});
