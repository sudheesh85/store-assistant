'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, Upload, MessageSquare, TrendingUp, LogOut } from 'lucide-react';
import { authService } from '@/lib/auth';

export default function Home() {
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    // Check authentication and redirect to login if not authenticated
    if (!authService.isAuthenticated()) {
      router.replace('/login');
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

  // Show loading during SSR and initial client render
  if (!isClient || !authService.isAuthenticated()) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600">
      <div className="min-h-screen bg-black/20 backdrop-blur-sm flex items-center justify-center px-4">
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

        <div className="w-full max-w-2xl">
          {/* Header */}
          <div className="text-center text-white mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-white/20 backdrop-blur-md mb-6">
              <Sparkles className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              AI Store Assistant
            </h1>
            <p className="text-xl text-white/90">
              Your intelligent retail analytics assistant for Kerala SMB stores
            </p>
            <p className="text-lg text-white/80 mt-3">
              Ask questions in <strong>Malayalam or English</strong>, get instant insights from your sales, 
              inventory, and staff data.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col gap-4">
            <button
              onClick={handleGetStarted}
              className="bg-white text-purple-600 hover:bg-gray-100 font-bold py-5 px-8 rounded-xl text-lg transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
            >
              <Upload className="w-6 h-6" />
              Upload Data & Get Started
            </button>
            
            <button
              onClick={handleGoToChat}
              className="bg-white/10 backdrop-blur-md text-white border-2 border-white/30 hover:bg-white/20 font-bold py-5 px-8 rounded-xl text-lg transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
            >
              <MessageSquare className="w-6 h-6" />
              Continue to Chat
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

