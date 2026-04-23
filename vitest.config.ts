import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [sveltekit()],
  test: {
    include: ['src/**/*.{test,spec}.{js,ts}', 'tests/ui/**/*.{test,spec}.{js,ts}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary', 'json', 'html'],
      reportsDirectory: './coverage',
      include: ['src/**/*.{js,ts,svelte}'],
      exclude: ['src/**/*.d.ts', 'src/app.html', 'src/**/*.test.{js,ts}', 'src/**/*.spec.{js,ts}']
    }
  }
});
