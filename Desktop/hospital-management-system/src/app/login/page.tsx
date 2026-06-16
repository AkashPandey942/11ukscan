'use client';

import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import Link from '@mui/material/Link';
import TextField from '@mui/material/TextField';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useRouter } from 'next/navigation';
import { LoaderButton } from '../../common/component/LoaderButton/LoaderButton';

export default function LoginPage() {
    const router = useRouter();
    const [showPassword, setShowPassword] = useState(false);

    const formik = useFormik({
        initialValues: {
            username: '',
            password: '',
        },
        validationSchema: Yup.object({
            username: Yup.string().required('Required'),
            password: Yup.string().required('Required'),
        }),
        onSubmit: async (values) => {
            // Simulate API call
            await new Promise((resolve) => setTimeout(resolve, 1500));
            // Role handling would happen here normally. For now we redirect to dashboard.
            router.push('/secure/dashboard');
        },
    });

    return (
        <Box
            sx={{
                height: '100vh',
                width: '100vw',
                backgroundImage: 'url(https://images.unsplash.com/photo-1538108149393-fbbd81895907?q=80&w=2628&auto=format&fit=crop)', // Clean Hospital/Abstract background
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                display: 'flex',
                alignItems: 'center',
                position: 'relative',
            }}
        >
            <Card
                sx={{
                    marginLeft: '12vw',
                    width: '100%',
                    maxWidth: '430px',
                    padding: '32px',
                    borderRadius: '24px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 3,
                }}
            >
                <Typography variant="h4">Log In</Typography>

                <form onSubmit={formik.handleSubmit}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                        <TextField
                            fullWidth
                            id="username"
                            name="username"
                            label="Username"
                            value={formik.values.username}
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                            error={formik.touched.username && Boolean(formik.errors.username)}
                            helperText={formik.touched.username && formik.errors.username}
                        />
                        <TextField
                            fullWidth
                            id="password"
                            name="password"
                            label="Password"
                            type={showPassword ? 'text' : 'password'}
                            value={formik.values.password}
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                            error={formik.touched.password && Boolean(formik.errors.password)}
                            helperText={formik.touched.password && formik.errors.password}
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton
                                            aria-label="toggle password visibility"
                                            onClick={() => setShowPassword(!showPassword)}
                                            edge="end"
                                        >
                                            {showPassword ? <VisibilityOff /> : <Visibility />}
                                        </IconButton>
                                    </InputAdornment>
                                ),
                            }}
                        />

                        <Box sx={{ textAlign: 'right', mt: -1 }}>
                            <Link href="#" underline="hover" color="text.secondary" sx={{ fontWeight: 500 }}>
                                Forgot Your Password?
                            </Link>
                        </Box>

                        <LoaderButton
                            fullWidth
                            type="submit"
                            variant="contained"
                            isLoading={formik.isSubmitting}
                            sx={{ mt: 1 }}
                        >
                            LOG IN
                        </LoaderButton>
                    </Box>
                </form>
            </Card>

            <Box
                sx={{
                    position: 'absolute',
                    bottom: 32,
                    width: '100%',
                    textAlign: 'center',
                    color: 'white',
                }}
            >
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    © 2024 Hospital Management System
                </Typography>
            </Box>
        </Box>
    );
}
