import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'IDLEBIN - Municipal Solid Waste Compactor Digital Twin & Civic Suite',
  description: 'Production Decentralized Mechanical Solid Waste Compactor & Civic Suite for Greater Chennai Corporation (GCC) Zone 11.',
  icons: {
    icon: '/iconlogo.jpg',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col antialiased">
        <Navbar />
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 py-6 sm:px-6">
          {children}
        </main>
        <footer className="w-full border-t border-zinc-800/80 bg-zinc-950 py-4 text-center text-xs font-mono text-zinc-500">
          IDLEBIN Municipal Solid Waste Compactor Platform - Greater Chennai Corporation (GCC) Zone 11 Valasaravakkam - SWM Rules 2016 Parity
        </footer>
      </body>
    </html>
  );
}
