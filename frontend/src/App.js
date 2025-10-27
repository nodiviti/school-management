import React, { createContext, useContext, useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Context
const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

// API Helper
const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth Provider
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      api.get('/auth/me')
        .then(res => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    localStorage.setItem('access_token', res.data.access_token);
    localStorage.setItem('refresh_token', res.data.refresh_token);
    const userRes = await api.get('/auth/me');
    setUser(userRes.data);
    return userRes.data;
  };

  const register = async (userData) => {
    await api.post('/auth/register', userData);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected Route
const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" />;
  }

  return children;
};

// Login Page
const LoginPage = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const user = await login(email, password);
      window.location.href = getDashboardRoute(user.role);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const getDashboardRoute = (role) => {
    const routes = {
      superadmin: '/admin',
      admin: '/admin',
      headmaster: '/admin',
      teacher: '/teacher',
      student: '/student',
      parent: '/parent',
      finance: '/finance',
      staff: '/staff',
      librarian: '/library'
    };
    return routes[role] || '/dashboard';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900">School Management</h2>
            <p className="text-gray-600 mt-2">Sign in to your account</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg" data-testid="login-error">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="admin@school.com"
                required
                data-testid="login-email-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                required
                data-testid="login-password-input"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              data-testid="login-submit-button"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            <p>Demo Credentials:</p>
            <p className="text-xs mt-1">Email: admin@school.com | Password: SecurePass123!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Register Page
const RegisterPage = () => {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'student',
    phone: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register(formData);
      setSuccess(true);
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Registration Successful!</h2>
          <p className="text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Create Account</h2>
            <p className="text-gray-600 mt-2">Register for the school management system</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                  data-testid="register-first-name-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                  data-testid="register-last-name-input"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
                data-testid="register-username-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
                data-testid="register-email-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
                minLength={8}
                data-testid="register-password-input"
              />
              <p className="text-xs text-gray-500 mt-1">Min 8 characters, include uppercase, number, and special character</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone (Optional)</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                data-testid="register-phone-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
                data-testid="register-role-select"
              >
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
                <option value="parent">Parent</option>
                <option value="staff">Staff</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              data-testid="register-submit-button"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium">Already have an account? Sign In</a>
          </div>
        </div>
      </div>
    </div>
  );
};

// Dashboard Layout
const DashboardLayout = ({ children, title }) => {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white border-b border-gray-200 fixed w-full z-30 top-0">
        <div className="px-3 py-3 lg:px-5 lg:pl-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center justify-start">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="inline-flex items-center p-2 text-sm text-gray-500 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200"
                data-testid="sidebar-toggle-button"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path clipRule="evenodd" fillRule="evenodd" d="M2 4.75A.75.75 0 012.75 4h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 4.75zm0 10.5a.75.75 0 01.75-.75h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 01-.75-.75zM2 10a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 10z" />
                </svg>
              </button>
              <span className="ml-2 text-xl font-semibold">School Management</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900" data-testid="user-display-name">{user?.first_name} {user?.last_name}</div>
                <div className="text-xs text-gray-500" data-testid="user-display-role">{user?.role}</div>
              </div>
              <button
                onClick={logout}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                data-testid="logout-button"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Sidebar */}
      <aside className={`fixed top-0 left-0 z-20 w-64 h-screen pt-20 transition-transform ${sidebarOpen ? '' : '-translate-x-full'} bg-white border-r border-gray-200`}>
        <div className="h-full px-3 pb-4 overflow-y-auto">
          <ul className="space-y-2 font-medium">
            <NavItem href="/dashboard" icon="📊" label="Dashboard" testId="nav-dashboard" />
            {['superadmin', 'admin', 'headmaster'].includes(user?.role) && (
              <>
                <NavItem href="/students" icon="🎓" label="Students" testId="nav-students" />
                <NavItem href="/teachers" icon="👨‍🏫" label="Teachers" testId="nav-teachers" />
                <NavItem href="/classes" icon="🏫" label="Classes" testId="nav-classes" />
                <NavItem href="/subjects" icon="📚" label="Subjects" testId="nav-subjects" />
              </>
            )}
            <NavItem href="/attendance" icon="✅" label="Attendance" testId="nav-attendance" />
            <NavItem href="/grades" icon="📝" label="Grades" testId="nav-grades" />
            {['finance', 'admin', 'superadmin'].includes(user?.role) && (
              <NavItem href="/finance" icon="💰" label="Finance" testId="nav-finance" />
            )}
            {['librarian', 'admin', 'superadmin'].includes(user?.role) && (
              <NavItem href="/library" icon="📖" label="Library" testId="nav-library" />
            )}
            {['admin', 'superadmin'].includes(user?.role) && (
              <NavItem href="/dormitory" icon="🏠" label="Dormitory" testId="nav-dormitory" />
            )}
          </ul>
        </div>
      </aside>

      {/* Main Content */}
      <div className={`p-4 ${sidebarOpen ? 'sm:ml-64' : ''} mt-14`}>
        <div className="p-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-6" data-testid="page-title">{title}</h1>
          {children}
        </div>
      </div>
    </div>
  );
};

const NavItem = ({ href, icon, label, testId }) => (
  <li>
    <a
      href={href}
      className="flex items-center p-2 text-gray-900 rounded-lg hover:bg-gray-100"
      data-testid={testId}
    >
      <span className="text-xl mr-3">{icon}</span>
      <span>{label}</span>
    </a>
  </li>
);

