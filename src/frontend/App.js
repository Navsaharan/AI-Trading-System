import React, { useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Box, CircularProgress } from '@mui/material';

// Layouts
import DashboardLayout from './layouts/DashboardLayout';
import AuthLayout from './layouts/AuthLayout';

// Pages
import Dashboard from './pages/Dashboard';
import Trading from './pages/Trading';
import Portfolio from './pages/Portfolio';
import Analysis from './pages/Analysis';
import Backtesting from './pages/Backtesting';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Register from './pages/Register';
import NotFound from './pages/NotFound';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import AlertSnackbar from './components/AlertSnackbar';

// Hooks
import { useAuth } from './hooks/useAuth';
import { useWebSocket } from './hooks/useWebSocket';

// Actions
import { setUser, clearUser } from './store/slices/authSlice';
import { setMarketData } from './store/slices/marketSlice';

const App = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();
  const { lastMessage } = useWebSocket('ws://localhost:5000/ws');

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);
        if (data.type === 'MARKET_DATA') {
          dispatch(setMarketData(data.payload));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    }
  }, [lastMessage, dispatch]);

  // Handle authentication state
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token && !isLoading) {
      dispatch(clearUser());
      navigate('/login');
    }
  }, [isLoading, dispatch, navigate]);

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <>
      <Routes>
        {/* Auth Routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>

        {/* Protected Routes */}
        <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} />}>
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/trading" element={<Trading />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/backtesting" element={<Backtesting />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>

        {/* 404 Route */}
        <Route path="*" element={<NotFound />} />
      </Routes>

      {/* Global Components */}
      <AlertSnackbar />
    </>
  );
};

export default App;
