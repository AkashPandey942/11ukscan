'use client';

import React from 'react';
import { NavLayout } from '../../common/component/navLayout/NavLayout';

export default function SecureLayout({ children }: { children: React.ReactNode }) {
    return (
        <NavLayout>
            {children}
        </NavLayout>
    );
}
