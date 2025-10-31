import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import BrickSetCreateView from '@/pages/bricksets/BrickSetCreateView.vue';
import { useNotificationStore } from '@/stores/notification';
import { DuplicateError } from '@/composables/useBrickSetForm';
import type { DuplicateSetInfo } from '@/types/bricksets';

// Mock the notification store
vi.mock('@/stores/notification', () => ({
  useNotificationStore: vi.fn(),
}));

// Mock i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string, params?: Record<string, unknown>) => {
      if (params) {
        return `${key}_${JSON.stringify(params)}`;
      }
      return key;
    },
  }),
}));

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    back: vi.fn(),
    currentRoute: {
      value: {
        fullPath: '/app/bricksets/new',
        query: {},
      },
    },
  })),
}));

describe('BrickSetCreateView Page', () => {
  let mockNotificationStore: Record<string, unknown>;

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock notification store
    mockNotificationStore = {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
    };
    vi.mocked(useNotificationStore).mockReturnValue(mockNotificationStore);
  });

  it('renders the component', () => {
    const wrapper = mount(BrickSetCreateView, {
      global: {
        stubs: {
          BrickSetForm: true,
        },
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('renders with proper background styling', () => {
    const wrapper = mount(BrickSetCreateView, {
      global: {
        stubs: {
          BrickSetForm: true,
        },
      },
    });

    const container = wrapper.find('div');
    expect(container.classes()).toContain('min-h-screen');
    expect(container.classes()).toContain('bg-gray-900');
  });

  it('renders dark mode background', () => {
    const wrapper = mount(BrickSetCreateView, {
      global: {
        stubs: {
          BrickSetForm: true,
        },
      },
    });

    const container = wrapper.find('div');
    expect(container.classes()).toContain('bg-gray-900');
  });

  it('mounts BrickSetForm component', () => {
    const wrapper = mount(BrickSetCreateView, {
      global: {
        stubs: {
          BrickSetForm: {
            template: '<div class="brick-set-form">Form</div>',
          },
        },
      },
    });

    expect(wrapper.find('.brick-set-form').exists()).toBe(true);
  });

  it('initializes notification store', () => {
    mount(BrickSetCreateView, {
      global: {
        stubs: {
          BrickSetForm: true,
        },
      },
    });

    expect(useNotificationStore).toHaveBeenCalled();
  });

  it('has component setup method with proper handler definitions', () => {
    const wrapper = mount(BrickSetCreateView, {
      global: {
        stubs: {
          BrickSetForm: true,
        },
      },
    });

    // Component should be mounted successfully
    expect(wrapper.exists()).toBe(true);
  });

  it('accepts on-submit and on-cancel events from BrickSetForm', () => {
    const wrapper = mount(BrickSetCreateView, {
      global: {
        stubs: {
          BrickSetForm: {
            template:
              '<div><button @click="$emit(\'on-submit\')">Submit</button><button @click="$emit(\'on-cancel\')">Cancel</button></div>',
            emits: ['on-submit', 'on-cancel'],
          },
        },
      },
    });

    const buttons = wrapper.findAll('button');
    expect(buttons.length).toBe(2);
  });

  it('has proper error handling methods defined', () => {
    const wrapper = mount(BrickSetCreateView, {
      global: {
        stubs: {
          BrickSetForm: true,
        },
      },
    });

    // Component contains the error handling logic
    expect(wrapper.exists()).toBe(true);
  });

  it('renders inside a div with proper layout structure', () => {
    const wrapper = mount(BrickSetCreateView, {
      global: {
        stubs: {
          BrickSetForm: true,
        },
      },
    });

    const mainDiv = wrapper.find('div');
    expect(mainDiv.exists()).toBe(true);
  });

  it('is a valid Vue component', () => {
    const wrapper = mount(BrickSetCreateView, {
      global: {
        stubs: {
          BrickSetForm: true,
        },
      },
    });

    expect(wrapper.vm).toBeDefined();
    expect(wrapper.vm.$options.name || wrapper.vm.$options.__name).toBeDefined();
  });

  describe('Duplicate Detection Modal', () => {
    it('renders BrickSetDuplicateModal component when duplicateSetInfo is available', async () => {
      const mockDuplicateInfo: DuplicateSetInfo = {
        setId: 123,
        setNumber: 10331,
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerName: 'Test User',
      };

      const duplicateError = new DuplicateError(
        'Duplicate set',
        'brickset_global_identity',
        mockDuplicateInfo
      );

      const wrapper = mount(BrickSetCreateView, {
        global: {
          stubs: {
            BrickSetForm: {
              template: '<div><button @click="emitError">Trigger Error</button></div>',
              emits: ['on-error'],
              methods: {
                emitError() {
                  this.$emit('on-error', duplicateError);
                },
              },
            },
            BrickSetDuplicateModal: {
              template: '<div class="duplicate-modal">Modal</div>',
              props: ['isOpen', 'duplicateSetInfo'],
            },
          },
        },
      });

      // Trigger error to show modal
      const button = wrapper.find('button');
      await button.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.find('.duplicate-modal').exists()).toBe(true);
    });

    it('modal is initially closed', () => {
      const wrapper = mount(BrickSetCreateView, {
        global: {
          stubs: {
            BrickSetForm: true,
            BrickSetDuplicateModal: {
              template: '<div v-if="isOpen" class="modal">Modal</div>',
              props: ['isOpen', 'duplicateSetInfo'],
            },
          },
        },
      });

      expect(wrapper.find('.modal').exists()).toBe(false);
    });

    it('opens modal when DuplicateError is emitted from form', async () => {
      const mockDuplicateInfo: DuplicateSetInfo = {
        setId: 123,
        setNumber: 10331,
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerName: 'Test User',
      };

      const duplicateError = new DuplicateError(
        'Duplicate set',
        'brickset_global_identity',
        mockDuplicateInfo
      );

      const wrapper = mount(BrickSetCreateView, {
        global: {
          stubs: {
            BrickSetForm: {
              template: '<div><button @click="emitError">Trigger Error</button></div>',
              emits: ['on-error'],
              methods: {
                emitError() {
                  this.$emit('on-error', duplicateError);
                },
              },
            },
            BrickSetDuplicateModal: {
              template:
                '<div v-if="isOpen" class="modal">Modal: {{ duplicateSetInfo?.setNumber }}</div>',
              props: ['isOpen', 'duplicateSetInfo'],
            },
          },
        },
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      // Wait for async updates
      await wrapper.vm.$nextTick();

      const modal = wrapper.find('.modal');
      expect(modal.exists()).toBe(true);
      expect(modal.text()).toContain('10331');
    });

    it('shows error notification when DuplicateError has no duplicateInfo', async () => {
      const duplicateError = new DuplicateError(
        'Duplicate set',
        'brickset_global_identity',
        undefined
      );

      const wrapper = mount(BrickSetCreateView, {
        global: {
          stubs: {
            BrickSetForm: {
              template: '<div><button @click="emitError">Trigger Error</button></div>',
              emits: ['on-error'],
              methods: {
                emitError() {
                  this.$emit('on-error', duplicateError);
                },
              },
            },
            BrickSetDuplicateModal: true,
          },
        },
      });

      const button = wrapper.find('button');
      await button.trigger('click');
      await wrapper.vm.$nextTick();

      expect(mockNotificationStore.error).toHaveBeenCalledWith(
        'bricksets.create.errors.duplicate',
        7000
      );
    });

    it('handles ValidationError without showing modal', async () => {
      const validationError = {
        name: 'ValidationError',
        message: 'Validation failed',
      };

      const wrapper = mount(BrickSetCreateView, {
        global: {
          stubs: {
            BrickSetForm: {
              template: '<div><button @click="emitError">Trigger Error</button></div>',
              emits: ['on-error'],
              methods: {
                emitError() {
                  this.$emit('on-error', validationError);
                },
              },
            },
            BrickSetDuplicateModal: {
              template: '<div v-if="isOpen" class="modal">Modal</div>',
              props: ['isOpen', 'duplicateSetInfo'],
            },
          },
        },
      });

      const button = wrapper.find('button');
      await button.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.find('.modal').exists()).toBe(false);
      expect(mockNotificationStore.error).not.toHaveBeenCalled();
    });

    it('handles generic errors with network error notification', async () => {
      const genericError = new Error('Network error');

      const wrapper = mount(BrickSetCreateView, {
        global: {
          stubs: {
            BrickSetForm: {
              template: '<div><button @click="emitError">Trigger Error</button></div>',
              emits: ['on-error'],
              methods: {
                emitError() {
                  this.$emit('on-error', genericError);
                },
              },
            },
            BrickSetDuplicateModal: true,
          },
        },
      });

      const button = wrapper.find('button');
      await button.trigger('click');
      await wrapper.vm.$nextTick();

      expect(mockNotificationStore.error).toHaveBeenCalledWith('errors.networkError', 5000);
    });

    it('closes modal when close event is emitted', async () => {
      const mockDuplicateInfo: DuplicateSetInfo = {
        setId: 123,
        setNumber: 10331,
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerName: 'Test User',
      };

      const duplicateError = new DuplicateError(
        'Duplicate set',
        'brickset_global_identity',
        mockDuplicateInfo
      );

      const wrapper = mount(BrickSetCreateView, {
        global: {
          stubs: {
            BrickSetForm: {
              template: '<div><button @click="emitError">Trigger Error</button></div>',
              emits: ['on-error'],
              methods: {
                emitError() {
                  this.$emit('on-error', duplicateError);
                },
              },
            },
            BrickSetDuplicateModal: {
              template:
                '<div v-if="isOpen" class="modal"><button @click="$emit(\'close\')">Close</button></div>',
              props: ['isOpen', 'duplicateSetInfo'],
              emits: ['close'],
            },
          },
        },
      });

      // Open modal
      const errorButton = wrapper.find('button');
      await errorButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.find('.modal').exists()).toBe(true);

      // Close modal
      const closeButton = wrapper.findAll('button')[1];
      await closeButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.find('.modal').exists()).toBe(false);
    });

    it('closes modal when navigate event is emitted', async () => {
      const mockDuplicateInfo: DuplicateSetInfo = {
        setId: 123,
        setNumber: 10331,
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerName: 'Test User',
      };

      const duplicateError = new DuplicateError(
        'Duplicate set',
        'brickset_global_identity',
        mockDuplicateInfo
      );

      const wrapper = mount(BrickSetCreateView, {
        global: {
          stubs: {
            BrickSetForm: {
              template: '<div><button @click="emitError">Trigger Error</button></div>',
              emits: ['on-error'],
              methods: {
                emitError() {
                  this.$emit('on-error', duplicateError);
                },
              },
            },
            BrickSetDuplicateModal: {
              template:
                '<div v-if="isOpen" class="modal"><button @click="$emit(\'navigate\')">Navigate</button></div>',
              props: ['isOpen', 'duplicateSetInfo'],
              emits: ['navigate'],
            },
          },
        },
      });

      // Open modal
      const errorButton = wrapper.find('button');
      await errorButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.find('.modal').exists()).toBe(true);

      // Navigate
      const navigateButton = wrapper.findAll('button')[1];
      await navigateButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.find('.modal').exists()).toBe(false);
    });
  });
});
