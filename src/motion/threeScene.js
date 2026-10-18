import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

// Pre-allocated math helpers at module scope — zero GC in render loop
const _vec3 = new THREE.Vector3();
const _vec3B = new THREE.Vector3();
const _mat4 = new THREE.Matrix4();
const _quat = new THREE.Quaternion();
const _euler = new THREE.Euler();
const _scale = new THREE.Vector3();
const _color = new THREE.Color();

const WORKFLOW_PRESETS = {
  all: {
    label: "Full Omnichannel Topology",
    subtitle: "WhatsApp Cloud API ↔ Qefro Deterministic Core ↔ Tally, Zoho, POS & UPI",
    metric: "4 Active Connectors · < 280ms Execution",
    camPos: [0, 6.2, 11.8],
    lookAt: [0, 1.1, 0],
    activeNodes: [0, 1, 2, 3],
    accentHex: 0x6366f1,
  },
  realestate: {
    label: "Real Estate Site Visit & CRM Flow",
    subtitle: "WhatsApp Lead Qualification → Budget Filter → Agent Calendar Slot Locked",
    metric: "Site Visit Booked in 30s · CRM Synced",
    camPos: [-3.8, 4.4, 8.2],
    lookAt: [-1.8, 1.1, 0.2],
    activeNodes: [0, 3],
    accentHex: 0x0ea5e9,
  },
  restaurant: {
    label: "Restaurant POS Table Reservation Flow",
    subtitle: "Inbound WhatsApp Request → Live POS Table Check → Table #8 Locked",
    metric: "100% Automated POS Sync · Zero Missed Calls",
    camPos: [-4.2, 4.8, 7.6],
    lookAt: [-2.0, 1.0, -0.6],
    activeNodes: [0, 3],
    accentHex: 0xf59e0b,
  },
  billing: {
    label: "Tally & Zoho GST Invoicing + UPI Rail",
    subtitle: "Overdue Ledger Query → Dynamic UPI Link Dispatched → Auto-Reconciled",
    metric: "₹45,000 Settled · Tally Voucher Posted",
    camPos: [4.2, 4.6, 8.2],
    lookAt: [1.9, 1.1, 0.1],
    activeNodes: [0, 1, 2],
    accentHex: 0x10b981,
  },
  crm: {
    label: "Human-in-the-Loop Approval Gate",
    subtitle: "Sensitive Discount / Refund → 1-Click Manager Approval → Audit Logged",
    metric: "RBAC Enforced · TLS 1.3 & AES-256",
    camPos: [0, 3.6, 6.4],
    lookAt: [0, 1.45, 0],
    activeNodes: [0, 1, 2, 3],
    accentHex: 0x8b5cf6,
  },
};

const NODE_SPECS = [
  {
    id: "whatsapp",
    name: "01. WhatsApp Cloud API",
    role: "Inbound & Outbound Customer Conversations",
    detail: "Official Meta Cloud API · Hindi, Tamil, Hinglish & English",
    pos: [-4.6, 0, 2.1],
    color: 0x10b981,
  },
  {
    id: "erp",
    name: "02. Tally Prime & Zoho Books",
    role: "Two-Way Accounting & GST Ledger Sync",
    detail: "Live SKU pricing, voucher creation & automated reconciliation",
    pos: [4.6, 0, -1.9],
    color: 0x6366f1,
  },
  {
    id: "upi",
    name: "03. UPI & Razorpay Rail",
    role: "1-Click Payment Links & Instant Settlement",
    detail: "Dynamic QR generation & webhook payment verification",
    pos: [4.6, 0, 2.1],
    color: 0x06b6d4,
  },
  {
    id: "pos",
    name: "04. POS & Google Sheets",
    role: "Live Inventory, Appointments & Table Locks",
    detail: "Real-time row updates, slot availability & calendar passes",
    pos: [-4.6, 0, -1.9],
    color: 0xf59e0b,
  },
];

function createProceduralDialTexture(maxAnisotropy) {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = "#0f172a";
  ctx.fillRect(0, 0, 512, 512);

  const cx = 256;
  const cy = 256;

  // Concentric technical rings
  ctx.strokeStyle = "rgba(99, 102, 241, 0.45)";
  ctx.lineWidth = 2;
  [70, 120, 175, 225].forEach((r) => {
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  });

  // Precision radial tick marks
  for (let i = 0; i < 72; i++) {
    const angle = (i / 72) * Math.PI * 2;
    const isMajor = i % 6 === 0;
    const rInner = isMajor ? 185 : 200;
    const rOuter = 220;
    ctx.strokeStyle = isMajor ? "rgba(56, 189, 248, 0.9)" : "rgba(148, 163, 184, 0.4)";
    ctx.lineWidth = isMajor ? 3 : 1.5;
    ctx.beginPath();
    ctx.moveTo(cx + Math.cos(angle) * rInner, cy + Math.sin(angle) * rInner);
    ctx.lineTo(cx + Math.cos(angle) * rOuter, cy + Math.sin(angle) * rOuter);
    ctx.stroke();
  }

  // Circuit routing traces
  ctx.strokeStyle = "rgba(16, 185, 129, 0.65)";
  ctx.lineWidth = 2.5;
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(cx + Math.cos(a) * 70, cy + Math.sin(a) * 70);
    ctx.lineTo(cx + Math.cos(a + 0.18) * 175, cy + Math.sin(a + 0.18) * 175);
    ctx.stroke();
  }

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = maxAnisotropy;
  return tex;
}

function createProceduralQRTexture(maxAnisotropy) {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext("2d");

  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, 256, 256);

  ctx.fillStyle = "#0f172a";
  const drawFinder = (x, y) => {
    ctx.fillRect(x, y, 56, 56);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(x + 8, y + 8, 40, 40);
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(x + 16, y + 16, 24, 24);
  };
  drawFinder(20, 20);
  drawFinder(180, 20);
  drawFinder(20, 180);

  // Deterministic pseudo-random QR modules
  for (let r = 0; r < 12; r++) {
    for (let c = 0; c < 12; c++) {
      if ((r < 4 && c < 4) || (r < 4 && c > 7) || (r > 7 && c < 4)) continue;
      if ((r * 7 + c * 13) % 3 !== 0) {
        ctx.fillStyle = (r + c) % 5 === 0 ? "#0284c7" : "#0f172a";
        ctx.fillRect(24 + c * 17, 24 + r * 17, 12, 12);
      }
    }
  }

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = maxAnisotropy;
  return tex;
}

