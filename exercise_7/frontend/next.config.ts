import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker
  output: 'standalone',
  
  // Configure API base URL from environment
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8002',
  },
  
  // Enable experimental features for better Docker support
  experimental: {
    // Optimize for Docker containers
    outputFileTracingRoot: process.cwd(),
  },
  
  // Configure rewrites for API proxy (optional)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8002'}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
