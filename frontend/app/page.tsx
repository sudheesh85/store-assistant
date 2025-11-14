'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, Upload, MessageSquare, TrendingUp, LogOut } from 'lucide-react';
import { authService } from '@/lib/auth';

export default function Home() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication status
    const authenticated = authService.isAuthenticated();
    setIsAuthenticated(authenticated);
    setIsLoading(false);
    
    // If not authenticated, redirect to login
    if (!authenticated) {
      router.push('/login');
    }
  }, [router]);

  const handleGetStarted = () => {
    router.push('/upload');
  };

  const handleGoToChat = () => {
    router.push('/chat');
  };

  const handleLogout = () => {
    authService.clearAuth();
    router.push('/login');
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  // If not authenticated, don't show anything (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600">
      <div className="min-h-screen bg-black/20 backdrop-blur-sm">
        {/* Logout Button */}
        <div className="absolute top-4 right-4">
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-white/10 hover:bg-white/20 backdrop-blur-md text-white px-4 py-2 rounded-lg transition-colors border border-white/20"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>

        <div className="container mx-auto px-4 py-12">
          {/* Hero Section */}
          <div className="text-center text-white mb-16 pt-12">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-white/20 backdrop-blur-md mb-6">
              <Sparkles className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              AI Store Assistant
            </h1>
            <p className="text-xl md:text-2xl mb-4 text-white/90 max-w-3xl mx-auto">
              Your intelligent retail analytics assistant for Kerala SMB stores
            </p>
            <p className="text-lg text-white/80 max-w-2xl mx-auto">
              Ask questions in <strong>Malayalam or English</strong>, get instant insights from your sales, 
              inventory, and staff data. No technical knowledge required!
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-20">
            <button
              onClick={handleGetStarted}
              className="group bg-white text-purple-600 hover:bg-gray-100 font-bold py-4 px-8 rounded-xl text-lg transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
            >
              <Upload className="w-6 h-6" />
              Upload Data & Get Started
              <span className="text-sm bg-green-500 text-white px-2 py-1 rounded-full">New</span>
            </button>
            
            <button
              onClick={handleGoToChat}
              className="group bg-white/10 backdrop-blur-md text-white border-2 border-white/30 hover:bg-white/20 font-bold py-4 px-8 rounded-xl text-lg transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
            >
              <MessageSquare className="w-6 h-6" />
              Continue to Chat
            </button>
          </div>

          {/* Features Grid */}
          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 text-white border border-white/20">
              <div className="w-14 h-14 rounded-xl bg-blue-500/30 flex items-center justify-center mb-4">
                <span className="text-3xl">🇮🇳</span>
              </div>
              <h3 className="text-xl font-bold mb-3">Malayalam & English</h3>
              <p className="text-white/80">
                Ask questions naturally in your language. Supports Malayalam, English, and Manglish.
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 text-white border border-white/20">
              <div className="w-14 h-14 rounded-xl bg-purple-500/30 flex items-center justify-center mb-4">
                <TrendingUp className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold mb-3">Historical Data</h3>
              <p className="text-white/80">
                Upload daily data and track trends over time. All your historical data is preserved.
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 text-white border border-white/20">
              <div className="w-14 h-14 rounded-xl bg-pink-500/30 flex items-center justify-center mb-4">
                <span className="text-3xl">🤖</span>
              </div>
              <h3 className="text-xl font-bold mb-3">Smart Insights</h3>
              <p className="text-white/80">
                Get AI-powered recommendations and advice, not just numbers. Like having a virtual analyst.
              </p>
            </div>
          </div>

          {/* Example Questions */}
          <div className="max-w-4xl mx-auto mt-16 bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">
              Try asking questions like:
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                'ഇന്നത്തെ വിൽപ്പന എത്ര?',
                'Which products are selling best?',
                'സ്റ്റോക്ക് കുറവുള്ള സാധനങ്ങൾ ഏതൊക്കെ?',
                'Show staff performance this month',
                'How can I improve tea sales?',
                'Yesterday evening revenue?',
              ].map((question, idx) => (
                <div
                  key={idx}
                  className="bg-white/5 hover:bg-white/10 rounded-lg p-3 text-white/90 text-sm transition-colors cursor-pointer border border-white/10"
                >
                  💬 {question}
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="text-center text-white/70 mt-16">
            <p className="text-sm">
              🔐 Your data is secure • 📊 Works offline • 💰 Affordable for SMB
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

