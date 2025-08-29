# Frontend Structure Migration Fix Design

## Overview

This document outlines the issues and solution for fixing the frontend application after the src structure migration cleanup. The frontend is currently not working due to incorrect Vite configuration that doesn't match the project's documented structure.

## Problem Analysis

### Current Issues

1. **Incorrect Vite root configuration**: The Vite configuration has `root: '.'` but according to project documentation it should be `root: 'frontend'`
2. **Incorrect index.html script reference**: The index.html file directly references `/frontend/src/main.tsx` which doesn't work with the current Vite configuration
3. **Path resolution issues**: The mismatch between Vite root configuration and file structure is causing module resolution failures

### Root Cause

The project documentation clearly states that the Vite configuration should have `root: 'frontend'` to specify that the frontend source code resides in the `frontend` directory. However, the current configuration has `root: '.'` which causes path resolution issues when trying to reference files.

## Solution Design

### 1. Fix Vite Configuration

Update the Vite configuration to match the documented project structure:

**Current (incorrect):**
```javascript
root: '.', // Указываем, что корень проекта для Vite - это текущая директория
```

**Fixed:**
```javascript
root: 'frontend', // Specify that frontend source code resides in the frontend directory
```

This change aligns the Vite configuration with the project documentation and will properly resolve paths within the frontend directory.

Additionally, there is a discrepancy in the backend port configuration. The README.md states the backend works on port 8000, but the Dockerfile shows it should run on port 8888. The proxy configuration should point to `http://localhost:8888` to match the Dockerfile configuration:

**Current (incorrect):**
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false,
  },
}
```

**Fixed:**
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8888',
    changeOrigin: true,
    secure: false,
  },
}
```

To start the backend on the correct port to match the proxy configuration, use the following command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

Alternatively, if you want to use the default port 8000, update the proxy configuration to point to `http://localhost:8000`.

### 2. Update index.html Entry Point

With the corrected Vite configuration, update the index.html script reference:

**Current (incorrect):**
```html
<script type="module" src="/frontend/src/main.tsx"></script>
```

**Fixed:**
```html
<script type="module" src="/src/main.tsx"></script>
```

With `root: 'frontend'`, Vite will serve from the frontend directory, so `/src/main.tsx` will correctly resolve to `frontend/src/main.tsx`.

### 3. Verify Build Configuration

Ensure the build configuration properly outputs to the correct directory:

```javascript
build: {
  outDir: '../dist', // Output directory relative to frontend directory
  rollupOptions: {
    input: {
      main: path.resolve(__dirname, 'index.html'), // Path relative to frontend directory
    },
  },
}
```

## Implementation Steps

### Step 1: Update Vite Configuration

Modify the vite.config.ts file to set the correct root directory:

```javascript
root: 'frontend', // Specify that frontend source code resides in the frontend directory
```

### Step 2: Update index.html

Modify the script tag in index.html to use the correct path resolution:

```html
<script type="module" src="/src/main.tsx"></script>
```

### Step 3: Test the Fix

1. Run `npm run dev` to start the development server
2. Verify that the application loads correctly in the browser
3. Check that all components and functionality work as expected
4. Run tests to ensure nothing is broken

## Expected Outcomes

After implementing these changes:

1. The frontend application will load correctly in the browser
2. All components will render properly
3. API calls will work as expected
4. The development server will run without path resolution errors
5. Tests will continue to pass

## Rollback Plan

If issues persist after the fix:

1. Revert the vite.config.ts changes
2. Restore the previous index.html script reference
3. Check for any missing dependencies or misconfigured aliases

## Testing Verification

After implementation, verify:

1. Development server starts without errors
2. Application loads in browser
3. All pages and components render correctly
4. Form submissions and API calls work
5. All existing tests continue to pass

## Summary of Changes Needed

To fix the frontend issue, the following changes need to be made:

1. **Update vite.config.ts**:
   - Change `root: '.'` to `root: 'frontend'`
   - Change `outDir: 'dist'` to `outDir: '../dist'` (optional but recommended for consistency with documentation)
   - Update proxy target from `http://localhost:8000` to `http://localhost:8888`

2. **Update index.html**:
   - Change `<script type="module" src="/frontend/src/main.tsx"></script>` to `<script type="module" src="/src/main.tsx"></script>`

These changes will align the Vite configuration with the project's documented structure and properly resolve the frontend module paths.

Additionally, start the backend with the correct port to match the proxy configuration:
```bash
# From the backend directory
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

Alternatively, if you prefer to use the default port 8000, update the proxy configuration to point to `http://localhost:8000`.

## Conclusion

The frontend issue is caused by a mismatch between the Vite configuration and the project's documented structure. By updating the Vite root configuration to `frontend` and correcting the index.html script reference, the frontend should work correctly. The proxy configuration should also be updated to match the backend port to ensure proper API communication.

These changes will restore the frontend functionality while maintaining consistency with the project's documented architecture.3. Check that all components and functionality work as expected
4. Run tests to ensure nothing is broken

## Expected Outcomes

After implementing these changes:

1. The frontend application will load correctly in the browser
2. All components will render properly
3. API calls will work as expected
4. The development server will run without path resolution errors
5. Tests will continue to pass

## Rollback Plan

If issues persist after the fix:

1. Revert the index.html change
2. Restore the previous vite.config.ts if it was modified
3. Check for any missing dependencies or misconfigured aliases
4. Verify that all files were properly migrated from root src/ to frontend/src/

## Testing Verification

After implementation, verify:

1. Development server starts without errors
2. Application loads in browser at http://localhost:5173
3. All pages and components render correctly
4. Form submissions and API calls work
5. All existing tests continue to pass```html
<script type="module" src="/frontend/src/main.tsx"></script>
```

**Fixed:**
```html
<script type="module" src="/src/main.tsx"></script>
```

This change works because Vite's root is set to the project root ('.') and it will resolve /src/main.tsx relative to the root, which correctly points to frontend/src/main.tsx given the directory structure.

### 2. Update Vite Configuration

Adjust the Vite configuration to properly handle the frontend/src structure:

```javascript
export default defineConfig({
  // ... existing plugins config
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
    },
  },
  root: '.', // Keep root as project root
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'),
      },
    },
  },
  server: {
    // ... proxy config
  },
});
```

### 3. Verify TypeScript Configuration

Ensure tsconfig.app.json properly includes the frontend/src directory:

```json
{
  "include": ["frontend/src", "tests"]
}
```

## Implementation Steps

### Step 1: Update index.html

Modify the script tag in index.html to use the correct path resolution:

```html
<script type="module" src="/src/main.tsx"></script>
```

### Step 2: Verify Vite Configuration

Confirm that the vite.config.ts properly resolves the alias paths and has the correct root setting.

### Step 3: Test the Fix

1. Run `npm run dev` to start the development server
2. Verify that the application loads correctly in the browser
3. Check that all components and functionality work as expected
4. Run tests to ensure nothing is broken

## Expected Outcomes

After implementing these changes:

1. The frontend application will load correctly in the browser
2. All components will render properly
3. API calls will work as expected
4. The development server will run without path resolution errors
5. Tests will continue to pass

## Rollback Plan

If issues persist after the fix:

1. Revert the index.html change
2. Restore the previous vite.config.ts if it was modified
3. Check for any missing dependencies or misconfigured aliases
4. Verify that all files were properly migrated from root src/ to frontend/src/

## Testing Verification

After implementation, verify:

1. Development server starts without errors
2. Application loads in browser at http://localhost:5173
3. All pages and components render correctly
4. Form submissions and API calls work
5. All existing tests continue to pass
























































































































