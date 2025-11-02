import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import ValuationCard from '@/components/bricksets/ValuationCard.vue';
import LikeButton from '@/components/bricksets/LikeButton.vue';
import type { ValuationViewModel } from '@/types/bricksets';

describe('ValuationCard Component', () => {
  const createMockValuation = (
    overrides: Partial<ValuationViewModel> = {}
  ): ValuationViewModel => ({
    id: 1,
    userId: 10,
    valueFormatted: '450 PLN',
    comment: 'Great set in excellent condition!',
    likesCount: 15,
    createdAtRelative: '2 dni temu',
    createdAt: '2024-01-01T10:00:00Z',
    ...overrides,
  });

  beforeEach(() => {
    // Reset mocks before each test
  });

  type ValuationCardProps = {
    valuation: ValuationViewModel;
    canLike: boolean;
    currentUserId: number | null;
    isLikedByMe?: boolean;
  };

  const mountComponent = (props: Partial<ValuationCardProps>) => {
    const pinia = createPinia();
    return mount(ValuationCard, {
      props: Object.assign({}, props),
      global: {
        plugins: [pinia],
        mocks: {
          $t: (key: string) => key,
        },
      },
    });
  };

  it('renders valuation with all information', () => {
    const valuation = createMockValuation();

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: 20,
    });

    expect(wrapper.text()).toContain('450 PLN');
    expect(wrapper.text()).toContain('Great set in excellent condition!');
    expect(wrapper.text()).toContain('2 dni temu');
    expect(wrapper.text()).toContain('#10');
  });

  it('renders LikeButton component', () => {
    const valuation = createMockValuation();

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: 20,
    });

    expect(wrapper.findComponent(LikeButton).exists()).toBe(true);
  });

  it('disables like button when user is the author', () => {
    const valuation = createMockValuation({ userId: 10 });

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: 10, // Same as valuation.userId
    });

    const likeButton = wrapper.findComponent(LikeButton);
    expect(likeButton.props('disabled')).toBe(true);
  });

  it('disables like button when currentUserId is null', () => {
    const valuation = createMockValuation();

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: null,
    });

    const likeButton = wrapper.findComponent(LikeButton);
    expect(likeButton.props('disabled')).toBe(true);
  });

  it('enables like button when user is not the author and currentUserId exists', () => {
    const valuation = createMockValuation({ userId: 10 });

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: 20,
    });

    const likeButton = wrapper.findComponent(LikeButton);
    expect(likeButton.props('disabled')).toBe(false);
  });

  it('truncates long comments', () => {
    const longComment = 'A'.repeat(250);
    const valuation = createMockValuation({ comment: longComment });

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: 20,
    });

    const commentText = wrapper.find('.text-gray-300').text();
    expect(commentText.length).toBeLessThan(longComment.length);
    expect(commentText).toContain('...');
  });

  it('shows expand button for long comments', () => {
    const longComment = 'A'.repeat(250);
    const valuation = createMockValuation({ comment: longComment });

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: 20,
    });

    const expandButton = wrapper.find('button.text-blue-400');
    expect(expandButton.exists()).toBe(true);
  });

  it('expands comment when expand button is clicked', async () => {
    const longComment = 'A'.repeat(250);
    const valuation = createMockValuation({ comment: longComment });

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: 20,
    });

    const expandButton = wrapper.find('button.text-blue-400');
    await expandButton.trigger('click');

    const commentText = wrapper.find('.text-gray-300').text();
    expect(commentText.length).toBe(longComment.length);
    expect(commentText).not.toContain('...');
  });

  it('does not show expand button for short comments', () => {
    const shortComment = 'Short comment';
    const valuation = createMockValuation({ comment: shortComment });

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: 20,
    });

    const expandButton = wrapper.find('button.text-blue-400');
    expect(expandButton.exists()).toBe(false);
  });

  it('displays empty comment correctly', () => {
    const valuation = createMockValuation({ comment: '' });

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: 20,
    });

    expect(wrapper.text()).toContain('450 PLN');
    expect(wrapper.text()).toContain('#10');
  });

  it('passes correct likesCount to LikeButton', () => {
    const valuation = createMockValuation({ likesCount: 42 });

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: 20,
    });

    const likeButton = wrapper.findComponent(LikeButton);
    expect(likeButton.props('likesCount')).toBe(42);
  });

  it('passes isLiked prop to LikeButton when provided', () => {
    const valuation = createMockValuation();

    const wrapper = mountComponent({
      valuation,
      canLike: true,
      currentUserId: 20,
      isLikedByMe: true,
    });

    const likeButton = wrapper.findComponent(LikeButton);
    expect(likeButton.props('isLiked')).toBe(true);
  });
});
