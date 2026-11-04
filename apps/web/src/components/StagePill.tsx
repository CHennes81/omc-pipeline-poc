import './StagePill.css';

interface StagePillProps {
  stage: string;
  count: number;
  /** Override the displayed label (defaults to the stage name with underscores removed). */
  label?: string;
  /** When provided, the pill renders as a toggle button. */
  onClick?: () => void;
  /** Selected state, only meaningful when onClick is provided. */
  selected?: boolean;
}

export function StagePill({ stage, count, label, onClick, selected = false }: StagePillProps) {
  const content = (
    <>
      <div className="stage-pill-label">{label ?? stage.replace(/_/g, ' ')}</div>
      <div className="stage-pill-count">{count}</div>
    </>
  );

  if (onClick) {
    return (
      <button
        type="button"
        className="stage-pill"
        data-stage={stage}
        aria-pressed={selected}
        disabled={count === 0}
        onClick={onClick}
      >
        {content}
      </button>
    );
  }

  return (
    <div className="stage-pill" data-stage={stage}>
      {content}
    </div>
  );
}
