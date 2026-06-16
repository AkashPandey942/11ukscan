'use client';

import React from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import PeopleIcon from '@mui/icons-material/People';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import EventAvailableIcon from '@mui/icons-material/EventAvailable';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';

interface KPICardProps {
    title: string;
    value: string;
    icon: React.ReactNode;
    color: string;
}

const KPICard: React.FC<KPICardProps> = ({ title, value, icon, color }) => (
    <Card sx={{ p: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
        <Box>
            <Typography variant="h4" sx={{ mb: 0.5, fontWeight: 'bold' }}>{value}</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 600 }}>{title}</Typography>
        </Box>
        <Box sx={{
            width: 56,
            height: 56,
            borderRadius: '50%',
            backgroundColor: `${color}15`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: color
        }}>
            {icon}
        </Box>
    </Card>
);

export default function DashboardPage() {
    return (
        <Box>
            <Typography variant="h5" sx={{ mb: 4 }}>Overview</Typography>
            <Grid container spacing={3}>
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <KPICard title="Total Patients" value="3,240" icon={<PeopleIcon fontSize="medium" />} color="#212121" />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <KPICard title="Available Doctors" value="24" icon={<LocalHospitalIcon fontSize="medium" />} color="#60A5FA" />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <KPICard title="Appointments" value="86" icon={<EventAvailableIcon fontSize="medium" />} color="#10B981" />
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                    <KPICard title="Revenue (Daily)" value="$12.4k" icon={<AttachMoneyIcon fontSize="medium" />} color="#F59E0B" />
                </Grid>
            </Grid>

            <Box sx={{ mt: 4 }}>
                <Grid container spacing={3}>
                    <Grid size={{ xs: 12, md: 8 }}>
                        <Card sx={{ p: 3, minHeight: 400 }}>
                            <Typography variant="h6" sx={{ mb: 2 }}>Hospital Analytics</Typography>
                            <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#F9FAFB', borderRadius: 2 }}>
                                <Typography color="text.secondary">Chart Area</Typography>
                            </Box>
                        </Card>
                    </Grid>
                    <Grid size={{ xs: 12, md: 4 }}>
                        <Card sx={{ p: 3, minHeight: 400 }}>
                            <Typography variant="h6" sx={{ mb: 2 }}>Recent Activity</Typography>
                            {/* List of activities */}
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                {[1, 2, 3, 4].map((i) => (
                                    <Box key={i} sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                                        <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'black' }} />
                                        <Box>
                                            <Typography variant="body2" sx={{ fontWeight: 600 }}>New Patient Registered</Typography>
                                            <Typography variant="caption" color="text.secondary">2 mins ago</Typography>
                                        </Box>
                                    </Box>
                                ))}
                            </Box>
                        </Card>
                    </Grid>
                </Grid>
            </Box>
        </Box>
    );
}
