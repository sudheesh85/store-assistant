'use client';

import { ChatMessage as MessageType } from '@/types';
import { User, Bot, Copy, Check, Eye, EyeOff } from 'lucide-react';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import dynamic from 'next/dynamic';

const SyntaxHighlighter = dynamic(
  () => import('react-syntax-highlighter').then((mod) => mod.Prism),
  { ssr: false }
);
import DataVisualization from './DataVisualization';
import { format } from 'date-fns';

interface ChatMessageProps {
  message: MessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const [showSQL, setShowSQL] = useState(false);
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopySQL = () => {
    if (message.sql) {
      navigator.clipboard.writeText(message.sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className={`flex gap-4 mb-6 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser 
          ? 'bg-primary-600 text-white' 
          : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
      }`}>
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-3xl ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-2`}>
        <div className={`rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-primary-600 text-white rounded-br-sm'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-sm'
        }`}>
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="space-y-4">
              {/* Error Message */}
              {message.error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
                  <p className="text-sm text-red-600 dark:text-red-400">{message.error}</p>
                </div>
              )}

              {/* Main Response */}
              {message.content && (
                <div className="markdown-content prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code({ node, inline, className, children, ...props }: any) {
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                          <SyntaxHighlighter
                            language={match[1]}
                            PreTag="div"
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        );
                      },
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              )}

              {/* SQL Query (Hidden by default for non-technical users) */}
              {message.sql && (
                <div className="mt-4 border-t border-gray-200 dark:border-gray-700 pt-4">
                  <div className="flex items-center justify-between mb-2">
                    <button
                      onClick={() => setShowSQL(!showSQL)}
                      className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
                    >
                      {showSQL ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      {showSQL ? 'Hide' : 'Show'} SQL Query
                    </button>
                    {showSQL && (
                      <button
                        onClick={handleCopySQL}
                        className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
                      >
                        {copied ? (
                          <>
                            <Check className="w-4 h-4" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4" />
                            Copy
                          </>
                        )}
                      </button>
                    )}
                  </div>
                  {showSQL && (
                    <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                      <SyntaxHighlighter
                        language="sql"
                        customStyle={{ 
                          margin: 0, 
                          background: 'transparent',
                          color: '#d4d4d4',
                          fontSize: '14px',
                        }}
                        PreTag="div"
                      >
                        {message.sql}
                      </SyntaxHighlighter>
                    </div>
                  )}
                </div>
              )}

              {/* Data Visualization */}
              {message.data && !message.error && (
                <div className="mt-4">
                  <DataVisualization
                    data={message.data}
                    visualization={message.visualization}
                  />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Timestamp */}
        <span className={`text-xs text-gray-500 dark:text-gray-400 ${isUser ? 'text-right' : 'text-left'}`}>
          {format(message.timestamp, 'h:mm a')}
        </span>
      </div>
    </div>
  );
}

