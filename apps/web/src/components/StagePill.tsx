import './StagePill.css';

interface StagePillProps {
  stage: string;
  count: number;
}

export function StagePill({ stage, count }: StagePillProps) {
  return (
    <div className="stage-pill" data-stage={stage}>
      <div className="stage-pill-label">{stage.replace(/_/g, ' ')}</div>
      <div className="stage-pill-count">{count}</div>
    </div>
  );
}
