'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import ChatContainer from '@/components/ChatContainer';

export default function ChatPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    const auth = authService.getAuth();
    
    if (!auth || !auth.isAuthenticated) {
      // Redirect to login if not authenticated
      router.push('/login');
      return;
    }
    
    setIsAuthenticated(true);
    setIsLoading(false);
    
    // Set up API client with auth
    if (auth.token) {
      apiClient.setAuth(auth.token);
    } else if (auth.apiKey) {
      apiClient.setAuth(undefined, auth.apiKey);
    }
  }, [router]);

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  // Don't render if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col">
      <ChatContainer />
    </div>
  );
}

