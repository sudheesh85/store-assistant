'use client';

import { useState, KeyboardEvent, useRef, useEffect } from 'react';
import { Send, Loader2, Mic, Square } from 'lucide-react';
import { QueryExample } from '@/types';
import { queryExamples } from '@/lib/queryExamples';
import { apiClient } from '@/lib/api';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

function VoiceInput({ onTranscript, disabled }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [language, setLanguage] = useState<'ml-IN' | 'en-US'>('ml-IN');
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
    }
  }, []);

  const startRecording = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser. Please use Chrome.');
      return;
    }

    recognitionRef.current.lang = language;

    recognitionRef.current.onstart = () => {
      setIsRecording(true);
    };

    recognitionRef.current.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
    };

    recognitionRef.current.onerror = (event: any) => {
      console.error('Speech recognition error', event.error);
      setIsRecording(false);
    };

    recognitionRef.current.start();
  };

  const stopRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop();
    }
  };

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'ml-IN' ? 'en-US' : 'ml-IN');
  };

  if (typeof window !== 'undefined' && !('webkitSpeechRecognition' in window)) {
    return null; // Hide if not supported
  }

  return (
    <div className="flex flex-col gap-1 items-center">
      <button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={disabled}
        className={`flex-shrink-0 w-12 h-12 rounded-lg transition-colors flex items-center justify-center ${isRecording
            ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        title={`Start voice input (${language === 'ml-IN' ? 'Malayalam' : 'English'})`}
      >
        {isRecording ? (
          <Square className="w-5 h-5" />
        ) : (
          <Mic className="w-5 h-5" />
        )}
      </button>
      <button
        onClick={toggleLanguage}
        className="text-[10px] font-medium text-gray-500 hover:text-primary-600 uppercase tracking-wider"
        title="Switch Language"
      >
        {language === 'ml-IN' ? 'MAL' : 'ENG'}
      </button>
    </div>
  );
}

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  showExamples?: boolean;
  placeholder?: string;
  disabled?: boolean;
}

export default function ChatInput({
  onSend,
  isLoading = false,
  showExamples = true,
  placeholder = 'Ask your question...',
  disabled = false,
}: ChatInputProps) {
  const [input, setInput] = useState('');
  const [showExamplePanel, setShowExamplePanel] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    const trimmedInput = input.trim();
    if (trimmedInput && !isLoading && !disabled) {
      onSend(trimmedInput);
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleExampleClick = (example: QueryExample) => {
    setInput(example.text);
    setShowExamplePanel(false);
    textareaRef.current?.focus();
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
      {/* Example Queries Panel */}
      {showExamples && showExamplePanel && (
        <div className="px-4 py-3 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Try asking:
            </h3>
            <div className="flex flex-wrap gap-2">
              {queryExamples.slice(0, 6).map((example) => (
                <button
                  key={example.id}
                  onClick={() => handleExampleClick(example)}
                  className="px-3 py-1.5 text-sm bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-primary-500 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                >
                  {example.text}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              rows={1}
              disabled={isLoading || disabled}
              className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ minHeight: '52px', maxHeight: '200px' }}
            />
            {showExamples && input.length === 0 && (
              <button
                onClick={() => setShowExamplePanel(!showExamplePanel)}
                className="absolute right-3 bottom-3 text-xs text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
              >
                {showExamplePanel ? 'Hide' : 'Show'} examples
              </button>
            )}
          </div>
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading || disabled}
            className="flex-shrink-0 w-12 h-12 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            aria-label="Send message"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>

          {/* Voice Input Button */}
          <VoiceInput onTranscript={(text) => setInput(text)} disabled={isLoading || disabled} />
        </div>
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}

