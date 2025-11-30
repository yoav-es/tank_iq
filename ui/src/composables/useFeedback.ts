// ui/src/composables/useFeedback.ts
import { ref } from 'vue';

/**
 * Feedback types supported by the composable.
 * - 'success': positive confirmation
 * - 'error': error or failure message
 * - ''      : no feedback active
 */
export type FeedbackType = 'success' | 'error' | '';

/**
 * Composable for showing temporary feedback messages.
 * Provides reactive state and helper functions to display and clear feedback.
 */
export function useFeedback() {
  /** Current feedback message text */
  const feedbackMessage = ref('');

  /** Current feedback type (success, error, or none) */
  const feedbackType = ref<FeedbackType>('');

  /**
   * Show a feedback message of a given type.
   * Automatically clears after 3 seconds.
   *
   * @param message - The feedback text to display
   * @param type - The feedback type ('success' or 'error')
   */
  function showFeedback(message: string, type: Exclude<FeedbackType, ''>) {
    feedbackMessage.value = message;
    feedbackType.value = type;
    setTimeout(() => clearFeedback(), 3000);
  }

  /**
   * Clear the current feedback message and type.
   */
  function clearFeedback() {
    feedbackMessage.value = '';
    feedbackType.value = '';
  }

  return {
    feedbackMessage,
    feedbackType,
    showFeedback,
    clearFeedback,
  };
}
