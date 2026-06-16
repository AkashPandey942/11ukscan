'use client';

import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import Grid from '@mui/material/Grid2';
import TextField from '@mui/material/TextField';
import Avatar from '@mui/material/Avatar';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { LoaderButton } from '../../../common/component/LoaderButton/LoaderButton';

export default function SettingsPage() {

    const profileFormik = useFormik({
        initialValues: {
            firstName: 'Akash',
            lastName: 'Pandey',
            email: 'akash@hospital.com',
            phone: '+91 98765 43210'
        },
        validationSchema: Yup.object({
            firstName: Yup.string().required(),
            email: Yup.string().email().required()
        }),
        onSubmit: async (values) => {
            await new Promise(r => setTimeout(r, 1000));
            alert('Profile Updated');
        }
    });

    return (
        <Box>
            <Typography variant="h5" sx={{ mb: 4 }}>Settings</Typography>

            <Grid container spacing={4}>
                <Grid size={{ xs: 12, md: 4 }}>
                    <Card sx={{ p: 4, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                        <Avatar sx={{ width: 100, height: 100, mb: 2, bgcolor: 'black', fontSize: '2rem' }}>A</Avatar>
                        <Typography variant="h6">Akash Pandey</Typography>
                        <Typography color="text.secondary" sx={{ mb: 2 }}>Administrator</Typography>
                        <LoaderButton variant="outlined" fullWidth>Upload New Picture</LoaderButton>
                    </Card>
                </Grid>

                <Grid size={{ xs: 12, md: 8 }}>
                    <Card sx={{ p: 4, mb: 4 }}>
                        <Typography variant="h6" sx={{ mb: 3 }}>Profile Information</Typography>
                        <form onSubmit={profileFormik.handleSubmit}>
                            <Grid container spacing={3}>
                                <Grid size={{ xs: 12, sm: 6 }}>
                                    <TextField
                                        fullWidth
                                        label="First Name"
                                        name="firstName"
                                        value={profileFormik.values.firstName}
                                        onChange={profileFormik.handleChange}
                                    />
                                </Grid>
                                <Grid size={{ xs: 12, sm: 6 }}>
                                    <TextField
                                        fullWidth
                                        label="Last Name"
                                        name="lastName"
                                        value={profileFormik.values.lastName}
                                        onChange={profileFormik.handleChange}
                                    />
                                </Grid>
                                <Grid size={{ xs: 12, sm: 6 }}>
                                    <TextField
                                        fullWidth
                                        label="Email Address"
                                        name="email"
                                        value={profileFormik.values.email}
                                        onChange={profileFormik.handleChange}
                                    />
                                </Grid>
                                <Grid size={{ xs: 12, sm: 6 }}>
                                    <TextField
                                        fullWidth
                                        label="Phone Number"
                                        name="phone"
                                        value={profileFormik.values.phone}
                                        onChange={profileFormik.handleChange}
                                    />
                                </Grid>
                                <Grid size={{ xs: 12 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                                        <LoaderButton type="submit" isLoading={profileFormik.isSubmitting}>Save Changes</LoaderButton>
                                    </Box>
                                </Grid>
                            </Grid>
                        </form>
                    </Card>

                    <Card sx={{ p: 4 }}>
                        <Typography variant="h6" sx={{ mb: 3 }}>Security</Typography>
                        <Grid container spacing={3}>
                            <Grid size={{ xs: 12 }}>
                                <TextField fullWidth label="Current Password" type="password" />
                            </Grid>
                            <Grid size={{ xs: 12, sm: 6 }}>
                                <TextField fullWidth label="New Password" type="password" />
                            </Grid>
                            <Grid size={{ xs: 12, sm: 6 }}>
                                <TextField fullWidth label="Confirm Data" type="password" />
                            </Grid>
                            <Grid size={{ xs: 12 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                                    <LoaderButton variant="outlined">Update Password</LoaderButton>
                                </Box>
                            </Grid>
                        </Grid>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
}
