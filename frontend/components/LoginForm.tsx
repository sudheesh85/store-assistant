'use client';

import { useState, FormEvent } from 'react';
import { LogIn, Key, Mail, Lock } from 'lucide-react';
import { authService } from '@/lib/auth';
import { apiClient } from '@/lib/api';

interface LoginFormProps {
  onLoginSuccess: () => void;
}

export default function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [authType, setAuthType] = useState<'api_key' | 'jwt'>('api_key');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (authType === 'api_key') {
        // API Key authentication
        if (!apiKey.trim()) {
          setError('Please enter your API key');
          setLoading(false);
          return;
        }

        // Store API key and authenticate
        authService.setAuth({
          isAuthenticated: true,
          apiKey: apiKey.trim(),
        });

        // Set API key in client
        apiClient.setAuth(undefined, apiKey.trim());

        // Test connection
        const isHealthy = await apiClient.healthCheck();
        if (!isHealthy) {
          console.warn('Health check failed, but proceeding with authentication');
        }

        onLoginSuccess();
      } else {
        // JWT authentication
        if (!email.trim() || !password.trim()) {
          setError('Please enter both email and password');
          setLoading(false);
          return;
        }

        // In a real implementation, you would call the auth endpoint
        // For now, we'll simulate it
        const authEndpoint = process.env.NEXT_PUBLIC_AUTH_ENDPOINT || '/api/v1/auth/login';
        
        // This is a placeholder - implement actual JWT login
        setError('JWT authentication not fully implemented. Please use API Key for now.');
        setLoading(false);
        return;
      }
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 px-4">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-full mb-4">
            <Key className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome Back
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Sign in to ask questions about your data
          </p>
        </div>

        {/* Auth Type Toggle */}
        <div className="flex gap-2 mb-6 p-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
          <button
            type="button"
            onClick={() => setAuthType('api_key')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              authType === 'api_key'
                ? 'bg-white dark:bg-gray-600 text-primary-600 dark:text-primary-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400'
            }`}
          >
            API Key
          </button>
          <button
            type="button"
            onClick={() => setAuthType('jwt')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              authType === 'jwt'
                ? 'bg-white dark:bg-gray-600 text-primary-600 dark:text-primary-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400'
            }`}
          >
            Email & Password
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {authType === 'api_key' ? (
            <div>
              <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                API Key
              </label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="apiKey"
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your API key"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  disabled={loading}
                />
              </div>
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                Your API key is stored securely in your browser
              </p>
            </div>
          ) : (
            <>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your.email@example.com"
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    disabled={loading}
                  />
                </div>
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    disabled={loading}
                  />
                </div>
              </div>
            </>
          )}

          {authType === 'jwt' && (
            <div className="flex items-center">
              <input
                id="rememberMe"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                disabled={loading}
              />
              <label htmlFor="rememberMe" className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                Remember me
              </label>
            </div>
          )}

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Signing in...
              </>
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                Sign In
              </>
            )}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          Don't have an account?{' '}
          <a href="#" className="text-primary-600 hover:text-primary-700 font-medium">
            Contact your administrator
          </a>
        </p>
      </div>
    </div>
  );
}

