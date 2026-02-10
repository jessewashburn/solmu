import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import Navbar from './components/layout/Navbar';
import HomePage from './pages/HomePage';
import LoadingSpinner from './components/ui/LoadingSpinner';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import './App.css';

// Lazy load pages that aren't immediately needed
const WorkListPage = lazy(() => import('./pages/WorkListPage'));
const ComposerListPage = lazy(() => import('./pages/ComposerListPage'));
const ComposerDetailPage = lazy(() => import('./pages/ComposerDetailPage'));
const WorkDetailPage = lazy(() => import('./pages/WorkDetailPage'));
const SearchPage = lazy(() => import('./pages/SearchPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));
const AdminComposers = lazy(() => import('./pages/AdminComposers'));

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App">
          <Navbar />
          <Suspense fallback={<LoadingSpinner />}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/works" element={<WorkListPage />} />
              <Route path="/composers" element={<ComposerListPage />} />
              <Route path="/composers/:id" element={<ComposerDetailPage />} />
              <Route path="/works/:id" element={<WorkDetailPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/about" element={<AboutPage />} />
              
              {/* Admin routes */}
              <Route path="/admin/login" element={<LoginPage />} />
              <Route 
                path="/admin" 
                element={
                  <ProtectedRoute>
                    <AdminDashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/admin/composers" 
                element={
                  <ProtectedRoute>
                    <AdminComposers />
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </Suspense>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
