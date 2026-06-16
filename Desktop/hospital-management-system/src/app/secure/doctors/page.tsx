'use client';

import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid2';
import Card from '@mui/material/Card';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';

const doctors = [
    { name: 'Dr. Sarah Wilson', specialty: 'Cardiology', patients: 124, exp: '12 Yrs' },
    { name: 'Dr. James Martin', specialty: 'Neurology', patients: 89, exp: '8 Yrs' },
    { name: 'Dr. Emily Chen', specialty: 'Pediatrics', patients: 230, exp: '15 Yrs' },
    { name: 'Dr. Michael Brown', specialty: 'Orthopedics', patients: 65, exp: '5 Yrs' },
    { name: 'Dr. Lisa Ray', specialty: 'Dermatology', patients: 110, exp: '9 Yrs' },
    { name: 'Dr. Robert King', specialty: 'General Surgery', patients: 45, exp: '20 Yrs' },
];

export default function DoctorsPage() {
    return (
        <Box>
            <Typography variant="h5" sx={{ mb: 4 }}>Doctors</Typography>
            <Grid container spacing={3}>
                {doctors.map((doc, index) => (
                    <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
                        <Card sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 2 }}>
                            <Avatar sx={{ width: 80, height: 80, bgcolor: '#F7F8F8', color: '#000', fontWeight: 'bold', fontSize: '1.5rem' }}>{doc.name.split(' ')[1][0]}</Avatar>
                            <Box>
                                <Typography variant="h6" sx={{ fontSize: '1.1rem', fontWeight: 600 }}>{doc.name}</Typography>
                                <Typography variant="body2" color="text.secondary">{doc.specialty}</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', gap: 4, width: '100%', justifyContent: 'center', my: 1 }}>
                                <Box>
                                    <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>{doc.patients}</Typography>
                                    <Typography variant="caption" color="text.secondary">Patients</Typography>
                                </Box>
                                <Box>
                                    <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>{doc.exp}</Typography>
                                    <Typography variant="caption" color="text.secondary">Exp.</Typography>
                                </Box>
                            </Box>
                            <Button variant="outlined" fullWidth sx={{ borderRadius: '24px', mt: 1, textTransform: 'uppercase', letterSpacing: '1px' }}>View Profile</Button>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
}
