import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Button,
  Alert,
  CircularProgress,
  Grid,
  Paper,
} from '@mui/material';
import {
  DataGrid,
  GridToolbar,
} from '@mui/x-data-grid';
import { apiClient } from '../services/api';

function InvoiceList() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/invoices');
      setInvoices(response.data);
    } catch (err) {
      setError('Failed to fetch invoices');
      console.error('Error fetching invoices:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'PASSED':
        return 'success';
      case 'FAILED':
        return 'error';
      case 'WARNING':
        return 'warning';
      default:
        return 'default';
    }
  };

  const columns = [
    {
      field: 'id',
      headerName: 'ID',
      width: 70,
    },
    {
      field: 'filename',
      headerName: 'Filename',
      width: 200,
      renderCell: (params) => (
        <Typography variant="body2" noWrap>
          {params.value}
        </Typography>
      ),
    },
    {
      field: 'vendor_name',
      headerName: 'Vendor',
      width: 200,
    },
    {
      field: 'invoice_number',
      headerName: 'Invoice #',
      width: 150,
    },
    {
      field: 'invoice_date',
      headerName: 'Date',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value ? new Date(params.value).toLocaleDateString() : 'N/A'}
        </Typography>
      ),
    },
    {
      field: 'total_amount',
      headerName: 'Amount',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value ? `$${params.value.toFixed(2)}` : 'N/A'}
        </Typography>
      ),
    },
    {
      field: 'created_at',
      headerName: 'Processed',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2">
          {new Date(params.value).toLocaleDateString()}
        </Typography>
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      renderCell: (params) => (
        <Button
          variant="outlined"
          size="small"
          onClick={() => handleViewDetails(params.row.id)}
        >
          View
        </Button>
      ),
    },
  ];

  const handleViewDetails = (invoiceId) => {
    // This would open a detailed view or modal
    console.log('View details for invoice:', invoiceId);
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
        Invoice List
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                All Processed Invoices
              </Typography>
              
              <Box sx={{ height: 600, width: '100%' }}>
                <DataGrid
                  rows={invoices}
                  columns={columns}
                  pageSize={10}
                  rowsPerPageOptions={[10, 25, 50]}
                  checkboxSelection
                  disableSelectionOnClick
                  components={{
                    Toolbar: GridToolbar,
                  }}
                  sx={{
                    border: 1,
                    borderColor: 'divider',
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default InvoiceList;