import { ChatMessage } from '@/types';

const CHAT_HISTORY_KEY = 'nl2sql_chat_history';
const MAX_HISTORY = parseInt(process.env.NEXT_PUBLIC_MAX_CHAT_HISTORY || '100', 10);

export const storageService = {
  // Save chat history
  saveChatHistory(messages: ChatMessage[]): void {
    if (typeof window === 'undefined') return;
    
    // Keep only the last MAX_HISTORY messages
    const limitedMessages = messages.slice(-MAX_HISTORY);
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(limitedMessages));
  },

  // Load chat history
  loadChatHistory(): ChatMessage[] {
    if (typeof window === 'undefined') return [];
    
    const stored = localStorage.getItem(CHAT_HISTORY_KEY);
    if (!stored) return [];
    
    try {
      const messages = JSON.parse(stored);
      // Convert timestamp strings back to Date objects
      return messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      }));
    } catch {
      return [];
    }
  },

  // Clear chat history
  clearChatHistory(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(CHAT_HISTORY_KEY);
  },
};

