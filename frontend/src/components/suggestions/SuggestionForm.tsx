import { useState } from 'react';
import axios from 'axios';
import './SuggestionForm.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Function to get CSRF token from cookies
const getCSRFToken = () => {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

export default function SuggestionForm() {
  const [formData, setFormData] = useState({
    suggestion_type: 'new_work',
    title: '',
    description: '',
    submitter_name: '',
    submitter_email: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus('idle');
    setErrorMessage('');

    try {
      // Get CSRF token first
      await axios.get(`${API_URL}/auth/csrf/`, { withCredentials: true });
      const csrfToken = getCSRFToken();
      
      // Submit with CSRF token
      await axios.post(`${API_URL}/suggestions/`, formData, {
        withCredentials: true,
        headers: {
          'X-CSRFToken': csrfToken,
        }
      });
      setSubmitStatus('success');
      setFormData({
        suggestion_type: 'new_work',
        title: '',
        description: '',
        submitter_name: '',
        submitter_email: '',
      });
    } catch (error: any) {
      setSubmitStatus('error');
      setErrorMessage(error.response?.data?.detail || 'Failed to submit suggestion. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="suggestion-form-container">
      <h2>Submit a Suggestion</h2>
      <p className="form-description">
        Have a new work, composer, or correction to suggest? Let us know!
      </p>

      {submitStatus === 'success' && (
        <div className="alert alert-success">
          ✓ Thank you! Your suggestion has been submitted and will be reviewed by our team.
        </div>
      )}

      {submitStatus === 'error' && (
        <div className="alert alert-error">
          {errorMessage}
        </div>
      )}

      <form onSubmit={handleSubmit} className="suggestion-form">
        <div className="form-group">
          <label htmlFor="suggestion_type">Type</label>
          <select
            id="suggestion_type"
            value={formData.suggestion_type}
            onChange={(e) => setFormData({ ...formData, suggestion_type: e.target.value })}
            required
          >
            <option value="new_work">New Work</option>
            <option value="new_composer">New Composer</option>
            <option value="edit_work">Edit Existing Work</option>
            <option value="edit_composer">Edit Existing Composer</option>
            <option value="correction">Correction/Error Report</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            id="title"
            type="text"
            placeholder="Brief summary of your suggestion"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
            maxLength={200}
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description *</label>
          <textarea
            id="description"
            rows={6}
            placeholder="Provide details about your suggestion..."
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="submitter_name">Your Name (optional)</label>
            <input
              id="submitter_name"
              type="text"
              placeholder="Your name"
              value={formData.submitter_name}
              onChange={(e) => setFormData({ ...formData, submitter_name: e.target.value })}
              maxLength={100}
            />
          </div>

          <div className="form-group">
            <label htmlFor="submitter_email">Your Email (optional)</label>
            <input
              id="submitter_email"
              type="email"
              placeholder="your@email.com"
              value={formData.submitter_email}
              onChange={(e) => setFormData({ ...formData, submitter_email: e.target.value })}
            />
          </div>
        </div>

        <button type="submit" className="submit-button" disabled={isSubmitting}>
          {isSubmitting ? 'Submitting...' : 'Submit Suggestion'}
        </button>
      </form>
    </div>
  );
}
