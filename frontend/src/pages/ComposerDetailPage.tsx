import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { composerService } from '../lib';
import { Composer, Work } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorMessage from '../components/ui/ErrorMessage';
import MetadataList from '../components/ui/MetadataList';
import '../styles/shared/DetailPage.css';

export default function ComposerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [composer, setComposer] = useState<Composer | null>(null);
  const [works, setWorks] = useState<Work[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadComposer();
  }, [id]);

  const loadComposer = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const [composerData, worksData] = await Promise.all([
        composerService.getById(parseInt(id)),
        composerService.getWorks(parseInt(id)),
      ]);
      setComposer(composerData);
      setWorks(worksData);
    } catch (error) {
      console.error('Error loading composer:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!composer) return <ErrorMessage title="Composer Not Found" message="The requested composer could not be found." />;

  const hasDates = composer.birth_year || composer.death_year || composer.is_living;
  const birth = composer.birth_year || '?';
  const death = composer.death_year || (composer.is_living ? 'present' : '?');

  const metadataItems = [
    composer.country && { label: 'Country', value: composer.country.name },
    composer.period && { label: 'Period', value: composer.period },
    { label: 'Works', value: works.length },
  ].filter(Boolean) as Array<{ label: string; value: string | number }>;

  return (
    <div className="page-container-narrow">
      <Link to="/composers" className="back-link">← Back to Composers</Link>
      
      <header className="detail-header">
        <h1>{composer.full_name}</h1>
        {hasDates && (
          <p className="detail-subtitle">
            {birth} – {death}
          </p>
        )}
        
        <MetadataList items={metadataItems} />

        {composer.biography && (
          <div className="detail-biography">
            <p>{composer.biography}</p>
          </div>
        )}
      </header>

      <section className="detail-section">
        <h2>Works ({works.length})</h2>
        <div className="works-grid">
          {works.map((work) => (
            <Link
              key={work.id}
              to={`/works/${work.id}`}
              className="work-card"
            >
              <h3>{work.title}</h3>
              {work.catalog_number && (
                <p className="work-card-meta">
                  Catalog: {work.catalog_number}
                </p>
              )}
              {work.instrumentation_detail && (
                <p className="work-card-meta">
                  {work.instrumentation_detail}
                </p>
              )}
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
