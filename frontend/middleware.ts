import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Get auth token from cookie or localStorage simulation
  const authCookie = request.cookies.get('nl2sql_auth');
  
  // Public paths that don't require authentication
  const publicPaths = ['/login'];
  const isPublicPath = publicPaths.includes(pathname);
  
  // Protected paths
  const protectedPaths = ['/', '/chat', '/upload'];
  const isProtectedPath = protectedPaths.includes(pathname);
  
  // If user is not authenticated and trying to access protected path
  if (isProtectedPath && !authCookie) {
    // Redirect to login
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  // If user is authenticated and trying to access login page
  if (isPublicPath && authCookie) {
    // Redirect to home
    return NextResponse.redirect(new URL('/', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ['/', '/login', '/chat', '/upload'],
};
