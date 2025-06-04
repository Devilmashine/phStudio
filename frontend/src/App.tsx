import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Studios from './components/Studios';
import BookingForm from './components/BookingForm';
import Footer from './components/Footer';
import AdminPanel from './pages/AdminPanel';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import { StudioSettingsForm } from './components/StudioSettingsForm';
import { Gallery } from './components/Gallery';
import NewsAdmin from './pages/NewsAdmin';
import BookingTable from './components/BookingTable';
import { ToastProvider } from './components/Toast';

const Dashboard = () => (
  <div>
    <h2 className="text-xl font-bold mb-4">Бронирования</h2>
    <BookingTable />
  </div>
);

function App() {
  return (
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
                        className="text-indigo-600 hover:underline font-semibold border border-indigo-600 px-4 py-2 rounded-lg transition-colors"
                      >
                        Войти в админ-панель
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
                <Route index element={<Dashboard />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="settings" element={<StudioSettingsForm />} />
                <Route path="gallery" element={<Gallery />} />
                <Route path="news" element={<NewsAdmin />} />
                <Route path="schedule" element={<div>Расписание (заглушка)</div>} />
                <Route path="*" element={<Dashboard />} />
              </Route>
              <Route path="/login" element={<Login />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </ToastProvider>
  );
}

export default App;