function createContactShadowTexture() {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext("2d");
  const grad = ctx.createRadialGradient(128, 128, 12, 128, 128, 120);
  grad.addColorStop(0, "rgba(15, 23, 42, 0.55)");
  grad.addColorStop(0.55, "rgba(15, 23, 42, 0.22)");
  grad.addColorStop(1, "rgba(15, 23, 42, 0)");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 256, 256);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/**
 * Builds the 9-part Qefro Central Operations Core (THREE.Group)
 * Pivot is at bottom-center (y = 0) so it sits flush on the ground plane.
 */
function buildCentralCore(dialTex, shadowTex) {
  const group = new THREE.Group();
  group.name = "qefro-core";

  // 1. Contact shadow plane
  const shadowGeo = new THREE.PlaneGeometry(5.6, 5.6);
  const shadowMat = new THREE.MeshBasicMaterial({
    map: shadowTex,
    transparent: true,
    depthWrite: false,
    opacity: 0.55,
    polygonOffset: true,
    polygonOffsetFactor: -1,
    polygonOffsetUnits: -1,
  });
  const shadowMesh = new THREE.Mesh(shadowGeo, shadowMat);
  shadowMesh.rotation.x = -Math.PI / 2;
  shadowMesh.position.y = 0.01;
  group.add(shadowMesh);

  // 2. Primary Silhouette: Octagonal Brushed Titanium Base Plinth
  const plinthGeo = new THREE.CylinderGeometry(2.15, 2.45, 0.34, 8);
  const plinthMat = new THREE.MeshPhysicalMaterial({
    color: 0x1e293b,
    metalness: 0.88,
    roughness: 0.22,
    clearcoat: 0.4,
  });
  const plinth = new THREE.Mesh(plinthGeo, plinthMat);
  plinth.position.y = 0.17;
  plinth.castShadow = true;
  plinth.receiveShadow = true;
  group.add(plinth);

  // 3. Lower Circuit Dial Manifold
  const dialGeo = new THREE.CylinderGeometry(1.88, 1.96, 0.18, 48);
  const dialMat = new THREE.MeshStandardMaterial({
    map: dialTex,
    metalness: 0.45,
    roughness: 0.5,
  });
  const dialMesh = new THREE.Mesh(dialGeo, dialMat);
  dialMesh.position.y = 0.43;
  dialMesh.receiveShadow = true;
  group.add(dialMesh);

  // 4. Explodable Tier 1: Deterministic Rule Engine Matrix (Beveled Hex Core + 8 Fins)
  const tier1Group = new THREE.Group();
  tier1Group.position.y = 0.78;
  const hexShape = new THREE.Shape();
  const hexRadius = 1.25;
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2;
    const x = Math.cos(a) * hexRadius;
    const y = Math.sin(a) * hexRadius;
    if (i === 0) hexShape.moveTo(x, y);
    else hexShape.lineTo(x, y);
  }
  hexShape.closePath();
  const extrudeGeo = new THREE.ExtrudeGeometry(hexShape, {
    depth: 0.36,
    bevelEnabled: true,
    bevelThickness: 0.06,
    bevelSize: 0.06,
    bevelSegments: 3,
  });
  extrudeGeo.rotateX(Math.PI / 2);
  const tier1Mat = new THREE.MeshStandardMaterial({
    color: 0x312e81,
    metalness: 0.78,
    roughness: 0.28,
  });
  const hexCore = new THREE.Mesh(extrudeGeo, tier1Mat);
  hexCore.position.y = 0.18;
  hexCore.castShadow = true;
  tier1Group.add(hexCore);

  // 8 radial cooling/connector fins on Tier 1
  const finGeo = new THREE.BoxGeometry(0.18, 0.28, 0.42);
  const finMat = new THREE.MeshStandardMaterial({
    color: 0x38bdf8,
    metalness: 0.6,
    roughness: 0.35,
  });
  for (let i = 0; i < 8; i++) {
    const fin = new THREE.Mesh(finGeo, finMat);
    const a = (i / 8) * Math.PI * 2;
    fin.position.set(Math.cos(a) * 1.42, 0.02, Math.sin(a) * 1.42);
    fin.rotation.y = -a;
    tier1Group.add(fin);
  }
  group.add(tier1Group);

  // 5. Explodable Tier 2: Human-in-the-Loop Approval Gate Ring (Anodized Gold/Amber Gimbal)
  const tier2Group = new THREE.Group();
  tier2Group.position.y = 1.38;
  const gateRingGeo = new THREE.TorusGeometry(1.42, 0.075, 20, 64);
  gateRingGeo.rotateX(Math.PI / 2);
  const gateRingMat = new THREE.MeshPhysicalMaterial({
    color: 0xf59e0b,
    metalness: 0.92,
    roughness: 0.18,
    clearcoat: 0.6,
  });
  const gateRing = new THREE.Mesh(gateRingGeo, gateRingMat);
  tier2Group.add(gateRing);

  const lockNodeGeo = new THREE.CylinderGeometry(0.14, 0.14, 0.22, 16);
  const lockNodeMat = new THREE.MeshStandardMaterial({
    color: 0x10b981,
    emissive: 0x059669,
    emissiveIntensity: 0.45,
    metalness: 0.5,
    roughness: 0.45,
  });
  for (let i = 0; i < 4; i++) {
    const a = (i / 4) * Math.PI * 2 + Math.PI / 4;
    const node = new THREE.Mesh(lockNodeGeo, lockNodeMat);
    node.position.set(Math.cos(a) * 1.42, 0, Math.sin(a) * 1.42);
    tier2Group.add(node);
  }
  group.add(tier2Group);

  // 6. Explodable Tier 3: AI Intent & Action Processor (Octahedral Core + Inner Energy Sphere)
  const tier3Group = new THREE.Group();
  tier3Group.position.y = 1.95;
  const octGeo = new THREE.OctahedronGeometry(0.68, 1);
  const octMat = new THREE.MeshPhysicalMaterial({
    color: 0x6366f1,
    emissive: 0x4f46e5,
    emissiveIntensity: 0.5,
    metalness: 0.35,
    roughness: 0.15,
    wireframe: false,
    flatShading: true,
  });
  const octMesh = new THREE.Mesh(octGeo, octMat);
  octMesh.castShadow = true;
  tier3Group.add(octMesh);

  // Outer wireframe cage around octahedral core
  const cageGeo = new THREE.OctahedronGeometry(0.84, 1);
  const cageMat = new THREE.MeshStandardMaterial({
    color: 0x38bdf8,
    metalness: 0.85,
    roughness: 0.2,
    wireframe: true,
  });
  const cageMesh = new THREE.Mesh(cageGeo, cageMat);
  tier3Group.add(cageMesh);

  // Dual Gyroscopic Telemetry Rings
  const gimbal1Geo = new THREE.TorusGeometry(1.12, 0.032, 16, 64);
  const gimbalMat = new THREE.MeshStandardMaterial({
    color: 0x94a3b8,
    metalness: 0.9,
    roughness: 0.2,
  });
  const gimbal1 = new THREE.Mesh(gimbal1Geo, gimbalMat);
  tier3Group.add(gimbal1);

  const gimbal2Geo = new THREE.TorusGeometry(1.26, 0.028, 16, 64);
  const gimbal2 = new THREE.Mesh(gimbal2Geo, gimbalMat);
  gimbal2.rotation.y = Math.PI / 3;
  tier3Group.add(gimbal2);
  group.add(tier3Group);

  // 7. Optical Sapphire Containment Vessel (Explodable Tier 4)
  const glassGeo = new THREE.CylinderGeometry(1.62, 1.62, 1.65, 32, 1, true);
  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xe0f2fe,
    transmission: 0.92,
    opacity: 1,
    transparent: true,
    ior: 1.55,
    thickness: 1.2,
    roughness: 0.08,
    metalness: 0.05,
    clearcoat: 1.0,
    depthWrite: false,
    side: THREE.DoubleSide,
  });
  const glassVessel = new THREE.Mesh(glassGeo, glassMat);
  glassVessel.position.y = 1.65;
  glassVessel.renderOrder = 3;
  group.add(glassVessel);

  // 8. Top Crown Bezel Cap (Explodable Tier 5)
  const crownGroup = new THREE.Group();
  crownGroup.position.y = 2.55;
  const crownGeo = new THREE.CylinderGeometry(1.1, 1.64, 0.2, 16);
  const crownMat = new THREE.MeshPhysicalMaterial({
    color: 0x1e293b,
    metalness: 0.9,
    roughness: 0.22,
    clearcoat: 0.5,
  });
  const crownMesh = new THREE.Mesh(crownGeo, crownMat);
  crownGroup.add(crownMesh);

  const beaconGeo = new THREE.SphereGeometry(0.18, 24, 24);
  const beaconMat = new THREE.MeshStandardMaterial({
    color: 0x38bdf8,
    emissive: 0x0284c7,
    emissiveIntensity: 0.8,
    roughness: 0.2,
  });
  const beacon = new THREE.Mesh(beaconGeo, beaconMat);
  beacon.position.y = 0.16;
  crownGroup.add(beacon);
  group.add(crownGroup);

  group.userData = {
    tier1Group,
    tier2Group,
    tier3Group,
    glassVessel,
    crownGroup,
    octMesh,
    cageMesh,
    gimbal1,
    gimbal2,
    octMat,
    beaconMat,
    baseY: {
      tier1: 0.78,
      tier2: 1.38,
      tier3: 1.95,
      glass: 1.65,
      crown: 2.55,
    },
  };

  return group;
}

