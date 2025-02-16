import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  ThemeProvider,
  createTheme,
  CssBaseline,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import AdminSidebar from './AdminSidebar';
import UserManagement from './admin/UserManagement';
import SystemSettings from './admin/SystemSettings';
import ApiIntegrations from './admin/ApiIntegrations';
import Analytics from './admin/Analytics';
import { darkTheme, lightTheme } from '../themes';

const DashboardContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
}));

const MainContent = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  marginTop: '64px',
}));

const AdminPanel: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [activeSection, setActiveSection] = useState('dashboard');
  const [systemMetrics, setSystemMetrics] = useState({
    users: 0,
    trades: 0,
    revenue: 0,
    activeStrategies: 0,
  });

  const theme = createTheme(darkMode ? darkTheme : lightTheme);

  useEffect(() => {
    // Fetch system metrics
    fetchSystemMetrics();
  }, []);

  const fetchSystemMetrics = async () => {
    try {
      const response = await fetch('/api/admin/metrics');
      const data = await response.json();
      setSystemMetrics(data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  const renderSection = () => {
    switch (activeSection) {
      case 'users':
        return <UserManagement />;
      case 'settings':
        return <SystemSettings />;
      case 'api':
        return <ApiIntegrations />;
      case 'analytics':
        return <Analytics />;
      default:
        return <Dashboard metrics={systemMetrics} />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <DashboardContainer>
        <AdminSidebar
          activeSection={activeSection}
          onSectionChange={setActiveSection}
          onThemeToggle={() => setDarkMode(!darkMode)}
          darkMode={darkMode}
        />
        <MainContent>
          <Container maxWidth="lg">
            {renderSection()}
          </Container>
        </MainContent>
      </DashboardContainer>
    </ThemeProvider>
  );
};

const Dashboard: React.FC<{ metrics: any }> = ({ metrics }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Admin Dashboard
        </Typography>
      </Grid>
      <Grid item xs={12} md={3}>
        <MetricCard title="Total Users" value={metrics.users} />
      </Grid>
      <Grid item xs={12} md={3}>
        <MetricCard title="Total Trades" value={metrics.trades} />
      </Grid>
      <Grid item xs={12} md={3}>
        <MetricCard title="Revenue" value={`$${metrics.revenue}`} />
      </Grid>
      <Grid item xs={12} md={3}>
        <MetricCard title="Active Strategies" value={metrics.activeStrategies} />
      </Grid>
    </Grid>
  );
};

const MetricCard: React.FC<{ title: string; value: string | number }> = ({
  title,
  value,
}) => {
  return (
    <Paper
      sx={{
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Typography variant="h4">{value}</Typography>
    </Paper>
  );
};

export default AdminPanel;
