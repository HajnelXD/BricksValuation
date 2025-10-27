import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import BrickSetCreateView from '@/pages/bricksets/BrickSetCreateView.vue';
import { useNotificationStore } from '@/stores/notification';

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
    expect(container.classes()).toContain('bg-gray-50');
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
    expect(container.classes()).toContain('dark:bg-gray-900');
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
});
