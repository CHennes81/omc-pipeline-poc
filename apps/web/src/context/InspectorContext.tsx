import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

interface InspectorContextValue {
  isOpen: boolean;
  setOpen: (open: boolean) => void;
  toggleOpen: () => void;
  payload: unknown | null;
  setPayload: (obj: unknown | null) => void;
}

const InspectorContext = createContext<InspectorContextValue | null>(null);

export function InspectorProvider({ children }: { children: ReactNode }) {
  const [isOpen, setOpen] = useState(false);
  const [payload, setPayload] = useState<unknown | null>(null);

  const toggleOpen = useCallback(() => setOpen((o) => !o), []);

  const value: InspectorContextValue = {
    isOpen,
    setOpen,
    toggleOpen,
    payload,
    setPayload,
  };

  return <InspectorContext.Provider value={value}>{children}</InspectorContext.Provider>;
}

export function useInspector() {
  const ctx = useContext(InspectorContext);
  if (!ctx) throw new Error('useInspector must be used within InspectorProvider');
  return ctx;
}
