const globals = require('globals');
const typescript = require('@typescript-eslint/eslint-plugin');
const reactPlugin = require('eslint-plugin-react');
const reactHooks = require('eslint-plugin-react-hooks');
const eslintConfig = require('@eslint/js'); // Use @eslint/js for recommended config

module.exports = [
  eslintConfig.configs.recommended, // ESLint recommended config
  typescript.configs.recommended, // TypeScript recommended config
  reactPlugin.configs.recommended, // React recommended config
  reactHooks.configs.recommended, // React Hooks recommended config
  {
    plugins: {
      '@typescript-eslint': typescript,
      'react': reactPlugin,
      'react-hooks': reactHooks,
    },
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: {
        ...globals.browser,
      },
      parser: '@typescript-eslint/parser',
    },
    rules: {
      // Custom rules can be added here
      // 'react-refresh/only-export-components': [
      //   'warn',
      //   { allowConstantExport: true },
      // ],
    },
  },
];