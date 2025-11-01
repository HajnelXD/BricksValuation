import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import EditFormActionsBar from '@/components/bricksets/EditFormActionsBar.vue';
import BaseButton from '@/components/base/BaseButton.vue';
import type { FormActionsConfig } from '@/types/bricksets';

describe('EditFormActionsBar Component', () => {
  const defaultConfig: FormActionsConfig = {
    canSave: true,
    canDelete: true,
    isSaving: false,
    isDeleting: false,
  };

  it('renders all three buttons when showDelete is true', () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: defaultConfig,
        showDelete: true,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    expect(buttons.length).toBe(3); // Delete, Cancel, Save
  });

  it('renders only Cancel and Save buttons when showDelete is false', () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: defaultConfig,
        showDelete: false,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    expect(buttons.length).toBe(2); // Cancel, Save
  });

  it('does not render Delete button when canDelete is false', () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: {
          ...defaultConfig,
          canDelete: false,
        },
        showDelete: true,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    expect(buttons.length).toBe(2); // Cancel, Save only
  });

  it('emits save event when Save button is clicked', async () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: defaultConfig,
        showDelete: true,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const saveButton = buttons[2]; // Last button is Save

    // Emit click event from BaseButton
    await saveButton.vm.$emit('click');

    expect(wrapper.emitted('save')).toBeTruthy();
    expect(wrapper.emitted('save')?.length).toBe(1);
  });

  it('emits cancel event when Cancel button is clicked', async () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: defaultConfig,
        showDelete: true,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const cancelButton = buttons[1]; // Middle button is Cancel

    // Emit click event from BaseButton
    await cancelButton.vm.$emit('click');

    expect(wrapper.emitted('cancel')).toBeTruthy();
    expect(wrapper.emitted('cancel')?.length).toBe(1);
  });

  it('emits delete event when Delete button is clicked', async () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: defaultConfig,
        showDelete: true,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const deleteButton = buttons[0]; // First button is Delete

    // Emit click event from BaseButton
    await deleteButton.vm.$emit('click');

    expect(wrapper.emitted('delete')).toBeTruthy();
    expect(wrapper.emitted('delete')?.length).toBe(1);
  });

  it('disables Save button when canSave is false', () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: {
          ...defaultConfig,
          canSave: false,
        },
        showDelete: false,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const saveButton = buttons[1]; // Save button

    expect(saveButton.props('disabled')).toBe(true);
  });

  it('shows loading state on Save button when isSaving is true', () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: {
          ...defaultConfig,
          isSaving: true,
        },
        showDelete: false,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const saveButton = buttons[1]; // Save button

    expect(saveButton.props('loading')).toBe(true);
    expect(saveButton.props('disabled')).toBe(true);
  });

  it('shows loading state on Delete button when isDeleting is true', () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: {
          ...defaultConfig,
          isDeleting: true,
        },
        showDelete: true,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);
    const deleteButton = buttons[0]; // Delete button

    expect(deleteButton.props('loading')).toBe(true);
    expect(deleteButton.props('disabled')).toBe(true);
  });

  it('disables all buttons when isSaving is true', () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: {
          ...defaultConfig,
          isSaving: true,
        },
        showDelete: true,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);

    buttons.forEach((button) => {
      expect(button.props('disabled')).toBe(true);
    });
  });

  it('disables all buttons when isDeleting is true', () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: {
          ...defaultConfig,
          isDeleting: true,
        },
        showDelete: true,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);

    buttons.forEach((button) => {
      expect(button.props('disabled')).toBe(true);
    });
  });

  it('has correct button variants', () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: defaultConfig,
        showDelete: true,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);

    expect(buttons[0].props('variant')).toBe('danger'); // Delete
    expect(buttons[1].props('variant')).toBe('secondary'); // Cancel
    expect(buttons[2].props('variant')).toBe('primary'); // Save
  });

  it('has correct aria labels', () => {
    const wrapper = mount(EditFormActionsBar, {
      props: {
        config: defaultConfig,
        showDelete: true,
      },
      global: {
        components: {
          BaseButton,
        },
      },
    });

    const buttons = wrapper.findAllComponents(BaseButton);

    expect(buttons[0].attributes('aria-label')).toBe('Usuń zestaw');
    expect(buttons[1].attributes('aria-label')).toBe('Anuluj edycję');
    expect(buttons[2].attributes('aria-label')).toBe('Zapisz zmiany');
  });
});
