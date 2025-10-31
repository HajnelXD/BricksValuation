import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import RuleLockBadge from '@/components/bricksets/RuleLockBadge.vue';

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'errors.edit_forbidden': 'Nie możesz edytować tego zestawu',
        'errors.delete_forbidden': 'Nie możesz usunąć tego zestawu',
        'errors.edit_delete_forbidden': 'Nie możesz edytować ani usunąć tego zestawu',
      };
      return translations[key] || key;
    },
  }),
}));

describe('RuleLockBadge Component', () => {
  it('renders with edit type', () => {
    const wrapper = mount(RuleLockBadge, {
      props: {
        type: 'edit',
      },
    });

    expect(wrapper.text()).toContain('Nie możesz edytować tego zestawu');
    expect(wrapper.find('[role="alert"]').exists()).toBe(true);
  });

  it('renders with delete type', () => {
    const wrapper = mount(RuleLockBadge, {
      props: {
        type: 'delete',
      },
    });

    expect(wrapper.text()).toContain('Nie możesz usunąć tego zestawu');
  });

  it('renders with both type', () => {
    const wrapper = mount(RuleLockBadge, {
      props: {
        type: 'both',
      },
    });

    expect(wrapper.text()).toContain('Nie możesz edytować ani usunąć tego zestawu');
  });

  it('renders reason when provided', () => {
    const wrapper = mount(RuleLockBadge, {
      props: {
        type: 'edit',
        reason: 'Ten zestaw ma wyceny od innych użytkowników',
      },
    });

    expect(wrapper.text()).toContain('Nie możesz edytować tego zestawu');
    expect(wrapper.text()).toContain('Ten zestaw ma wyceny od innych użytkowników');
  });

  it('does not render reason when not provided', () => {
    const wrapper = mount(RuleLockBadge, {
      props: {
        type: 'edit',
      },
    });

    const paragraphs = wrapper.findAll('p');
    expect(paragraphs.length).toBe(1); // Only the main message
  });

  it('has correct accessibility attributes', () => {
    const wrapper = mount(RuleLockBadge, {
      props: {
        type: 'edit',
      },
    });

    const alertDiv = wrapper.find('div');
    expect(alertDiv.attributes('role')).toBe('alert');
    expect(alertDiv.attributes('aria-live')).toBe('polite');
  });

  it('has warning icon', () => {
    const wrapper = mount(RuleLockBadge, {
      props: {
        type: 'edit',
      },
    });

    expect(wrapper.find('svg').exists()).toBe(true);
  });

  it('has correct styling classes', () => {
    const wrapper = mount(RuleLockBadge, {
      props: {
        type: 'edit',
      },
    });

    const div = wrapper.find('div');
    expect(div.classes()).toContain('bg-amber-50');
    expect(div.classes()).toContain('border-amber-200');
  });
});