/**
 * Builds a 5-part Satellite Software Connector Assembly (THREE.Group)
 * Grounded at bottom-center (y = 0)
 */
function buildSatelliteNode(spec, index, qrTex, shadowTex) {
  const group = new THREE.Group();
  group.position.set(spec.pos[0], spec.pos[1], spec.pos[2]);
  group.name = `node-${spec.id}`;

  // 1. Contact shadow
  const shadowMesh = new THREE.Mesh(
    new THREE.PlaneGeometry(2.8, 2.8),
    new THREE.MeshBasicMaterial({
      map: shadowTex,
      transparent: true,
      depthWrite: false,
      opacity: 0.45,
      polygonOffset: true,
      polygonOffsetFactor: -1,
      polygonOffsetUnits: -1,
    })
  );
  shadowMesh.rotation.x = -Math.PI / 2;
  shadowMesh.position.y = 0.01;
  group.add(shadowMesh);

  // 2. Primary Base Pedestal
  const baseGeo = new THREE.CylinderGeometry(0.95, 1.12, 0.26, 8);
  const baseMat = new THREE.MeshStandardMaterial({
    color: 0x1e293b,
    metalness: 0.85,
    roughness: 0.25,
  });
  const baseMesh = new THREE.Mesh(baseGeo, baseMat);
  baseMesh.position.y = 0.13;
  baseMesh.castShadow = true;
  baseMesh.receiveShadow = true;
  group.add(baseMesh);

  // 3. Accent Status Ring
  const ringGeo = new THREE.TorusGeometry(0.98, 0.04, 16, 48);
  ringGeo.rotateX(Math.PI / 2);
  const ringMat = new THREE.MeshStandardMaterial({
    color: spec.color,
    emissive: spec.color,
    emissiveIntensity: 0.55,
    metalness: 0.5,
    roughness: 0.3,
  });
  const ringMesh = new THREE.Mesh(ringGeo, ringMat);
  ringMesh.position.y = 0.28;
  group.add(ringMesh);

  // 4. Domain-Specific Secondary Read & Accent Details
  const bodyGroup = new THREE.Group();
  bodyGroup.position.y = 0.32;

  if (index === 0) {
    // WhatsApp Cloud API Gateway: Transceiver column + signal rings + emerald core
    const colMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.48, 0.58, 0.95, 16),
      new THREE.MeshPhysicalMaterial({
        color: 0x065f46,
        metalness: 0.7,
        roughness: 0.25,
        clearcoat: 0.5,
      })
    );
    colMesh.position.y = 0.48;
    colMesh.castShadow = true;
    bodyGroup.add(colMesh);

    const orbMesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.36, 24, 24),
      new THREE.MeshStandardMaterial({
        color: 0x10b981,
        emissive: 0x059669,
        emissiveIntensity: 0.6,
        roughness: 0.2,
      })
    );
    orbMesh.position.y = 1.18;
    bodyGroup.add(orbMesh);

    const haloMesh = new THREE.Mesh(
      new THREE.TorusGeometry(0.56, 0.03, 12, 36),
      new THREE.MeshStandardMaterial({ color: 0x34d399, metalness: 0.8, roughness: 0.2 })
    );
    haloMesh.position.y = 1.18;
    haloMesh.rotation.x = Math.PI / 3;
    bodyGroup.add(haloMesh);
  } else if (index === 1) {
    // Tally & Zoho ERP Vault: 3 stacked precision ledger blades
    for (let b = 0; b < 3; b++) {
      const blade = new THREE.Mesh(
        new THREE.BoxGeometry(1.15, 0.26, 0.88),
        new THREE.MeshStandardMaterial({
          color: b === 1 ? 0x4338ca : 0x312e81,
          metalness: 0.8,
          roughness: 0.28 + b * 0.08,
        })
      );
      blade.position.y = 0.22 + b * 0.36;
      blade.castShadow = true;
      bodyGroup.add(blade);

      const ledBar = new THREE.Mesh(
        new THREE.BoxGeometry(0.95, 0.05, 0.92),
        new THREE.MeshStandardMaterial({
          color: 0x818cf8,
          emissive: 0x6366f1,
          emissiveIntensity: 0.65,
        })
      );
      ledBar.position.y = 0.22 + b * 0.36;
      bodyGroup.add(ledBar);
    }
  } else if (index === 2) {
    // UPI & Razorpay Rail: Angled payment terminal + procedural QR plate
    const stand = new THREE.Mesh(
      new THREE.BoxGeometry(0.92, 0.85, 0.72),
      new THREE.MeshStandardMaterial({
        color: 0x0f172a,
        metalness: 0.82,
        roughness: 0.28,
      })
    );
    stand.position.y = 0.44;
    stand.castShadow = true;
    bodyGroup.add(stand);

    const qrPlate = new THREE.Mesh(
      new THREE.PlaneGeometry(0.74, 0.74),
      new THREE.MeshBasicMaterial({ map: qrTex })
    );
    qrPlate.position.set(0, 0.92, 0);
    qrPlate.rotation.x = -Math.PI / 3;
    bodyGroup.add(qrPlate);

    const frame = new THREE.Mesh(
      new THREE.BoxGeometry(0.86, 0.08, 0.86),
      new THREE.MeshStandardMaterial({
        color: 0x06b6d4,
        metalness: 0.75,
        roughness: 0.2,
      })
    );
    frame.position.set(0, 0.89, 0);
    frame.rotation.x = -Math.PI / 6;
    bodyGroup.add(frame);
  } else {
    // POS & Google Sheets Sync Array: 2x2 modular grid cells + relay mast
    const cellGeo = new THREE.BoxGeometry(0.46, 0.42, 0.46);
    const offsets = [
      [-0.28, -0.28],
      [0.28, -0.28],
      [-0.28, 0.28],
      [0.28, 0.28],
    ];
    offsets.forEach(([ox, oz], idx) => {
      const cell = new THREE.Mesh(
        cellGeo,
        new THREE.MeshStandardMaterial({
          color: idx % 2 === 0 ? 0xd97706 : 0xf59e0b,
          metalness: 0.65,
          roughness: 0.25 + idx * 0.08,
        })
      );
      cell.position.set(ox, 0.25 + (idx % 2) * 0.14, oz);
      cell.castShadow = true;
      bodyGroup.add(cell);
    });

    const mast = new THREE.Mesh(
      new THREE.CylinderGeometry(0.06, 0.09, 0.75, 12),
      new THREE.MeshStandardMaterial({ color: 0xfbbf24, metalness: 0.85, roughness: 0.2 })
    );
    mast.position.y = 0.82;
    bodyGroup.add(mast);
  }

  group.add(bodyGroup);

  // Invisible simplified proxy collision box on layer 1 for fast raycasting
  const proxyGeo = new THREE.CylinderGeometry(1.15, 1.15, 1.8, 12);
  const proxyMat = new THREE.MeshBasicMaterial({ visible: false });
  const proxyMesh = new THREE.Mesh(proxyGeo, proxyMat);
  proxyMesh.position.y = 0.9;
  proxyMesh.layers.enable(1);
  proxyMesh.userData = { nodeIndex: index, spec };
  group.add(proxyMesh);

  group.userData = {
    spec,
    index,
    ringMat,
    bodyGroup,
    proxyMesh,
    activeWeight: 1,
  };

  return group;
}

