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
import IconButton from '@mui/material/IconButton';
import Grid from '@mui/material/Grid2'; // Using Grid2 as Grid V2 to solve type issues if regular Grid fails
import DownloadIcon from '@mui/icons-material/Download';
import VisibilityIcon from '@mui/icons-material/Visibility';

const invoices = [
    { id: 'INV-2024-001', patient: 'John Doe', date: 'Oct 24, 2024', amount: '$1,250.00', status: 'Paid' },
    { id: 'INV-2024-002', patient: 'Jane Smith', date: 'Oct 23, 2024', amount: '$450.00', status: 'Pending' },
    { id: 'INV-2024-003', patient: 'Michael Brown', date: 'Oct 22, 2024', amount: '$3,400.00', status: 'Unpaid' },
    { id: 'INV-2024-004', patient: 'Emily Davis', date: 'Oct 21, 2024', amount: '$210.00', status: 'Paid' },
    { id: 'INV-2024-005', patient: 'Robert King', date: 'Oct 20, 2024', amount: '$850.00', status: 'Paid' },
];

export default function BillingPage() {
    return (
        <Box>
            <Typography variant="h5" sx={{ mb: 4 }}>Billing & Invoices</Typography>

            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid size={{ xs: 12, md: 4 }}>
                    <Card sx={{ p: 3, bgcolor: '#212121', color: 'white' }}>
                        <Typography variant="body2" sx={{ opacity: 0.7 }}>Total Revenue</Typography>
                        <Typography variant="h4" sx={{ mt: 1, fontWeight: 'bold' }}>$42,500.00</Typography>
                    </Card>
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                    <Card sx={{ p: 3 }}>
                        <Typography variant="body2" color="text.secondary">Pending Payments</Typography>
                        <Typography variant="h4" sx={{ mt: 1, fontWeight: 'bold' }}>$3,850.00</Typography>
                    </Card>
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                    <Card sx={{ p: 3 }}>
                        <Typography variant="body2" color="text.secondary">Invoices Generated</Typography>
                        <Typography variant="h4" sx={{ mt: 1, fontWeight: 'bold' }}>1,240</Typography>
                    </Card>
                </Grid>
            </Grid>

            <Card sx={{ overflow: 'hidden' }}>
                <TableContainer>
                    <Table>
                        <TableHead sx={{ bgcolor: '#FAFAFA' }}>
                            <TableRow>
                                <TableCell>Invoice ID</TableCell>
                                <TableCell>Patient</TableCell>
                                <TableCell>Date</TableCell>
                                <TableCell>Amount</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell align="right">Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {invoices.map((inv) => (
                                <TableRow key={inv.id} hover>
                                    <TableCell sx={{ fontWeight: 600 }}>{inv.id}</TableCell>
                                    <TableCell>{inv.patient}</TableCell>
                                    <TableCell>{inv.date}</TableCell>
                                    <TableCell>{inv.amount}</TableCell>
                                    <TableCell>
                                        <Chip
                                            label={inv.status}
                                            size="small"
                                            sx={{
                                                fontWeight: 600,
                                                bgcolor: inv.status === 'Paid' ? '#dafbf0' : inv.status === 'Pending' ? '#fffbeb' : '#fee2e2',
                                                color: inv.status === 'Paid' ? '#059669' : inv.status === 'Pending' ? '#b45309' : '#dc2626'
                                            }}
                                        />
                                    </TableCell>
                                    <TableCell align="right">
                                        <IconButton size="small"><VisibilityIcon fontSize="small" /></IconButton>
                                        <IconButton size="small"><DownloadIcon fontSize="small" /></IconButton>
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
