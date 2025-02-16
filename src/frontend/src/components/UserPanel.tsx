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
  Button,
  IconButton,
  Dialog,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import TradingViewWidget from './trading/TradingViewWidget';
import OrderBook from './trading/OrderBook';
import StrategyBuilder from './trading/StrategyBuilder';
import Portfolio from './trading/Portfolio';
import AISignals from './trading/AISignals';
import { darkTheme, lightTheme } from '../themes';
import UserSidebar from './UserSidebar';
import CustomizationPanel from './customization/CustomizationPanel';
import { DragDropContext, Droppable } from 'react-beautiful-dnd';

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

const UserPanel: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [activeSection, setActiveSection] = useState('trading');
  const [layout, setLayout] = useState(null);
  const [customizing, setCustomizing] = useState(false);
  const [portfolioData, setPortfolioData] = useState(null);
  const [aiSignals, setAISignals] = useState([]);

  const theme = createTheme(darkMode ? darkTheme : lightTheme);

  useEffect(() => {
    // Load user's saved layout
    loadUserLayout();
    // Fetch portfolio data
    fetchPortfolioData();
    // Fetch AI signals
    fetchAISignals();
  }, []);

  const loadUserLayout = async () => {
    try {
      const response = await fetch('/api/user/layout');
      const data = await response.json();
      setLayout(data);
    } catch (error) {
      console.error('Error loading layout:', error);
    }
  };

  const fetchPortfolioData = async () => {
    try {
      const response = await fetch('/api/user/portfolio');
      const data = await response.json();
      setPortfolioData(data);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    }
  };

  const fetchAISignals = async () => {
    try {
      const response = await fetch('/api/user/ai-signals');
      const data = await response.json();
      setAISignals(data);
    } catch (error) {
      console.error('Error fetching AI signals:', error);
    }
  };

  const handleLayoutChange = async (newLayout) => {
    try {
      await fetch('/api/user/layout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newLayout),
      });
      setLayout(newLayout);
    } catch (error) {
      console.error('Error saving layout:', error);
    }
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const newLayout = { ...layout };
    // Update component positions
    handleLayoutChange(newLayout);
  };

  const renderSection = () => {
    switch (activeSection) {
      case 'trading':
        return (
          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="dashboard">
              {(provided) => (
                <Grid
                  container
                  spacing={2}
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                >
                  <Grid item xs={12} md={8}>
                    <TradingViewWidget />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <OrderBook />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <AISignals signals={aiSignals} />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Portfolio data={portfolioData} />
                  </Grid>
                  {provided.placeholder}
                </Grid>
              )}
            </Droppable>
          </DragDropContext>
        );
      case 'strategy':
        return <StrategyBuilder />;
      case 'portfolio':
        return <Portfolio data={portfolioData} fullWidth />;
      case 'settings':
        return <UserSettings />;
      default:
        return null;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <DashboardContainer>
        <UserSidebar
          activeSection={activeSection}
          onSectionChange={setActiveSection}
          onThemeToggle={() => setDarkMode(!darkMode)}
          darkMode={darkMode}
        />
        <MainContent>
          <Container maxWidth="xl">
            <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="h4">
                {activeSection.charAt(0).toUpperCase() + activeSection.slice(1)}
              </Typography>
              <Button
                variant="contained"
                color="primary"
                onClick={() => setCustomizing(true)}
              >
                Customize Dashboard
              </Button>
            </Box>
            {renderSection()}
          </Container>
        </MainContent>

        <Dialog
          fullScreen
          open={customizing}
          onClose={() => setCustomizing(false)}
        >
          <CustomizationPanel
            layout={layout}
            onSave={(newLayout) => {
              handleLayoutChange(newLayout);
              setCustomizing(false);
            }}
            onClose={() => setCustomizing(false)}
          />
        </Dialog>
      </DashboardContainer>
    </ThemeProvider>
  );
};

const UserSettings: React.FC = () => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            User Settings
          </Typography>
          {/* Add settings components */}
        </Paper>
      </Grid>
    </Grid>
  );
};

export default UserPanel;
