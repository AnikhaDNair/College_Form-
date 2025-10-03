import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  AttachMoney as MoneyIcon,
  Description as InvoiceIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import { apiClient } from '../services/api';

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/reports/summary');
      setSummary(response.data);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Error fetching summary:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  const stats = [
    {
      title: 'Total Invoices',
      value: summary?.total_invoices || 0,
      icon: <InvoiceIcon sx={{ fontSize: 40 }} />,
      color: '#1976d2',
    },
    {
      title: 'Processed',
      value: summary?.total_processed || 0,
      icon: <CheckIcon sx={{ fontSize: 40 }} />,
      color: '#4caf50',
    },
    {
      title: 'With Issues',
      value: (summary?.status_breakdown?.FAILED || 0) + (summary?.status_breakdown?.WARNING || 0),
      icon: <WarningIcon sx={{ fontSize: 40 }} />,
      color: '#ff9800',
    },
    {
      title: 'Passed',
      value: summary?.status_breakdown?.PASSED || 0,
      icon: <CheckIcon sx={{ fontSize: 40 }} />,
      color: '#4caf50',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Box sx={{ color: stat.color, mr: 2 }}>
                    {stat.icon}
                  </Box>
                  <Box>
                    <Typography variant="h4" component="div">
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.title}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {summary?.status_breakdown && (
        <Box mt={4}>
          <Typography variant="h6" gutterBottom>
            Processing Status Breakdown
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(summary.status_breakdown).map(([status, count]) => (
              <Grid item xs={12} sm={6} md={3} key={status}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="primary">
                      {count}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {status}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Box>
  );
}

export default Dashboard;