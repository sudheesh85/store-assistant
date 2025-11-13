import { AuthState } from '@/types';

const AUTH_STORAGE_KEY = 'nl2sql_auth';

export const authService = {
  // Get current auth state
  getAuth(): AuthState | null {
    if (typeof window === 'undefined') return null;
    
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!stored) return null;
    
    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  },

  // Set auth state
  setAuth(auth: AuthState): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(auth));
  },

  // Clear auth state
  clearAuth(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(AUTH_STORAGE_KEY);
  },

  // Check if authenticated
  isAuthenticated(): boolean {
    const auth = this.getAuth();
    return auth?.isAuthenticated === true;
  },

  // Get token or API key
  getToken(): string | undefined {
    const auth = this.getAuth();
    return auth?.token || auth?.apiKey;
  },
};

