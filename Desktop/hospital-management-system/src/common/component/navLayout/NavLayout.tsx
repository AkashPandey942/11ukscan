'use client';

import React, { useState } from 'react';
import Box from '@mui/material/Box';
import { Sidebar } from './Sidebar';
import { HeaderBar } from '../HeaderBar/HeaderBar';
import { colors } from '../../themes/DefaultTheme/colors';

export const NavLayout = ({ children }: { children: React.ReactNode }) => {
    const [open, setOpen] = useState(true);

    const toggleDrawer = () => {
        setOpen(!open);
    };

    const drawerWidth = open ? 240 : 64;

    return (
        <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: colors.background.default }}>
            <HeaderBar drawerWidth={drawerWidth} />
            <Sidebar open={open} onToggle={toggleDrawer} />
            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    p: 3, // "CONTENT AREA: Padding: 24px" (3 * 8px = 24px)
                    width: { sm: `calc(100% - ${drawerWidth}px)` },
                    marginTop: '64px', // Below AppBar
                    transition: 'width 0.2s, margin 0.2s',
                    display: 'flex',
                    flexDirection: 'column',
                }}
            >
                {children}
            </Box>
        </Box>
    );
};
