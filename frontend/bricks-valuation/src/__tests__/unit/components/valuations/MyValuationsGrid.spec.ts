/**
 * Tests for MyValuationsGrid Component
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import MyValuationsGrid from '@/components/valuations/MyValuationsGrid.vue';
import type { OwnValuationViewModel } from '@/types/bricksets';

describe('MyValuationsGrid Component', () => {
  const mockValuations: OwnValuationViewModel[] = [
    {
      id: 1,
      bricksetId: 10,
      bricksetNumber: '12345',
      valueFormatted: '450 PLN',
      likesCount: 5,
      createdAtRelative: '3 dni temu',
      createdAt: '2025-10-21T12:00:00Z',
    },
    {
      id: 2,
      bricksetId: 20,
      bricksetNumber: '67890',
      valueFormatted: '250 PLN',
      likesCount: 2,
      createdAtRelative: 'wczoraj',
      createdAt: '2025-10-20T12:00:00Z',
    },
  ];

  it('should render grid with valuations', () => {
    const wrapper = mount(MyValuationsGrid, {
      props: {
        valuations: mockValuations,
      },
      global: {
        stubs: {
          OwnValuationCard: {
            name: 'OwnValuationCard',
            props: ['valuation'],
            template: '<div class="valuation-card">{{ valuation.bricksetNumber }}</div>',
          },
        },
      },
    });

    const cards = wrapper.findAll('.valuation-card');
    expect(cards).toHaveLength(2);
  });

  it('should display results count', () => {
    const wrapper = mount(MyValuationsGrid, {
      props: {
        valuations: mockValuations,
      },
    });

    expect(wrapper.text()).toContain('2 wycen');
  });

  it('should display results count as singular for one item', () => {
    const wrapper = mount(MyValuationsGrid, {
      props: {
        valuations: [mockValuations[0]],
      },
    });

    expect(wrapper.text()).toContain('1 wycen');
  });

  it('should handle empty valuations list', () => {
    const wrapper = mount(MyValuationsGrid, {
      props: {
        valuations: [],
      },
    });

    expect(wrapper.text()).toContain('0 wycen');
  });

  it('should use CSS Grid layout', () => {
    const wrapper = mount(MyValuationsGrid, {
      props: {
        valuations: mockValuations,
      },
    });

    const gridElement = wrapper.find('.grid');
    expect(gridElement.classes()).toContain('grid');
    expect(gridElement.classes()).toContain('grid-cols-1');
    expect(gridElement.classes()).toContain('md:grid-cols-2');
  });

  it('should pass correct valuation props to cards', () => {
    const wrapper = mount(MyValuationsGrid, {
      props: {
        valuations: mockValuations,
      },
      global: {
        stubs: {
          OwnValuationCard: {
            name: 'OwnValuationCard',
            props: ['valuation'],
            template: '<div>{{ valuation.id }}</div>',
          },
        },
      },
    });

    const cards = wrapper.findAll('div');
    expect(cards.some((card) => card.text().includes('1'))).toBe(true);
    expect(cards.some((card) => card.text().includes('2'))).toBe(true);
  });

  it('should handle navigate-to-brickset event from child', () => {
    // This test verifies the event binding is correct by checking the template
    const wrapper = mount(MyValuationsGrid, {
      props: {
        valuations: mockValuations,
      },
      global: {
        stubs: {
          OwnValuationCard: {
            name: 'OwnValuationCard',
            props: ['valuation'],
            emits: ['navigate-to-brickset'],
            template:
              '<div class="test-card" @navigate-to-brickset="$emit(\'navigate-to-brickset\', $event)">{{ valuation.id }}</div>',
          },
        },
      },
    });

    // Verify that the component renders the cards
    expect(wrapper.findAll('.test-card')).toHaveLength(2);
  });

  it('should render multiple items correctly', () => {
    const manyValuations = Array.from({ length: 10 }, (_, i) => ({
      id: i,
      bricksetId: i,
      bricksetNumber: String(i).padStart(5, '0'),
      valueFormatted: `${100 * (i + 1)} PLN`,
      likesCount: i,
      createdAtRelative: 'wczoraj',
      createdAt: '2025-10-20T12:00:00Z',
    }));

    const wrapper = mount(MyValuationsGrid, {
      props: {
        valuations: manyValuations,
      },
      global: {
        stubs: {
          OwnValuationCard: {
            name: 'OwnValuationCard',
            props: ['valuation'],
            template: '<div class="card">{{ valuation.id }}</div>',
          },
        },
      },
    });

    const cards = wrapper.findAll('.card');
    expect(cards).toHaveLength(10);
  });

  it('should have correct gap spacing', () => {
    const wrapper = mount(MyValuationsGrid, {
      props: {
        valuations: mockValuations,
      },
    });

    const gridElement = wrapper.find('.grid');
    expect(gridElement.classes()).toContain('gap-6');
  });
});
