'use client';

import { ChangeEvent, useEffect, useRef, useState } from 'react';
import { APIRequest, ChatMessage as MessageType } from '@/types';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { apiClient } from '@/lib/api';
import { storageService } from '@/lib/storage';
import { authService } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { HelpCircle, Loader2, LogOut, Trash2, UploadCloud } from 'lucide-react';

export default function ChatContainer() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState<string>(() => `session-${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const [isUploadingDataset, setIsUploadingDataset] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  // Dataset type is no longer used - LLM automatically selects the right table
  // Keeping this state for backward compatibility but not showing it in UI
  const [selectedDatasetType] = useState<string>('auto');
  const defaultStoreId =
    process.env.NEXT_PUBLIC_STORE_ID || 'demo-store';
  const defaultDatasetType =
    process.env.NEXT_PUBLIC_DEFAULT_DATASET_TYPE || 'sales';
  const configuredMaxUpload = Number(process.env.NEXT_PUBLIC_MAX_UPLOAD_MB);
  const maxUploadMb =
    Number.isFinite(configuredMaxUpload) && configuredMaxUpload > 0
      ? configuredMaxUpload
      : 25;

  // Load chat history on mount
  useEffect(() => {
    const history = storageService.loadChatHistory();
    if (history.length > 0) {
      setMessages(history);
    }
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

  const handleUploadButtonClick = () => {
    setUploadError(null);
    fileInputRef.current?.click();
  };

  const handleDatasetSelection = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setUploadError(null);
    setUploadStatus(null);

    const maxBytes = maxUploadMb * 1024 * 1024;
    if (file.size > maxBytes) {
      setUploadError(`File exceeds ${maxUploadMb} MB limit.`);
      event.target.value = '';
      return;
    }

    setIsUploadingDataset(true);
    try {
      const dataset = await apiClient.uploadDataset(
        file,
        selectedDatasetType,
        {
          name: file.name.replace(/\.[^/.]+$/, ''),
          storeId: defaultStoreId,
        }
      );
      setUploadStatus(
        `Uploaded ${dataset.dataset_type} (${dataset.row_count.toLocaleString()} rows)`
      );
    } catch (error: any) {
      setUploadError(error.message || 'Failed to upload dataset.');
    } finally {
      setIsUploadingDataset(false);
      event.target.value = '';
    }
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to clear all chat history?')) {
      setMessages([]);
      storageService.clearChatHistory();
    }
  };

  const handleLogout = () => {
    if (confirm('Are you sure you want to clear your session?')) {
      authService.clearAuth();
      // Authentication is disabled, so just clear auth without redirecting
      // router.push('/login');
    }
  };

  return (
    <>
      <input
        type="file"
        accept=".csv"
        ref={fileInputRef}
        className="hidden"
        onChange={handleDatasetSelection}
      />
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        <aside className="hidden md:flex w-72 flex-col border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
          <div className="px-4 py-5 border-b border-gray-200 dark:border-gray-800">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              🤖 AI Store Assistant
            </h2>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Ask any question in Malayalam or English. AI automatically analyzes all your uploaded data and finds the answer.
            </p>
          </div>
          <div className="px-4 py-4 space-y-3">
            <button
              onClick={handleUploadButtonClick}
              disabled={isUploadingDataset}
              className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isUploadingDataset ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Uploading…
                </>
              ) : (
                <>
                  <UploadCloud className="h-4 w-4" />
                  Upload CSV
                </>
              )}
            </button>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              CSV format, max {maxUploadMb} MB.
            </p>
            {uploadStatus && (
              <p className="text-xs text-green-600 dark:text-green-400">
                {uploadStatus}
              </p>
            )}
            {uploadError && (
              <p className="text-xs text-red-600 dark:text-red-400">
                {uploadError}
              </p>
            )}
          </div>
        </aside>

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
                  onClick={handleUploadButtonClick}
                  className="flex items-center justify-center rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 md:hidden"
                  title="Upload CSV"
                >
                  {isUploadingDataset ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <UploadCloud className="h-5 w-5" />
                  )}
                </button>
                <button
                  onClick={handleClearChat}
                  className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200"
                  title="Clear chat history"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
                <button
                  onClick={handleLogout}
                  className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200"
                  title="Logout"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            </div>
            {uploadStatus && (
              <div className="mt-3 rounded-lg border border-green-100 bg-green-50 px-4 py-2 text-xs text-green-700 dark:border-green-900/50 dark:bg-green-900/30 dark:text-green-300 md:hidden">
                {uploadStatus}
              </div>
            )}
            {uploadError && (
              <div className="mt-3 rounded-lg border border-red-100 bg-red-50 px-4 py-2 text-xs text-red-700 dark:border-red-900/50 dark:bg-red-900/30 dark:text-red-300 md:hidden">
                {uploadError}
              </div>
            )}
          </header>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-4 py-6">
            <div className="max-w-4xl mx-auto">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-12">
                  <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center mb-4">
                    <HelpCircle className="w-8 h-8 text-primary-600 dark:text-primary-400" />
                  </div>
                  <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                    AI assistant for your store
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
                    Ask in Malayalam, Manglish, or English. e.g., "ഇന്ന് മൊത്തം വിൽപ്പന എത്ര?", "Top 5 products by revenue", "Which staff sold most items?"
                  </p>
                </div>
              ) : (
                <>
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
                </>
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
