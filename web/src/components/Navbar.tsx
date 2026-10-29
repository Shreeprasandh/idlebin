'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { Cpu, Truck, ShieldAlert, Coins, BarChart3, Radio } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: '3D Compactor Twin', icon: Cpu },
    { href: '/fleet-dispatch', label: 'Municipal Fleet Map', icon: Truck },
    { href: '/citizen', label: 'Citizen RVM Portal', icon: Coins },
    { href: '/ward-officer', label: 'Ward Grievances', icon: ShieldAlert },
    { href: '/analytics', label: 'CapEx & Trajectory', icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-800/80 bg-zinc-950/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        
        {/* Brand identity */}
        <div className="flex items-center gap-4">
          <Link href="/" className="group flex items-center gap-3">
            <div className="relative h-10 w-10 overflow-hidden rounded-lg shadow-[0_4px_12px_rgba(0,0,0,0.5)] transition-shadow duration-200 group-hover:shadow-none">
              <Image
                src="/iconlogo.jpg"
                alt="IDLEBIN Logo"
                width={40}
                height={40}
                priority
                className="h-full w-full object-cover"
              />
            </div>
            <div className="flex flex-col">
              <span className="text-base font-bold tracking-tight text-zinc-100">
                IDLEBIN
              </span>
              <span className="text-[10px] font-medium tracking-wider text-emerald-400 uppercase">
                GCC Zone 11 - Valasaravakkam
              </span>
            </div>
          </Link>
        </div>

        {/* Navigation links */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-zinc-800 text-emerald-400 shadow-inner'
                    : 'text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Live System Status Pill */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-950/40 px-3 py-1 text-xs text-emerald-300">
            <Radio className="h-3 w-3 animate-pulse text-emerald-400" />
            <span className="hidden sm:inline font-mono">10 Nodes Grid Live</span>
            <span className="sm:hidden font-mono">10 Nodes</span>
          </div>
        </div>

      </div>

      {/* Mobile nav scrollbar */}
      <div className="flex md:hidden overflow-x-auto border-t border-zinc-800/60 px-4 py-2 gap-2 bg-zinc-950">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex shrink-0 items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium ${
                isActive
                  ? 'bg-zinc-800 text-emerald-400'
                  : 'text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200'
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </header>
  );
}
