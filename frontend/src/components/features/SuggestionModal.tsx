import { useState } from 'react';
import './SuggestionModal.css';

interface SuggestionModalProps {
  isOpen: boolean;
  onClose: () => void;
  itemType: 'composer' | 'work';
  itemData: any;
}

export default function SuggestionModal({ isOpen, onClose, itemType, itemData }: SuggestionModalProps) {
  const [formData, setFormData] = useState<any>(itemData);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus('idle');

    try {
      const response = await fetch('http://localhost:8000/api/suggestions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item_type: itemType,
          item_id: itemData.id,
          original_data: itemData,
          suggested_data: formData,
          comment: comment,
        }),
      });

      if (response.ok) {
        setSubmitStatus('success');
        setTimeout(() => {
          onClose();
          setSubmitStatus('idle');
          setComment('');
        }, 2000);
      } else {
        setSubmitStatus('error');
      }
    } catch (error) {
      console.error('Error submitting suggestion:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (field: string, value: any) => {
    setFormData({ ...formData, [field]: value });
  };

  const renderComposerFields = () => (
    <>
      <div className="form-group">
        <label>Full Name</label>
        <input
          type="text"
          value={formData.full_name || ''}
          onChange={(e) => handleChange('full_name', e.target.value)}
        />
      </div>
      <div className="form-row">
        <div className="form-group">
          <label>Birth Year</label>
          <input
            type="number"
            value={formData.birth_year || ''}
            onChange={(e) => handleChange('birth_year', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Death Year</label>
          <input
            type="number"
            value={formData.death_year || ''}
            onChange={(e) => handleChange('death_year', e.target.value)}
          />
        </div>
      </div>
      <div className="form-group">
        <label>Country</label>
        <input
          type="text"
          value={formData.country_name || ''}
          onChange={(e) => handleChange('country_name', e.target.value)}
        />
      </div>
      <div className="form-group">
        <label>Period</label>
        <input
          type="text"
          value={formData.period || ''}
          onChange={(e) => handleChange('period', e.target.value)}
        />
      </div>
    </>
  );

  const renderWorkFields = () => (
    <>
      <div className="form-group">
        <label>Title</label>
        <input
          type="text"
          value={formData.title || ''}
          onChange={(e) => handleChange('title', e.target.value)}
        />
      </div>
      <div className="form-group">
        <label>Composer</label>
        <input
          type="text"
          value={formData.composer?.full_name || ''}
          disabled
        />
      </div>
      <div className="form-group">
        <label>Instrumentation</label>
        <input
          type="text"
          value={formData.instrumentation || ''}
          onChange={(e) => handleChange('instrumentation', e.target.value)}
        />
      </div>
      <div className="form-group">
        <label>Year Composed</label>
        <input
          type="number"
          value={formData.year_composed || ''}
          onChange={(e) => handleChange('year_composed', e.target.value)}
        />
      </div>
    </>
  );

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Suggest Changes</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="suggestion-form">
          {itemType === 'composer' ? renderComposerFields() : renderWorkFields()}

          <div className="form-group">
            <label>Additional Comments (optional)</label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Explain your suggested changes..."
              rows={3}
            />
          </div>

          {submitStatus === 'success' && (
            <div className="success-message">
              Thank you! Your suggestion has been submitted.
            </div>
          )}

          {submitStatus === 'error' && (
            <div className="error-message">
              Failed to submit suggestion. Please try again.
            </div>
          )}

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-cancel">
              Cancel
            </button>
            <button type="submit" disabled={isSubmitting} className="btn-submit">
              {isSubmitting ? 'Submitting...' : 'Submit Suggestion'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
