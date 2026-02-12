import { Link, Outlet, useNavigate } from 'react-router-dom';
import { authAPI } from '../lib/api';

export default function Layout() {
  const navigate = useNavigate();
  const isAuthenticated = authAPI.isAuthenticated();

  const handleLogout = () => {
    authAPI.logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="bg-blue-600 text-white shadow-lg">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="text-xl font-bold">
              Jones County XC
            </Link>

            <div className="flex gap-6">
              <Link to="/" className="hover:text-blue-200 transition">
                Home
              </Link>
              <Link to="/athletes" className="hover:text-blue-200 transition">
                Athletes
              </Link>
              <Link to="/meets" className="hover:text-blue-200 transition">
                Schedule
              </Link>
              <Link to="/results" className="hover:text-blue-200 transition">
                Results
              </Link>

              {isAuthenticated ? (
                <>
                  <Link to="/admin" className="hover:text-blue-200 transition">
                    Admin
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="hover:text-blue-200 transition"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <Link to="/login" className="hover:text-blue-200 transition">
                  Login
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2026 Jones County Cross Country. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
