import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="admin-dashboard">
      <div className="admin-simple">
        <h1>Admin Mode</h1>
        <p>Logged in as: <strong>{user?.username}</strong></p>
        
        <div className="admin-actions">
          <Link to="/admin/composers" className="admin-link">
            Edit Composers
          </Link>
          <Link to="/works" className="admin-link">
            Edit Works  
          </Link>
          <button onClick={handleLogout} className="admin-link admin-logout">
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
