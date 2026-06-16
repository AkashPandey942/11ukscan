'use client';

import React from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Box from '@mui/material/Box';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import EventIcon from '@mui/icons-material/Event';
import ReceiptIcon from '@mui/icons-material/Receipt';
import SettingsIcon from '@mui/icons-material/Settings';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { SvgIconProps } from '@mui/material/SvgIcon';
import { colors } from '../../themes/DefaultTheme/colors';
import { AUTH_ROUTES } from '../../authRoutes';

const getIcon = (key: string, props?: SvgIconProps) => {
    switch (key) {
        case 'dashboard': return <DashboardIcon {...props} />;
        case 'patients': return <PeopleIcon {...props} />;
        case 'doctors': return <LocalHospitalIcon {...props} />;
        case 'appointments': return <EventIcon {...props} />;
        case 'billing': return <ReceiptIcon {...props} />;
        case 'settings': return <SettingsIcon {...props} />;
        default: return <DashboardIcon {...props} />;
    }
};

export const Sidebar = ({ open, onToggle }: { open: boolean, onToggle: () => void }) => {
    const pathname = usePathname();
    const drawerWidth = 240;
    const collapsedWidth = 64;

    return (
        <Drawer
            variant="permanent"
            sx={{
                width: open ? drawerWidth : collapsedWidth,
                flexShrink: 0,
                whiteSpace: 'nowrap',
                boxSizing: 'border-box',
                '& .MuiDrawer-paper': {
                    width: open ? drawerWidth : collapsedWidth,
                    transition: 'width 0.2s',
                    overflowX: 'visible',
                    backgroundColor: '#FFFFFF',
                    borderRight: 'none',
                },
            }}
        >
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: open ? 'flex-start' : 'center',
                    height: '64px',
                    pl: open ? 3 : 0,
                }}
            >
                <Box
                    sx={{
                        fontWeight: '800',
                        fontSize: '1.2rem',
                        color: colors.primary.main,
                        opacity: open ? 1 : 0,
                        transition: 'opacity 0.2s',
                        whiteSpace: 'nowrap'
                    }}
                >
                    HOSPITAL
                </Box>
            </Box>

            <Box
                onClick={onToggle}
                sx={{
                    position: 'absolute',
                    top: 35,
                    right: -15,
                    width: 30,
                    height: 30,
                    borderRadius: '50%',
                    backgroundColor: '#000000',
                    color: '#FFFFFF',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    zIndex: 1201,
                    boxShadow: '0px 2px 4px rgba(0,0,0,0.2)',
                }}
            >
                {open ? <ChevronLeftIcon fontSize="small" /> : <ChevronRightIcon fontSize="small" />}
            </Box>

            <List sx={{ px: 1 }}>
                {AUTH_ROUTES.map((item) => {
                    const isActive = pathname.startsWith(item.path);

                    return (
                        <Link key={item.path} href={item.path} style={{ textDecoration: 'none' }}>
                            <ListItem disablePadding sx={{ display: 'block', mb: 1 }}>
                                <ListItemButton
                                    sx={{
                                        minHeight: 48,
                                        justifyContent: open ? 'initial' : 'center',
                                        px: 1,
                                        borderRadius: '20px',
                                        backgroundColor: isActive ? '#000000' : 'transparent',
                                        color: isActive ? '#FFFFFF' : '#000000',
                                        '&:hover': {
                                            backgroundColor: isActive ? '#000000' : colors.sidebar.inactiveBg,
                                        },
                                    }}
                                >
                                    <ListItemIcon
                                        sx={{
                                            minWidth: 0,
                                            mr: open ? 2 : 'auto',
                                            justifyContent: 'center',
                                            width: 35,
                                            height: 35,
                                            borderRadius: '50%',
                                            backgroundColor: isActive ? '#000000' : colors.sidebar.inactiveBg,
                                            color: isActive ? '#FFFFFF' : '#000000',
                                            display: 'flex',
                                            alignItems: 'center',
                                        }}
                                    >
                                        {getIcon(item.iconKey, { sx: { fontSize: 20 } })}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={item.label}
                                        sx={{ opacity: open ? 1 : 0 }}
                                        primaryTypographyProps={{ fontWeight: 600, fontSize: '0.9rem' }}
                                    />
                                </ListItemButton>
                            </ListItem>
                        </Link>
                    );
                })}
            </List>
        </Drawer>
    );
};
