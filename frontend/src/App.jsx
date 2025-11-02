import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthScreen from './components/auth/AuthScreen';
import Header from './components/layout/Header';
import DashboardPage from './pages/DashboardPage';
import GroupPage from './pages/GroupPage';
import Spinner from './components/ui/Spinner';

/**
 * Main Application Component
 */
const AppContent = () => {
  const { user, loading } = useAuth();
  const [page, setPage] = useState('dashboard'); // 'dashboard' | 'group'
  const [currentGroupId, setCurrentGroupId] = useState(null);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (!user) {
    return <AuthScreen />;
  }

  const handleViewGroup = (groupId) => {
    setCurrentGroupId(groupId);
    setPage('group');
  };

  const handleBackToDashboard = () => {
    setCurrentGroupId(null);
    setPage('dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main>
        {page === 'dashboard' && <DashboardPage onViewGroup={handleViewGroup} />}
        {page === 'group' && <GroupPage groupId={currentGroupId} onBack={handleBackToDashboard} />}
      </main>
    </div>
  );
};

/**
 * Root component that wraps the app with AuthProvider
 */
export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
