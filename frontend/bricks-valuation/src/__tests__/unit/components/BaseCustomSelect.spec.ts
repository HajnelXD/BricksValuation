import { describe, it, expect, beforeEach } from 'vitest';
import { mount, VueWrapper } from '@vue/test-utils';
import BaseCustomSelect from '@/components/base/BaseCustomSelect.vue';
import type { SelectOption } from '@/types/bricksets';

describe('BaseCustomSelect Component', () => {
  const mockOptions: SelectOption[] = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3', disabled: true },
  ];

  let wrapper: VueWrapper;

  beforeEach(() => {
    // Clear any event listeners from previous tests
    document.body.innerHTML = '';
  });

  describe('Rendering', () => {
    it('renders the component', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
      });

      expect(wrapper.exists()).toBe(true);
    });

    it('displays label text', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'My Custom Select',
          options: mockOptions,
        },
      });

      expect(wrapper.find('label').text()).toContain('My Custom Select');
    });

    it('shows required asterisk when required prop is true', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          required: true,
        },
      });

      expect(wrapper.find('label').text()).toContain('*');
    });

    it('displays placeholder when no value is selected', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          placeholder: 'Choose an option',
        },
      });

      expect(wrapper.find('button').text()).toContain('Choose an option');
    });

    it('displays selected option label', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: 'option2',
          label: 'Test Select',
          options: mockOptions,
        },
      });

      expect(wrapper.find('button').text()).toContain('Option 2');
    });

    it('renders animated chevron icon', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
      });

      const svg = wrapper.find('svg');
      expect(svg.exists()).toBe(true);
      expect(svg.classes()).toContain('transition-transform');
    });

    it('chevron is properly positioned', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
      });

      const svg = wrapper.find('svg');
      expect(svg.classes()).toContain('flex-shrink-0');
    });
  });

  describe('Dropdown Opening/Closing', () => {
    it('dropdown is closed by default', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
      });

      const dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(false);
    });

    it('opens dropdown when button is clicked', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(true);

      wrapper.unmount();
    });

    it('rotates chevron 180 degrees when dropdown is open', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const svg = wrapper.find('svg');
      expect(svg.classes()).toContain('rotate-0');

      const button = wrapper.find('button');
      await button.trigger('click');

      expect(svg.classes()).toContain('rotate-180');
      expect(svg.classes()).not.toContain('rotate-0');

      wrapper.unmount();
    });

    it('closes dropdown when button is clicked again', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');
      await button.trigger('click');

      const dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(false);

      wrapper.unmount();
    });

    it('closes dropdown when clicking outside', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      // Verify dropdown is open
      let dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(true);

      // Simulate click outside by creating a new element and clicking it
      const outsideElement = document.createElement('div');
      document.body.appendChild(outsideElement);

      const clickEvent = new MouseEvent('mousedown', {
        bubbles: true,
        cancelable: true,
      });
      outsideElement.dispatchEvent(clickEvent);

      await wrapper.vm.$nextTick();

      dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(false);

      document.body.removeChild(outsideElement);
      wrapper.unmount();
    });
  });

  describe('Options Rendering', () => {
    it('renders all options in dropdown', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const options = wrapper.findAll('[role="option"]');
      expect(options.length).toBe(3);

      wrapper.unmount();
    });

    it('displays option labels correctly', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.text()).toContain('Option 1');
      expect(dropdown.text()).toContain('Option 2');
      expect(dropdown.text()).toContain('Option 3');

      wrapper.unmount();
    });

    it('highlights selected option', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: 'option2',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const selectedOption = wrapper.findAll('[role="option"]')[1];
      expect(selectedOption.classes()).toContain('bg-blue-100');

      wrapper.unmount();
    });

    it('shows checkmark on selected option', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: 'option2',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const selectedOption = wrapper.findAll('[role="option"]')[1];
      const checkmark = selectedOption.find('svg');
      expect(checkmark.exists()).toBe(true);

      wrapper.unmount();
    });

    it('disables disabled options', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const disabledOption = wrapper.findAll('[role="option"]')[2];
      expect(disabledOption.classes()).toContain('opacity-50');
      expect(disabledOption.classes()).toContain('cursor-not-allowed');

      wrapper.unmount();
    });
  });

  describe('Selection Behavior', () => {
    it('emits update:modelValue when option is selected', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const firstOption = wrapper.findAll('[role="option"]')[0];
      await firstOption.trigger('click');

      expect(wrapper.emitted('update:modelValue')).toBeTruthy();
      expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['option1']);

      wrapper.unmount();
    });

    it('closes dropdown after selection', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const firstOption = wrapper.findAll('[role="option"]')[0];
      await firstOption.trigger('click');

      const dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(false);

      wrapper.unmount();
    });

    it('does not emit update:modelValue when disabled option is clicked', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const disabledOption = wrapper.findAll('[role="option"]')[2];
      await disabledOption.trigger('click');

      expect(wrapper.emitted('update:modelValue')).toBeFalsy();

      wrapper.unmount();
    });
  });

  describe('Keyboard Navigation', () => {
    it('opens dropdown on Enter key', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('keydown', { key: 'Enter' });

      const dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(true);

      wrapper.unmount();
    });

    it('opens dropdown on Space key', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('keydown', { key: ' ' });

      const dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(true);

      wrapper.unmount();
    });

    it('closes dropdown on Escape key', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');
      await button.trigger('keydown', { key: 'Escape' });

      const dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(false);

      wrapper.unmount();
    });

    it('opens dropdown on ArrowDown key', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('keydown', { key: 'ArrowDown' });

      const dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(true);

      wrapper.unmount();
    });

    it('closes dropdown on Tab key', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');
      await button.trigger('keydown', { key: 'Tab' });

      const dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(false);

      wrapper.unmount();
    });
  });

  describe('Events', () => {
    it('emits focus event when dropdown opens', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      expect(wrapper.emitted('focus')).toBeTruthy();

      wrapper.unmount();
    });

    it('emits blur event when dropdown closes', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');
      await button.trigger('click');

      expect(wrapper.emitted('blur')).toBeTruthy();

      wrapper.unmount();
    });

    it('emits blur event when option is selected', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const firstOption = wrapper.findAll('[role="option"]')[0];
      await firstOption.trigger('click');

      expect(wrapper.emitted('blur')).toBeTruthy();

      wrapper.unmount();
    });
  });

  describe('Error State', () => {
    it('displays error message when error prop is provided', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          error: 'This field is required',
        },
      });

      expect(wrapper.text()).toContain('This field is required');
    });

    it('applies error styling when error prop is provided', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          error: 'Error message',
        },
      });

      const button = wrapper.find('button');
      expect(button.classes()).toContain('border-red-500');
    });

    it('sets aria-invalid attribute when error is present', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          error: 'Error',
        },
      });

      const button = wrapper.find('button');
      expect(button.attributes('aria-invalid')).toBe('true');
    });

    it('sets aria-describedby attribute when error is present', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          error: 'Error message',
        },
      });

      const button = wrapper.find('button');
      expect(button.attributes('aria-describedby')).toBeTruthy();
    });
  });

  describe('Disabled State', () => {
    it('disables button when disabled prop is true', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          disabled: true,
        },
      });

      const button = wrapper.find('button');
      expect(button.element.disabled).toBe(true);
    });

    it('does not open dropdown when disabled', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          disabled: true,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const dropdown = wrapper.find('[role="listbox"]');
      expect(dropdown.isVisible()).toBe(false);

      wrapper.unmount();
    });

    it('applies disabled styling', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          disabled: true,
        },
      });

      const button = wrapper.find('button');
      expect(button.classes()).toContain('opacity-60');
      expect(button.classes()).toContain('cursor-not-allowed');
    });
  });

  describe('Search Functionality', () => {
    it('shows search input when searchable prop is true', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          searchable: true,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const searchInput = wrapper.find('input[type="text"]');
      expect(searchInput.exists()).toBe(true);

      wrapper.unmount();
    });

    it('does not show search input when searchable is false', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          searchable: false,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const searchInput = wrapper.find('input[type="text"]');
      expect(searchInput.exists()).toBe(false);

      wrapper.unmount();
    });

    it('filters options based on search query', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          searchable: true,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const searchInput = wrapper.find('input[type="text"]');
      await searchInput.setValue('Option 1');

      const options = wrapper.findAll('[role="option"]');
      expect(options.length).toBe(1);
      expect(options[0].text()).toContain('Option 1');

      wrapper.unmount();
    });

    it('shows "No options found" when search yields no results', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
          searchable: true,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const searchInput = wrapper.find('input[type="text"]');
      await searchInput.setValue('Nonexistent');

      expect(wrapper.text()).toContain('No options found');

      wrapper.unmount();
    });
  });

  describe('Accessibility', () => {
    it('sets aria-expanded attribute correctly', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      expect(button.attributes('aria-expanded')).toBe('false');

      await button.trigger('click');
      expect(button.attributes('aria-expanded')).toBe('true');

      wrapper.unmount();
    });

    it('sets aria-haspopup attribute', () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: '',
          label: 'Test Select',
          options: mockOptions,
        },
      });

      const button = wrapper.find('button');
      expect(button.attributes('aria-haspopup')).toBe('true');
    });

    it('sets aria-selected on selected option', async () => {
      wrapper = mount(BaseCustomSelect, {
        props: {
          modelValue: 'option2',
          label: 'Test Select',
          options: mockOptions,
        },
        attachTo: document.body,
      });

      const button = wrapper.find('button');
      await button.trigger('click');

      const selectedOption = wrapper.findAll('[role="option"]')[1];
      expect(selectedOption.attributes('aria-selected')).toBe('true');

      wrapper.unmount();
    });
  });
});
