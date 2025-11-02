/**
 * Tests for OwnValuationCard Component
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import OwnValuationCard from '@/components/valuations/OwnValuationCard.vue';
import type { OwnValuationViewModel } from '@/types/bricksets';

describe('OwnValuationCard Component', () => {
  const mockValuation: OwnValuationViewModel = {
    id: 1,
    bricksetId: 10,
    bricksetNumber: '12345',
    valueFormatted: '450 PLN',
    likesCount: 5,
    createdAtRelative: '3 dni temu',
    createdAt: '2025-10-21T12:00:00Z',
  };

  it('should render valuation card with all data', () => {
    const wrapper = mount(OwnValuationCard, {
      props: {
        valuation: mockValuation,
      },
    });

    expect(wrapper.text()).toContain('12345');
    expect(wrapper.text()).toContain('450 PLN');
    expect(wrapper.text()).toContain('5');
    expect(wrapper.text()).toContain('3 dni temu');
  });

  it('should display brickset number in header', () => {
    const wrapper = mount(OwnValuationCard, {
      props: {
        valuation: mockValuation,
      },
    });

    // Check that brickset number is displayed
    expect(wrapper.text()).toContain('12345');
  });

  it('should display valuation value prominently', () => {
    const wrapper = mount(OwnValuationCard, {
      props: {
        valuation: mockValuation,
      },
    });

    const valueElement = wrapper.find('p');
    expect(valueElement.classes()).toContain('text-4xl');
    expect(valueElement.text()).toBe('450 PLN');
  });

  it('should display likes count', () => {
    const wrapper = mount(OwnValuationCard, {
      props: {
        valuation: mockValuation,
      },
    });

    expect(wrapper.text()).toContain('❤️');
    expect(wrapper.text()).toContain('5');
  });

  it('should display relative time', () => {
    const wrapper = mount(OwnValuationCard, {
      props: {
        valuation: mockValuation,
      },
    });

    expect(wrapper.text()).toContain('3 dni temu');
  });

  it('should emit navigate-to-brickset event on click', async () => {
    const wrapper = mount(OwnValuationCard, {
      props: {
        valuation: mockValuation,
      },
    });

    await wrapper.find('.bg-white').trigger('click');

    expect(wrapper.emitted('navigate-to-brickset')).toBeTruthy();
    expect(wrapper.emitted('navigate-to-brickset')?.[0]).toEqual([10]);
  });

  it('should display action button with text "Przejdź"', () => {
    const wrapper = mount(OwnValuationCard, {
      props: {
        valuation: mockValuation,
      },
    });

    // Check that "Przejdź" button text is displayed
    expect(wrapper.text()).toContain('Przejdź');
  });

  it('should render with different valuation data', () => {
    const anotherValuation: OwnValuationViewModel = {
      id: 2,
      bricksetId: 20,
      bricksetNumber: '67890',
      valueFormatted: '250 PLN',
      likesCount: 2,
      createdAtRelative: 'wczoraj',
      createdAt: '2025-10-20T12:00:00Z',
    };

    const wrapper = mount(OwnValuationCard, {
      props: {
        valuation: anotherValuation,
      },
    });

    expect(wrapper.text()).toContain('67890');
    expect(wrapper.text()).toContain('250 PLN');
    expect(wrapper.text()).toContain('2');
    expect(wrapper.text()).toContain('wczoraj');
  });

  it('should handle zero likes count', () => {
    const valuationWithoutLikes: OwnValuationViewModel = {
      ...mockValuation,
      likesCount: 0,
    };

    const wrapper = mount(OwnValuationCard, {
      props: {
        valuation: valuationWithoutLikes,
      },
    });

    expect(wrapper.text()).toContain('❤️');
    expect(wrapper.text()).toContain('0');
  });

  it('should apply correct CSS classes for styling', () => {
    const wrapper = mount(OwnValuationCard, {
      props: {
        valuation: mockValuation,
      },
    });

    const mainDiv = wrapper.find('.bg-white');
    expect(mainDiv.classes()).toContain('rounded-lg');
    expect(mainDiv.classes()).toContain('shadow-md');
    expect(mainDiv.classes()).toContain('cursor-pointer');
  });
});
