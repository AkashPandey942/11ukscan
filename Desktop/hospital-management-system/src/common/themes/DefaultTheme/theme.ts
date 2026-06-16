'use client';

import { createTheme } from '@mui/material/styles';
import { colors } from './colors';
import { typography } from './typography';

const theme = createTheme({
  palette: {
    primary: {
      main: colors.primary.main,
    },
    secondary: {
      main: colors.secondary.main,
    },
    background: {
      default: colors.background.default,
      paper: colors.background.paper,
    },
    text: {
      primary: colors.text.primary,
      secondary: colors.text.secondary,
    },
    info: {
      main: colors.info.main,
    },
  },
  typography: typography,
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '24px',
          textTransform: 'uppercase',
          letterSpacing: '1px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '24px',
          boxShadow: 'none', // Flat visuals are clearer unless shadow specified
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: '4px',
          '& fieldset': {
            borderColor: colors.border.main,
          },
          '&.Mui-focused fieldset': {
            borderColor: colors.primary.main,
          },
        },
        input: {
            padding: '16px 14px',
        }
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
            backgroundColor: colors.background.default,
            borderBottom: `1px solid ${colors.border.appBar}`,
            boxShadow: 'none',
            color: colors.text.primary,
        }
      }
    }
  },
});

export default theme;
