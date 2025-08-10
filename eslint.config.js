import typescript from '@typescript-eslint/eslint-plugin';
import reactPlugin from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import eslintConfig from '@eslint/js';
import tsParser from '@typescript-eslint/parser';

export default [
  {
    ignores: ['venv/', '.venv/', 'node_modules/', 'dist/', '**/site-packages/', '**/emscripten_fetch_worker.js', '**/debugger.js'],
  },
  eslintConfig.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: {
        // Standard browser globals
        'window': 'readonly',
        'document': 'readonly',
        'navigator': 'readonly',
        'console': 'readonly',
        'fetch': 'readonly',
        'setTimeout': 'readonly',
        'clearTimeout': 'readonly',
        'setInterval': 'readonly',
        'clearInterval': 'readonly',
        'Promise': 'readonly',
        'Error': 'readonly',
        'Array': 'readonly',
        'Object': 'readonly',
        'Date': 'readonly',
        'Math': 'readonly',
        'JSON': 'readonly',
        
        // Additional globals
        'process': 'readonly',
        'URL': 'readonly',
        'URLSearchParams': 'readonly',
        'Blob': 'readonly',
        'alert': 'readonly',
        'React': 'readonly',
        'HTMLInputElement': 'readonly',
        'localStorage': 'readonly',
        'HTMLElement': 'readonly',
        'RequestInit': 'readonly',
        'self': 'readonly',
        'TextEncoder': 'readonly',
        'requestAnimationFrame': 'readonly',
        'JSX': 'readonly',
        'File': 'readonly',
        'FormData': 'readonly',
        'atob': 'readonly',
        'HTMLTextAreaElement': 'readonly',
        'RequestInfo': 'readonly',
        'Response': 'readonly'
      },
      parser: tsParser,
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    plugins: {
      '@typescript-eslint': typescript,
      'react': reactPlugin,
      'react-hooks': reactHooks,
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
    rules: {
      ...typescript.configs.recommended.rules,
      ...reactPlugin.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off',
      'react/prop-types': 'off',
      'react/display-name': 'off',  // Disable display name requirement
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/no-explicit-any': 'off',  // Allow any type
      '@typescript-eslint/no-unused-vars': ['warn', { 
        'argsIgnorePattern': '^_',
        'varsIgnorePattern': '^_',
      }],
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      'react/no-unescaped-entities': 'warn',
    },
  },
  {
    files: ['**/*.test.{ts,tsx}', '**/*.spec.ts', '**/*.test.js'],
    languageOptions: {
      globals: {
        'jest': 'readonly',
        'describe': 'readonly',
        'it': 'readonly',
        'expect': 'readonly',
        'beforeEach': 'readonly',
        'afterEach': 'readonly',
        'beforeAll': 'readonly',
        'afterAll': 'readonly',
      }
    }
  },
  {
    files: ['**/*.js', '**/*.cjs', '**/*.mjs'],
    languageOptions: {
      globals: {
        'module': 'readonly',
        'require': 'readonly',
        '__dirname': 'readonly',
        'global': 'readonly'
      }
    }
  },
  {
    files: ['frontend/src/tests/**/*.tsx', 'tests/**/*.tsx'],
    languageOptions: {
      globals: {
        'jest': 'readonly',
        'describe': 'readonly',
        'it': 'readonly',
        'expect': 'readonly',
        'beforeEach': 'readonly',
        'afterEach': 'readonly',
        'beforeAll': 'readonly',
        'afterAll': 'readonly',
      }
    }
  }
];
