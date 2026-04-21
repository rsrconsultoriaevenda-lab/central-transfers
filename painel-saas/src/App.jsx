import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Pedidos from './pages/Pedidos';

// Simples verificação de rota protegida
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const Layout = ({ children }) => (
  <div className="flex flex-col min-h-screen bg-slate-50">
    <nav className="bg-white border-b border-slate-200 px-8 py-4 flex justify-between items-center sticky top-0 z-50">
      <div className="flex items-center gap-10">
        <span className="font-black text-2xl text-indigo-600 tracking-tighter italic">CENTRAL TRANSFERS</span>
        <div className="flex gap-6">
          <Link to="/" className="text-sm font-bold text-slate-600 hover:text-indigo-600 transition-colors uppercase tracking-widest">Dashboard</Link>
          <Link to="/pedidos" className="text-sm font-bold text-slate-600 hover:text-indigo-600 transition-colors uppercase tracking-widest">Pedidos</Link>
        </div>
      </div>
      <button onClick={() => { localStorage.removeItem('token'); window.location.href='/login'; }} className="text-slate-400 hover:text-red-500 font-bold text-xs uppercase transition-colors">Sair</button>
    </nav>
    {children}
  </div>
);

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <Layout><Dashboard /></Layout>
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/pedidos" 
          element={
            <ProtectedRoute>
              <Layout><Pedidos /></Layout>
            </ProtectedRoute>
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;