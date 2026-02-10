interface ExternalLinksProps {
  imslpUrl?: string | null;
  sheerpluckUrl?: string | null;
  youtubeUrl?: string | null;
  scoreUrl?: string | null;
  variant?: 'default' | 'detailed';
}

export default function ExternalLinks({
  imslpUrl,
  sheerpluckUrl,
  youtubeUrl,
  scoreUrl,
  variant = 'default'
}: ExternalLinksProps) {
  const hasAnyLink = imslpUrl || sheerpluckUrl || youtubeUrl || scoreUrl;

  if (!hasAnyLink) return null;

  const containerClass = variant === 'detailed' ? 'external-links' : 'work-links';
  const linkClass = variant === 'detailed' ? 'external-link' : 'work-link';

  return (
    <div className={containerClass}>
      {imslpUrl && (
        <a 
          href={imslpUrl} 
          target="_blank" 
          rel="noopener noreferrer" 
          className={linkClass}
        >
          View on IMSLP →
        </a>
      )}
      {sheerpluckUrl && (
        <a 
          href={sheerpluckUrl} 
          target="_blank" 
          rel="noopener noreferrer" 
          className={linkClass}
        >
          View on SheerPluck →
        </a>
      )}
      {youtubeUrl && (
        <a 
          href={youtubeUrl} 
          target="_blank" 
          rel="noopener noreferrer" 
          className={linkClass}
        >
          {variant === 'detailed' ? 'Watch on YouTube' : 'View on YouTube'} →
        </a>
      )}
      {scoreUrl && (
        <a 
          href={scoreUrl} 
          target="_blank" 
          rel="noopener noreferrer" 
          className={linkClass}
        >
          View Score →
        </a>
      )}
    </div>
  );
}
