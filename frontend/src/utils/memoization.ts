import { useCallback, useMemo } from 'react';

export const useMemoizeFunction = <T extends (...args: any[]) => any>(fn: T): T => {
  return useCallback(fn, [fn]);
};

export const useMemoizeValue = <T>(value: T): T => {
  return useMemo(() => value, [value]);
};