/**
 * Initializes the main Interactive 3D Operations Topology Viewport (#qefro-3d-stage)
 */
function initMainArchitectureStage() {
  const stageEl = document.getElementById("qefro-3d-stage");
  const canvasMount = document.getElementById("qefro-3d-canvas-mount");
  if (!stageEl || !canvasMount) return null;

  const isHeadless =
    navigator.webdriver || /HeadlessChrome/i.test(navigator.userAgent);

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      antialias: !isHeadless,
      alpha: false,
      powerPreference: "high-performance",
    });
  } catch (_) {
    stageEl.classList.add("webgl-fallback");
    return null;
  }

  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;
  renderer.setPixelRatio(isHeadless ? 1 : Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = !isHeadless;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const width = canvasMount.clientWidth || 960;
  const height = canvasMount.clientHeight || 540;
  renderer.setSize(width, height);
  canvasMount.appendChild(renderer.domElement);

  const scene = new THREE.Scene();

  // Studio Environment Reflection (RoomEnvironment + PMREMGenerator)
  const pmremGenerator = new THREE.PMREMGenerator(renderer);
  scene.environment = pmremGenerator.fromScene(new RoomEnvironment(), 0.04).texture;
  pmremGenerator.dispose();

  const isDarkInitial = document.documentElement.getAttribute("data-theme") === "dark";
  const bgHex = isDarkInitial ? 0x090d16 : 0xf1f5f9;
  scene.background = new THREE.Color(bgHex);
  scene.fog = new THREE.FogExp2(bgHex, 0.032);

  const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
  camera.position.set(0, 6.2, 11.8);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.06;
  controls.enablePan = false;
  controls.minDistance = 5.2;
  controls.maxDistance = 16.5;
  controls.maxPolarAngle = Math.PI / 2 - 0.06;
  controls.minPolarAngle = 0.25;
  controls.target.set(0, 1.1, 0);

  // 3-Point Studio Lighting Rig
  const hemiLight = new THREE.HemisphereLight(0xe0f2fe, 0x1e1b4b, isDarkInitial ? 0.95 : 1.35);
  scene.add(hemiLight);

  const keyLight = new THREE.DirectionalLight(0xfffbeb, isDarkInitial ? 2.2 : 2.6);
  keyLight.position.set(6, 11, 7);
  keyLight.castShadow = !isHeadless;
  keyLight.shadow.mapSize.width = 1024;
  keyLight.shadow.mapSize.height = 1024;
  keyLight.shadow.camera.near = 1;
  keyLight.shadow.camera.far = 28;
  const d = 8.5;
  keyLight.shadow.camera.left = -d;
  keyLight.shadow.camera.right = d;
  keyLight.shadow.camera.top = d;
  keyLight.shadow.camera.bottom = -d;
  keyLight.shadow.bias = -0.0005;
  keyLight.shadow.normalBias = 0.02;
  scene.add(keyLight);

  const rimLight = new THREE.DirectionalLight(0x38bdf8, 1.65);
  rimLight.position.set(-7, 5, -6);
  scene.add(rimLight);

  // Ground Platform & Subtle Engineering Grid (Offset to avoid coplanar Z-fighting)
  const floorGeo = new THREE.PlaneGeometry(42, 42);
  const floorMat = new THREE.MeshStandardMaterial({
    color: isDarkInitial ? 0x0b0f19 : 0xe2e8f0,
    roughness: 0.85,
    metalness: 0.1,
  });
  const floorMesh = new THREE.Mesh(floorGeo, floorMat);
  floorMesh.rotation.x = -Math.PI / 2;
  floorMesh.position.y = 0;
  floorMesh.receiveShadow = true;
  scene.add(floorMesh);

  const gridHelper = new THREE.GridHelper(
    26,
    26,
    isDarkInitial ? 0x312e81 : 0x94a3b8,
    isDarkInitial ? 0x1e293b : 0xcbd5e1
  );
  gridHelper.position.y = 0.02;
  scene.add(gridHelper);

  // Procedural Textures
  const maxAniso = renderer.capabilities.getMaxAnisotropy();
  const dialTex = createProceduralDialTexture(maxAniso);
  const qrTex = createProceduralQRTexture(maxAniso);
  const shadowTex = createContactShadowTexture();

  // Central Core
  const coreGroup = buildCentralCore(dialTex, shadowTex);
  scene.add(coreGroup);

  // Proxy collision cylinder for Central Core on layer 1
  const coreProxy = new THREE.Mesh(
    new THREE.CylinderGeometry(2.1, 2.1, 2.8, 16),
    new THREE.MeshBasicMaterial({ visible: false })
  );
  coreProxy.position.y = 1.4;
  coreProxy.layers.enable(1);
  coreProxy.userData = {
    isCore: true,
    spec: {
      name: "00. Qefro Deterministic Core",
      role: "Schema-Validated Execution & Human Approval Engine",
      detail: "Validates SKU pricing, RBAC permissions & audit logs before executing actions",
    },
  };
  coreGroup.add(coreProxy);

  // Satellite Nodes & Curved Optical Conduits
  const satelliteGroups = [];
  const curves = [];
  const conduitMats = [];

  NODE_SPECS.forEach((spec, idx) => {
    const nodeGroup = buildSatelliteNode(spec, idx, qrTex, shadowTex);
    scene.add(nodeGroup);
    satelliteGroups.push(nodeGroup);

    const start = new THREE.Vector3(spec.pos[0], 0.65, spec.pos[2]);
    const mid = new THREE.Vector3(spec.pos[0] * 0.48, 1.35, spec.pos[2] * 0.48);
    const end = new THREE.Vector3(0, 1.15, 0);
    const curve = new THREE.CatmullRomCurve3([start, mid, end]);
    curves.push(curve);

    const tubeGeo = new THREE.TubeGeometry(curve, 36, 0.038, 8, false);
    const tubeMat = new THREE.MeshStandardMaterial({
      color: spec.color,
      emissive: spec.color,
      emissiveIntensity: 0.35,
      metalness: 0.5,
      roughness: 0.3,
      transparent: true,
      opacity: 0.78,
    });
    const tubeMesh = new THREE.Mesh(tubeGeo, tubeMat);
    scene.add(tubeMesh);
    conduitMats.push(tubeMat);
  });

  // Instanced Data Packets (48 bi-directional packets across 4 curves)
  const packetCount = 48;
  const packetGeo = new THREE.SphereGeometry(0.085, 12, 12);
  const packetMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const packetInstanced = new THREE.InstancedMesh(packetGeo, packetMat, packetCount);
  packetInstanced.frustumCulled = false;

  const packetData = [];
  for (let i = 0; i < packetCount; i++) {
    const curveIndex = i % 4;
    const inbound = i % 2 === 0;
    const tOffset = (Math.floor(i / 4) / (packetCount / 4)) % 1;
    packetData.push({
      curveIndex,
      inbound,
      t: tOffset,
      speed: 0.28 + (i % 5) * 0.04,
      scale: 0.85 + (i % 3) * 0.15,
    });
    _color.setHex(NODE_SPECS[curveIndex].color);
    packetInstanced.setColorAt(i, _color);
    _mat4.makeScale(1, 1, 1);
    packetInstanced.setMatrixAt(i, _mat4);
  }
  if (packetInstanced.instanceColor) packetInstanced.instanceColor.needsUpdate = true;
  packetInstanced.computeBoundingSphere();
  scene.add(packetInstanced);

  // Pre-warm shaders
  renderer.compile(scene, camera);

  // Interactive State
  const state = {
    preset: "all",
    explodedTarget: 0,
    explodedCurrent: 0,
    autoOrbit: true,
    camTargetPos: new THREE.Vector3(...WORKFLOW_PRESETS.all.camPos),
    camTargetLook: new THREE.Vector3(...WORKFLOW_PRESETS.all.lookAt),
    transitioningCamera: false,
    isVisible: true,
    burstTimer: 0,
  };

  // DOM HUD Elements
  const hudTitle = document.getElementById("qefro-3d-hud-title");
  const hudSub = document.getElementById("qefro-3d-hud-sub");
  const hudMetric = document.getElementById("qefro-3d-hud-metric");
  const explodeSlider = document.getElementById("qefro-3d-explode-slider");
  const explodeVal = document.getElementById("qefro-3d-explode-val");
  const orbitBtn = document.getElementById("qefro-3d-orbit-btn");
  const resetBtn = document.getElementById("qefro-3d-reset-btn");
  const dockWrap = document.getElementById("qefro-3d-dock-wrap");
  const dockToggle = document.getElementById("qefro-3d-dock-toggle");
  const presetBtns = stageEl.querySelectorAll("[data-3d-preset]");

  function applyPreset(presetKey, animateCamera = true) {
    const p = WORKFLOW_PRESETS[presetKey] || WORKFLOW_PRESETS.all;
    state.preset = presetKey;
    if (animateCamera) {
      state.camTargetPos.set(...p.camPos);
      state.camTargetLook.set(...p.lookAt);
      state.transitioningCamera = true;
    }
    state.burstTimer = 1.2;

    if (hudTitle) hudTitle.textContent = p.label;
    if (hudSub) hudSub.textContent = p.subtitle;
    if (hudMetric) hudMetric.textContent = p.metric;

    presetBtns.forEach((btn) => {
      const active = btn.getAttribute("data-3d-preset") === presetKey;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-pressed", String(active));
    });

    satelliteGroups.forEach((sg, idx) => {
      const isActive = p.activeNodes.includes(idx);
      sg.userData.activeWeight = isActive ? 1.0 : 0.25;
      conduitMats[idx].opacity = isActive ? 0.88 : 0.16;
      conduitMats[idx].emissiveIntensity = isActive ? 0.55 : 0.1;
      sg.userData.ringMat.emissiveIntensity = isActive ? 0.8 : 0.15;
    });

    coreGroup.userData.octMat.emissive.setHex(p.accentHex);
    coreGroup.userData.beaconMat.emissive.setHex(p.accentHex);
  }

  presetBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const key = btn.getAttribute("data-3d-preset");
      applyPreset(key, true);
    });
  });

  if (explodeSlider) {
    explodeSlider.addEventListener("input", (e) => {
      const val = parseFloat(e.target.value) || 0;
      state.explodedTarget = val / 100;
      if (explodeVal) explodeVal.textContent = `${Math.round(val)}%`;
    });
  }

  if (orbitBtn) {
    orbitBtn.addEventListener("click", () => {
      state.autoOrbit = !state.autoOrbit;
      orbitBtn.classList.toggle("is-active", state.autoOrbit);
      orbitBtn.setAttribute("aria-pressed", String(state.autoOrbit));
      orbitBtn.textContent = state.autoOrbit ? "Auto-Orbit: On" : "Auto-Orbit: Off";
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      state.explodedTarget = 0;
      if (explodeSlider) explodeSlider.value = "0";
      if (explodeVal) explodeVal.textContent = "0%";
      applyPreset("all", true);
    });
  }

  if (dockToggle && dockWrap) {
    dockToggle.addEventListener("click", () => {
      const collapsed = dockWrap.classList.toggle("is-collapsed");
      dockToggle.setAttribute("aria-expanded", String(!collapsed));
      dockToggle.textContent = collapsed ? "▴ Show Controls" : "▾ Hide Controls";
    });
  }

  // Stop camera preset glide when user manually drags OrbitControls
  controls.addEventListener("start", () => {
    state.transitioningCamera = false;
  });

  // High-performance Raycasting on Layer 1 for Hover/Click Node Inspection
  const raycaster = new THREE.Raycaster();
  raycaster.layers.set(1);
  const pointer = new THREE.Vector2();
  let lastRaycastTime = 0;

  renderer.domElement.addEventListener("pointermove", (e) => {
    const now = performance.now();
    if (now - lastRaycastTime < 50) return;
    lastRaycastTime = now;

    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster.intersectObjects(scene.children, true);
    renderer.domElement.style.cursor = hits.length > 0 ? "pointer" : "grab";
  });

  renderer.domElement.addEventListener("click", (e) => {
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster.intersectObjects(scene.children, true);
    if (hits.length > 0) {
      const hitData = hits[0].object.userData;
      if (hitData && hitData.spec) {
        if (hudTitle) hudTitle.textContent = hitData.spec.name;
        if (hudSub) hudSub.textContent = hitData.spec.detail;
        if (hudMetric) hudMetric.textContent = hitData.spec.role;
        state.burstTimer = 1.0;
      }
    }
  });

  // Theme Sync Observer
  const updateThemeColors = () => {
    const dark = document.documentElement.getAttribute("data-theme") === "dark";
    const nextBg = dark ? 0x090d16 : 0xf1f5f9;
    scene.background.setHex(nextBg);
    scene.fog.color.setHex(nextBg);
    floorMat.color.setHex(dark ? 0x0b0f19 : 0xe2e8f0);
    hemiLight.intensity = dark ? 0.95 : 1.35;
    keyLight.intensity = dark ? 2.2 : 2.6;
  };

  const themeObserver = new MutationObserver(updateThemeColors);
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });

  // Pause rendering when scrolled out of viewport
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        state.isVisible = entry.isIntersecting;
      });
    },
    { threshold: 0.05 }
  );
  io.observe(stageEl);

  // Resize Handling
  const onResize = () => {
    const w = canvasMount.clientWidth || 960;
    const h = canvasMount.clientHeight || 540;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  };
  window.addEventListener("resize", onResize);

  // Animation Loop with Clock + Exponential Damping
  const clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);
    if (!state.isVisible) return;

    const delta = Math.min(clock.getDelta(), 0.1);
    const elapsed = clock.getElapsedTime();

    // Smoothly damp exploded view separation
    state.explodedCurrent = THREE.MathUtils.damp(
      state.explodedCurrent,
      state.explodedTarget,
      6.5,
      delta
    );
    const ex = state.explodedCurrent;
    const {
      tier1Group,
      tier2Group,
      tier3Group,
      glassVessel,
      crownGroup,
      octMesh,
      cageMesh,
      gimbal1,
      gimbal2,
      baseY,
    } = coreGroup.userData;

    tier1Group.position.y = baseY.tier1 + ex * 0.45;
    tier2Group.position.y = baseY.tier2 + ex * 1.05;
    tier3Group.position.y = baseY.tier3 + ex * 1.75;
    glassVessel.position.y = baseY.glass + ex * 1.15;
    crownGroup.position.y = baseY.crown + ex * 2.45;

    // Core mechanical kinematics
    octMesh.rotation.y += delta * 0.65;
    octMesh.rotation.x = Math.sin(elapsed * 1.2) * 0.18;
    cageMesh.rotation.y -= delta * 0.4;
    gimbal1.rotation.x += delta * 0.8;
    gimbal1.rotation.y += delta * 0.5;
    gimbal2.rotation.z -= delta * 0.7;
    tier2Group.rotation.y += delta * 0.25;

    // Satellite subtle float
    satelliteGroups.forEach((sg, idx) => {
      sg.userData.bodyGroup.position.y =
        0.32 + Math.sin(elapsed * 1.8 + idx * 1.4) * 0.04;
    });

    // Update Instanced Data Packets along curves
    if (state.burstTimer > 0) {
      state.burstTimer = Math.max(0, state.burstTimer - delta);
    }
    const speedBoost = 1 + state.burstTimer * 1.6;
    const activeNodes =
      (WORKFLOW_PRESETS[state.preset] || WORKFLOW_PRESETS.all).activeNodes;

    for (let i = 0; i < packetCount; i++) {
      const p = packetData[i];
      const isNodeActive = activeNodes.includes(p.curveIndex);
      p.t = (p.t + delta * p.speed * speedBoost * (isNodeActive ? 1 : 0.25)) % 1;
      const sampleT = p.inbound ? p.t : 1 - p.t;
      curves[p.curveIndex].getPointAt(sampleT, _vec3);

      const s = isNodeActive ? p.scale : p.scale * 0.35;
      _scale.set(s, s, s);
      _quat.identity();
      _mat4.compose(_vec3, _quat, _scale);
      packetInstanced.setMatrixAt(i, _mat4);
    }
    packetInstanced.instanceMatrix.needsUpdate = true;

    // Camera preset smooth damping or gentle auto-orbit
    if (state.transitioningCamera) {
      camera.position.x = THREE.MathUtils.damp(
        camera.position.x,
        state.camTargetPos.x,
        4.5,
        delta
      );
      camera.position.y = THREE.MathUtils.damp(
        camera.position.y,
        state.camTargetPos.y,
        4.5,
        delta
      );
      camera.position.z = THREE.MathUtils.damp(
        camera.position.z,
        state.camTargetPos.z,
        4.5,
        delta
      );
      controls.target.x = THREE.MathUtils.damp(
        controls.target.x,
        state.camTargetLook.x,
        5.0,
        delta
      );
      controls.target.y = THREE.MathUtils.damp(
        controls.target.y,
        state.camTargetLook.y,
        5.0,
        delta
      );
      controls.target.z = THREE.MathUtils.damp(
        controls.target.z,
        state.camTargetLook.z,
        5.0,
        delta
      );
      if (camera.position.distanceTo(state.camTargetPos) < 0.08) {
        state.transitioningCamera = false;
      }
    } else if (state.autoOrbit) {
      controls.autoRotate = true;
      controls.autoRotateSpeed = 0.65;
    } else {
      controls.autoRotate = false;
    }

    controls.update();
    renderer.render(scene, camera);
  }

  animate();

  return {
    applyPreset,
    triggerBurst() {
      state.burstTimer = 1.5;
    },
  };
}

