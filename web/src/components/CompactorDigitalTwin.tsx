'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';
import { Play, Plus, RefreshCw, Gauge, Zap, Shield, ArrowDown } from 'lucide-react';

interface BottleItem {
  id: number;
  mesh: THREE.Group;
  isCrushed: boolean;
  baseY: number;
}

export default function CompactorDigitalTwin() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [bottleCount, setBottleCount] = useState(0);
  const [isCompacting, setIsCompacting] = useState(false);
  const [strokeMm, setStrokeMm] = useState(0);
  const [mechAdvantage, setMechAdvantage] = useState(3.8);
  const [compactionForceN, setCompactionForceN] = useState(340);
  const [chamberFillPercent, setChamberFillPercent] = useState(12);

  // Three.js scene refs
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const ramMeshRef = useRef<THREE.Mesh | null>(null);
  const toggleArm1Ref = useRef<THREE.Mesh | null>(null);
  const toggleArm2Ref = useRef<THREE.Mesh | null>(null);
  const pedalRef = useRef<THREE.Mesh | null>(null);
  const flapRef = useRef<THREE.Mesh | null>(null);
  const bottlesRef = useRef<BottleItem[]>([]);
  const animationFrameIdRef = useRef<number | null>(null);

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight || 480;

    // 1. Scene & Camera
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x09090b);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
    camera.position.set(0, 1.2, 5.2);
    camera.lookAt(0, 0.8, 0);

    // 2. Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 3. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.8);
    dirLight.position.set(4, 6, 4);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 1024;
    dirLight.shadow.mapSize.height = 1024;
    scene.add(dirLight);

    const fillLight = new THREE.PointLight(0x10b981, 1.2, 8);
    fillLight.position.set(-2, 2, 2);
    scene.add(fillLight);

    // 4. Housing & Bin Framework
    const housingMat = new THREE.MeshStandardMaterial({
      color: 0x18181b,
      metalness: 0.8,
      roughness: 0.25,
      wireframe: false
    });
    const glassMat = new THREE.MeshPhysicalMaterial({
      color: 0x71717a,
      metalness: 0.1,
      roughness: 0.1,
      transmission: 0.85,
      transparent: true,
      opacity: 0.35,
      depthWrite: false
    });
    const steelMat = new THREE.MeshStandardMaterial({
      color: 0xa1a1aa,
      metalness: 0.9,
      roughness: 0.2
    });
    const brassMat = new THREE.MeshStandardMaterial({
      color: 0xd97706,
      metalness: 0.7,
      roughness: 0.3
    });

    // Outer frame pillars
    const pillarGeo = new THREE.BoxGeometry(0.08, 3.2, 0.08);
    [
      [-0.8, 0.8, 0.6],
      [0.8, 0.8, 0.6],
      [-0.8, 0.8, -0.6],
      [0.8, 0.8, -0.6]
    ].forEach(([x, y, z]) => {
      const p = new THREE.Mesh(pillarGeo, steelMat);
      p.position.set(x, y, z);
      p.castShadow = true;
      scene.add(p);
    });

    // Glass inspection chamber walls
    const frontGlass = new THREE.Mesh(new THREE.BoxGeometry(1.5, 2.0, 0.02), glassMat);
    frontGlass.position.set(0, 0.4, 0.6);
    scene.add(frontGlass);

    // Solid back and bottom
    const backWall = new THREE.Mesh(new THREE.BoxGeometry(1.55, 3.0, 0.04), housingMat);
    backWall.position.set(0, 0.8, -0.6);
    scene.add(backWall);

    const baseFloor = new THREE.Mesh(new THREE.BoxGeometry(1.65, 0.1, 1.25), housingMat);
    baseFloor.position.set(0, -0.7, 0);
    baseFloor.receiveShadow = true;
    scene.add(baseFloor);

    // Anvil plate at bottom
    const anvil = new THREE.Mesh(
      new THREE.BoxGeometry(1.4, 0.08, 1.0),
      new THREE.MeshStandardMaterial({ color: 0x52525b, metalness: 0.9, roughness: 0.3 })
    );
    anvil.position.set(0, -0.62, 0);
    scene.add(anvil);

    // 5. Intake Aperture & Escutcheon (Top Hood)
    const hood = new THREE.Mesh(new THREE.BoxGeometry(1.65, 0.5, 1.25), housingMat);
    hood.position.set(0, 2.3, 0);
    scene.add(hood);

    // Visor Canopy (9 deg angle)
    const visor = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.06, 0.4), steelMat);
    visor.position.set(0, 2.45, 0.65);
    visor.rotation.x = 0.15;
    scene.add(visor);

    // Brass safety sill
    const sill = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.03, 0.08), brassMat);
    sill.position.set(0, 2.12, 0.63);
    scene.add(sill);

    // Stainless Flap Door
    const flap = new THREE.Mesh(new THREE.BoxGeometry(0.76, 0.28, 0.02), steelMat);
    flap.position.set(0, 2.27, 0.63);
    flap.castShadow = true;
    scene.add(flap);
    flapRef.current = flap;

    // 6. Sliding Compactor Ram with V-Creaser Blade
    const ramGroup = new THREE.Group();
    ramGroup.position.set(0, 1.8, 0);

    const ramPlate = new THREE.Mesh(
      new THREE.BoxGeometry(1.38, 0.12, 0.96),
      new THREE.MeshStandardMaterial({ color: 0x27272a, metalness: 0.9, roughness: 0.2 })
    );
    ramPlate.castShadow = true;
    ramGroup.add(ramPlate);

    // V-Creaser blade beneath ram
    const bladeGeo = new THREE.ConeGeometry(0.08, 0.12, 4);
    bladeGeo.rotateY(Math.PI / 4);
    [-0.4, 0, 0.4].forEach((bx) => {
      const blade = new THREE.Mesh(bladeGeo, brassMat);
      blade.position.set(bx, -0.1, 0);
      blade.rotation.x = Math.PI;
      ramGroup.add(blade);
    });

    scene.add(ramGroup);
    ramMeshRef.current = ramGroup as unknown as THREE.Mesh;

    // 7. Compound Toggle Linkage
    const toggleMat = new THREE.MeshStandardMaterial({ color: 0x3f3f46, metalness: 0.85, roughness: 0.2 });
    const arm1 = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.6), toggleMat);
    arm1.position.set(0, 2.1, 0);
    scene.add(arm1);
    toggleArm1Ref.current = arm1;

    const arm2 = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.6), toggleMat);
    arm2.position.set(0, 1.9, 0);
    scene.add(arm2);
    toggleArm2Ref.current = arm2;

    // 8. Foot Pedal Mechanism
    const pedal = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.04, 0.45), steelMat);
    pedal.position.set(0, -0.65, 0.7);
    scene.add(pedal);
    pedalRef.current = pedal;

    // Render loop
    let lastTime = performance.now();
    const renderLoop = (time: number) => {
      animationFrameIdRef.current = requestAnimationFrame(renderLoop);
      renderer.render(scene, camera);
    };
    animationFrameIdRef.current = requestAnimationFrame(renderLoop);

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current || !renderer || !camera) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight || 480;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationFrameIdRef.current) cancelAnimationFrame(animationFrameIdRef.current);
      renderer.dispose();
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
    };
  }, []);

  // Helper: create realistic 500ml PET bottle group
  const createBottleGroup = () => {
    const group = new THREE.Group();
    const petMat = new THREE.MeshPhysicalMaterial({
      color: 0x38bdf8,
      metalness: 0.05,
      roughness: 0.15,
      transmission: 0.8,
      transparent: true,
      opacity: 0.7
    });
    const capMat = new THREE.MeshStandardMaterial({ color: 0xef4444, roughness: 0.4 });

    // Main cylinder body
    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.42, 16), petMat);
    body.castShadow = true;
    group.add(body);

    // Tapered shoulder
    const shoulder = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.12, 0.12, 16), petMat);
    shoulder.position.y = 0.27;
    group.add(shoulder);

    // Neck & cap
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.05, 12), capMat);
    cap.position.y = 0.35;
    group.add(cap);

    // Lay flat horizontally on anvil
    group.rotation.z = Math.PI / 2;
    group.rotation.y = (Math.random() - 0.5) * 0.4;
    return group;
  };

  // Drop Plastic Bottle (0 to 3 max)
  const handleDropBottle = useCallback(() => {
    if (!sceneRef.current || bottleCount >= 3 || isCompacting) return;

    // Flap animation
    if (flapRef.current) {
      flapRef.current.rotation.x = -0.7;
      setTimeout(() => {
        if (flapRef.current) flapRef.current.rotation.x = 0;
      }, 350);
    }

    const bottleGroup = createBottleGroup();
    // Stacking offset based on existing bottles
    const baseY = -0.52 + bottleCount * 0.16;
    bottleGroup.position.set((Math.random() - 0.5) * 0.3, 2.0, (Math.random() - 0.5) * 0.2);
    sceneRef.current.add(bottleGroup);

    // Drop animation downwards
    let currentY = 2.0;
    const dropInterval = setInterval(() => {
      currentY -= 0.15;
      if (currentY <= baseY) {
        currentY = baseY;
        clearInterval(dropInterval);
      }
      bottleGroup.position.y = currentY;
    }, 16);

    bottlesRef.current.push({
      id: Date.now(),
      mesh: bottleGroup,
      isCrushed: false,
      baseY
    });

    const newCount = bottleCount + 1;
    setBottleCount(newCount);
    setChamberFillPercent(Math.min(98, 15 + newCount * 26));
  }, [bottleCount, isCompacting]);

  // Step on Pedal & Execute Compaction Stroke
  const handleStepPedal = useCallback(() => {
    if (isCompacting || !ramMeshRef.current) return;
    setIsCompacting(true);

    const ram = ramMeshRef.current;
    const startY = 1.8;
    const bottomDeadCenter = -0.35;
    const totalStroke = startY - bottomDeadCenter;
    let progress = 0;
    let forward = true;

    const interval = setInterval(() => {
      if (forward) {
        progress += 0.045;
        if (progress >= 1.0) {
          progress = 1.0;
          forward = false;
        }
      } else {
        progress -= 0.035;
        if (progress <= 0) {
          progress = 0;
          clearInterval(interval);
          setIsCompacting(false);
          setStrokeMm(0);
          setMechAdvantage(3.8);
          setCompactionForceN(340);
          return;
        }
      }

      // Kinematic non-linear toggle position
      const currentRamY = startY - totalStroke * Math.sin(progress * Math.PI * 0.5);
      ram.position.y = currentRamY;

      // Calculate stroke in mm (0 to 185 mm)
      const mm = Math.round(progress * 185);
      setStrokeMm(mm);

      // Mechanical advantage non-linear curve: 3.8x up to 12.4x at bottom
      const ma = +(3.8 + 8.6 * Math.pow(progress, 2.5)).toFixed(1);
      setMechAdvantage(ma);

      // Force = Input (120N human leg) * MA
      const force = Math.round(120 * ma);
      setCompactionForceN(force);

      // Pedal animation
      if (pedalRef.current) {
        pedalRef.current.position.y = -0.65 - progress * 0.08;
      }

      // SELECTIVE CRUSHING: Check deformation of bottles
      bottlesRef.current.forEach((b) => {
        // Only deform if ram has descended past the bottle height AND bottle is NOT already crushed!
        if (currentRamY <= b.baseY + 0.28 && !b.isCrushed) {
          const crushRatio = Math.max(0.22, (currentRamY - b.baseY) / 0.28);
          b.mesh.scale.set(1.0 + (1 - crushRatio) * 0.35, crushRatio, 1.0 + (1 - crushRatio) * 0.35);
          if (crushRatio <= 0.25) {
            b.isCrushed = true; // Permanently marked crushed; will NEVER undergo crushing again!
          }
        }
      });
    }, 16);
  }, [isCompacting]);

  // Keyboard shortcut listeners (B for drop, Space for pedal)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.code === 'KeyB') {
        e.preventDefault();
        handleDropBottle();
      } else if (e.code === 'Space') {
        e.preventDefault();
        handleStepPedal();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleDropBottle, handleStepPedal]);

  // Empty Chamber
  const handleEmptyChamber = () => {
    if (isCompacting || !sceneRef.current) return;
    bottlesRef.current.forEach((b) => {
      sceneRef.current?.remove(b.mesh);
    });
    bottlesRef.current = [];
    setBottleCount(0);
    setChamberFillPercent(8);
  };

  return (
    <div className="flex flex-col rounded-xl border border-zinc-800 bg-zinc-950 p-4 shadow-xl">
      
      {/* Header telemetry readout */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-800/80 pb-3">
        <div>
          <h2 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
            <Shield className="h-4 w-4 text-emerald-400" />
            Compound Toggle Kinematics & Selective Compaction
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Decentralized Mechanical Advantage (3.8x to 12.4x) - Zero 3-Phase Grid Power
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center rounded-md border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-xs font-mono text-zinc-300">
            Bottles in Intake: <strong className="ml-1 text-emerald-400">{bottleCount}/3</strong>
          </span>
          {bottleCount > 0 && (
            <button
              onClick={handleEmptyChamber}
              disabled={isCompacting}
              className="flex items-center gap-1 rounded-md border border-zinc-700/60 bg-zinc-900 px-2.5 py-1 text-xs font-medium text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 transition-colors"
              title="Empty compactor chamber"
            >
              <RefreshCw className="h-3 w-3" />
              <span>Empty</span>
            </button>
          )}
        </div>
      </div>

      {/* Main 3D Canvas Container */}
      <div className="relative mt-4 h-96 w-full overflow-hidden rounded-lg border border-zinc-800/80 bg-zinc-950">
        <div ref={containerRef} className="h-full w-full cursor-grab active:cursor-grabbing" />

        {/* Live HUD Floating Indicators */}
        <div className="pointer-events-none absolute top-3 left-3 flex flex-col gap-2 font-mono text-xs">
          <div className="rounded-md border border-zinc-800 bg-zinc-950/85 px-3 py-1.5 backdrop-blur-sm text-zinc-300">
            <span className="text-zinc-500">Stroke:</span> <strong className="text-emerald-400">{strokeMm} mm</strong> / 185 mm
          </div>
          <div className="rounded-md border border-zinc-800 bg-zinc-950/85 px-3 py-1.5 backdrop-blur-sm text-zinc-300">
            <span className="text-zinc-500">Mech Advantage:</span> <strong className="text-cyan-400">{mechAdvantage}x</strong>
          </div>
          <div className="rounded-md border border-zinc-800 bg-zinc-950/85 px-3 py-1.5 backdrop-blur-sm text-zinc-300">
            <span className="text-zinc-500">Force Delivered:</span> <strong className="text-amber-400">{compactionForceN} N</strong>
          </div>
        </div>

        {/* Chamber Volume Bar */}
        <div className="absolute right-3 top-3 bottom-3 flex flex-col items-center justify-between rounded-md border border-zinc-800 bg-zinc-950/85 p-2 backdrop-blur-sm">
          <span className="text-[10px] font-mono text-zinc-400">100%</span>
          <div className="relative h-64 w-3 rounded-full bg-zinc-800 overflow-hidden">
            <div
              className={`absolute bottom-0 w-full transition-all duration-300 ${
                chamberFillPercent > 80 ? 'bg-amber-500' : 'bg-emerald-500'
              }`}
              style={{ height: `${chamberFillPercent}%` }}
            />
          </div>
          <span className="text-[10px] font-mono text-zinc-400">{chamberFillPercent}%</span>
        </div>
      </div>

      {/* Action Buttons (Aligned and Clean) */}
      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <button
          onClick={handleDropBottle}
          disabled={bottleCount >= 3 || isCompacting}
          className={`flex items-center justify-center gap-2 rounded-lg border px-4 py-3 text-sm font-semibold transition-all ${
            bottleCount >= 3
              ? 'border-zinc-800 bg-zinc-900 text-zinc-600 cursor-not-allowed'
              : 'border-zinc-700 bg-zinc-900 text-zinc-100 hover:bg-zinc-800 hover:border-zinc-600 active:scale-[0.98]'
          }`}
        >
          <Plus className="h-4 w-4 text-cyan-400" />
          <span>1. Drop Bottle</span>
          <kbd className="rounded border border-zinc-700 bg-zinc-800 px-1.5 py-0.5 text-[10px] font-mono text-zinc-400">B</kbd>
        </button>

        <button
          onClick={handleStepPedal}
          disabled={isCompacting}
          className={`flex items-center justify-center gap-2 rounded-lg border px-4 py-3 text-sm font-semibold transition-all ${
            isCompacting
              ? 'border-emerald-600/50 bg-emerald-950/40 text-emerald-300 cursor-wait'
              : 'border-emerald-500/40 bg-emerald-600/20 text-emerald-300 hover:bg-emerald-600/30 hover:border-emerald-500 active:scale-[0.98]'
          }`}
        >
          <Zap className="h-4 w-4 text-emerald-400" />
          <span>{isCompacting ? 'Compactor Stroke Active...' : '2. Step on Pedal'}</span>
          <kbd className="rounded border border-zinc-700 bg-zinc-800 px-1.5 py-0.5 text-[10px] font-mono text-zinc-400">Space</kbd>
        </button>
      </div>

      {/* Engineering Specifications Card */}
      <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
        <div className="rounded-md border border-zinc-900 bg-zinc-900/50 p-2 text-zinc-400">
          <div className="text-[10px] text-zinc-500">Volume Reduction</div>
          <div className="text-zinc-200 font-bold mt-0.5">4.8 : 1 (79.2%)</div>
        </div>
        <div className="rounded-md border border-zinc-900 bg-zinc-900/50 p-2 text-zinc-400">
          <div className="text-[10px] text-zinc-500">Blade Profile</div>
          <div className="text-zinc-200 font-bold mt-0.5">V-Creaser Stainless</div>
        </div>
        <div className="rounded-md border border-zinc-900 bg-zinc-900/50 p-2 text-zinc-400">
          <div className="text-[10px] text-zinc-500">Reed Switch Trigger</div>
          <div className="text-zinc-200 font-bold mt-0.5">GPIO 33 Wake-Up</div>
        </div>
        <div className="rounded-md border border-zinc-900 bg-zinc-900/50 p-2 text-zinc-400">
          <div className="text-[10px] text-zinc-500">Peak Hydraulic Eq</div>
          <div className="text-zinc-200 font-bold mt-0.5">1,488 N @ 185mm</div>
        </div>
      </div>

    </div>
  );
}
