'use client';

import { useEffect } from 'react';
import { authService } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import ChatContainer from '@/components/ChatContainer';

export default function Home() {
  useEffect(() => {
    // Authentication is disabled for testing
    // If auth exists, use it; otherwise proceed without auth
    const auth = authService.getAuth();
    
    if (auth && auth.isAuthenticated) {
      // Set up API client with auth if available
      if (auth.token) {
        apiClient.setAuth(auth.token);
      } else if (auth.apiKey) {
        apiClient.setAuth(undefined, auth.apiKey);
      }
    }
    // If no auth, proceed without authentication headers
  }, []);

  return <ChatContainer />;
}

