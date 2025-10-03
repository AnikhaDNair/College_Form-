import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Grid,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { apiClient } from '../services/api';

function Reports() {
  const [discrepancies, setDiscrepancies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDiscrepancies();
  }, []);

  const fetchDiscrepancies = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/reports/discrepancies');
      setDiscrepancies(response.data.discrepancies || []);
    } catch (err) {
      setError('Failed to fetch discrepancy report');
      console.error('Error fetching discrepancies:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'HIGH':
        return <ErrorIcon color="error" />;
      case 'MEDIUM':
        return <WarningIcon color="warning" />;
      case 'LOW':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'HIGH':
        return 'error';
      case 'MEDIUM':
        return 'warning';
      case 'LOW':
        return 'info';
      default:
        return 'default';
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

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Discrepancy Reports
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Invoices Requiring Attention ({discrepancies.length})
              </Typography>
              
              {discrepancies.length === 0 ? (
                <Alert severity="success">
                  No discrepancies found! All invoices have been processed successfully.
                </Alert>
              ) : (
                <Box>
                  {discrepancies.map((item, index) => (
                    <Accordion key={index} sx={{ mb: 2 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box display="flex" alignItems="center" width="100%">
                          <Box mr={2}>
                            {getSeverityIcon(
                              item.discrepancies.length > 0 
                                ? item.discrepancies[0].severity 
                                : 'LOW'
                            )}
                          </Box>
                          <Box flexGrow={1}>
                            <Typography variant="subtitle1">
                              Invoice #{item.invoice_number} - {item.vendor_name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Status: {item.status} | Score: {(item.validation_score * 100).toFixed(1)}%
                            </Typography>
                          </Box>
                          <Chip
                            label={item.status}
                            color={item.status === 'FAILED' ? 'error' : 'warning'}
                            size="small"
                          />
                        </Box>
                      </AccordionSummary>
                      
                      <AccordionDetails>
                        <Grid container spacing={2}>
                          <Grid item xs={12} md={6}>
                            <Typography variant="h6" gutterBottom>
                              Discrepancies Found
                            </Typography>
                            <List dense>
                              {item.discrepancies.map((discrepancy, idx) => (
                                <React.Fragment key={idx}>
                                  <ListItem>
                                    <ListItemText
                                      primary={
                                        <Box display="flex" alignItems="center">
                                          {getSeverityIcon(discrepancy.severity)}
                                          <Typography variant="body2" ml={1}>
                                            {discrepancy.message}
                                          </Typography>
                                        </Box>
                                      }
                                      secondary={
                                        <Box mt={1}>
                                          {discrepancy.field && (
                                            <Typography variant="caption" display="block">
                                              Field: {discrepancy.field}
                                            </Typography>
                                          )}
                                          {discrepancy.expected && (
                                            <Typography variant="caption" display="block">
                                              Expected: {discrepancy.expected}
                                            </Typography>
                                          )}
                                          {discrepancy.actual && (
                                            <Typography variant="caption" display="block">
                                              Actual: {discrepancy.actual}
                                            </Typography>
                                          )}
                                        </Box>
                                      }
                                    />
                                  </ListItem>
                                  {idx < item.discrepancies.length - 1 && <Divider />}
                                </React.Fragment>
                              ))}
                            </List>
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <Typography variant="h6" gutterBottom>
                              Recommendations
                            </Typography>
                            <List dense>
                              {item.recommendations.map((recommendation, idx) => (
                                <ListItem key={idx}>
                                  <ListItemText
                                    primary={
                                      <Typography variant="body2">
                                        {recommendation}
                                      </Typography>
                                    }
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </Grid>
                        </Grid>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Reports;