'use client';

import { useState } from 'react';
import { Key, ArrowRight, HelpCircle, ExternalLink } from 'lucide-react';
import { authService } from '@/lib/auth';

interface OnboardingFlowProps {
  onComplete: () => void;
}

export default function OnboardingFlow({ onComplete }: OnboardingFlowProps) {
  const [step, setStep] = useState<'welcome' | 'setup'>('welcome');
  const [setupOption, setSetupOption] = useState<'demo' | 'openai' | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDemoMode = () => {
    setLoading(true);
    // Set up demo mode - no API key required
    authService.setAuth({
      isAuthenticated: true,
      apiKey: 'demo-mode',
    });
    setTimeout(() => {
      onComplete();
    }, 500);
  };

  const handleOpenAISetup = () => {
    if (!apiKey.trim() || !apiKey.startsWith('sk-')) {
      setError('Please enter a valid OpenAI API key (starts with sk-)');
      return;
    }

    setLoading(true);
    authService.setAuth({
      isAuthenticated: true,
      apiKey: apiKey.trim(),
    });
    
    setTimeout(() => {
      onComplete();
    }, 500);
  };

  if (step === 'welcome') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 px-4">
        <div className="max-w-2xl w-full bg-white/10 backdrop-blur-lg rounded-3xl shadow-2xl p-8 md:p-12 border border-white/20">
          {/* Welcome Content */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-white/20 backdrop-blur-md mb-6">
              <span className="text-4xl">🤖</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Welcome to AI Store Assistant
            </h1>
            <p className="text-xl text-white/90 mb-2">
              Your intelligent retail analytics companion
            </p>
            <p className="text-lg text-white/80">
              Ask questions in Malayalam or English, get instant insights
            </p>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 text-center border border-white/10">
              <div className="text-3xl mb-2">🇮🇳</div>
              <p className="text-white/90 text-sm">Malayalam & English Support</p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 text-center border border-white/10">
              <div className="text-3xl mb-2">📊</div>
              <p className="text-white/90 text-sm">Smart Analytics</p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 text-center border border-white/10">
              <div className="text-3xl mb-2">🔒</div>
              <p className="text-white/90 text-sm">Secure & Private</p>
            </div>
          </div>

          {/* Get Started Button */}
          <button
            onClick={() => setStep('setup')}
            className="w-full bg-white text-purple-600 hover:bg-gray-100 font-bold py-4 px-6 rounded-xl text-lg transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
          >
            Get Started
            <ArrowRight className="w-6 h-6" />
          </button>

          <p className="text-center text-white/70 text-sm mt-6">
            Free for small retail stores • No credit card required
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 px-4">
      <div className="max-w-2xl w-full bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8 md:p-12">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">
            Choose Your Setup
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            How would you like to use AI Store Assistant?
          </p>
        </div>

        {/* Setup Options */}
        <div className="space-y-4 mb-8">
          {/* Demo Mode Option */}
          <button
            onClick={() => setSetupOption('demo')}
            className={`w-full text-left p-6 rounded-xl border-2 transition-all ${
              setupOption === 'demo'
                ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-700'
            }`}
          >
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-2xl">🚀</span>
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  Demo Mode (Recommended)
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-3">
                  Try the app with sample data and limited AI features. Perfect for testing!
                </p>
                <div className="flex flex-wrap gap-2">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                    ✓ No setup required
                  </span>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                    ✓ Start immediately
                  </span>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200">
                    ⚠ Limited AI features
                  </span>
                </div>
              </div>
            </div>
          </button>

          {/* OpenAI Key Option */}
          <button
            onClick={() => setSetupOption('openai')}
            className={`w-full text-left p-6 rounded-xl border-2 transition-all ${
              setupOption === 'openai'
                ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-700'
            }`}
          >
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                <Key className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  Use Your OpenAI API Key
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-3">
                  Get full AI features by connecting your own OpenAI account. Pay only for what you use.
                </p>
                <div className="flex flex-wrap gap-2">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                    ✓ Full AI features
                  </span>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                    ✓ Best quality
                  </span>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                    💰 ~₹10-50/day
                  </span>
                </div>
              </div>
            </div>
          </button>
        </div>

        {/* OpenAI Key Input */}
        {setupOption === 'openai' && (
          <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-6 mb-6">
            <div className="flex items-start gap-3 mb-4">
              <HelpCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-gray-700 dark:text-gray-300">
                <p className="font-medium mb-2">How to get your OpenAI API key:</p>
                <ol className="list-decimal list-inside space-y-1 text-gray-600 dark:text-gray-400">
                  <li>Go to <a href="https://platform.openai.com" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline inline-flex items-center gap-1">platform.openai.com <ExternalLink className="w-3 h-3" /></a></li>
                  <li>Sign up or log in to your account</li>
                  <li>Click "API keys" in the left menu</li>
                  <li>Click "Create new secret key"</li>
                  <li>Copy and paste your key below</li>
                </ol>
              </div>
            </div>

            <div className="mb-4">
              <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                OpenAI API Key
              </label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="apiKey"
                  type="password"
                  value={apiKey}
                  onChange={(e) => {
                    setApiKey(e.target.value);
                    setError('');
                  }}
                  placeholder="sk-..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  disabled={loading}
                />
              </div>
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                Your key is stored securely in your browser only
              </p>
            </div>

            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 mb-4">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={() => setStep('welcome')}
            className="flex-1 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-medium py-3 px-6 rounded-lg transition-colors"
            disabled={loading}
          >
            Back
          </button>
          <button
            onClick={setupOption === 'demo' ? handleDemoMode : handleOpenAISetup}
            disabled={loading || !setupOption || (setupOption === 'openai' && !apiKey.trim())}
            className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Setting up...
              </>
            ) : (
              <>
                Continue
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

