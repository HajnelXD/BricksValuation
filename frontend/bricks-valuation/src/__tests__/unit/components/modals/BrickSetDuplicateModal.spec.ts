import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, VueWrapper } from '@vue/test-utils';
import { createRouter, createMemoryHistory, Router } from 'vue-router';
import BrickSetDuplicateModal from '@/components/modals/BrickSetDuplicateModal.vue';
import type { DuplicateSetInfo } from '@/types/bricksets';

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
  }),
}));

describe('BrickSetDuplicateModal Component', () => {
  let router: Router;
  let wrapper: VueWrapper;

  const mockDuplicateSetInfo: DuplicateSetInfo = {
    setId: 123,
    setNumber: 10331,
    productionStatus: 'ACTIVE',
    completeness: 'COMPLETE',
    hasInstructions: true,
    hasBox: true,
    isFactorySealed: false,
    ownerName: 'Test User',
  };

  beforeEach(() => {
    // Create a mock router
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
        { path: '/bricksets', name: 'bricksets', component: { template: '<div>List</div>' } },
        {
          path: '/bricksets/:id',
          name: 'brickset-detail',
          component: { template: '<div>Detail</div>' },
        },
      ],
    });

    vi.clearAllMocks();
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  describe('Rendering', () => {
    it('renders modal when isOpen is true', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      // Modal is teleported to #app, so we need to check the DOM
      const dialog = document.querySelector('[role="dialog"]');
      expect(dialog).toBeTruthy();
    });

    it('does not render modal when isOpen is false', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: false,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const dialog = document.querySelector('[role="dialog"]');
      expect(dialog).toBeFalsy();
    });

    it('displays modal title', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const appDiv = document.getElementById('app');
      expect(appDiv?.textContent).toContain('bricksets.duplicate.title');
    });

    it('displays duplicate message', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const appDiv = document.getElementById('app');
      expect(appDiv?.textContent).toContain('bricksets.duplicate.message');
    });

    it('displays set number', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const appDiv = document.getElementById('app');
      expect(appDiv?.textContent).toContain('10331');
    });

    it('displays production status', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const appDiv = document.getElementById('app');
      expect(appDiv?.textContent).toContain('bricksets.active');
    });

    it('displays completeness', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const appDiv = document.getElementById('app');
      expect(appDiv?.textContent).toContain('bricksets.complete');
    });

    it('displays hasInstructions badge when true', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const appDiv = document.getElementById('app');
      expect(appDiv?.textContent).toContain('bricksets.create.fields.hasInstructions.label');
    });

    it('displays hasBox badge when true', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const appDiv = document.getElementById('app');
      expect(appDiv?.textContent).toContain('bricksets.create.fields.hasBox.label');
    });

    it('does not display isFactorySealed badge when false', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const badges = document.querySelectorAll('.attribute-badge');
      const sealedBadge = Array.from(badges).find((badge) =>
        badge.textContent?.includes('bricksets.create.fields.isFactorySealed.label')
      );
      expect(sealedBadge).toBeUndefined();
    });

    it('displays help text', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const appDiv = document.getElementById('app');
      expect(appDiv?.textContent).toContain('bricksets.duplicate.helpText');
    });
  });

  describe('User Interactions', () => {
    it('emits close event when close button is clicked', async () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const closeButton = document.querySelector('[aria-label="common.close"]') as HTMLElement;
      closeButton?.click();
      await wrapper.vm.$nextTick();

      expect(wrapper.emitted('close')).toBeTruthy();
      expect(wrapper.emitted('close')).toHaveLength(1);
    });

    it('emits close event when cancel button is clicked', async () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const buttons = document.querySelectorAll('button');
      const cancelButton = Array.from(buttons).find((btn) =>
        btn.textContent?.includes('common.close')
      ) as HTMLElement;
      cancelButton?.click();
      await wrapper.vm.$nextTick();

      expect(wrapper.emitted('close')).toBeTruthy();
    });

    it('emits close event when clicking on overlay', async () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const overlay = document.querySelector('[role="dialog"]') as HTMLElement;
      overlay?.click();
      await wrapper.vm.$nextTick();

      expect(wrapper.emitted('close')).toBeTruthy();
    });

    it('does not emit close when clicking inside modal content', async () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const modalContent = document.querySelector('[role="dialog"] > div') as HTMLElement;
      modalContent?.click();
      await wrapper.vm.$nextTick();

      expect(wrapper.emitted('close')).toBeFalsy();
    });
  });

  describe('Navigation', () => {
    it('navigates to brickset detail when setId is available', async () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const routerPushSpy = vi.spyOn(router, 'push');

      const buttons = document.querySelectorAll('button');
      const viewButton = Array.from(buttons).find((btn) =>
        btn.textContent?.includes('bricksets.duplicate.viewExisting')
      ) as HTMLElement;
      viewButton?.click();

      // Wait for async navigation
      await wrapper.vm.$nextTick();
      await new Promise((resolve) => setTimeout(resolve, 0));

      expect(routerPushSpy).toHaveBeenCalledWith({
        name: 'brickset-detail',
        params: { id: 123 },
      });
      expect(wrapper.emitted('navigate')).toBeTruthy();
      expect(wrapper.emitted('close')).toBeTruthy();
    });

    it('navigates to bricksets list with query when setId is not available', async () => {
      const infoWithoutId: DuplicateSetInfo = {
        ...mockDuplicateSetInfo,
        setId: 0,
      };

      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: infoWithoutId,
        },
        global: {
          plugins: [router],
        },
      });

      const routerPushSpy = vi.spyOn(router, 'push');

      const buttons = document.querySelectorAll('button');
      const viewButton = Array.from(buttons).find((btn) =>
        btn.textContent?.includes('bricksets.duplicate.viewExisting')
      ) as HTMLElement;
      viewButton?.click();

      // Wait for async navigation
      await wrapper.vm.$nextTick();
      await new Promise((resolve) => setTimeout(resolve, 0));

      expect(routerPushSpy).toHaveBeenCalledWith({
        name: 'bricksets',
        query: { q: '10331' },
      });
      expect(wrapper.emitted('navigate')).toBeTruthy();
      expect(wrapper.emitted('close')).toBeTruthy();
    });
  });

  describe('Keyboard Support', () => {
    it('closes modal on Escape key', async () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const overlay = document.querySelector('[role="dialog"]') as HTMLElement;
      const event = new KeyboardEvent('keydown', { key: 'Escape' });
      overlay?.dispatchEvent(event);
      await wrapper.vm.$nextTick();

      expect(wrapper.emitted('close')).toBeTruthy();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const dialog = document.querySelector('[role="dialog"]');
      expect(dialog?.getAttribute('aria-modal')).toBe('true');
      expect(dialog?.getAttribute('aria-labelledby')).toContain('modal-title-10331');
    });

    it('has accessible close button', () => {
      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: mockDuplicateSetInfo,
        },
        global: {
          plugins: [router],
        },
      });

      const closeButton = document.querySelector('[aria-label="common.close"]');
      expect(closeButton).toBeTruthy();
      expect(closeButton?.getAttribute('type')).toBe('button');
    });
  });

  describe('Different BrickSet States', () => {
    it('renders correctly for RETIRED and INCOMPLETE set', () => {
      const retiredSet: DuplicateSetInfo = {
        ...mockDuplicateSetInfo,
        productionStatus: 'RETIRED',
        completeness: 'INCOMPLETE',
      };

      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: retiredSet,
        },
        global: {
          plugins: [router],
        },
      });

      const appDiv = document.getElementById('app');
      expect(appDiv?.textContent).toContain('bricksets.retired');
      expect(appDiv?.textContent).toContain('bricksets.incomplete');
    });

    it('displays all attributes when all are true', () => {
      const fullSet: DuplicateSetInfo = {
        ...mockDuplicateSetInfo,
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: true,
      };

      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: fullSet,
        },
        global: {
          plugins: [router],
        },
      });

      const appDiv = document.getElementById('app');
      expect(appDiv?.textContent).toContain('bricksets.create.fields.hasInstructions.label');
      expect(appDiv?.textContent).toContain('bricksets.create.fields.hasBox.label');
      expect(appDiv?.textContent).toContain('bricksets.create.fields.isFactorySealed.label');
    });

    it('displays no attributes when all are false', () => {
      const minimalSet: DuplicateSetInfo = {
        ...mockDuplicateSetInfo,
        hasInstructions: false,
        hasBox: false,
        isFactorySealed: false,
      };

      wrapper = mount(BrickSetDuplicateModal, {
        props: {
          isOpen: true,
          duplicateSetInfo: minimalSet,
        },
        global: {
          plugins: [router],
        },
      });

      const attributeBadges = document.querySelectorAll('.attribute-badge');
      expect(attributeBadges).toHaveLength(0);
    });
  });
});
