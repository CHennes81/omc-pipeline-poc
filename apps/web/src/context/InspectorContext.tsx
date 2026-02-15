import { useState, useCallback, type ReactNode } from 'react';
import { InspectorContext } from './inspector-context';

export function InspectorProvider({ children }: { children: ReactNode }) {
  const [isOpen, setOpen] = useState(false);
  const [payload, setPayload] = useState<unknown | null>(null);

  const toggleOpen = useCallback(() => setOpen((o) => !o), []);

  const value = {
    isOpen,
    setOpen,
    toggleOpen,
    payload,
    setPayload,
  };

  return <InspectorContext.Provider value={value}>{children}</InspectorContext.Provider>;
}
