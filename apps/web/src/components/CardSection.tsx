import './CardSection.css';

interface CardSectionProps {
  title: string;
  subtitle?: string;
  warning?: boolean;
  /** Stage key (e.g. DAILIES, or ALL) whose colour tints the header rule. */
  accent?: string;
  children: React.ReactNode;
}

export function CardSection({
  title,
  subtitle,
  warning = false,
  accent,
  children,
}: CardSectionProps) {
  return (
    <div className={`card-section ${warning ? 'card-section-warning' : ''}`} data-accent={accent}>
      <div className="card-section-header">
        <div>
          <h2 className="card-section-title">{title}</h2>
          {subtitle && <p className="card-section-subtitle">{subtitle}</p>}
        </div>
      </div>
      {children}
    </div>
  );
}
