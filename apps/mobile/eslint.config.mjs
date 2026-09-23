import js from '@eslint/js';
import { defineConfig } from 'eslint/config';
import tseslint from 'typescript-eslint';
import hooks from 'eslint-plugin-react-hooks';

export default defineConfig([
  { ignores: ['node_modules/**', '.work/**', '.expo/**'] },
  {
    files: ['**/*.{mjs,ts,tsx}'],
    extends: [js.configs.recommended, tseslint.configs.recommended],
    languageOptions: { globals: { process: 'readonly' } },
  },
  {
    files: ['src/**/*.{ts,tsx}'],
    plugins: { 'react-hooks': hooks },
    rules: { 'react-hooks/rules-of-hooks': 'error', 'react-hooks/exhaustive-deps': 'error' },
  },
]);
