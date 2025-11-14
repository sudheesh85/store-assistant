'use client';

import { ChangeEvent, useEffect, useRef, useState } from 'react';
import { APIRequest, ChatMessage as MessageType } from '@/types';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { apiClient } from '@/lib/api';
import { storageService } from '@/lib/storage';
import { authService } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { HelpCircle, Loader2, LogOut, Trash2 } from 'lucide-react';

export default function ChatContainer() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState<string>(() => `session-${Date.now()}`);
  const [isCentered, setIsCentered] = useState(true); // Start centered
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const defaultStoreId =
    process.env.NEXT_PUBLIC_STORE_ID || 'demo-store';

  // Don't load chat history - start fresh each session
  // User requested: "each session ends chat should be cleared"
  useEffect(() => {
    // Clear any old chat history on mount
    storageService.clearChatHistory();
  }, []);

  // Save chat history whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      storageService.saveChatHistory(messages);
    }
  }, [messages]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    const defaultOrgId = Number(process.env.NEXT_PUBLIC_DEFAULT_ORG_ID);

    // Move to bottom layout after first message
    if (isCentered) {
      setIsCentered(false);
    }

    // Add user message
    const userMessage: MessageType = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Add placeholder assistant message
    const assistantMessageId = `assistant-${Date.now()}`;
    const assistantMessage: MessageType = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);

    try {
      const request: APIRequest = {
        question: content,
        session_id: sessionId,
        store_id: defaultStoreId,
        // dataset_type is NOT sent - LLM will analyze question and choose the right table automatically
      };

      if (!Number.isNaN(defaultOrgId)) {
        request.org_id = defaultOrgId;
      }

      // Check if streaming is enabled (you can make this configurable)
      const useStreaming = process.env.NEXT_PUBLIC_USE_STREAMING !== 'false';

      if (useStreaming) {
        // Streaming response
        let fullResponse = '';
        
        await apiClient.askQuestionStream(
          request,
          (chunk: string) => {
            fullResponse += chunk;
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, content: fullResponse }
                  : msg
              )
            );
          },
          (response) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? {
                      ...msg,
                      content: response.response || fullResponse,
                      sql: response.sql,
                      data: response.data,
                      visualization: response.visualization,
                      error: response.error,
                    }
                  : msg
              )
            );
            setIsLoading(false);
          },
          (error) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? {
                      ...msg,
                      content: '',
                      error: error.message || 'Failed to get response. Please try again.',
                    }
                  : msg
              )
            );
            setIsLoading(false);
          }
        );
      } else {
        // Non-streaming response
        const response = await apiClient.askQuestion(request);
        
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? {
                  ...msg,
                  content: response.response || '',
                  sql: response.sql,
                  data: response.data,
                  visualization: response.visualization,
                  error: response.error,
                }
              : msg
          )
        );
        setIsLoading(false);
      }
    } catch (error: any) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: '',
                error: error.message || 'Something went wrong. Please try again.',
              }
            : msg
        )
      );
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to clear all chat history?')) {
      setMessages([]);
      storageService.clearChatHistory();
    }
  };

  // Centered layout (before first message)
  if (isCentered && messages.length === 0) {
    return (
      <div className="h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex flex-col">
        {/* Header */}
        <header className="absolute top-0 left-0 right-0 px-4 py-4 flex justify-between items-center z-10">
          <h1 className="text-lg font-bold text-gray-900 dark:text-white">
            AI Store Assistant
          </h1>
          <div className="flex items-center gap-2">
            <button
              onClick={() => router.push('/')}
              className="rounded-lg p-2 text-gray-600 hover:bg-white/50 dark:hover:bg-gray-700 transition-colors"
              title="Go to Home"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Centered Content */}
        <div className="flex-1 flex flex-col items-center justify-center px-4 pb-32">
          <div className="w-full max-w-2xl">
            {/* Welcome Section */}
            <div className="text-center mb-12">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 mb-6 shadow-lg">
                <HelpCircle className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                How can I help you today?
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-400">
                Ask questions in Malayalam, English, or Manglish
              </p>
            </div>

            {/* Example Questions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-12">
              {[
                '💰 ഇന്നത്തെ വിൽപ്പന എത്ര?',
                '📊 Top 5 selling products?',
                '👥 Which staff performed best?',
                '📦 സ്റ്റോക്ക് കുറവുള്ള items?',
              ].map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(question.replace(/^[^\s]+\s/, ''))}
                  className="text-left p-4 bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm rounded-xl hover:bg-white dark:hover:bg-gray-800 transition-all border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md"
                >
                  <p className="text-sm text-gray-700 dark:text-gray-300">{question}</p>
                </button>
              ))}
            </div>

            {/* Input */}
            <div className="relative">
              <ChatInput
                onSend={handleSendMessage}
                isLoading={isLoading}
                placeholder="Type your question here..."
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Bottom layout (after first message)
  return (
    <>
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        <div className="flex flex-1 flex-col">
          {/* Header */}
          <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
            <div className="mx-auto flex max-w-4xl items-center justify-between">
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  Store Assistant
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  🤖 <span className="font-semibold text-primary-600 dark:text-primary-400">AI Automatically Selects the Right Data</span>
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleClearChat}
                  className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200"
                  title="Clear current chat"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
                <button
                  onClick={() => router.push('/')}
                  className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200"
                  title="Go to Home"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
          </header>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-4 py-6">
            <div className="max-w-4xl mx-auto">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex gap-4 mb-6">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                    <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                  </div>
                  <div className="text-gray-500 dark:text-gray-400 italic">
                    Thinking...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-4">
            <div className="max-w-4xl mx-auto">
              <ChatInput
                onSend={handleSendMessage}
                isLoading={isLoading}
                placeholder="Ask about today's sales, top products, staff performance, inventory..."
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
