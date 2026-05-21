import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      'chat/MainContent': path.resolve(__dirname, './packages/chat/src/components/MainContent.tsx'),
      'chat/ChatSidebar': path.resolve(__dirname, './packages/chat/src/components/ChatSidebar.tsx'),
      'upload/UploadPage': path.resolve(__dirname, './packages/upload/src/components/UploadPage.tsx'),
      '@mfa/shared': path.resolve(__dirname, './packages/shared/src/index.ts'),
    },
  },
  test: {
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: true,
      },
    },
    fileParallelism: false,
    globals: true,
    environment: 'jsdom',
    setupFiles: './setupTests.ts',
    coverage: {
      provider: 'istanbul',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      },
      include: ['packages/**/src/**/*.{ts,tsx}'],
      exclude: ['packages/**/src/main.tsx', 'packages/**/src/vite-env.d.ts', '**/*.d.ts']
    },
  },
});