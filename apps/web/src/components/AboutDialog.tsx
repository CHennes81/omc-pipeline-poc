import { BUILD_ID } from '../buildConstants';

interface AboutDialogProps {
  open: boolean;
  onClose: () => void;
}

export function AboutDialog({ open, onClose }: AboutDialogProps) {
  const buildDate = new Date(__BUILD_ISO__);
  const formattedBuildDate = new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(buildDate);

  if (!open) return null;

  return (
    <div
      className="modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="about-title"
      id="about-dialog"
      onClick={onClose}
    >
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <h2 id="about-title">About This Build</h2>
        <div style={{ lineHeight: 1.6 }}>
          <div>
            <strong>Version:</strong> {BUILD_ID}
          </div>
          <div>
            <strong>Build Date:</strong> {formattedBuildDate}
          </div>
        </div>
        <div className="modal-actions">
          <button className="btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
