import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  LinearProgress,
  Alert,
  Chip,
  Grid,
  Paper,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { apiClient } from '../services/api';

function InvoiceUpload() {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  const onDrop = async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    await uploadFile(file);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.tiff'],
      'application/pdf': ['.pdf'],
    },
    multiple: false,
  });

  const uploadFile = async (file) => {
    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post('/api/invoices/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'PASSED':
        return <CheckIcon />;
      case 'FAILED':
        return <ErrorIcon />;
      case 'WARNING':
        return <ErrorIcon />;
      default:
        return null;
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Upload Invoice
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Drag & Drop Invoice File
              </Typography>
              
              <Paper
                {...getRootProps()}
                sx={{
                  p: 4,
                  textAlign: 'center',
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                  cursor: 'pointer',
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
              >
                <input {...getInputProps()} />
                <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography variant="body1" gutterBottom>
                  {isDragActive
                    ? 'Drop the invoice file here...'
                    : 'Drag & drop an invoice file here, or click to select'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Supported formats: JPEG, PNG, PDF, TIFF, BMP
                </Typography>
              </Paper>

              {uploading && (
                <Box mt={2}>
                  <LinearProgress />
                  <Typography variant="body2" color="text.secondary" mt={1}>
                    Processing invoice...
                  </Typography>
                </Box>
              )}

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          {uploadResult && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Processing Results
                </Typography>
                
                <Box mb={2}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    icon={getStatusIcon(uploadResult.status)}
                    label={uploadResult.status}
                    color={getStatusColor(uploadResult.status)}
                    variant="outlined"
                  />
                </Box>

                <Box mb={2}>
                  <Typography variant="body2" color="text.secondary">
                    Validation Score
                  </Typography>
                  <Typography variant="h6">
                    {(uploadResult.validation_score * 100).toFixed(1)}%
                  </Typography>
                </Box>

                {uploadResult.discrepancies && (
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Discrepancies Found
                    </Typography>
                    <Typography variant="body2">
                      {JSON.parse(uploadResult.discrepancies).length} issues detected
                    </Typography>
                  </Box>
                )}

                <Button
                  variant="outlined"
                  fullWidth
                  sx={{ mt: 2 }}
                  onClick={() => window.location.href = '/invoices'}
                >
                  View All Invoices
                </Button>
              </CardContent>
            </Card>
          )}

          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Processing Features
              </Typography>
              <Typography variant="body2" component="div">
                <ul>
                  <li>AI-powered data extraction</li>
                  <li>Purchase order validation</li>
                  <li>Automated discrepancy detection</li>
                  <li>Validation rules engine</li>
                  <li>Comprehensive reporting</li>
                </ul>
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default InvoiceUpload;