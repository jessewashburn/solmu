import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface User {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
  is_superuser: boolean;
  first_name?: string;
  last_name?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Configure axios defaults for session authentication
axios.defaults.withCredentials = true;

// Function to get CSRF cookie value
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

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = async () => {
    try {
      // First get CSRF token
      await axios.get(`${API_URL}/auth/csrf/`);
      
      // Then check if user is authenticated
      const response = await axios.get(`${API_URL}/auth/user/`);
      setUser(response.data);
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    // Get CSRF token first
    await axios.get(`${API_URL}/auth/csrf/`);
    
    // Get the CSRF token from cookie and set in header
    const csrfToken = getCSRFToken();
    
    // Perform login
    const response = await axios.post(`${API_URL}/auth/login/`, {
      username,
      password,
    }, {
      headers: {
        'X-CSRFToken': csrfToken,
      }
    });
    
    setUser(response.data.user);
  };

  const logout = async () => {
    try {
      // Get the CSRF token from cookie and set in header
      const csrfToken = getCSRFToken();
      
      await axios.post(`${API_URL}/auth/logout/`, {}, {
        headers: {
          'X-CSRFToken': csrfToken,
        }
      });
    } catch (error) {
      // Even if the server logout fails, we still want to clear local state
      console.error('Logout request failed:', error);
    } finally {
      // Always clear the user state locally
      setUser(null);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