// Dashboard Pages
const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    total_students: 0,
    total_teachers: 0,
    total_classes: 0,
    attendance_today: 0
  });

  useEffect(() => {
    // Load dashboard stats
    // api.get('/admin/dashboard').then(res => setStats(res.data));
  }, []);

  return (
    <DashboardLayout title="Dashboard">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard icon="🎓" label="Total Students" value="0" color="blue" testId="stat-students" />
        <StatCard icon="👨‍🏫" label="Total Teachers" value="0" color="green" testId="stat-teachers" />
        <StatCard icon="🏫" label="Total Classes" value="0" color="purple" testId="stat-classes" />
        <StatCard icon="✅" label="Attendance Today" value="0%" color="orange" testId="stat-attendance" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <p className="text-gray-500 text-sm">No recent activity</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="space-y-2">
            {user?.role === 'teacher' && (
              <>
                <ActionButton href="/attendance" label="Mark Attendance" />
                <ActionButton href="/grades" label="Enter Grades" />
              </>
            )}
            {user?.role === 'student' && (
              <>
                <ActionButton href="/grades" label="View Grades" />
                <ActionButton href="/attendance" label="View Attendance" />
              </>
            )}
            {['admin', 'superadmin'].includes(user?.role) && (
              <>
                <ActionButton href="/students" label="Manage Students" />
                <ActionButton href="/teachers" label="Manage Teachers" />
                <ActionButton href="/finance" label="View Finance" />
              </>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

const StatCard = ({ icon, label, value, color, testId }) => (
  <div className={`bg-white rounded-lg shadow p-6 border-l-4 border-${color}-500`} data-testid={testId}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-600 mb-1">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
      <div className="text-4xl">{icon}</div>
    </div>
  </div>
);

const ActionButton = ({ href, label }) => (
  <a
    href={href}
    className="block w-full px-4 py-2 text-center text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
  >
    {label}
  </a>
);

const StudentsPage = () => (
  <DashboardLayout title="Students Management">
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <input
          type="text"
          placeholder="Search students..."
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          data-testid="search-students-input"
        />
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" data-testid="add-student-button">
          + Add Student
        </button>
      </div>
      <div className="text-center text-gray-500 py-12">
        <p>No students found. Click "Add Student" to create one.</p>
      </div>
    </div>
  </DashboardLayout>
);

const TeachersPage = () => (
  <DashboardLayout title="Teachers Management">
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <input
          type="text"
          placeholder="Search teachers..."
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" data-testid="add-teacher-button">
          + Add Teacher
        </button>
      </div>
      <div className="text-center text-gray-500 py-12">
        <p>No teachers found.</p>
      </div>
    </div>
  </DashboardLayout>
);

const AttendancePage = () => (
  <DashboardLayout title="Attendance Management">
    <div className="bg-white rounded-lg shadow p-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <select className="px-4 py-2 border border-gray-300 rounded-lg" data-testid="attendance-class-select">
          <option>Select Class</option>
        </select>
        <input type="date" className="px-4 py-2 border border-gray-300 rounded-lg" data-testid="attendance-date-input" />
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700" data-testid="mark-attendance-button">
          Mark Attendance
        </button>
      </div>
      <div className="text-center text-gray-500 py-12">
        <p>Select a class and date to view or mark attendance.</p>
      </div>
    </div>
  </DashboardLayout>
);

const GradesPage = () => (
  <DashboardLayout title="Grades Management">
    <div className="bg-white rounded-lg shadow p-6">
      <div className="text-center text-gray-500 py-12">
        <p>Grades management interface</p>
      </div>
    </div>
  </DashboardLayout>
);

const FinancePage = () => (
  <DashboardLayout title="Finance Management">
    <div className="bg-white rounded-lg shadow p-6">
      <div className="text-center text-gray-500 py-12">
        <p>Finance management interface</p>
      </div>
    </div>
  </DashboardLayout>
);

const LibraryPage = () => (
  <DashboardLayout title="Library Management">
    <div className="bg-white rounded-lg shadow p-6">
      <div className="text-center text-gray-500 py-12">
        <p>Library management interface</p>
      </div>
    </div>
  </DashboardLayout>
);

const UnauthorizedPage = () => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">403</h1>
      <p className="text-gray-600 mb-4">You don't have permission to access this page.</p>
      <a href="/dashboard" className="text-blue-600 hover:text-blue-700">Go to Dashboard</a>
    </div>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/unauthorized" element={<UnauthorizedPage />} />
          
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/admin" element={
            <ProtectedRoute allowedRoles={['superadmin', 'admin', 'headmaster']}>
              <Dashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/students" element={
            <ProtectedRoute allowedRoles={['superadmin', 'admin', 'headmaster', 'teacher']}>
              <StudentsPage />
            </ProtectedRoute>
          } />
          
          <Route path="/teachers" element={
            <ProtectedRoute allowedRoles={['superadmin', 'admin', 'headmaster']}>
              <TeachersPage />
            </ProtectedRoute>
          } />
          
          <Route path="/attendance" element={
            <ProtectedRoute>
              <AttendancePage />
            </ProtectedRoute>
          } />
          
          <Route path="/grades" element={
            <ProtectedRoute>
              <GradesPage />
            </ProtectedRoute>
          } />
          
          <Route path="/finance" element={
            <ProtectedRoute allowedRoles={['superadmin', 'admin', 'finance']}>
              <FinancePage />
            </ProtectedRoute>
          } />
          
          <Route path="/library" element={
            <ProtectedRoute allowedRoles={['superadmin', 'admin', 'librarian', 'teacher', 'student']}>
              <LibraryPage />
            </ProtectedRoute>
          } />
          
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;