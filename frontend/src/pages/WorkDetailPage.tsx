import { useState, useEffect } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { workService } from '../lib';
import { Work } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorMessage from '../components/ui/ErrorMessage';
import MetadataList from '../components/ui/MetadataList';
import '../styles/shared/DetailPage.css';

export default function WorkDetailPage() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const [work, setWork] = useState<Work | null>(null);
  const [loading, setLoading] = useState(true);

  // Check if we came from the works list
  const fromWorks = location.state?.from === 'works';

  useEffect(() => {
    loadWork();
  }, [id]);

  const loadWork = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await workService.getById(parseInt(id));
      setWork(data);
    } catch (error) {
      console.error('Error loading work:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!work) return <ErrorMessage title="Work Not Found" message="The requested work could not be found." />;

  const metadataItems = [
    work.catalog_number && { label: 'Catalog Number', value: work.catalog_number },
    work.instrumentation_detail && { label: 'Instrumentation', value: work.instrumentation_detail },
    work.duration_minutes && { label: 'Duration', value: `${work.duration_minutes} minutes` },
    work.movements && { label: 'Movements', value: work.movements },
  ].filter(Boolean) as Array<{ label: string; value: string | number }>;

  return (
    <div className="page-container-narrow">
      {fromWorks ? (
        <Link to="/works" className="back-link">
          ← Back to Works
        </Link>
      ) : work.composer ? (
        <Link to={`/composers/${work.composer.id}`} className="back-link">
          ← Back to Composer
        </Link>
      ) : null}
      
      <header className="detail-header">
        <h1>{work.title}</h1>
        <p className="detail-subtitle">
          by{' '}
          {work.composer ? (
            <Link to={`/composers/${work.composer.id}`}>
              {work.composer.full_name}
            </Link>
          ) : (
            <span>Unknown Composer</span>
          )}
        </p>
      </header>

      <section className="detail-section">
        <h2>Details</h2>
        <MetadataList items={metadataItems} />

        {work.tags && work.tags.length > 0 && (
          <div className="detail-tags">
            <strong>Tags:</strong>
            {work.tags.map((tag) => (
              <span key={tag.id} className="detail-tag">
                {tag.name}
              </span>
            ))}
          </div>
        )}
      </section>

      {(work.imslp_url || work.sheerpluck_url || work.youtube_url || work.score_url) && (
        <section className="detail-section">
          <h2>External Links</h2>
          <div className="external-links">
            {work.imslp_url && (
              <a href={work.imslp_url} target="_blank" rel="noopener noreferrer" className="external-link">
                View on IMSLP →
              </a>
            )}
            {work.sheerpluck_url && (
              <a href={work.sheerpluck_url} target="_blank" rel="noopener noreferrer" className="external-link">
                View on SheerPluck →
              </a>
            )}
            {work.youtube_url && (
              <a href={work.youtube_url} target="_blank" rel="noopener noreferrer" className="external-link">
                Watch on YouTube →
              </a>
            )}
            {work.score_url && (
              <a href={work.score_url} target="_blank" rel="noopener noreferrer" className="external-link">
                View Score →
              </a>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
