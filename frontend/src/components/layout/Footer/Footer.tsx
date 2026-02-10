import { Link } from 'react-router-dom';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-links">
          <Link to="/privacy" className="footer-link">Privacy Policy</Link>
          <Link to="/about" className="footer-link">About</Link>
        </div>
        <div className="footer-copyright">
          © {new Date().getFullYear()} Solmu - Guitar Music Network
        </div>
      </div>
    </footer>
  );
}
