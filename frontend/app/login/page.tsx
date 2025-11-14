'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/lib/auth';
import OnboardingFlow from '@/components/OnboardingFlow';

export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect if already authenticated
    if (authService.isAuthenticated()) {
      router.push('/');
    }
  }, [router]);

  const handleOnboardingComplete = () => {
    router.push('/');
  };

  return <OnboardingFlow onComplete={handleOnboardingComplete} />;
}

