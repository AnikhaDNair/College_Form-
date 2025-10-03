import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, AppBar, Toolbar, Typography, Container } from '@mui/material';
import Dashboard from './components/Dashboard';
import InvoiceUpload from './components/InvoiceUpload';
import InvoiceList from './components/InvoiceList';
import Reports from './components/Reports';
import Navigation from './components/Navigation';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Back Office AI Agent - Invoice Processing
              </Typography>
            </Toolbar>
          </AppBar>
          
          <Navigation />
          
          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<InvoiceUpload />} />
              <Route path="/invoices" element={<InvoiceList />} />
              <Route path="/reports" element={<Reports />} />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;