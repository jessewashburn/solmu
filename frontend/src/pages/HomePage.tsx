import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { workService, composerService } from '../lib';
import { Work, Composer } from '../types';
import './HomePage.css';

// Generate a random work ID based on today's date
const getDailyWorkId = (totalWorks: number): number => {
  const today = new Date();
  const seed = today.getFullYear() * 10000 + (today.getMonth() + 1) * 100 + today.getDate();
  // Use date as seed for consistent random selection per day
  const random = Math.sin(seed) * 10000;
  const normalized = random - Math.floor(random);
  return Math.floor(normalized * totalWorks) + 1;
};

export default function HomePage() {
  const [highlightedWork, setHighlightedWork] = useState<Work | null>(null);
  const [composer, setComposer] = useState<Composer | null>(null);
  const [loading, setLoading] = useState(true);
  const [totalComposers, setTotalComposers] = useState<number>(0);
  const [totalWorks, setTotalWorks] = useState<number>(0);

  useEffect(() => {
    loadHighlightedWork();
  }, []);

  const loadHighlightedWork = async () => {
    setLoading(true);
    try {
      // Get total counts
      const [worksResponse, composersResponse] = await Promise.all([
        workService.getAll(1, ''),
        composerService.getAll(1, '')
      ]);
      
      setTotalWorks(worksResponse.count);
      setTotalComposers(composersResponse.count);
      
      // Get today's work ID
      const workId = getDailyWorkId(worksResponse.count);
      
      // Fetch the highlighted work
      const work = await workService.getById(workId);
      setHighlightedWork(work);
      
      // Fetch full composer details if available
      if (work.composer) {
        const composerData = await composerService.getById(work.composer.id);
        setComposer(composerData);
      }
    } catch (error) {
      console.error('Error loading highlighted work:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      <section className="highlighted-work-section">
        <h2 className="section-title">Today's Highlighted Work</h2>
        <p className="section-description">
          Each day we highlight a randomly selected work from our collection.
        </p>
        {loading ? (
          <div className="highlighted-work-card loading">
            <p>Loading today's work...</p>
          </div>
        ) : highlightedWork ? (
          <div className="highlighted-work-card">
            <div className="work-header">
              <h3 className="work-title">
                <Link to={`/works/${highlightedWork.id}`} className="work-title-link">
                  {highlightedWork.title}
                </Link>
              </h3>
              <div className="work-composer">
                <span className="composer-by">by </span>
                {highlightedWork.composer ? (
                  <Link to={`/composers/${highlightedWork.composer.id}`} className="composer-link">
                    {highlightedWork.composer.full_name}
                  </Link>
                ) : (
                  <span>Unknown Composer</span>
                )}
              </div>
              {composer && (
                <div className="composer-metadata">
                  {composer.birth_year && (
                    <div className="composer-meta-item">
                      <span className="meta-label">Born</span>
                      <span className="meta-value">
                        {composer.death_year
                          ? `${composer.birth_year}–${composer.death_year}`
                          : composer.birth_year}
                      </span>
                    </div>
                  )}
                  {composer.country && (
                    <div className="composer-meta-item">
                      <span className="meta-label">Country</span>
                      <span className="meta-value">{composer.country.name}</span>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="work-metadata">
              {highlightedWork.instrumentation_detail && (
                <div className="metadata-item">
                  <span className="metadata-label">Instrumentation</span>
                  <span className="metadata-value">{highlightedWork.instrumentation_detail}</span>
                </div>
              )}
              {highlightedWork.catalog_number && (
                <div className="metadata-item">
                  <span className="metadata-label">Catalog Number</span>
                  <span className="metadata-value">{highlightedWork.catalog_number}</span>
                </div>
              )}
              {highlightedWork.duration_minutes && (
                <div className="metadata-item">
                  <span className="metadata-label">Duration</span>
                  <span className="metadata-value">{highlightedWork.duration_minutes} min</span>
                </div>
              )}
              {highlightedWork.movements && (
                <div className="metadata-item">
                  <span className="metadata-label">Movements</span>
                  <span className="metadata-value">{highlightedWork.movements}</span>
                </div>
              )}
            </div>

            {highlightedWork.tags && highlightedWork.tags.length > 0 && (
              <div className="work-tags">
                <strong>Tags:</strong>
                {highlightedWork.tags.map((tag) => (
                  <span key={tag.id} className="work-tag">
                    {tag.name}
                  </span>
                ))}
              </div>
            )}

            {(highlightedWork.imslp_url || highlightedWork.sheerpluck_url || highlightedWork.youtube_url || highlightedWork.score_url) && (
              <div className="work-links">
                {highlightedWork.imslp_url && (
                  <a href={highlightedWork.imslp_url} target="_blank" rel="noopener noreferrer" className="work-link">
                    View on IMSLP →
                  </a>
                )}
                {highlightedWork.sheerpluck_url && (
                  <a href={highlightedWork.sheerpluck_url} target="_blank" rel="noopener noreferrer" className="work-link">
                    View on SheerPluck →
                  </a>
                )}
                {highlightedWork.youtube_url && (
                  <a href={highlightedWork.youtube_url} target="_blank" rel="noopener noreferrer" className="work-link">
                    View on YouTube →
                  </a>
                )}
                {highlightedWork.score_url && (
                  <a href={highlightedWork.score_url} target="_blank" rel="noopener noreferrer" className="work-link">
                    View Score →
                  </a>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="highlighted-work-card error">
            <p>Could not load today's highlighted work</p>
          </div>
        )}
      </section>

      <section className="browse-section">
        <h2 className="section-title">Explore the Database</h2>
        <p className="section-description">
          Our comprehensive database features {totalComposers.toLocaleString()} composers and {totalWorks.toLocaleString()} works, spanning centuries of guitar music from around the world.
        </p>
        <div className="browse-cards">
          <Link to="/composers" className="browse-card">
            <h3>Browse Composers</h3>
            <p>Explore our complete collection of classical guitar composers</p>
          </Link>
          <Link to="/works" className="browse-card">
            <h3>Browse Works</h3>
            <p>Discover thousands of guitar works from across history</p>
          </Link>
        </div>
      </section>
    </div>
  );
}
