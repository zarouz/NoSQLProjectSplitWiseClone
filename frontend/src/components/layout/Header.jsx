import { useAuth } from '../../context/AuthContext';

/**
 * Header component for the main app
 */
const Header = () => {
  const { user, logout } = useAuth();
  return (
    <header className="bg-white shadow-md">
      <nav className="container mx-auto px-4 py-3 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-blue-600">Splitwise</h1>
        <div className="flex items-center space-x-4">
          <span className="text-gray-700 hidden sm:block">{user.email}</span>
          <button
            onClick={logout}
            className="px-4 py-2 bg-gray-200 text-gray-700 font-semibold rounded-md hover:bg-gray-300 transition-all"
          >
            Logout
          </button>
        </div>
      </nav>
    </header>
  );
};

export default Header;
