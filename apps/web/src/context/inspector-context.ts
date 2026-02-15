import { createContext, useContext } from 'react';

export interface InspectorContextValue {
  isOpen: boolean;
  setOpen: (open: boolean) => void;
  toggleOpen: () => void;
  payload: unknown | null;
  setPayload: (obj: unknown | null) => void;
}

export const InspectorContext = createContext<InspectorContextValue | null>(null);

export function useInspector() {
  const ctx = useContext(InspectorContext);
  if (!ctx) throw new Error('useInspector must be used within InspectorProvider');
  return ctx;
}
