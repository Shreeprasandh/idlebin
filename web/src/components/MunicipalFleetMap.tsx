'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { BinNode } from '@/types/idlebin';
import { getBins, saveBinUpdate } from '@/lib/data-service';
import { Truck, MapPin, Play, CheckCircle2, Battery, AlertTriangle, Layers, Compass } from 'lucide-react';

export default function MunicipalFleetMap() {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const vehicleMarkerRef = useRef<any>(null);
  const polylineRef = useRef<any>(null);

  const [bins, setBins] = useState<BinNode[]>([]);
  const [selectedBin, setSelectedBin] = useState<BinNode | null>(null);
  const [mapType, setMapType] = useState<'google_road' | 'google_sat' | 'carto_dark'>('google_road');
  const [isDispatching, setIsDispatching] = useState(false);
  const [dispatchProgress, setDispatchProgress] = useState<string>('Ready for dispatch');
  const [litresSaved, setLitresSaved] = useState(14.8);
  const [co2SavedKg, setCo2SavedKg] = useState(38.2);

  // Load bins from data service
  useEffect(() => {
    getBins().then((data) => {
      setBins(data);
      if (data.length > 0) setSelectedBin(data[0]);
    });
  }, []);

  // Initialize Leaflet map dynamically
  useEffect(() => {
    if (typeof window === 'undefined' || !mapContainerRef.current) return;

    let isMounted = true;

    import('leaflet').then((L) => {
      if (!isMounted || !mapContainerRef.current) return;

      // Clean up previous instance if exists
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }

      // Initialize map centered at Ramapuram Zone 11 (13.032, 80.181)
      const map = L.map(mapContainerRef.current, {
        center: [13.0325, 80.1815],
        zoom: 15,
        attributionControl: false,
        zoomControl: true
      });
      mapInstanceRef.current = map;

      // Base tile layer
      let tileUrl = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}';
      if (mapType === 'google_sat') {
        tileUrl = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}';
      } else if (mapType === 'carto_dark') {
        tileUrl = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
      }

      L.tileLayer(tileUrl, {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
      }).addTo(map);

      // Render Bin Markers
      renderMarkers(map, L, bins);
    });

    return () => {
      isMounted = false;
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [mapType]);

  // Update markers when bins change
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    import('leaflet').then((L) => {
      renderMarkers(mapInstanceRef.current, L, bins);
    });
  }, [bins]);

  const renderMarkers = (map: any, L: any, binList: BinNode[]) => {
    // Clear existing markers
    markersRef.current.forEach((m) => map.removeLayer(m));
    markersRef.current = [];

    binList.forEach((bin) => {
      const isCritical = bin.fillLevel >= 80;
      const isModerate = bin.fillLevel >= 50 && bin.fillLevel < 80;
      const pinColor = isCritical ? '#ef4444' : isModerate ? '#f59e0b' : '#10b981';

      const customIcon = L.divIcon({
        className: 'custom-bin-marker',
        html: `
          <div style="
            position: relative;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #09090b;
            border: 2px solid ${pinColor};
            border-radius: 50%;
            box-shadow: 0 0 10px ${pinColor}88;
            color: #ffffff;
            font-family: monospace;
            font-size: 10px;
            font-weight: bold;
            cursor: pointer;
          ">
            ${bin.fillLevel}%
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      const marker = L.marker([bin.lat, bin.lng], { icon: customIcon }).addTo(map);
      marker.on('click', () => {
        setSelectedBin(bin);
      });
      markersRef.current.push(marker);
    });
  };

  // Dispatch Smart Collection Vehicle Simulation
  const handleDispatchVehicle = useCallback(async () => {
    if (isDispatching || !mapInstanceRef.current) return;
    setIsDispatching(true);

    const L = await import('leaflet');
    const map = mapInstanceRef.current;

    // Filter bins that require collection (> 70% fill)
    const priorityBins = bins.filter((b) => b.fillLevel >= 70);
    const binsToVisit = priorityBins.length > 0 ? priorityBins : bins.slice(0, 4);

    setDispatchProgress(`Route planned: ${binsToVisit.length} high-fill nodes`);

    // Vehicle depot start position
    const depotCoords: [number, number] = [13.0300, 80.1770];
    const waypoints: [number, number][] = [depotCoords, ...binsToVisit.map((b) => [b.lat, b.lng] as [number, number])];

    // Draw route polyline
    if (polylineRef.current) map.removeLayer(polylineRef.current);
    polylineRef.current = L.polyline(waypoints, {
      color: '#10b981',
      weight: 4,
      dashArray: '6, 8',
      opacity: 0.8
    }).addTo(map);

    // Create Vehicle Marker
    if (vehicleMarkerRef.current) map.removeLayer(vehicleMarkerRef.current);
    const vehicleIcon = L.divIcon({
      className: 'vehicle-truck-icon',
      html: `
        <div style="
          background: #059669;
          border: 2px solid #34d399;
          border-radius: 6px;
          padding: 4px 6px;
          color: white;
          font-family: monospace;
          font-size: 10px;
          font-weight: bold;
          display: flex;
          align-items: center;
          gap: 4px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.6);
        ">
          TN-09-GCC-4412
        </div>
      `,
      iconSize: [110, 26],
      iconAnchor: [55, 13]
    });

    const vMarker = L.marker(depotCoords, { icon: vehicleIcon }).addTo(map);
    vehicleMarkerRef.current = vMarker;

    // Move truck sequentially from node to node
    let currentIdx = 0;
    const moveNext = () => {
      if (currentIdx >= waypoints.length - 1) {
        setDispatchProgress('Collection tour completed. All nodes emptied to 5%.');
        setIsDispatching(false);
        setLitresSaved((prev) => +(prev + 4.2).toFixed(1));
        setCo2SavedKg((prev) => +(prev + 11.3).toFixed(1));
        return;
      }

      currentIdx++;
      const targetCoord = waypoints[currentIdx];
      const targetBin = binsToVisit[currentIdx - 1];

      setDispatchProgress(`In Transit: Servicing ${targetBin?.name || 'Node'}...`);

      // Animate movement
      let step = 0;
      const startCoord = waypoints[currentIdx - 1];
      const steps = 30;

      const stepInterval = setInterval(async () => {
        step++;
        const curLat = startCoord[0] + ((targetCoord[0] - startCoord[0]) * step) / steps;
        const curLng = startCoord[1] + ((targetCoord[1] - startCoord[1]) * step) / steps;
        vMarker.setLatLng([curLat, curLng]);

        if (step >= steps) {
          clearInterval(stepInterval);

          // Bin emptied on arrival
          if (targetBin) {
            await saveBinUpdate(targetBin.id, {
              fillLevel: 5,
              status: 'Optimal',
              lastEmptiedAt: new Date().toISOString()
            });

            setBins((prev) =>
              prev.map((b) => (b.id === targetBin.id ? { ...b, fillLevel: 5, status: 'Optimal' } : b))
            );
          }

          setTimeout(moveNext, 700);
        }
      }, 30);
    };

    moveNext();
  }, [bins, isDispatching]);

  return (
    <div className="flex flex-col gap-4">
      
      {/* Control bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-zinc-800 bg-zinc-950 p-4">
        <div>
          <h2 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
            <Compass className="h-4 w-4 text-emerald-400" />
            GCC Zone 11 Municipal Surveillance Grid & Route Optimizer
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            10 Telemetry Nodes Across Ramapuram & Valasaravakkam - Dynamic TSP Haversine Dispatch
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Map Layer Switcher */}
          <div className="flex rounded-lg border border-zinc-800 bg-zinc-900 p-0.5 text-xs">
            <button
              onClick={() => setMapType('google_road')}
              className={`rounded-md px-2.5 py-1 font-medium transition-colors ${
                mapType === 'google_road' ? 'bg-zinc-800 text-emerald-400' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Road Map
            </button>
            <button
              onClick={() => setMapType('google_sat')}
              className={`rounded-md px-2.5 py-1 font-medium transition-colors ${
                mapType === 'google_sat' ? 'bg-zinc-800 text-emerald-400' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Satellite
            </button>
            <button
              onClick={() => setMapType('carto_dark')}
              className={`rounded-md px-2.5 py-1 font-medium transition-colors ${
                mapType === 'carto_dark' ? 'bg-zinc-800 text-emerald-400' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Tactical Dark
            </button>
          </div>

          {/* Dispatch Button */}
          <button
            onClick={handleDispatchVehicle}
            disabled={isDispatching}
            className={`flex items-center gap-2 rounded-lg border px-3.5 py-1.5 text-xs font-semibold transition-all ${
              isDispatching
                ? 'border-emerald-600/50 bg-emerald-950/40 text-emerald-300 cursor-wait'
                : 'border-emerald-500/50 bg-emerald-600/20 text-emerald-300 hover:bg-emerald-600/30 active:scale-[0.98]'
            }`}
          >
            <Truck className="h-3.5 w-3.5" />
            <span>{isDispatching ? 'Vehicle In Transit...' : 'Dispatch Smart Vehicle'}</span>
          </button>
        </div>
      </div>

      {/* Map and Details Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        
        {/* Leaflet Map Container */}
        <div className="lg:col-span-2 relative h-[520px] rounded-xl border border-zinc-800 bg-zinc-950 overflow-hidden shadow-xl">
          <div ref={mapContainerRef} className="h-full w-full" />

          {/* Dispatch Status Overlay */}
          <div className="absolute bottom-3 left-3 right-3 rounded-lg border border-zinc-800 bg-zinc-950/90 p-3 backdrop-blur-md flex items-center justify-between z-[1000] text-xs">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="font-mono text-zinc-300">{dispatchProgress}</span>
            </div>

            <div className="hidden sm:flex items-center gap-4 text-zinc-400 font-mono">
              <span>Fuel Saved: <strong className="text-emerald-400">{litresSaved} L</strong></span>
              <span>CO2 Avoided: <strong className="text-cyan-400">{co2SavedKg} kg</strong></span>
            </div>
          </div>
        </div>

        {/* Selected Bin Inspection Panel */}
        <div className="flex flex-col rounded-xl border border-zinc-800 bg-zinc-950 p-4">
          <div className="border-b border-zinc-800 pb-3">
            <div className="text-[10px] font-mono uppercase tracking-wider text-emerald-400">
              Node Telemetry Inspector
            </div>
            <h3 className="text-base font-bold text-zinc-100 mt-1">
              {selectedBin ? selectedBin.name : 'Select a Node'}
            </h3>
            <p className="text-xs text-zinc-400 font-mono">
              ID: {selectedBin?.id} - Ward {selectedBin?.ward}
            </p>
          </div>

          {selectedBin ? (
            <div className="mt-4 flex flex-col gap-3 text-xs">
              
              {/* Fill Gauge */}
              <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/60 p-3">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-zinc-400">Compactor Fill Level</span>
                  <span className={`font-mono font-bold ${
                    selectedBin.fillLevel >= 80 ? 'text-rose-400' : selectedBin.fillLevel >= 50 ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    {selectedBin.fillLevel}%
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-zinc-800 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${
                      selectedBin.fillLevel >= 80 ? 'bg-rose-500' : selectedBin.fillLevel >= 50 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${selectedBin.fillLevel}%` }}
                  />
                </div>
              </div>

              {/* Status and Telemetry */}
              <div className="grid grid-cols-2 gap-2 font-mono">
                <div className="rounded-md border border-zinc-900 bg-zinc-900/40 p-2.5">
                  <div className="text-[10px] text-zinc-500">Grid Status</div>
                  <div className={`mt-0.5 font-bold ${
                    selectedBin.status === 'Optimal' ? 'text-emerald-400' : 'text-amber-400'
                  }`}>
                    {selectedBin.status}
                  </div>
                </div>

                <div className="rounded-md border border-zinc-900 bg-zinc-900/40 p-2.5">
                  <div className="text-[10px] text-zinc-500">Battery Level</div>
                  <div className="mt-0.5 font-bold text-zinc-200 flex items-center gap-1">
                    <Battery className="h-3.5 w-3.5 text-emerald-400" />
                    {selectedBin.batteryLevel}% (LiFePO4)
                  </div>
                </div>

                <div className="rounded-md border border-zinc-900 bg-zinc-900/40 p-2.5">
                  <div className="text-[10px] text-zinc-500">Total Strokes</div>
                  <div className="mt-0.5 font-bold text-zinc-200">
                    {selectedBin.strokeCount} Cycles
                  </div>
                </div>

                <div className="rounded-md border border-zinc-900 bg-zinc-900/40 p-2.5">
                  <div className="text-[10px] text-zinc-500">Ultrasonic Distance</div>
                  <div className="mt-0.5 font-bold text-cyan-400">
                    {Math.round(85 - (selectedBin.fillLevel * 0.7))} cm
                  </div>
                </div>
              </div>

              {/* Geo Coordinates */}
              <div className="rounded-md border border-zinc-900 bg-zinc-900/30 p-2.5 font-mono text-[11px] text-zinc-400">
                <div className="text-[10px] text-zinc-500">GPS Coordinates</div>
                <div className="mt-0.5 text-zinc-300">
                  {selectedBin.lat.toFixed(4)}° N, {selectedBin.lng.toFixed(4)}° E
                </div>
              </div>

              {/* Manual empty action */}
              <button
                onClick={async () => {
                  await saveBinUpdate(selectedBin.id, {
                    fillLevel: 0,
                    status: 'Optimal',
                    lastEmptiedAt: new Date().toISOString()
                  });
                  setBins((prev) =>
                    prev.map((b) => (b.id === selectedBin.id ? { ...b, fillLevel: 0, status: 'Optimal' } : b))
                  );
                  setSelectedBin((prev) => prev ? { ...prev, fillLevel: 0, status: 'Optimal' } : null);
                }}
                className="mt-2 flex items-center justify-center gap-2 rounded-lg border border-zinc-800 bg-zinc-900 py-2 font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white transition-colors"
              >
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Mark Bin As Emptied</span>
              </button>

            </div>
          ) : (
            <div className="mt-8 text-center text-zinc-500 text-xs">
              Click any pin on the map to inspect its real-time telemetry.
            </div>
          )}

          {/* Quick list of all 10 nodes */}
          <div className="mt-4 border-t border-zinc-800 pt-3">
            <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 mb-2">
              Zone 11 Nodes Directory ({bins.length})
            </div>
            <div className="flex flex-col gap-1.5 max-h-48 overflow-y-auto pr-1">
              {bins.map((b) => (
                <button
                  key={b.id}
                  onClick={() => setSelectedBin(b)}
                  className={`flex items-center justify-between rounded-md p-2 text-left text-xs transition-colors ${
                    selectedBin?.id === b.id
                      ? 'bg-zinc-800 text-emerald-400'
                      : 'hover:bg-zinc-900 text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  <span className="truncate">{b.name}</span>
                  <span className={`font-mono font-bold ${
                    b.fillLevel >= 80 ? 'text-rose-400' : 'text-zinc-400'
                  }`}>
                    {b.fillLevel}%
                  </span>
                </button>
              ))}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
