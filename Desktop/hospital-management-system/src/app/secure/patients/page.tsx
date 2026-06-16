'use client';

import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Grid from '@mui/material/Grid2';
import Avatar from '@mui/material/Avatar';
import Chip from '@mui/material/Chip';

const rows = [
    { id: 1, name: 'John Doe', age: 32, gender: 'Male', status: 'Admitted', room: '101' },
    { id: 2, name: 'Jane Smith', age: 28, gender: 'Female', status: 'Outpatient', room: '-' },
    { id: 3, name: 'Michael Brown', age: 45, gender: 'Male', status: 'Surgery', room: '204' },
    { id: 4, name: 'Emily Davis', age: 19, gender: 'Female', status: 'Admitted', room: '105' },
];

export default function PatientsPage() {
    return (
        <Box>
            <Typography variant="h5" sx={{ mb: 4 }}>Patients</Typography>

            <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 8 }}>
                    <Card sx={{ p: 0, overflow: 'hidden' }}>
                        <TableContainer>
                            <Table>
                                <TableHead sx={{ bgcolor: '#FAFAFA' }}>
                                    <TableRow>
                                        <TableCell>Name</TableCell>
                                        <TableCell>Age</TableCell>
                                        <TableCell>Gender</TableCell>
                                        <TableCell>Status</TableCell>
                                        <TableCell>Room</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {rows.map((row) => (
                                        <TableRow key={row.id} hover>
                                            <TableCell sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                                <Avatar sx={{ width: 32, height: 32 }}>{row.name[0]}</Avatar>
                                                {row.name}
                                            </TableCell>
                                            <TableCell>{row.age}</TableCell>
                                            <TableCell>{row.gender}</TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={row.status}
                                                    size="small"
                                                    sx={{
                                                        bgcolor: row.status === 'Admitted' ? '#E0F2FE' : row.status === 'Surgery' ? '#FEE2E2' : '#F3F4F6',
                                                        color: row.status === 'Admitted' ? '#0284C7' : row.status === 'Surgery' ? '#DC2626' : '#374151',
                                                        fontWeight: 600
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell>{row.room}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Card>
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                    <Card sx={{ p: 4, height: '100%' }}>
                        <Typography variant="h6" sx={{ mb: 3 }}>Patient Details</Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
                            <Avatar sx={{ width: 80, height: 80, mb: 2, bgcolor: 'black' }}>JD</Avatar>
                            <Typography variant="h6">John Doe</Typography>
                            <Typography color="text.secondary">ID: #P-12345</Typography>
                        </Box>

                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography color="text.secondary">Condition</Typography>
                                <Typography fontWeight={600}>Flu Symptoms</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography color="text.secondary">Admitted</Typography>
                                <Typography fontWeight={600}>Oct 24, 2024</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography color="text.secondary">Insurance</Typography>
                                <Typography fontWeight={600}>BlueCross</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography color="text.secondary">Doctor</Typography>
                                <Typography fontWeight={600}>Dr. Sarah Wilson</Typography>
                            </Box>
                        </Box>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
}
