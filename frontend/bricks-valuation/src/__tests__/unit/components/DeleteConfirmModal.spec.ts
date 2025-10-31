import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import DeleteConfirmModal from '@/components/modals/DeleteConfirmModal.vue';
import BaseButton from '@/components/base/BaseButton.vue';
import type { DeleteConfirmData } from '@/types/bricksets';

describe('DeleteConfirmModal Component', () => {
  const mockData: DeleteConfirmData = {
    brickSetNumber: '10331',
    brickSetId: 1,
  };

  // Create app div for Teleport
  beforeEach(() => {
    const app = document.createElement('div');
    app.id = 'app';
    document.body.appendChild(app);
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('does not render when open is false', () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: false,
        data: mockData,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    expect(wrapper.find('[role="alertdialog"]').exists()).toBe(false);
  });

  it('renders when open is true', () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    expect(wrapper.find('[role="alertdialog"]').exists()).toBe(true);
  });

  it('displays BrickSet number in message', () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    expect(wrapper.text()).toContain('10331');
  });

  it('displays warning message about irreversibility', () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    expect(wrapper.text()).toContain('Ta operacja jest nieodwracalna');
    expect(wrapper.text()).toContain('Wszystkie powiązane wyceny również zostaną usunięte');
  });

  it('emits confirm event when confirm button is clicked', async () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const confirmButton = buttons[1]; // Second button is confirm

    // Emit click event from BaseButton
    await confirmButton.vm.$emit('click');

    expect(wrapper.emitted('confirm')).toBeTruthy();
    expect(wrapper.emitted('confirm')?.length).toBe(1);
  });

  it('emits cancel event when cancel button is clicked', async () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const cancelButton = buttons[0]; // First button is cancel

    // Emit click event from BaseButton
    await cancelButton.vm.$emit('click');

    expect(wrapper.emitted('cancel')).toBeTruthy();
    expect(wrapper.emitted('cancel')?.length).toBe(1);
  });

  it('emits cancel event when backdrop is clicked', async () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    const backdrop = wrapper.find('[role="alertdialog"]');
    await backdrop.trigger('click');

    expect(wrapper.emitted('cancel')).toBeTruthy();
  });

  it('does not emit cancel when backdrop clicked during deletion', async () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
        isDeleting: true,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    const backdrop = wrapper.find('[role="alertdialog"]');
    await backdrop.trigger('click');

    expect(wrapper.emitted('cancel')).toBeFalsy();
  });

  it('shows loading state on confirm button when isDeleting is true', () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
        isDeleting: true,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const confirmButton = buttons[1];

    expect(confirmButton.props('loading')).toBe(true);
    expect(confirmButton.props('disabled')).toBe(true);
  });

  it('disables cancel button when isDeleting is true', () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
        isDeleting: true,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const cancelButton = buttons[0];

    expect(cancelButton.props('disabled')).toBe(true);
  });

  it('has correct button variants', () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);

    expect(buttons[0].props('variant')).toBe('secondary'); // Cancel
    expect(buttons[1].props('variant')).toBe('danger'); // Confirm
  });

  it('has correct accessibility attributes', () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    const dialog = wrapper.find('[role="alertdialog"]');

    expect(dialog.attributes('aria-modal')).toBe('true');
    expect(dialog.attributes('aria-labelledby')).toBe('delete-modal-title');
    expect(dialog.attributes('aria-describedby')).toBe('delete-modal-description');
  });

  it('has warning icon', () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    expect(wrapper.find('svg').exists()).toBe(true);
  });

  it('displays correct button text when not deleting', () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
        isDeleting: false,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const confirmButton = buttons[1];

    expect(confirmButton.text()).toBe('Usuń zestaw');
  });

  it('displays correct button text when deleting', () => {
    const wrapper = mount(DeleteConfirmModal, {
      props: {
        open: true,
        data: mockData,
        isDeleting: true,
      },
      global: {
        components: {
          BaseButton,
        },
        stubs: {
          Teleport: true,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const confirmButton = buttons[1];

    expect(confirmButton.text()).toBe('Usuwanie...');
  });
});
