'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';
import ChatContainer from '@/components/ChatContainer';

export default function ChatPage() {
  const router = useRouter();

  useEffect(() => {
    // Check authentication and redirect to login if not authenticated
    if (!authService.isAuthenticated()) {
      router.replace('/login');
    }
  }, [router]);

  // Don't render if not authenticated
  if (!authService.isAuthenticated()) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col">
      <ChatContainer />
    </div>
  );
}

