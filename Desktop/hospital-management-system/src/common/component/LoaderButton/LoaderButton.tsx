'use client';

import React from 'react';
import Button, { ButtonProps } from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import { styled } from '@mui/material/styles';

interface LoaderButtonProps extends ButtonProps {
    isLoading?: boolean;
}

const StyledButton = styled(Button)<LoaderButtonProps>(({ theme, variant }) => ({
    borderRadius: '24px',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    boxShadow: 'none',
    padding: '12px 24px', // Adjusted for pill shape comfort
    '&:hover': {
        boxShadow: 'none',
    },
    // Primary (contained) by default or explicit
    ...(variant === 'contained' && {
        backgroundColor: '#212121',
        color: '#FFFFFF',
        '&:hover': {
            backgroundColor: '#000000',
        },
        '&.Mui-disabled': {
            backgroundColor: '#212121',
            opacity: 0.7,
            color: '#FFFFFF'
        }
    }),
    // Secondary (outlined)
    ...(variant === 'outlined' && {
        border: '1px solid #000000',
        color: '#000000',
        backgroundColor: 'transparent',
        '&:hover': {
            backgroundColor: 'rgba(0,0,0,0.04)',
            border: '1px solid #000000',
        }
    }),
}));

export const LoaderButton: React.FC<LoaderButtonProps> = ({ isLoading, children, disabled, variant = 'contained', ...props }) => {
    return (
        <StyledButton
            variant={variant}
            disabled={isLoading || disabled}
            isLoading={isLoading}
            {...props}
        >
            {isLoading ? <CircularProgress size={24} style={{ color: variant === 'contained' ? 'white' : 'black' }} /> : children}
        </StyledButton>
    );
};
