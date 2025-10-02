import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { UserCog } from 'lucide-react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Studios from './components/Studios';
import BookingForm from './components/BookingForm';
import Footer from './components/Footer';
import AdminPanel from './pages/AdminPanel';
import ManagerPanel from './pages/ManagerPanel';
import Login from './pages/Login';
import PrivacyPolicy from './pages/PrivacyPolicy';
import CookiePolicy from './pages/CookiePolicy';
import ProtectedRoute from './components/ProtectedRoute';
import { StudioSettingsForm } from './components/StudioSettingsForm';
import { Gallery } from './components/Gallery';
import NewsAdmin from './pages/NewsAdmin';
import BookingTable from './components/BookingTable';
import { ToastProvider } from './components/Toast';
import AdminCalendarPage from './pages/AdminCalendarPage';
import UserManagement from './components/UserManagement';
import CookieConsentBanner from './components/CookieConsentBanner';
import { EnhancedAdminDashboard } from './components/enhanced';
import { DarkModeProvider } from './contexts/DarkModeContext';
import KanbanBoard from './components/KanbanBoard';

const Dashboard = () => (
  <div>
    <h2 className="text-xl font-bold mb-4">Бронирования</h2>
    <BookingTable />
  </div>
);

function App() {
  return (
    <DarkModeProvider>
      <ToastProvider>
        <Router>
          <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-grow">
              <Routes>
                <Route
                  path="/"
                  element={
                    <>
                      <Hero />
                      <Studios />
                      <BookingForm />
                      <div className="flex justify-center mt-8">
                        <a
                          href="/admin"
                          className="inline-flex items-center justify-center w-12 h-12 border border-indigo-600 rounded-full text-indigo-600 hover:bg-indigo-50 transition-colors"
                          aria-label="Вход для сотрудников"
                        >
                          <UserCog className="h-6 w-6" />
                        </a>
                      </div>
                    </>
                  }
                />
                <Route
                  path="/admin"
                  element={
                    <ProtectedRoute allowedRoles={['admin']}>
                      <AdminPanel />
                    </ProtectedRoute>
                  }
                >
                  <Route index element={<EnhancedAdminDashboard />} />
                  <Route path="dashboard" element={<EnhancedAdminDashboard />} />
                  <Route path="settings" element={<StudioSettingsForm />} />
                  <Route path="gallery" element={<Gallery />} />
                  <Route path="news" element={<NewsAdmin />} />
                  <Route path="schedule" element={<KanbanBoard />} />
                  <Route path="calendar" element={<AdminCalendarPage />} />
                  <Route path="users" element={<UserManagement />} />
                  <Route path="*" element={<EnhancedAdminDashboard />} />
                </Route>
                <Route
                  path="/manager"
                  element={
                    <ProtectedRoute allowedRoles={['admin', 'manager']}>
                      <ManagerPanel />
                    </ProtectedRoute>
                  }
                />
                <Route path="/login" element={<Login />} />
                <Route path="/privacy" element={<PrivacyPolicy />} />
                <Route path="/cookie-policy" element={<CookiePolicy />} />
              </Routes>
            </main>
            <Footer />
            <CookieConsentBanner />
          </div>
        </Router>
      </ToastProvider>
    </DarkModeProvider>
  );
}

export default App;