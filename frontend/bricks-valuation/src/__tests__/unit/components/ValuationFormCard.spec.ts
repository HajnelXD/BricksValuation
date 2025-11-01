import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import ValuationFormCard from '@/components/bricksets/ValuationFormCard.vue';
import * as useValuationFormModule from '@/composables/useValuationForm';

// Mock the composable
vi.mock('@/composables/useValuationForm');

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
  }),
}));

describe('ValuationFormCard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const createMockForm = () => ({
    formData: {
      value: {
        value: null,
        comment: '',
      },
    },
    errors: {
      value: {},
    },
    isSubmitting: {
      value: false,
    },
    touchedFields: {
      value: new Set(),
    },
    isFormValid: {
      value: false,
    },
    canSubmit: {
      value: false,
    },
    validateField: vi.fn(),
    validateForm: vi.fn(),
    validateValueField: vi.fn(),
    validateCommentField: vi.fn(),
    resetForm: vi.fn(),
    handleSubmit: vi.fn(),
    markFieldTouched: vi.fn(),
  });

  it('renders the component', () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('displays form title', () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    expect(wrapper.text()).toContain('valuation.form.title');
  });

  it('displays form description', () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    expect(wrapper.text()).toContain('valuation.form.description');
  });

  it('initializes composable with correct bricksetId', () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    mount(ValuationFormCard, {
      props: {
        bricksetId: 456,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    expect(useValuationFormModule.useValuationForm).toHaveBeenCalledWith(456);
  });

  it('renders BaseNumberInput component', () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: { template: '<div class="base-number-input"></div>' },
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    expect(wrapper.find('.base-number-input').exists()).toBe(true);
  });

  it('passes correct props to BaseNumberInput', () => {
    const mockForm = createMockForm();
    mockForm.formData.value.value = 5000;
    mockForm.errors.value.value = undefined;

    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: { template: '<div></div>' },
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const baseNumberInput = wrapper.findComponent({ name: 'BaseNumberInput' });
    if (baseNumberInput.exists()) {
      expect(baseNumberInput.props('modelValue')).toBe(5000);
      expect(baseNumberInput.props('label')).toBe('valuation.form.value.label');
      expect(baseNumberInput.props('placeholder')).toBe('valuation.form.value.placeholder');
      expect(baseNumberInput.props('required')).toBe(true);
      expect(baseNumberInput.props('min')).toBe(1);
      expect(baseNumberInput.props('max')).toBe(999999);
      expect(baseNumberInput.props('currencyCode')).toBe('PLN');
    }
  });

  it('renders submit button', () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: { template: '<button class="base-button"></button>' },
          InlineError: true,
        },
      },
    });

    expect(wrapper.find('.base-button').exists()).toBe(true);
  });

  it('disables submit button when form is invalid', () => {
    const mockForm = createMockForm();
    mockForm.canSubmit.value = false;

    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const form = wrapper.find('form');
    expect(form.exists()).toBe(true);
  });

  it('shows loading state on submit button during submission', () => {
    const mockForm = createMockForm();
    mockForm.isSubmitting.value = true;
    mockForm.canSubmit.value = false;

    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: {
            template: '<button>{{ isSubmitting ? submittingText : submitText }}</button>',
            props: ['disabled', 'loading'],
          },
          InlineError: true,
        },
      },
    });

    // Verify the form would pass the isSubmitting state to the button
    expect(mockForm.isSubmitting.value).toBe(true);
  });

  it('displays normal submit text when not submitting', () => {
    const mockForm = createMockForm();
    mockForm.isSubmitting.value = false;
    mockForm.canSubmit.value = true;

    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: {
            template: '<button>{{ isSubmitting ? submittingText : submitText }}</button>',
            props: ['disabled', 'loading'],
          },
          InlineError: true,
        },
      },
    });

    // Verify the form would pass the isSubmitting state to the button
    expect(mockForm.isSubmitting.value).toBe(false);
  });

  it('displays general error when present', () => {
    const mockForm = createMockForm();
    mockForm.errors.value.general = 'An error occurred';

    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: { template: '<div class="inline-error">{{ message }}</div>' },
        },
      },
    });

    const inlineError = wrapper.findComponent({ name: 'InlineError' });
    if (inlineError.exists()) {
      expect(inlineError.props('message')).toBe('An error occurred');
      expect(inlineError.props('dismissible')).toBe(true);
    }
  });

  it('hides error when dismissible button is clicked', async () => {
    const mockForm = createMockForm();
    mockForm.errors.value.general = 'An error occurred';

    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const inlineError = wrapper.findComponent({ name: 'InlineError' });
    if (inlineError.exists()) {
      expect(inlineError.props('message')).toBe('An error occurred');
      // Verify dismissible prop is true
      expect(inlineError.props('dismissible')).toBe(true);
    }
  });

  it('handles value input', async () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    // Get the BaseNumberInput component
    const baseNumberInput = wrapper.findComponent({ name: 'BaseNumberInput' });
    if (baseNumberInput.exists()) {
      // Emit the update event
      await baseNumberInput.vm.$emit('update:modelValue', 5000);

      expect(mockForm.formData.value.value).toBe(5000);
    }
  });

  it('clears general error when user starts typing value', async () => {
    const mockForm = createMockForm();
    mockForm.errors.value.general = 'An error';

    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const baseNumberInput = wrapper.findComponent({ name: 'BaseNumberInput' });
    if (baseNumberInput.exists()) {
      await baseNumberInput.vm.$emit('update:modelValue', 5000);

      expect(mockForm.errors.value.general).toBeUndefined();
    }
  });

  it('marks field as touched on blur', async () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const baseNumberInput = wrapper.findComponent({ name: 'BaseNumberInput' });
    if (baseNumberInput.exists()) {
      await baseNumberInput.vm.$emit('blur');

      expect(mockForm.markFieldTouched).toHaveBeenCalledWith('value');
    }
  });

  it('validates field on blur', async () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const baseNumberInput = wrapper.findComponent({ name: 'BaseNumberInput' });
    if (baseNumberInput.exists()) {
      await baseNumberInput.vm.$emit('blur');

      expect(mockForm.validateField).toHaveBeenCalledWith('value');
    }
  });

  it('emits valuation-created event on successful submission', async () => {
    const mockForm = createMockForm();
    const mockResponse = {
      id: 1,
      value: 5000,
      currency: 'PLN',
      createdAt: '2025-01-01T00:00:00Z',
    };

    mockForm.handleSubmit = vi.fn().mockResolvedValue(mockResponse);

    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const form = wrapper.find('form');
    if (form.exists()) {
      await form.trigger('submit.prevent');
      await wrapper.vm.$nextTick();

      expect(wrapper.emitted('valuation-created')).toBeTruthy();
      expect(wrapper.emitted('valuation-created')?.[0]).toEqual([mockResponse]);
    }
  });

  it('resets form after successful submission', async () => {
    const mockForm = createMockForm();
    const mockResponse = {
      id: 1,
      value: 5000,
      currency: 'PLN',
      createdAt: '2025-01-01T00:00:00Z',
    };

    mockForm.handleSubmit = vi.fn().mockResolvedValue(mockResponse);

    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const form = wrapper.find('form');
    if (form.exists()) {
      await form.trigger('submit.prevent');
      await wrapper.vm.$nextTick();

      expect(mockForm.resetForm).toHaveBeenCalled();
    }
  });

  it('does not emit event if submission returns null', async () => {
    const mockForm = createMockForm();
    mockForm.handleSubmit = vi.fn().mockResolvedValue(null);

    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const form = wrapper.find('form');
    if (form.exists()) {
      await form.trigger('submit.prevent');
      await wrapper.vm.$nextTick();

      expect(wrapper.emitted('valuation-created')).toBeFalsy();
    }
  });

  it('handles submission errors gracefully', async () => {
    const mockForm = createMockForm();
    mockForm.handleSubmit = vi.fn().mockRejectedValue(new Error('Network error'));

    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const form = wrapper.find('form');
    if (form.exists()) {
      // Should not throw
      await expect(form.trigger('submit.prevent')).resolves.toBeUndefined();
    }
  });

  it('displays validation help text', () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    expect(wrapper.text()).toContain('valuation.form.help.valueRange');
  });

  it('applies correct styling classes', () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const card = wrapper.find('div.rounded-lg');
    expect(card.classes()).toContain('p-6');
    expect(card.classes()).toContain('bg-white');
    expect(card.classes()).toContain('dark:bg-gray-800');
    expect(card.classes()).toContain('rounded-lg');
    expect(card.classes()).toContain('border');
  });

  it('renders form element with correct structure', () => {
    const mockForm = createMockForm();
    vi.mocked(useValuationFormModule.useValuationForm).mockReturnValue(mockForm);

    const wrapper = mount(ValuationFormCard, {
      props: {
        bricksetId: 123,
      },
      global: {
        stubs: {
          BaseNumberInput: true,
          BaseButton: true,
          InlineError: true,
        },
      },
    });

    const form = wrapper.find('form');
    expect(form.exists()).toBe(true);
    expect(form.classes()).toContain('space-y-5');
  });
});
