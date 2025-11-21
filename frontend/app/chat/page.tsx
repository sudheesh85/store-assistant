'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import ChatContainer from '@/components/ChatContainer';

export default function ChatPage() {
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    // Check authentication and redirect to login if not authenticated
    if (!authService.isAuthenticated()) {
      router.replace('/login');
    } else {
      // Set token for API client
      const token = authService.getToken();
      if (token) {
        apiClient.setAuth(token);
      }
    }
  }, [router]);

  // Show loading during SSR and initial client render
  if (!isClient || !authService.isAuthenticated()) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      <ChatContainer />
    </div>
  );
}

