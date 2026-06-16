'use client';

import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Box from '@mui/material/Box';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import IconButton from '@mui/material/IconButton';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import { usePathname } from 'next/navigation';
import { colors } from '../../themes/DefaultTheme/colors';

interface HeaderBarProps {
    drawerWidth: number;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({ drawerWidth }) => {
    // Simple breadcrumb logic
    // In a real app we might map paths to titles
    const pathname = usePathname();
    const segments = pathname.split('/').filter(p => p !== 'secure'); // 'secure' is internal structural
    const title = segments.length > 0 ? segments[segments.length - 1] : 'Dashboard';

    return (
        <AppBar
            position="fixed"
            sx={{
                width: { sm: `calc(100% - ${drawerWidth}px)` },
                ml: { sm: `${drawerWidth}px` },
                height: '64px',
                backgroundColor: colors.background.default,
                borderBottom: `1px solid ${colors.border.appBar}`,
                boxShadow: 'none',
                color: colors.text.primary,
                transition: 'width 0.2s, margin 0.2s', // Smooth transition for drawer width change
            }}
        >
            <Toolbar sx={{ height: '64px', minHeight: '64px !important' }}>
                <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
                    <Breadcrumbs
                        separator={<NavigateNextIcon fontSize="small" />}
                        aria-label="breadcrumb"
                    >
                        <Typography key="home" color="text.secondary">App</Typography>
                        <Typography key="curr" color="text.primary" sx={{ textTransform: 'capitalize', fontWeight: 600 }}>
                            {title}
                        </Typography>
                    </Breadcrumbs>
                </Box>

                <Box>
                    <IconButton sx={{ p: 0 }}>
                        <Avatar sx={{ bgcolor: colors.primary.main }}>A</Avatar>
                    </IconButton>
                </Box>
            </Toolbar>
        </AppBar>
    );
};
