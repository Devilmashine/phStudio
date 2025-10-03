import { useCallback, useMemo, useState } from 'react';

interface UseLegalDocumentResult {
  content: string;
  isLoading: boolean;
  error: string | null;
  load: (force?: boolean) => Promise<void>;
}

export const useLegalDocument = (documentPath: string): UseLegalDocumentResult => {
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resolvedPath = useMemo(() => {
    if (/^https?:/i.test(documentPath)) {
      return documentPath;
    }

    const base = import.meta.env.BASE_URL ?? '/';
    const normalizedBase = base.endsWith('/') ? base.slice(0, -1) : base;
    const normalizedPath = documentPath.startsWith('/') ? documentPath.slice(1) : documentPath;
    return `${normalizedBase}/${normalizedPath}`;
  }, [documentPath]);

  const load = useCallback(
    async (force = false) => {
      if (isLoading) {
        return;
      }

      if (!force && content) {
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(resolvedPath, {
          headers: {
            Accept: 'text/html, text/plain, */*'
          },
          cache: 'no-cache'
        });

        if (!response.ok) {
          throw new Error(`Документ недоступен (HTTP ${response.status})`);
        }

        const text = await response.text();
        setContent(text);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Не удалось загрузить документ';
        setError(message);
      } finally {
        setIsLoading(false);
      }
    },
    [content, isLoading, resolvedPath]
  );

  return {
    content,
    isLoading,
    error,
    load
  };
};

export default useLegalDocument;