/**
 * Initializes the subtle, interactive 3D spatial field inside the Hero section (#hero-three-canvas)
 * Responds to pointer tilt and Hero scenario tab switches.
 */
function initHeroSpatialBackdrop(mainStageController) {
  const heroCanvasMount = document.getElementById("hero-three-mount");
  if (!heroCanvasMount) return;

  const isHeadless =
    navigator.webdriver || /HeadlessChrome/i.test(navigator.userAgent);

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      antialias: !isHeadless,
      alpha: true,
      powerPreference: "high-performance",
    });
  } catch (_) {
    return;
  }

  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.setPixelRatio(isHeadless ? 1 : Math.min(window.devicePixelRatio, 1.75));

  const w = heroCanvasMount.clientWidth || 1200;
  const h = heroCanvasMount.clientHeight || 640;
  renderer.setSize(w, h);
  heroCanvasMount.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  pmrem.dispose();

  const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 60);
  camera.position.set(0, 0, 11);

  const hemi = new THREE.HemisphereLight(0xe0f2fe, 0x312e81, 1.2);
  scene.add(hemi);
  const dir = new THREE.DirectionalLight(0xffffff, 1.8);
  dir.position.set(4, 6, 5);
  scene.add(dir);

  // Build an orbital 3D assembly positioned behind the right-hand Hero Demo Bezel
  const cluster = new THREE.Group();
  cluster.position.set(2.8, 0.2, -1.5);
  scene.add(cluster);

  // Outer precision ring
  const outerRing = new THREE.Mesh(
    new THREE.TorusGeometry(3.4, 0.025, 16, 80),
    new THREE.MeshStandardMaterial({
      color: 0x6366f1,
      metalness: 0.85,
      roughness: 0.2,
      transparent: true,
      opacity: 0.42,
    })
  );
  outerRing.rotation.x = Math.PI / 3;
  cluster.add(outerRing);

  // Inner counter-rotating ring
  const innerRing = new THREE.Mesh(
    new THREE.TorusGeometry(2.45, 0.02, 16, 64),
    new THREE.MeshStandardMaterial({
      color: 0x06b6d4,
      metalness: 0.8,
      roughness: 0.25,
      transparent: true,
      opacity: 0.38,
    })
  );
  innerRing.rotation.y = Math.PI / 4;
  cluster.add(innerRing);

  // 24 Instanced orbital relay nodes around the hero backdrop
  const nodeCount = 24;
  const nodeGeo = new THREE.OctahedronGeometry(0.11, 0);
  const nodeMat = new THREE.MeshStandardMaterial({
    color: 0x818cf8,
    metalness: 0.75,
    roughness: 0.25,
  });
  const nodesInstanced = new THREE.InstancedMesh(nodeGeo, nodeMat, nodeCount);
  const nodeAngles = [];
  for (let i = 0; i < nodeCount; i++) {
    const angle = (i / nodeCount) * Math.PI * 2;
    const radius = 2.4 + (i % 3) * 0.65;
    const yOff = Math.sin(angle * 3) * 0.9;
    nodeAngles.push({ angle, radius, yOff, speed: 0.12 + (i % 4) * 0.03 });
    _vec3.set(Math.cos(angle) * radius, yOff, Math.sin(angle) * radius);
    _quat.identity();
    _scale.setScalar(0.7 + (i % 3) * 0.25);
    _mat4.compose(_vec3, _quat, _scale);
    nodesInstanced.setMatrixAt(i, _mat4);
  }
  nodesInstanced.computeBoundingSphere();
  cluster.add(nodesInstanced);

  let pointerX = 0;
  let pointerY = 0;
  let isHeroVisible = true;

  window.addEventListener(
    "pointermove",
    (e) => {
      pointerX = (e.clientX / window.innerWidth - 0.5) * 2;
      pointerY = (e.clientY / window.innerHeight - 0.5) * 2;
    },
    { passive: true }
  );

  // Connect Hero scenario tabs & action buttons to both 3D scenes
  const SCENARIO_COLORS = {
    realestate: 0x0ea5e9,
    restaurant: 0xf59e0b,
    billing: 0x10b981,
    crm: 0x8b5cf6,
  };

  document.querySelectorAll("[data-hero-tab]").forEach((tab) => {
    tab.addEventListener("click", () => {
      const key = tab.dataset.heroTab;
      const hex = SCENARIO_COLORS[key] || 0x6366f1;
      outerRing.material.color.setHex(hex);
      nodeMat.color.setHex(hex);
      if (mainStageController && WORKFLOW_PRESETS[key]) {
        mainStageController.applyPreset(key, true);
      }
    });
  });

  // Wire interactive buttons inside the Hero Demo cards so clicking them triggers live feedback + 3D burst
  document.querySelectorAll(".hero-demo-body .demo-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const originalText = btn.dataset.originalText || btn.textContent;
      btn.dataset.originalText = originalText;
      btn.textContent = "✓ Executed via Qefro Core";
      btn.classList.add("is-executed");
      if (mainStageController) mainStageController.triggerBurst();
      setTimeout(() => {
        btn.textContent = originalText;
        btn.classList.remove("is-executed");
      }, 2200);
    });
  });

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        isHeroVisible = entry.isIntersecting;
      });
    },
    { threshold: 0.05 }
  );
  io.observe(heroCanvasMount);

  window.addEventListener("resize", () => {
    const nw = heroCanvasMount.clientWidth || 1200;
    const nh = heroCanvasMount.clientHeight || 640;
    camera.aspect = nw / nh;
    camera.updateProjectionMatrix();
    renderer.setSize(nw, nh);
  });

  const clock = new THREE.Clock();
  function animateHero() {
    requestAnimationFrame(animateHero);
    if (!isHeroVisible) return;

    const dt = Math.min(clock.getDelta(), 0.1);
    const t = clock.getElapsedTime();

    cluster.rotation.y = THREE.MathUtils.damp(
      cluster.rotation.y,
      pointerX * 0.28 + t * 0.08,
      3.5,
      dt
    );
    cluster.rotation.x = THREE.MathUtils.damp(
      cluster.rotation.x,
      -pointerY * 0.18,
      3.5,
      dt
    );

    outerRing.rotation.z += dt * 0.15;
    innerRing.rotation.x -= dt * 0.22;

    for (let i = 0; i < nodeCount; i++) {
      const n = nodeAngles[i];
      const a = n.angle + t * n.speed;
      _vec3.set(
        Math.cos(a) * n.radius,
        n.yOff + Math.sin(t * 1.5 + i) * 0.12,
        Math.sin(a) * n.radius
      );
      _euler.set(t * 0.5, a, 0);
      _quat.setFromEuler(_euler);
      const s = 0.7 + (i % 3) * 0.25;
      _scale.set(s, s, s);
      _mat4.compose(_vec3, _quat, _scale);
      nodesInstanced.setMatrixAt(i, _mat4);
    }
    nodesInstanced.instanceMatrix.needsUpdate = true;

    renderer.render(scene, camera);
  }
  animateHero();
}

export function initThreeExperience() {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const mainController = initMainArchitectureStage();
  if (!reducedMotion) {
    initHeroSpatialBackdrop(mainController);
  }
}
