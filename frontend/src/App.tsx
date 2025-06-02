import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import BookingPage from './pages/BookingPage';
// import BookingDetailsPage from './pages/BookingDetailsPage'; // Временно убираем, если файла нет
import ProtectedRoute from './components/ProtectedRoute';
import AdminPanel from './pages/AdminPanel';
import ManagerPanel from './pages/ManagerPanel';
import Login from './pages/Login';
import { ToastProvider } from './components/Toast';
// import Spinner from './components/Spinner'; // пример, если потребуется глобальный спиннер

// Если BookingDetailsPage отсутствует, временно убираю этот маршрут:
// <Route path="/booking/:id" element={<BookingDetailsPage />} />

if (typeof window !== "undefined") {
  window.onerror = function (message, source, lineno, colno, error) {
    console.error("[GLOBAL ERROR]", { message, source, lineno, colno, error });
  };
  window.onunhandledrejection = function (event) {
    console.error("[UNHANDLED PROMISE REJECTION]", event.reason);
  };
}

const App: React.FC = () => {
  // const [loading, setLoading] = React.useState(false); // пример глобального спиннера
  return (
    <ToastProvider>
      {/* {loading && <Spinner />} */}
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<BookingPage />} />
            {/* <Route path="/booking/:id" element={<BookingDetailsPage />} /> */}
            <Route path="/login" element={<Login />} />
            <Route
              path="/admin/*"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminPanel />
                </ProtectedRoute>
              }
            />
            <Route
              path="/manager/*"
              element={
                <ProtectedRoute allowedRoles={['admin', 'manager']}>
                  <ManagerPanel />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Layout>
      </Router>
    </ToastProvider>
  );
};

export default App;