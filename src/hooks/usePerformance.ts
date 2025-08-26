import { useCallback, useMemo, useRef, useEffect, useState } from 'react';

/**
 * Performance optimization hooks for React components
 */

// Debounce hook for input fields
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Throttle hook for scroll events and similar
export const useThrottle = <T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T => {
  const throttledCallback = useRef<T>();
  const lastExecuted = useRef<number>(0);

  return useCallback(
    ((...args) => {
      const now = Date.now();
      
      if (now - lastExecuted.current >= delay) {
        lastExecuted.current = now;
        return callback(...args);
      }
    }) as T,
    [callback, delay]
  );
};

// Memoized calculation hook
export const useMemoizedCalculation = <T>(
  calculation: () => T,
  dependencies: React.DependencyList
): T => {
  return useMemo(calculation, dependencies);
};

// Stable callback hook to prevent unnecessary re-renders
export const useStableCallback = <T extends (...args: any[]) => any>(
  callback: T
): T => {
  const callbackRef = useRef<T>(callback);
  
  useEffect(() => {
    callbackRef.current = callback;
  });

  return useCallback(
    ((...args) => callbackRef.current(...args)) as T,
    []
  );
};

// Hook for lazy loading components
export const useLazyLoad = (triggerRef: React.RefObject<Element>) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (triggerRef.current) {
      observer.observe(triggerRef.current);
    }

    return () => observer.disconnect();
  }, [triggerRef]);

  return isVisible;
};

// Performance measurement hook
export const usePerformanceMonitor = (componentName: string) => {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(Date.now());

  useEffect(() => {
    renderCount.current += 1;
    const now = Date.now();
    const timeSinceLastRender = now - lastRenderTime.current;
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`${componentName} rendered ${renderCount.current} times. Time since last render: ${timeSinceLastRender}ms`);
    }
    
    lastRenderTime.current = now;
  });
};

// Bundle loading optimization
export const usePreloadComponent = (componentLoader: () => Promise<any>) => {
  useEffect(() => {
    const preloadTimer = setTimeout(() => {
      componentLoader().catch(() => {
        // Ignore preload errors
      });
    }, 100);

    return () => clearTimeout(preloadTimer);
  }, [componentLoader]);
};

// Memory leak prevention for async operations
export const useAsyncOperation = () => {
  const isMounted = useRef(true);

  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  const safeSetState = useCallback((setter: () => void) => {
    if (isMounted.current) {
      setter();
    }
  }, []);

  return { isMounted: isMounted.current, safeSetState };
};