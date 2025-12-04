import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import LoginPage from './pages/LoginPage';
import FilesPage from './pages/FilesPage';

function App() {
  const { checkAuth, isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (user) {
      document.documentElement.setAttribute('data-theme', user.theme);
      document.documentElement.setAttribute('data-accent', user.accent_color);
      document.documentElement.setAttribute('data-icon-size', user.icon_size);
    }
  }, [user]);

  return (
    <div className="app">
      <Routes>
        <Route
          path="/login"
          element={!isAuthenticated ? <LoginPage /> : <Navigate to="/files" />}
        />
        <Route
          path="/files"
          element={isAuthenticated ? <FilesPage /> : <Navigate to="/login" />}
        />
        <Route path="/" element={<Navigate to="/files" />} />
      </Routes>
    </div>
  );
}

export default App;
