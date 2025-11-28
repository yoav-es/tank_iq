// ui/src/composables/useFeedback.ts
import { ref } from 'vue';

export type FeedbackType = 'success' | 'error' | '';

export function useFeedback() {
  const feedbackMessage = ref<string>('');
  const feedbackType = ref<FeedbackType>('');

  function showFeedback(message: string, type: Exclude<FeedbackType, ''>) {
    feedbackMessage.value = message;
    feedbackType.value = type;
    setTimeout(() => {
      feedbackMessage.value = '';
      feedbackType.value = '';
    }, 3000); // auto‑clear after 3 seconds
  }

  return {
    feedbackMessage,
    feedbackType,
    showFeedback,
  };
}
