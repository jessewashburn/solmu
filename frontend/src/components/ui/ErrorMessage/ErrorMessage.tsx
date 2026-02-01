import './ErrorMessage.css';

interface ErrorMessageProps {
  message?: string;
  title?: string;
}

export default function ErrorMessage({ 
  title = 'Error', 
  message = 'Something went wrong. Please try again.' 
}: ErrorMessageProps) {
  return (
    <div className="error-message-container">
      <div className="error-icon">⚠️</div>
      <h2 className="error-title">{title}</h2>
      <p className="error-text">{message}</p>
    </div>
  );
}
