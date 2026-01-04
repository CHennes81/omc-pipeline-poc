import { useState } from 'react';
import { AboutDialog } from './AboutDialog';

export function AboutLink() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <a
        href="#"
        onClick={(e) => {
          e.preventDefault();
          setOpen(true);
        }}
        style={{
          textDecoration: 'none',
          color: 'var(--nav-link)',
          marginLeft: 'auto',
        }}
      >
        About
      </a>
      {open && <AboutDialog open={open} onClose={() => setOpen(false)} />}
    </>
  );
}
