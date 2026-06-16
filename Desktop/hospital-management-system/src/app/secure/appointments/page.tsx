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
import Chip from '@mui/material/Chip';
import Avatar from '@mui/material/Avatar';

const appointments = [
    { id: 101, patient: 'John Doe', doctor: 'Dr. Sarah Wilson', date: 'Oct 24, 2024', time: '10:00 AM', status: 'Confirmed' },
    { id: 102, patient: 'Jane Smith', doctor: 'Dr. Emily Chen', date: 'Oct 24, 2024', time: '11:30 AM', status: 'Pending' },
    { id: 103, patient: 'Michael Brown', doctor: 'Dr. Michael Brown', date: 'Oct 25, 2024', time: '09:00 AM', status: 'Cancelled' },
    { id: 104, patient: 'Emily Davis', doctor: 'Dr. Sarah Wilson', date: 'Oct 25, 2024', time: '02:15 PM', status: 'Confirmed' },
    { id: 105, patient: 'Robert Wilson', doctor: 'Dr. James Martin', date: 'Oct 26, 2024', time: '04:00 PM', status: 'Confirmed' },
];

export default function AppointmentsPage() {
    return (
        <Box>
            <Typography variant="h5" sx={{ mb: 4 }}>Appointments</Typography>
            <Card sx={{ overflow: 'hidden' }}>
                <TableContainer>
                    <Table>
                        <TableHead sx={{ bgcolor: '#FAFAFA' }}>
                            <TableRow>
                                <TableCell>ID</TableCell>
                                <TableCell>Patient</TableCell>
                                <TableCell>Doctor</TableCell>
                                <TableCell>Date</TableCell>
                                <TableCell>Time</TableCell>
                                <TableCell>Status</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {appointments.map((apt) => (
                                <TableRow key={apt.id} hover>
                                    <TableCell>#{apt.id}</TableCell>
                                    <TableCell sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                                        <Avatar sx={{ width: 28, height: 28, fontSize: '0.8rem' }}>{apt.patient[0]}</Avatar>
                                        {apt.patient}
                                    </TableCell>
                                    <TableCell>{apt.doctor}</TableCell>
                                    <TableCell>{apt.date}</TableCell>
                                    <TableCell>{apt.time}</TableCell>
                                    <TableCell>
                                        <Chip
                                            label={apt.status}
                                            size="small"
                                            sx={{
                                                fontWeight: 600,
                                                bgcolor: apt.status === 'Confirmed' ? '#dafbf0' : apt.status === 'Pending' ? '#fffbeb' : '#fee2e2',
                                                color: apt.status === 'Confirmed' ? '#059669' : apt.status === 'Pending' ? '#b45309' : '#dc2626'
                                            }}
                                        />
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Card>
        </Box>
    );
}
