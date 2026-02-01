import './PageHeader.css';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  tagline?: string;
  children?: React.ReactNode;
}

export default function PageHeader({ title, subtitle, tagline, children }: PageHeaderProps) {
  return (
    <header className="page-header">
      {tagline && <p className="page-tagline">{tagline}</p>}
      <h1 className="page-title">{title}</h1>
      {subtitle && <p className="page-subtitle">{subtitle}</p>}
      {children && <div className="page-header-content">{children}</div>}
    </header>
  );
}
