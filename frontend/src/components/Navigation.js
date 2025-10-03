import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { BottomNavigation, BottomNavigationAction, Paper } from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Upload as UploadIcon,
  List as ListIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();

  const getCurrentPath = () => {
    switch (location.pathname) {
      case '/':
        return 0;
      case '/upload':
        return 1;
      case '/invoices':
        return 2;
      case '/reports':
        return 3;
      default:
        return 0;
    }
  };

  return (
    <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 1000 }} elevation={3}>
      <BottomNavigation
        value={getCurrentPath()}
        onChange={(event, newValue) => {
          switch (newValue) {
            case 0:
              navigate('/');
              break;
            case 1:
              navigate('/upload');
              break;
            case 2:
              navigate('/invoices');
              break;
            case 3:
              navigate('/reports');
              break;
          }
        }}
        showLabels
      >
        <BottomNavigationAction label="Dashboard" icon={<DashboardIcon />} />
        <BottomNavigationAction label="Upload" icon={<UploadIcon />} />
        <BottomNavigationAction label="Invoices" icon={<ListIcon />} />
        <BottomNavigationAction label="Reports" icon={<AssessmentIcon />} />
      </BottomNavigation>
    </Paper>
  );
}

export default Navigation;