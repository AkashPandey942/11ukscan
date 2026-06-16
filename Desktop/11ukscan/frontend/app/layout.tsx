import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "BankScan — PDF Bank Statement Parser",
  description:
    "Upload your Monzo Business PDF bank statement and instantly download structured CSV and Excel exports. Enterprise-grade parsing — fast, accurate, and secure.",
  keywords: ["bank statement", "PDF parser", "Monzo", "CSV export", "Excel export", "finance"],
  authors: [{ name: "BankScan" }],
  robots: "noindex, nofollow", // Private financial tool — not for search indexing
  viewport: "width=device-width, initial-scale=1",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased bg-[#0a0a14] text-white min-h-screen">
        {children}
      </body>
    </html>
  );
}
