import { useCallback, useMemo } from 'react';

export function memoizeFunction<T extends (...args: any[]) => any>(
  fn: T,
  deps: any[]
): T {
  return useCallback(fn, deps);
}

export function memoizeValue<T>(value: T, deps: any[]): T {
  return useMemo(() => value, deps);
}