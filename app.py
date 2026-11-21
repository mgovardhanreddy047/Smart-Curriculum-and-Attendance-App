import http.server
import socketserver
import webbrowser
import threading
import json
import os

PORT = 8080
STATE_FILE = "mu_ict_shared_state.json"
STATE_LOCK = threading.Lock()
SHARED_STORE = {}

if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            SHARED_STORE = json.load(f)
    except Exception:
        SHARED_STORE = {}

def save_store_to_disk():
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(SHARED_STORE, f)
    except Exception:
        pass

FULL_WEBSITE_CODE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Marwadi University ICT - Smart Attendance & Activity System</title>

  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- React & ReactDOM -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>

  <!-- Babel Standalone for JSX compilation in the browser -->
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <!-- Lucide Icons (Vanilla JS UMD) -->
  <script src="https://unpkg.com/lucide@latest"></script>

  <!-- Real Optical QR Generation & Decoding Libraries -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js"></script>
  <script src="https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js"></script>
</head>
<body class="bg-[#090d16] text-slate-100 font-sans antialiased">
  <div id="root"></div>

  <script type="text/babel">
    const { useState, useEffect, useRef, useCallback } = React;

    // =========================================================================
    // 1. LUCIDE ICON WRAPPER FOR REACT
    // =========================================================================
    function createLucideIcon(iconName) {
      return function LucideIcon({ className = "" }) {
        const spanRef = useRef(null);
        useEffect(() => {
          if (spanRef.current && window.lucide && window.lucide.icons[iconName]) {
            const svg = window.lucide.createElement(window.lucide.icons[iconName]);
            if (className) {
              svg.setAttribute("class", className);
            }
            spanRef.current.innerHTML = "";
            spanRef.current.appendChild(svg);
          }
        }, [className]);

        return <span ref={spanRef} className="inline-flex items-center justify-center shrink-0" />;
      };
    }

    const User = createLucideIcon('User');
    const Lock = createLucideIcon('Lock');
    const Eye = createLucideIcon('Eye');
    const EyeOff = createLucideIcon('EyeOff');
    const QrCode = createLucideIcon('QrCode');
    const Camera = createLucideIcon('Camera');
    const CheckCircle = createLucideIcon('CheckCircle');
    const AlertTriangle = createLucideIcon('AlertTriangle');
    const BookOpen = createLucideIcon('BookOpen');
    const Calendar = createLucideIcon('Calendar');
    const Clock = createLucideIcon('Clock');
    const LogOut = createLucideIcon('LogOut');
    const Plus = createLucideIcon('Plus');
    const Shield = createLucideIcon('Shield');
    const GraduationCap = createLucideIcon('GraduationCap');
    const Award = createLucideIcon('Award');
    const FileText = createLucideIcon('FileText');
    const Upload = createLucideIcon('Upload');
    const BarChart2 = createLucideIcon('BarChart2');
    const Users = createLucideIcon('Users');
    const Bell = createLucideIcon('Bell');
    const Check = createLucideIcon('Check');
    const Trash2 = createLucideIcon('Trash2');
    const Video = createLucideIcon('Video');
    const HelpCircle = createLucideIcon('HelpCircle');
    const Layers = createLucideIcon('Layers');
    const AlertCircle = createLucideIcon('AlertCircle');
    const UserCheck = createLucideIcon('UserCheck');
    const Sliders = createLucideIcon('Sliders');
    const FileCheck = createLucideIcon('FileCheck');
    const MapPin = createLucideIcon('MapPin');
    const Zap = createLucideIcon('Zap');
    const Sparkles = createLucideIcon('Sparkles');
    const Gauge = createLucideIcon('Gauge');
    const FileCode2 = createLucideIcon('FileCode2');
    const CalendarCheck = createLucideIcon('CalendarCheck');
    const Download = createLucideIcon('Download');
    const Edit3 = createLucideIcon('Edit3');
    const RefreshCw = createLucideIcon('RefreshCw');
    const Maximize2 = createLucideIcon('Maximize2');
    const Menu = createLucideIcon('Menu');
    const X = createLucideIcon('X');
    const SwitchCamera = createLucideIcon('SwitchCamera');

    // =========================================================================
    // 2. RELIABLE MULTI-CAMERA HOOK (FRONT & BACK CAMERA FOR LAPTOP & MOBILE)
    // =========================================================================
    function useReliableCamera({ videoRef, initialFacingMode = 'environment', enabled = true }) {
      const [facingMode, setFacingMode] = useState(initialFacingMode);
      const [devices, setDevices] = useState([]);
      const [selectedDeviceId, setSelectedDeviceId] = useState('');
      const [cameraActive, setCameraActive] = useState(false);
      const [cameraLoading, setCameraLoading] = useState(false);
      const [cameraError, setCameraError] = useState('');
      const [activeLabel, setActiveLabel] = useState('');
      const [resolutionText, setResolutionText] = useState('');
      const [isMirrored, setIsMirrored] = useState(initialFacingMode === 'user');
      const [fitMode, setFitMode] = useState('cover');
      const [retryNonce, setRetryNonce] = useState(0);

      const streamRef = useRef(null);

      const stopActiveStream = useCallback(() => {
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => {
            try {
              track.stop();
            } catch (e) {}
          });
          streamRef.current = null;
        }
        if (videoRef.current) {
          try {
            videoRef.current.pause();
            videoRef.current.srcObject = null;
          } catch (e) {}
        }
        setCameraActive(false);
      }, [videoRef]);

      const refreshVideoDevices = useCallback(async () => {
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return [];
        try {
          const allDevices = await navigator.mediaDevices.enumerateDevices();
          const videoInputs = allDevices.filter((d) => d.kind === 'videoinput');
          setDevices(videoInputs);
          return videoInputs;
        } catch (e) {
          return [];
        }
      }, []);

      useEffect(() => {
        let cancelled = false;

        async function startCameraHardware() {
          if (!enabled) {
            stopActiveStream();
            return;
          }

          if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setCameraError('Camera API unavailable in this browser. Please open over HTTPS or localhost, or use Upload.');
            setCameraLoading(false);
            return;
          }

          setCameraLoading(true);
          setCameraError('');
          stopActiveStream();

          await new Promise((r) => setTimeout(r, 120));
          if (cancelled) return;

          const availableInputs = await refreshVideoDevices();
          if (cancelled) return;

          const attempts = [];

          if (selectedDeviceId) {
            attempts.push({
              video: {
                deviceId: { exact: selectedDeviceId },
                width: { ideal: 1280 },
                height: { ideal: 720 }
              },
              audio: false
            });
          }

          if (availableInputs.length > 0) {
            const wantFront = facingMode === 'user';
            const matched = availableInputs.find((d) => {
              const lbl = (d.label || '').toLowerCase();
              if (wantFront) {
                return lbl.includes('front') || lbl.includes('user') || lbl.includes('facetime') || lbl.includes('integrated') || lbl.includes('webcam');
              }
              return lbl.includes('back') || lbl.includes('rear') || lbl.includes('environment') || lbl.includes('world');
            });
            if (matched && matched.deviceId && matched.deviceId !== selectedDeviceId) {
              attempts.push({
                video: {
                  deviceId: { exact: matched.deviceId },
                  width: { ideal: 1280 },
                  height: { ideal: 720 }
                },
                audio: false
              });
            }
          }

          attempts.push({
            video: {
              facingMode: { ideal: facingMode },
              width: { ideal: 1280 },
              height: { ideal: 720 }
            },
            audio: false
          });

          attempts.push({
            video: { facingMode },
            audio: false
          });

          attempts.push({
            video: true,
            audio: false
          });

          let acquiredStream = null;
          let lastError = null;

          for (const constraints of attempts) {
            if (cancelled) break;
            try {
              acquiredStream = await navigator.mediaDevices.getUserMedia(constraints);
              if (acquiredStream) break;
            } catch (err) {
              lastError = err;
            }
          }

          if (cancelled) {
            if (acquiredStream) {
              acquiredStream.getTracks().forEach((t) => t.stop());
            }
            return;
          }

          if (!acquiredStream) {
            setCameraLoading(false);
            setCameraActive(false);
            const reason =
              lastError?.name === 'NotAllowedError'
                ? 'Camera permission denied. Please allow camera access in browser settings and tap Retry.'
                : lastError?.name === 'NotFoundError'
                ? 'No camera hardware detected on this device. Use Upload instead.'
                : 'Camera is busy or unavailable in another app. Close other camera apps and tap Retry.';
            setCameraError(reason);
            return;
          }

          streamRef.current = acquiredStream;
          const postDevices = await refreshVideoDevices();

          const videoTrack = acquiredStream.getVideoTracks()[0];
          const settings = videoTrack?.getSettings ? videoTrack.getSettings() : {};
          const rawLabel = videoTrack?.label || '';
          const lowerLabel = rawLabel.toLowerCase();

          let detectedFront = facingMode === 'user';
          if (settings.facingMode === 'environment' || lowerLabel.includes('back') || lowerLabel.includes('rear') || lowerLabel.includes('environment')) {
            detectedFront = false;
          } else if (settings.facingMode === 'user' || lowerLabel.includes('front') || lowerLabel.includes('facetime') || lowerLabel.includes('integrated') || lowerLabel.includes('webcam')) {
            detectedFront = true;
          }

          setIsMirrored(detectedFront);
          setActiveLabel(
            rawLabel
              ? rawLabel.slice(0, 32)
              : detectedFront
              ? 'Front Camera'
              : 'Back Camera'
          );

          if (settings.deviceId && postDevices.some((d) => d.deviceId === settings.deviceId)) {
            setSelectedDeviceId(settings.deviceId);
          }

          const videoEl = videoRef.current;
          if (videoEl) {
            videoEl.setAttribute('playsinline', 'true');
            videoEl.setAttribute('autoplay', 'true');
            videoEl.muted = true;
            videoEl.srcObject = acquiredStream;

            const finalizePlayback = () => {
              if (cancelled) return;
              if (videoEl.videoWidth > 0 && videoEl.videoHeight > 0) {
                setResolutionText(`${videoEl.videoWidth}×${videoEl.videoHeight}`);
              }
              setCameraActive(true);
              setCameraLoading(false);
            };

            videoEl.onloadedmetadata = () => {
              videoEl
                .play()
                .then(finalizePlayback)
                .catch(finalizePlayback);
            };

            videoEl
              .play()
              .then(finalizePlayback)
              .catch(() => {});
          } else {
            setCameraActive(true);
            setCameraLoading(false);
          }
        }

        startCameraHardware();

        return () => {
          cancelled = true;
          stopActiveStream();
        };
      }, [facingMode, selectedDeviceId, enabled, retryNonce, stopActiveStream, refreshVideoDevices, videoRef]);

      const selectFrontCamera = () => {
        setSelectedDeviceId('');
        setFacingMode('user');
      };

      const selectBackCamera = () => {
        setSelectedDeviceId('');
        setFacingMode('environment');
      };

      const cycleNextCamera = () => {
        if (devices.length > 1) {
          const idx = devices.findIndex((d) => d.deviceId === selectedDeviceId);
          const next = devices[(idx + 1) % devices.length];
          setSelectedDeviceId(next.deviceId);
        } else {
          setSelectedDeviceId('');
          setFacingMode((prev) => (prev === 'user' ? 'environment' : 'user'));
        }
      };

      const toggleFitMode = () => {
        setFitMode((prev) => (prev === 'cover' ? 'contain' : 'cover'));
      };

      const retryCamera = () => {
        setRetryNonce((n) => n + 1);
      };

      return {
        facingMode,
        devices,
        cameraActive,
        cameraLoading,
        cameraError,
        activeLabel,
        resolutionText,
        isMirrored,
        fitMode,
        toggleFitMode,
        selectFrontCamera,
        selectBackCamera,
        cycleNextCamera,
        retryCamera
      };
    }

    function CameraControlOverlay({
      facingMode,
      devices,
      cameraActive,
      cameraLoading,
      cameraError,
      activeLabel,
      resolutionText,
      fitMode,
      toggleFitMode,
      selectFrontCamera,
      selectBackCamera,
      cycleNextCamera,
      retryCamera
    }) {
      return (
        <>
          {cameraLoading && !cameraError && (
            <div className="absolute inset-0 bg-slate-950/85 flex flex-col items-center justify-center gap-2 z-20 pointer-events-none">
              <RefreshCw className="w-6 h-6 text-indigo-400 animate-spin" />
              <span className="text-[11px] font-semibold text-slate-200">Initializing Camera Lens...</span>
            </div>
          )}

          {cameraError && (
            <div className="absolute inset-0 bg-slate-950/95 p-4 flex flex-col items-center justify-center text-center gap-2.5 z-20">
              <AlertCircle className="w-6 h-6 text-amber-400" />
              <p className="text-slate-200 text-[11px] max-w-xs leading-relaxed">{cameraError}</p>
              <button
                type="button"
                onClick={retryCamera}
                className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-[11px] font-bold flex items-center gap-1.5 cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Retry Camera
              </button>
            </div>
          )}

          {cameraActive && (
            <div className="absolute top-2.5 right-2.5 px-2.5 py-1 bg-slate-950/85 border border-slate-800 rounded-lg text-[10px] font-mono text-emerald-300 flex items-center gap-1.5 z-10">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>{resolutionText ? `${resolutionText} • ` : ''}{activeLabel}</span>
            </div>
          )}

          <div className="absolute bottom-2.5 right-2.5 flex flex-wrap items-center justify-end gap-1.5 z-20">
            <button
              type="button"
              onClick={toggleFitMode}
              className="px-2 py-1.5 bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-slate-200 rounded-xl text-[10px] font-bold cursor-pointer"
              title="Toggle Fit / Fill aspect ratio"
            >
              {fitMode === 'cover' ? 'Fit' : 'Fill'}
            </button>

            {devices.length > 1 && (
              <button
                type="button"
                onClick={cycleNextCamera}
                className="px-2.5 py-1.5 bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-cyan-300 rounded-xl text-[10px] font-bold flex items-center gap-1 cursor-pointer"
                title="Switch among detected cameras"
              >
                <SwitchCamera className="w-3 h-3" /> Switch ({devices.length})
              </button>
            )}

            <button
              type="button"
              onClick={selectFrontCamera}
              className={`px-2.5 py-1.5 border rounded-xl text-[10px] font-bold cursor-pointer ${
                facingMode === 'user'
                  ? 'bg-indigo-600 border-indigo-400 text-white shadow'
                  : 'bg-slate-900/90 border-slate-700 text-slate-300 hover:text-white'
              }`}
            >
              Front Cam
            </button>
            <button
              type="button"
              onClick={selectBackCamera}
              className={`px-2.5 py-1.5 border rounded-xl text-[10px] font-bold cursor-pointer ${
                facingMode === 'environment'
                  ? 'bg-indigo-600 border-indigo-400 text-white shadow'
                  : 'bg-slate-900/90 border-slate-700 text-slate-300 hover:text-white'
              }`}
            >
              Back Cam
            </button>
          </div>
        </>
      );
    }

    // =========================================================================
    // 3. FACIAL BIOMETRIC VECTOR & BACKGROUND PHOTO COMPARISON ENGINE
    // =========================================================================
    function computeImageBiometricVector(sourceEl) {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = 24;
        canvas.height = 24;
        const ctx = canvas.getContext('2d');

        const sw = sourceEl.videoWidth || sourceEl.naturalWidth || sourceEl.width || 240;
        const sh = sourceEl.videoHeight || sourceEl.naturalHeight || sourceEl.height || 240;
        const cropW = sw * 0.65;
        const cropH = sh * 0.65;
        const sx = (sw - cropW) / 2;
        const sy = (sh - cropH) / 2;

        ctx.drawImage(sourceEl, sx, sy, cropW, cropH, 0, 0, 24, 24);
        const data = ctx.getImageData(0, 0, 24, 24).data;

        const raw = [];
        let sum = 0;
        for (let i = 0; i < data.length; i += 4) {
          const lum = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
          raw.push(lum);
          sum += lum;
        }

        const mean = sum / raw.length;
        let sqSum = 0;
        for (let i = 0; i < raw.length; i++) {
          const diff = raw[i] - mean;
          sqSum += diff * diff;
        }
        const std = Math.sqrt(sqSum / raw.length) || 1;

        return raw.map((v) => (v - mean) / std);
      } catch (e) {
        return null;
      }
    }

    function computeFrameBrightnessAndContrast(videoEl) {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = 32;
        canvas.height = 32;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoEl, 0, 0, 32, 32);
        const data = ctx.getImageData(0, 0, 32, 32).data;
        let sum = 0, min = 255, max = 0;
        for (let i = 0; i < data.length; i += 4) {
          const lum = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
          sum += lum;
          if (lum < min) min = lum;
          if (lum > max) max = lum;
        }
        const avg = sum / (data.length / 4);
        return { avgLuminance: avg, contrastRange: max - min };
      } catch (e) {
        return { avgLuminance: 0, contrastRange: 0 };
      }
    }

    function computeCosineSimilarity(vecA, vecB) {
      if (!vecA || !vecB || vecA.length !== vecB.length) return null;
      let dot = 0, magA = 0, magB = 0;
      for (let i = 0; i < vecA.length; i++) {
        dot += vecA[i] * vecB[i];
        magA += vecA[i] * vecA[i];
        magB += vecB[i] * vecB[i];
      }
      if (magA === 0 || magB === 0) return null;
      const rawCos = dot / (Math.sqrt(magA) * Math.sqrt(magB));
      return Math.max(0, Math.min(1, (rawCos + 1) / 2));
    }

    // =========================================================================
    // 4. REAL SCANNABLE QR CODE COMPONENT (QRCodeJS + Deterministic Fallback)
    // =========================================================================
    function RealScannableQrCode({ value, size = 190, id = "qr-canvas-box" }) {
      const containerRef = useRef(null);

      useEffect(() => {
        if (!containerRef.current) return;
        containerRef.current.innerHTML = "";
        if (window.QRCode) {
          try {
            new window.QRCode(containerRef.current, {
              text: value,
              width: size,
              height: size,
              colorDark: "#000000",
              colorLight: "#ffffff",
              correctLevel: window.QRCode.CorrectLevel.H
            });
            return;
          } catch (e) {
            console.warn("QRCodeJS fallback triggered", e);
          }
        }
        const gridSize = 17;
        let hash = 2166136261;
        for (let i = 0; i < value.length; i++) {
          hash ^= value.charCodeAt(i);
          hash = Math.imul(hash, 16777619);
        }
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("width", size);
        svg.setAttribute("height", size);
        svg.setAttribute("viewBox", `0 0 ${gridSize} ${gridSize}`);
        const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        bg.setAttribute("width", gridSize);
        bg.setAttribute("height", gridSize);
        bg.setAttribute("fill", "#ffffff");
        svg.appendChild(bg);

        let seed = hash >>> 0;
        for (let r = 0; r < gridSize; r++) {
          for (let c = 0; c < gridSize; c++) {
            seed = (seed * 1664525 + 1013904223) >>> 0;
            if (((seed >>> 16) & 1) === 1) {
              const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
              rect.setAttribute("x", c);
              rect.setAttribute("y", r);
              rect.setAttribute("width", "1");
              rect.setAttribute("height", "1");
              rect.setAttribute("fill", "#000000");
              svg.appendChild(rect);
            }
          }
        }
        containerRef.current.appendChild(svg);
      }, [value, size]);

      return (
        <div
          id={id}
          ref={containerRef}
          className="inline-flex items-center justify-center bg-white p-4 rounded-2xl shadow-inner"
        />
      );
    }

    // =========================================================================
    // 5. SYNCHRONIZED 30-SECOND ROLLING DYNAMIC QR ENGINE
    // =========================================================================
    function computeRollingQrForEpoch(epoch30, manualOffset = 0) {
      const validUntil = (epoch30 + 1) * 30000;
      const seedInput = `MU-ICT-ROLLING-QR-${epoch30}-${manualOffset}`;

      let h1 = 2166136261;
      let h2 = 374761393;
      for (let i = 0; i < seedInput.length; i++) {
        const ch = seedInput.charCodeAt(i);
        h1 ^= ch;
        h1 = Math.imul(h1, 16777619);
        h2 ^= ch + i * 31;
        h2 = Math.imul(h2, 2246822519);
      }
      const numPart = String(100000 + ((h1 >>> 0) % 900000));
      const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
      let codePart = '';
      let s = h2 >>> 0;
      for (let i = 0; i < 4; i++) {
        s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
        codePart += alphabet[s % alphabet.length];
      }

      return {
        token: `MU-QR-${numPart}-${codePart}`,
        epoch30,
        manualOffset,
        createdAt: epoch30 * 30000,
        validUntil
      };
    }

    function computeDeterministicRollingQr(manualOffset = 0) {
      const nowMs = Date.now();
      const epoch30 = Math.floor(nowMs / 30000);
      return computeRollingQrForEpoch(epoch30, manualOffset);
    }

    // =========================================================================
    // 6. INITIAL DATA & USER ACCOUNTS
    // =========================================================================
    const INITIAL_USERS = [
      {
        id: '92500133046',
        name: 'M. Madhu Mohan Kumar',
        email: 'madhu.kumar9250@marwadi.edu',
        role: 'student',
        pass: 'Madhu@123',
        dept: 'ICT Sem 3 - Div A',
        roll: '92500133046',
        faceSignature: 'BIO-FACE-33046-9A8F',
        faceVector: null,
        isRealEnrolled: false,
        photo: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=200'
      },
      {
        id: '92500133047',
        name: 'M. Govardhan Reddy',
        email: 'govardhan.reddy@marwadi.edu',
        role: 'student',
        pass: 'Govardhan@123',
        dept: 'ICT Sem 3 - Div A',
        roll: '92500133047',
        faceSignature: 'BIO-FACE-33047-4C2E',
        faceVector: null,
        isRealEnrolled: false,
        photo: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=200'
      },
      {
        id: '92500133026',
        name: 'M. Shivanag',
        email: 'shivanag.m@marwadi.edu',
        role: 'student',
        pass: 'Shivanag@123',
        dept: 'ICT Sem 3 - Div B',
        roll: '92500133026',
        faceSignature: 'BIO-FACE-33026-7D1B',
        faceVector: null,
        isRealEnrolled: false,
        photo: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=200'
      },
      {
        id: '92500133034',
        name: 'K. Preetham',
        email: 'preetham.k@marwadi.edu',
        role: 'student',
        pass: 'Preetham@123',
        dept: 'ICT Sem 3 - Div B',
        roll: '92500133034',
        faceSignature: 'BIO-FACE-33034-2E9D',
        faceVector: null,
        isRealEnrolled: false,
        photo: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&q=80&w=200'
      },
      // Faculty
      { id: 'FAC-102', name: 'Prof. R. K. Sharma', email: 'prof.sharma@marwadi.edu', role: 'faculty', pass: 'Sharma@123', dept: 'Python Programming', subject: 'PWP', photo: null },
      { id: 'FAC01', name: 'Prof. Kawal Kaur', email: 'pwp@marwadi.edu', role: 'faculty', pass: 'Kawal@123', dept: 'Python Web Programming', subject: 'PWP', photo: null },
      { id: 'FAC02', name: 'Prof. Biswajit', email: 'dmgt@marwadi.edu', role: 'faculty', pass: 'Biswajit@123', dept: 'Discrete Math & Graph Theory', subject: 'DMGT', photo: null },
      { id: 'FAC03', name: 'Prof. Vijay Dubey', email: 'coa@marwadi.edu', role: 'faculty', pass: 'Vijay@123', dept: 'Computer Architecture', subject: 'COA', photo: null },
      { id: 'FAC04', name: 'Prof. Alam', email: 'dsc@marwadi.edu', role: 'faculty', pass: 'Alam@123', dept: 'Data Structures in C', subject: 'DSC', photo: null },
      // Admin
      { id: 'ADMIN-01', name: 'Class Coordinator (HOD)', email: 'admin.ict@marwadi.edu', role: 'admin', pass: 'Admin@123', dept: 'ICT Department Head', roll: 'ADMIN-01', photo: null }
    ];

    const INITIAL_RESULTS = {
      '92500133046': { sgpa: { 'Sem 1': 8.4, 'Sem 2': 8.6, 'Sem 3': 8.9 }, cgpa: 8.63, backlogs: 0, subjects: { PWP: 'AA', DMGT: 'AB', COA: 'AA', DSC: 'BB' } },
      '92500133047': { sgpa: { 'Sem 1': 7.8, 'Sem 2': 8.2, 'Sem 3': 8.0 }, cgpa: 8.00, backlogs: 0, subjects: { PWP: 'AB', DMGT: 'BB', COA: 'AA', DSC: 'AB' } },
      '92500133026': { sgpa: { 'Sem 1': 6.5, 'Sem 2': 6.8, 'Sem 3': 6.2 }, cgpa: 6.50, backlogs: 1, subjects: { PWP: 'BC', DMGT: 'FF', COA: 'CC', DSC: 'BC' } },
      '92500133034': { sgpa: { 'Sem 1': 9.0, 'Sem 2': 9.2, 'Sem 3': 9.4 }, cgpa: 9.20, backlogs: 0, subjects: { PWP: 'AA', DMGT: 'AA', COA: 'AA', DSC: 'AA' } }
    };

    const INITIAL_ATTENDANCE = {
      '92500133046': { PWP: { present: 28, total: 30 }, DMGT: { present: 25, total: 28 }, COA: { present: 26, total: 26 }, DSC: { present: 24, total: 27 } },
      '92500133047': { PWP: { present: 26, total: 30 }, DMGT: { present: 24, total: 28 }, COA: { present: 22, total: 26 }, DSC: { present: 25, total: 27 } },
      '92500133026': { PWP: { present: 18, total: 30 }, DMGT: { present: 15, total: 28 }, COA: { present: 14, total: 26 }, DSC: { present: 16, total: 27 } },
      '92500133034': { PWP: { present: 30, total: 30 }, DMGT: { present: 28, total: 28 }, COA: { present: 25, total: 26 }, DSC: { present: 27, total: 27 } }
    };

    const INITIAL_CAMPUS_UPDATES = [
      {
        id: 'UPD-101',
        category: 'Assignment',
        subject: 'PWP',
        title: 'Django REST API & JWT Auth Lab Assignment',
        date: '2026-11-24',
        details: 'Build a complete CRUD endpoint with token verification and upload your GitHub repository link.',
        postedBy: 'Prof. R. K. Sharma'
      },
      {
        id: 'UPD-102',
        category: 'Holiday',
        subject: 'ALL',
        title: 'Guru Nanak Jayanti University Holiday',
        date: '2026-11-20',
        details: 'All ICT lectures and laboratory sessions remain suspended on account of Guru Nanak Jayanti.',
        postedBy: 'Prof. R. K. Sharma'
      },
      {
        id: 'UPD-103',
        category: 'Event',
        subject: 'ICT Dept',
        title: 'MU-HACK 2026 Smart Campus Hackathon',
        date: '2026-11-28',
        details: '24-hour coding sprint in Main Auditorium. All registered participants receive automatic On-Duty attendance.',
        postedBy: 'Prof. Kawal Kaur'
      }
    ];

    // =========================================================================
    // 7. REAL-TIME PYTHON SERVER + LOCALSTORAGE + BROADCAST SYNC HOOK
    // =========================================================================
    function usePersistentState(key, defaultValue) {
      const [state, setState] = useState(() => {
        try {
          const saved = localStorage.getItem(key);
          return saved !== null ? JSON.parse(saved) : defaultValue;
        } catch (e) {
          return defaultValue;
        }
      });

      const isExternalSyncRef = useRef(false);
      const lastSerializedRef = useRef(JSON.stringify(state));

      const pushToPythonServer = useCallback((val) => {
        try {
          const serialized = JSON.stringify(val);
          if (serialized === lastSerializedRef.current) return;
          lastSerializedRef.current = serialized;
          fetch('/api/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key, value: val })
          }).catch(() => {});
        } catch (e) {}
      }, [key]);

      useEffect(() => {
        if (isExternalSyncRef.current) {
          isExternalSyncRef.current = false;
          return;
        }
        try {
          const serialized = JSON.stringify(state);
          localStorage.setItem(key, serialized);
          if (typeof BroadcastChannel !== 'undefined') {
            const bc = new BroadcastChannel('mu_ict_realtime_sync');
            bc.postMessage({ key, value: state });
            bc.close();
          }
          pushToPythonServer(state);
        } catch (e) {
          console.warn('Storage sync warning:', e);
        }
      }, [key, state, pushToPythonServer]);

      useEffect(() => {
        let active = true;

        const pullFromServer = () => {
          fetch(`/api/sync?key=${encodeURIComponent(key)}&t=${Date.now()}`)
            .then((res) => (res.ok ? res.json() : null))
            .then((data) => {
              if (!active || !data) return;
              if (data.found) {
                const incomingStr = JSON.stringify(data.value);
                if (incomingStr !== lastSerializedRef.current) {
                  lastSerializedRef.current = incomingStr;
                  try {
                    localStorage.setItem(key, incomingStr);
                  } catch (e) {}
                  isExternalSyncRef.current = true;
                  setState(data.value);
                }
              } else {
                // Seed Python server with initial value if key not yet stored
                fetch('/api/sync', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ key, value: JSON.parse(lastSerializedRef.current) })
                }).catch(() => {});
              }
            })
            .catch(() => {});
        };

        pullFromServer();
        const pollTimer = setInterval(pullFromServer, 800);

        const handleStorage = (e) => {
          if (e.key === key && e.newValue !== null && e.newValue !== lastSerializedRef.current) {
            try {
              lastSerializedRef.current = e.newValue;
              isExternalSyncRef.current = true;
              setState(JSON.parse(e.newValue));
            } catch (err) {}
          }
        };

        let bc = null;
        if (typeof BroadcastChannel !== 'undefined') {
          bc = new BroadcastChannel('mu_ict_realtime_sync');
          bc.onmessage = (event) => {
            if (event.data && event.data.key === key) {
              const incomingStr = JSON.stringify(event.data.value);
              if (incomingStr !== lastSerializedRef.current) {
                lastSerializedRef.current = incomingStr;
                isExternalSyncRef.current = true;
                setState(event.data.value);
              }
            }
          };
        }

        window.addEventListener('storage', handleStorage);
        return () => {
          active = false;
          clearInterval(pollTimer);
          window.removeEventListener('storage', handleStorage);
          if (bc) bc.close();
        };
      }, [key]);

      return [state, setState];
    }

    // =========================================================================
    // 8. MAIN ROOT APPLICATION
    // =========================================================================
    function App() {
      const [users, setUsers] = usePersistentState('mu_ict_users_v6', INITIAL_USERS);
      const [currentUser, setCurrentUser] = useState(null);
      const [activeRoleTab, setActiveRoleTab] = useState('student');
      const [results, setResults] = usePersistentState('mu_ict_results_v6', INITIAL_RESULTS);
      const [attendance, setAttendance] = usePersistentState('mu_ict_attendance_v6', INITIAL_ATTENDANCE);
      const [mismatchLogs, setMismatchLogs] = usePersistentState('mu_ict_logs_v6', []);
      const [biometricThreshold, setBiometricThreshold] = usePersistentState('mu_ict_threshold_v6', 75);

      const [manualQrOffset, setManualQrOffset] = usePersistentState('mu_ict_qr_manual_offset_v6', 0);
      const [activeQrSession, setActiveQrSession] = useState(() => computeDeterministicRollingQr(0));
      const [usedQrTokensByStudent, setUsedQrTokensByStudent] = usePersistentState('mu_ict_used_qr_by_student_v6', {});
      const [qrCountdown, setQrCountdown] = useState(() => 30 - (Math.floor(Date.now() / 1000) % 30));

      const [studentSessionMarks, setStudentSessionMarks] = usePersistentState('mu_ict_session_marks_v6', {});
      const [campusUpdates, setCampusUpdates] = usePersistentState('mu_ict_updates_v6', INITIAL_CAMPUS_UPDATES);
      const [livePoll, setLivePoll] = usePersistentState('mu_ict_poll_v6', null);
      const [classSessionRecords, setClassSessionRecords] = usePersistentState('mu_ict_session_records_v6', [
        {
          id: 'SES-INIT-101',
          facultyName: 'Prof. R. K. Sharma',
          subject: 'PWP',
          date: '19 Nov 2026',
          startTime: '10:00 AM',
          endTime: '10:50 AM',
          totalStudents: 4,
          presentCount: 3,
          qrScannedCount: 3,
          absentCount: 1,
          students: [
            { id: '92500133046', roll: '92500133046', name: 'M. Madhu Mohan Kumar', status: 'Present', source: 'Optical QR (PWP)', time: '10:02 AM' },
            { id: '92500133047', roll: '92500133047', name: 'M. Govardhan Reddy', status: 'Present', source: 'Optical QR (PWP)', time: '10:04 AM' },
            { id: '92500133026', roll: '92500133026', name: 'M. Shivanag', status: 'Absent', source: 'Unscanned / Absent', time: '-' },
            { id: '92500133034', roll: '92500133034', name: 'K. Preetham', status: 'Present', source: 'Optical QR (PWP)', time: '10:05 AM' }
          ]
        }
      ]);
      const [liveSessionStartTime, setLiveSessionStartTime] = usePersistentState('mu_ict_live_session_start_v6', () =>
        new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      );
      const [isSessionLive, setIsSessionLive] = usePersistentState('mu_ict_is_session_live_v6', false);
      const [liveSessionDate, setLiveSessionDate] = usePersistentState('mu_ict_live_session_date_v6', () =>
        new Date().toISOString().split('T')[0]
      );
      const [liveSessionSubject, setLiveSessionSubject] = usePersistentState('mu_ict_live_session_subject_v6', 'PWP');

      const rotateQrTokenNow = () => {
        const nextOffset = manualQrOffset + 1;
        setManualQrOffset(nextOffset);
        setActiveQrSession(computeDeterministicRollingQr(nextOffset));
      };

      useEffect(() => {
        const updateRollingState = () => {
          const nowMs = Date.now();
          const secInWindow = Math.floor(nowMs / 1000) % 30;
          const remaining = 30 - secInWindow;
          setQrCountdown(remaining);
          const fresh = computeDeterministicRollingQr(manualQrOffset);
          setActiveQrSession((prev) => (prev.token === fresh.token ? prev : fresh));
        };
        updateRollingState();
        const timer = setInterval(updateRollingState, 500);
        return () => clearInterval(timer);
      }, [manualQrOffset]);

      const handleResetAllDemoData = () => {
        setUsers(INITIAL_USERS);
        setResults(INITIAL_RESULTS);
        setAttendance(INITIAL_ATTENDANCE);
        setMismatchLogs([]);
        setStudentSessionMarks({});
        setUsedQrTokensByStudent({});
        setCampusUpdates(INITIAL_CAMPUS_UPDATES);
        setBiometricThreshold(75);
        setLivePoll(null);
        setManualQrOffset(0);
        setActiveQrSession(computeDeterministicRollingQr(0));
        setClassSessionRecords([]);
        setIsSessionLive(false);
        setLiveSessionStartTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
      };

      return (
        <div className="min-h-screen bg-[#090d16] text-slate-100 font-sans antialiased flex flex-col">
          {!currentUser ? (
            <SystemAccessPortal
              users={users}
              activeRoleTab={activeRoleTab}
              setActiveRoleTab={setActiveRoleTab}
              onLogin={(user) => setCurrentUser(user)}
            />
          ) : (
            <PortalDashboard
              user={currentUser}
              onLogout={() => setCurrentUser(null)}
              users={users}
              setUsers={setUsers}
              attendance={attendance}
              setAttendance={setAttendance}
              results={results}
              setResults={setResults}
              activeQrSession={activeQrSession}
              qrCountdown={qrCountdown}
              rotateQrTokenNow={rotateQrTokenNow}
              usedQrTokensByStudent={usedQrTokensByStudent}
              setUsedQrTokensByStudent={setUsedQrTokensByStudent}
              mismatchLogs={mismatchLogs}
              setMismatchLogs={setMismatchLogs}
              studentSessionMarks={studentSessionMarks}
              setStudentSessionMarks={setStudentSessionMarks}
              classSessionRecords={classSessionRecords}
              setClassSessionRecords={setClassSessionRecords}
              isSessionLive={isSessionLive}
              setIsSessionLive={setIsSessionLive}
              liveSessionDate={liveSessionDate}
              setLiveSessionDate={setLiveSessionDate}
              liveSessionSubject={liveSessionSubject}
              setLiveSessionSubject={setLiveSessionSubject}
              liveSessionStartTime={liveSessionStartTime}
              setLiveSessionStartTime={setLiveSessionStartTime}
              campusUpdates={campusUpdates}
              setCampusUpdates={setCampusUpdates}
              biometricThreshold={biometricThreshold}
              setBiometricThreshold={setBiometricThreshold}
              livePoll={livePoll}
              setLivePoll={setLivePoll}
              onResetDemoData={handleResetAllDemoData}
            />
          )}
        </div>
      );
    }

    // =========================================================================
    // 9. SYSTEM ACCESS PORTAL (LOGIN SCREEN)
    // =========================================================================
    function SystemAccessPortal({ users, activeRoleTab, setActiveRoleTab, onLogin }) {
      const [idInput, setIdInput] = useState('92500133046');
      const [passInput, setPassInput] = useState('Madhu@123');
      const [showPass, setShowPass] = useState(false);
      const [error, setError] = useState('');
      const [forgotModal, setForgotModal] = useState(false);
      const [otpSent, setOtpSent] = useState(false);
      const [forgotId, setForgotId] = useState('');
      const [forgotEmail, setForgotEmail] = useState('');

      const handleRoleSelect = (role) => {
        setActiveRoleTab(role);
        setError('');
        if (role === 'student') {
          const firstStudent = users.find((u) => u.role === 'student');
          setIdInput(firstStudent?.roll || '92500133046');
          setPassInput(firstStudent?.pass || 'Madhu@123');
        } else if (role === 'faculty') {
          const firstFaculty = users.find((u) => u.role === 'faculty');
          setIdInput(firstFaculty?.id || 'FAC-102');
          setPassInput(firstFaculty?.pass || 'Sharma@123');
        } else {
          const firstAdmin = users.find((u) => u.role === 'admin');
          setIdInput(firstAdmin?.id || 'ADMIN-01');
          setPassInput(firstAdmin?.pass || 'Admin@123');
        }
      };

      const handleSubmit = (e) => {
        e.preventDefault();
        const found = users.find(
          (u) =>
            (u.id.toLowerCase() === idInput.toLowerCase() ||
              u.email.toLowerCase() === idInput.toLowerCase() ||
              (u.roll && u.roll.toLowerCase() === idInput.toLowerCase())) &&
            u.pass === passInput
        );

        if (found) {
          if (found.role !== activeRoleTab) {
            setError(`This user is registered as a ${found.role.toUpperCase()}. Please select the ${found.role.toUpperCase()} tab.`);
            return;
          }
          onLogin(found);
        } else {
          setError('Invalid ID / Enrollment Number or Password. Please try again.');
        }
      };

      return (
        <div className="flex-1 flex flex-col items-center justify-center p-4 bg-[#090d16] relative">
          <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-1/4 right-1/3 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

          <div className="mb-6 text-center z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-950/80 border border-indigo-800/60 rounded-full text-[11px] font-semibold text-indigo-300 mb-3">
              <Zap className="w-3.5 h-3.5 text-indigo-400" /> Marwadi University ICT Department
            </div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight sm:text-3xl">
              Smart Curriculum Activity and Attendance App
            </h1>
            <p className="text-xs text-slate-400 mt-1">Unified Multi-Factor Biometric & Activity Management System</p>
          </div>

          <div className="w-full max-w-md bg-[#0f1523] border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl z-10 relative">
            <div>
              <h2 className="text-lg font-bold text-white">System Access Portal</h2>
              <p className="text-xs text-slate-400">Select account type or use one-click access presets</p>
            </div>

            <div className="grid grid-cols-3 gap-1 bg-[#070a12] p-1.5 rounded-2xl border border-slate-800/80 text-xs font-semibold">
              <button
                type="button"
                onClick={() => handleRoleSelect('student')}
                className={`py-2.5 rounded-xl flex items-center justify-center gap-2 transition cursor-pointer ${
                  activeRoleTab === 'student' ? 'bg-[#5852f2] text-white shadow-lg shadow-indigo-500/30 font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <GraduationCap className="w-4 h-4" />
                <span>Student</span>
              </button>
              <button
                type="button"
                onClick={() => handleRoleSelect('faculty')}
                className={`py-2.5 rounded-xl flex items-center justify-center gap-2 transition cursor-pointer ${
                  activeRoleTab === 'faculty' ? 'bg-[#5852f2] text-white shadow-lg shadow-indigo-500/30 font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Users className="w-4 h-4" />
                <span>Faculty</span>
              </button>
              <button
                type="button"
                onClick={() => handleRoleSelect('admin')}
                className={`py-2.5 rounded-xl flex items-center justify-center gap-2 transition cursor-pointer ${
                  activeRoleTab === 'admin' ? 'bg-[#5852f2] text-white shadow-lg shadow-indigo-500/30 font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Shield className="w-4 h-4" />
                <span>Admin</span>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">
                  {activeRoleTab === 'student' ? 'Enrollment Number / University Email' : activeRoleTab === 'faculty' ? 'Faculty Staff ID / Email' : 'Admin Access ID'}
                </label>
                <div className="relative flex items-center">
                  <User className="w-4 h-4 text-slate-500 absolute left-3.5" />
                  <input
                    type="text"
                    required
                    value={idInput}
                    onChange={(e) => setIdInput(e.target.value)}
                    placeholder="Enter Enrollment No or ID..."
                    className="w-full pl-10 pr-4 py-3 bg-[#070a12] border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500 font-mono transition"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-slate-300">Password</label>
                  <button
                    type="button"
                    onClick={() => setForgotModal(true)}
                    className="text-indigo-400 hover:text-indigo-300 font-medium cursor-pointer"
                  >
                    Forgot password?
                  </button>
                </div>
                <div className="relative flex items-center">
                  <Lock className="w-4 h-4 text-slate-500 absolute left-3.5" />
                  <input
                    type={showPass ? 'text' : 'password'}
                    required
                    value={passInput}
                    onChange={(e) => setPassInput(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-10 py-3 bg-[#070a12] border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-indigo-500 font-mono transition"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass(!showPass)}
                    className="absolute right-3.5 text-slate-500 hover:text-slate-300 cursor-pointer"
                  >
                    {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {error && (
                <div className="p-3 rounded-xl bg-red-950/60 border border-red-800/80 text-xs text-red-300 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
                  <span>{error}</span>
                </div>
              )}

              <button
                type="submit"
                className="w-full py-3.5 bg-[#5852f2] hover:bg-indigo-600 text-white font-bold rounded-xl text-sm shadow-xl shadow-indigo-600/30 transition cursor-pointer"
              >
                Sign In to {activeRoleTab.charAt(0).toUpperCase() + activeRoleTab.slice(1)} Portal
              </button>
            </form>

            <div className="pt-4 border-t border-slate-800/80 space-y-2.5">
              <div className="text-[11px] font-semibold text-slate-500 text-center uppercase tracking-wider">
                Quick Demo Access Presets
              </div>
              <div className="grid grid-cols-1 gap-1.5 max-h-40 overflow-y-auto pr-1">
                {users
                  .filter((u) => u.role === activeRoleTab)
                  .map((preset) => (
                    <button
                      key={preset.id}
                      type="button"
                      onClick={() => {
                        setIdInput(preset.roll || preset.id);
                        setPassInput(preset.pass);
                        onLogin(preset);
                      }}
                      className="flex items-center justify-between px-3 py-2 bg-[#070a12] hover:bg-slate-800/90 border border-slate-800/80 rounded-xl text-left text-xs transition cursor-pointer group"
                    >
                      <span className="font-semibold text-slate-200 group-hover:text-white truncate">{preset.name}</span>
                      <span className="text-[10px] font-mono text-indigo-400 shrink-0 ml-2">{preset.roll || preset.id}</span>
                    </button>
                  ))}
              </div>
            </div>
          </div>

          {forgotModal && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
              <div className="bg-[#0f1523] border border-slate-800 rounded-3xl p-6 max-w-sm w-full space-y-4">
                <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                  <h3 className="text-sm font-bold text-white">University Account Recovery</h3>
                  <button
                    type="button"
                    onClick={() => {
                      setForgotModal(false);
                      setOtpSent(false);
                    }}
                    className="text-slate-400 hover:text-white font-bold cursor-pointer"
                  >
                    ✕
                  </button>
                </div>

                {!otpSent ? (
                  <div className="space-y-3 text-xs">
                    <p className="text-slate-400">Enter your Enrollment Number / Staff ID and University Email to receive a temporary OTP.</p>
                    <input
                      type="text"
                      placeholder="Enrollment / Staff ID"
                      value={forgotId}
                      onChange={(e) => setForgotId(e.target.value)}
                      className="w-full p-2.5 bg-[#070a12] border border-slate-800 rounded-xl text-white font-mono"
                    />
                    <input
                      type="email"
                      placeholder="University Email (@marwadi.edu)"
                      value={forgotEmail}
                      onChange={(e) => setForgotEmail(e.target.value)}
                      className="w-full p-2.5 bg-[#070a12] border border-slate-800 rounded-xl text-white"
                    />
                    <button
                      type="button"
                      onClick={() => setOtpSent(true)}
                      className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl cursor-pointer"
                    >
                      Send Verification OTP
                    </button>
                  </div>
                ) : (
                  <div className="space-y-3 text-xs text-center">
                    <div className="w-10 h-10 rounded-full bg-emerald-950 border border-emerald-800 text-emerald-400 flex items-center justify-center mx-auto">
                      <Check className="w-5 h-5" />
                    </div>
                    <p className="text-emerald-300 font-semibold">Password Reset Email Dispatched!</p>
                    <p className="text-slate-400 text-[11px]">
                      Temporary verification OTP: <strong className="text-white font-mono">849201</strong> sent to your email.
                    </p>
                    <button
                      type="button"
                      onClick={() => {
                        setForgotModal(false);
                        setOtpSent(false);
                      }}
                      className="w-full py-2.5 bg-indigo-600 text-white font-bold rounded-xl cursor-pointer"
                    >
                      Return to Login
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      );
    }

    // =========================================================================
    // 10. MAIN PORTAL DASHBOARD (AUTHENTICATED)
    // =========================================================================
    function PortalDashboard({
      user,
      onLogout,
      users,
      setUsers,
      attendance,
      setAttendance,
      results,
      setResults,
      activeQrSession,
      qrCountdown,
      rotateQrTokenNow,
      usedQrTokensByStudent,
      setUsedQrTokensByStudent,
      mismatchLogs,
      setMismatchLogs,
      studentSessionMarks,
      setStudentSessionMarks,
      classSessionRecords,
      setClassSessionRecords,
      isSessionLive,
      setIsSessionLive,
      liveSessionDate,
      setLiveSessionDate,
      liveSessionSubject,
      setLiveSessionSubject,
      liveSessionStartTime,
      setLiveSessionStartTime,
      campusUpdates,
      setCampusUpdates,
      biometricThreshold,
      setBiometricThreshold,
      livePoll,
      setLivePoll,
      onResetDemoData
    }) {
      const syncedUser = users.find((u) => u.id === user.id) || user;
      const [showUserPass, setShowUserPass] = useState(false);
      const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
      const [activeTab, setActiveTab] = useState(
        syncedUser.role === 'admin' ? 'directory' : syncedUser.role === 'faculty' ? 'live' : 'student-dashboard'
      );

      const [camEnrollModal, setCamEnrollModal] = useState(false);
      const [targetStudentForReset, setTargetStudentForReset] = useState(null);

      const handleSelectTab = (tab) => {
        setActiveTab(tab);
        setMobileMenuOpen(false);
      };

      const renderNavLinks = () => (
        <>
          {syncedUser.role === 'admin' && (
            <>
              <SidebarItem icon={BarChart2} label="System Analytics" active={activeTab === 'analytics'} onClick={() => handleSelectTab('analytics')} />
              <SidebarItem icon={Users} label="User Directory & Keys" active={activeTab === 'directory'} onClick={() => handleSelectTab('directory')} />
              <SidebarItem icon={AlertTriangle} label="Defaulter Alerts (<75%)" active={activeTab === 'defaulters'} onClick={() => handleSelectTab('defaulters')} />
              <SidebarItem icon={BookOpen} label="Master Curriculum" active={activeTab === 'curriculum'} onClick={() => handleSelectTab('curriculum')} />
              <SidebarItem icon={FileText} label="Activity Logs" active={activeTab === 'logs'} onClick={() => handleSelectTab('logs')} />
              <SidebarItem icon={MapPin} label="Classroom Allocator" active={activeTab === 'allocator'} onClick={() => handleSelectTab('allocator')} />
              <SidebarItem icon={Sliders} label="Biometric Sensitivity" active={activeTab === 'sensitivity'} onClick={() => handleSelectTab('sensitivity')} />
            </>
          )}

          {syncedUser.role === 'faculty' && (
            <>
              <SidebarItem icon={Video} label="Live Attendance Engine" active={activeTab === 'live'} onClick={() => handleSelectTab('live')} />
              <SidebarItem icon={Clock} label="Recorded Sessions & Student List" active={activeTab === 'recorded-sessions'} onClick={() => handleSelectTab('recorded-sessions')} />
              <SidebarItem icon={Calendar} label="Assignments, Holidays & Events" active={activeTab === 'updates'} onClick={() => handleSelectTab('updates')} />
              <SidebarItem icon={Award} label="Grade & Result Entry" active={activeTab === 'grades'} onClick={() => handleSelectTab('grades')} />
              <SidebarItem icon={HelpCircle} label="Live Quiz & Polls" active={activeTab === 'polls'} onClick={() => handleSelectTab('polls')} />
              <SidebarItem icon={FileCheck} label="Assignment Plagiarism" active={activeTab === 'plagiarism'} onClick={() => handleSelectTab('plagiarism')} />
              <SidebarItem icon={Bell} label="Low Attendance Alerts" active={activeTab === 'faculty-alerts'} onClick={() => handleSelectTab('faculty-alerts')} />
            </>
          )}

          {syncedUser.role === 'student' && (
            <>
              <SidebarItem icon={Gauge} label="Student Dashboard" active={activeTab === 'student-dashboard'} onClick={() => handleSelectTab('student-dashboard')} />
              <SidebarItem icon={QrCode} label="Scan Faculty QR" active={activeTab === 'scan'} onClick={() => handleSelectTab('scan')} />
              <SidebarItem icon={Calendar} label="Timetable & Schedule" active={activeTab === 'timetable'} onClick={() => handleSelectTab('timetable')} />
              <SidebarItem icon={FileCode2} label="Assignments Hub" active={activeTab === 'assignments'} onClick={() => handleSelectTab('assignments')} />
              <SidebarItem icon={GraduationCap} label="Results & Transcript" active={activeTab === 'results'} onClick={() => handleSelectTab('results')} />
              <SidebarItem icon={BookOpen} label="Curriculum Progress" active={activeTab === 'curriculum-progress'} onClick={() => handleSelectTab('curriculum-progress')} />
              <SidebarItem icon={CalendarCheck} label="Holidays & Events" active={activeTab === 'holidays-events'} onClick={() => handleSelectTab('holidays-events')} />
            </>
          )}
        </>
      );

      return (
        <div className="flex-1 flex flex-col overflow-hidden bg-[#090d16]">
          <header className="h-14 border-b border-slate-800 bg-[#0c101c] flex items-center justify-between px-4 sm:px-6 shrink-0 z-20">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white cursor-pointer"
                aria-label="Toggle Menu"
              >
                {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
              </button>
              <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-white text-xs shadow-lg shadow-indigo-600/30">
                MU
              </div>
              <div>
                <h1 className="text-xs sm:text-sm font-bold text-white tracking-wide">Marwadi University ICT</h1>
                <p className="text-[10px] text-emerald-400 flex items-center gap-1 font-semibold">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Smart Attendance & Activity System
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 sm:gap-3">
              <div className="hidden sm:flex items-center gap-3 bg-[#070a12] border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
                <div className="w-7 h-7 rounded-full bg-indigo-600/30 text-indigo-300 flex items-center justify-center font-bold overflow-hidden border border-indigo-500/40">
                  {syncedUser.photo ? (
                    <img src={syncedUser.photo} alt={syncedUser.name} className="w-full h-full object-cover" />
                  ) : (
                    syncedUser.name.charAt(0)
                  )}
                </div>
                <div className="text-left">
                  <div className="font-bold text-slate-200 text-[11px]">{syncedUser.name}</div>
                  <div className="text-[10px] text-slate-400 font-mono flex items-center gap-1.5">
                    <span className="text-slate-500">{syncedUser.role.toUpperCase()}</span> |
                    <span>
                      Pass: <strong className="text-cyan-300">{showUserPass ? syncedUser.pass : '••••••••'}</strong>
                    </span>
                    <button
                      type="button"
                      onClick={() => setShowUserPass(!showUserPass)}
                      className="text-slate-400 hover:text-cyan-400 transition cursor-pointer"
                    >
                      {showUserPass ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                    </button>
                  </div>
                </div>
              </div>

              {syncedUser.role === 'admin' && (
                <button
                  type="button"
                  onClick={() => {
                    setTargetStudentForReset(null);
                    setCamEnrollModal(true);
                  }}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-indigo-600/20 transition cursor-pointer"
                >
                  <Camera className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Camera Enrollment</span>
                </button>
              )}

              <button
                type="button"
                onClick={onLogout}
                className="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 shadow-lg shadow-red-600/30 transition cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Logout</span>
              </button>
            </div>
          </header>

          {mobileMenuOpen && (
            <div className="md:hidden bg-[#0c101c] border-b border-slate-800 p-4 space-y-1 z-30">
              {renderNavLinks()}
            </div>
          )}

          <div className="flex-1 flex overflow-hidden">
            <aside className="hidden md:flex w-60 border-r border-slate-800 bg-[#0c101c] p-4 flex-col space-y-1 text-xs shrink-0">
              {renderNavLinks()}
            </aside>

            <main className="flex-1 p-4 sm:p-6 overflow-y-auto bg-[#090d16]">
              {syncedUser.role === 'admin' && activeTab === 'directory' && (
                <AdminUserDirectory
                  users={users}
                  setUsers={setUsers}
                  onResetFace={(student) => {
                    setTargetStudentForReset(student.id);
                    setCamEnrollModal(true);
                  }}
                  onResetDemoData={onResetDemoData}
                />
              )}
              {syncedUser.role === 'admin' && activeTab === 'analytics' && <AdminAnalytics users={users} attendance={attendance} mismatchLogs={mismatchLogs} />}
              {syncedUser.role === 'admin' && activeTab === 'defaulters' && <AdminDefaulters attendance={attendance} users={users} />}
              {syncedUser.role === 'admin' && activeTab === 'sensitivity' && (
                <AdminBiometricSensitivity biometricThreshold={biometricThreshold} setBiometricThreshold={setBiometricThreshold} />
              )}
              {syncedUser.role === 'admin' && activeTab === 'allocator' && <AdminClassroomAllocator users={users} />}
              {syncedUser.role === 'admin' && activeTab === 'curriculum' && <AdminMasterCurriculum />}
              {syncedUser.role === 'admin' && activeTab === 'logs' && <AdminActivityLogs mismatchLogs={mismatchLogs} />}

              {syncedUser.role === 'faculty' && activeTab === 'live' && (
                <FacultyLiveAttendance
                  facultyUser={syncedUser}
                  users={users}
                  setUsers={setUsers}
                  activeQrSession={activeQrSession}
                  qrCountdown={qrCountdown}
                  rotateQrTokenNow={rotateQrTokenNow}
                  attendance={attendance}
                  setAttendance={setAttendance}
                  mismatchLogs={mismatchLogs}
                  setMismatchLogs={setMismatchLogs}
                  studentSessionMarks={studentSessionMarks}
                  setStudentSessionMarks={setStudentSessionMarks}
                  classSessionRecords={classSessionRecords}
                  setClassSessionRecords={setClassSessionRecords}
                  isSessionLive={isSessionLive}
                  setIsSessionLive={setIsSessionLive}
                  liveSessionDate={liveSessionDate}
                  setLiveSessionDate={setLiveSessionDate}
                  liveSessionSubject={liveSessionSubject}
                  setLiveSessionSubject={setLiveSessionSubject}
                  liveSessionStartTime={liveSessionStartTime}
                  setLiveSessionStartTime={setLiveSessionStartTime}
                  biometricThreshold={biometricThreshold}
                  onOpenRecordedSessions={() => handleSelectTab('recorded-sessions')}
                />
              )}
              {syncedUser.role === 'faculty' && activeTab === 'recorded-sessions' && (
                <FacultyRecordedSessionsDashboard
                  facultyUser={syncedUser}
                  users={users}
                  attendance={attendance}
                  setAttendance={setAttendance}
                  classSessionRecords={classSessionRecords}
                  setClassSessionRecords={setClassSessionRecords}
                  onBackToLive={() => handleSelectTab('live')}
                />
              )}
              {syncedUser.role === 'faculty' && activeTab === 'updates' && (
                <FacultyUpdatesManager facultyUser={syncedUser} campusUpdates={campusUpdates} setCampusUpdates={setCampusUpdates} />
              )}
              {syncedUser.role === 'faculty' && activeTab === 'grades' && <FacultyGradeEntry users={users} results={results} setResults={setResults} />}
              {syncedUser.role === 'faculty' && activeTab === 'polls' && (
                <FacultyLiveQuizPoll livePoll={livePoll} setLivePoll={setLivePoll} />
              )}
              {syncedUser.role === 'faculty' && activeTab === 'plagiarism' && <FacultyPlagiarismCheck />}
              {syncedUser.role === 'faculty' && activeTab === 'faculty-alerts' && <FacultyMassAlerts attendance={attendance} users={users} />}

              {syncedUser.role === 'student' && activeTab === 'student-dashboard' && (
                <StudentDashboardOverview
                  studentUser={syncedUser}
                  attendance={attendance[syncedUser.id]}
                  results={results[syncedUser.id]}
                  campusUpdates={campusUpdates}
                  studentSessionMarks={studentSessionMarks}
                  livePoll={livePoll}
                  setLivePoll={setLivePoll}
                  onNavigate={(tab) => handleSelectTab(tab)}
                />
              )}
              {syncedUser.role === 'student' && activeTab === 'scan' && (
                <StudentQrScanner
                  studentUser={syncedUser}
                  users={users}
                  activeQrSession={activeQrSession}
                  usedQrTokensByStudent={usedQrTokensByStudent}
                  setUsedQrTokensByStudent={setUsedQrTokensByStudent}
                  setAttendance={setAttendance}
                  setMismatchLogs={setMismatchLogs}
                  setStudentSessionMarks={setStudentSessionMarks}
                />
              )}
              {syncedUser.role === 'student' && activeTab === 'timetable' && <StudentTimetableSchedule users={users} />}
              {syncedUser.role === 'student' && activeTab === 'assignments' && <StudentAssignmentsHub campusUpdates={campusUpdates} />}
              {syncedUser.role === 'student' && activeTab === 'results' && (
                <StudentResultsTranscript studentUser={syncedUser} results={results[syncedUser.id]} />
              )}
              {syncedUser.role === 'student' && activeTab === 'curriculum-progress' && <StudentCurriculumProgress users={users} />}
              {syncedUser.role === 'student' && activeTab === 'holidays-events' && <StudentHolidaysEvents campusUpdates={campusUpdates} />}
            </main>
          </div>

          {camEnrollModal && (
            <CameraEnrollmentModal
              users={users}
              setUsers={setUsers}
              targetStudentId={targetStudentForReset}
              lockStudentSelection={syncedUser.role === 'student'}
              onClose={() => {
                setCamEnrollModal(false);
                setTargetStudentForReset(null);
              }}
            />
          )}
        </div>
      );
    }

    // =========================================================================
    // 11. ADMIN BIOMETRIC ENROLLMENT MODAL
    // =========================================================================
    function CameraEnrollmentModal({ users, setUsers, targetStudentId, lockStudentSelection = false, onClose }) {
      const students = users.filter((u) => u.role === 'student');
      const [selectedId, setSelectedId] = useState(targetStudentId || students[0]?.id || '');
      const [captured, setCaptured] = useState(false);
      const [tempImage, setTempImage] = useState(null);
      const [tempVector, setTempVector] = useState(null);
      const videoRef = useRef(null);
      const fileInputRef = useRef(null);

      const {
        facingMode,
        devices,
        cameraActive,
        cameraLoading,
        cameraError,
        activeLabel,
        resolutionText,
        isMirrored,
        fitMode,
        toggleFitMode,
        selectFrontCamera,
        selectBackCamera,
        cycleNextCamera,
        retryCamera
      } = useReliableCamera({
        videoRef,
        initialFacingMode: 'user',
        enabled: !captured
      });

      const handleCapture = () => {
        const video = videoRef.current;
        if (video && video.videoWidth > 0 && video.videoHeight > 0) {
          const canvas = document.createElement('canvas');
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const ctx = canvas.getContext('2d');
          if (isMirrored) {
            ctx.translate(canvas.width, 0);
            ctx.scale(-1, 1);
          }
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          const realDataUrl = canvas.toDataURL('image/jpeg', 0.92);
          const vec = computeImageBiometricVector(canvas);
          setTempImage(realDataUrl);
          setTempVector(vec);
          setCaptured(true);
        } else {
          fileInputRef.current?.click();
        }
      };

      const handleFileUpload = (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
          const dataUrl = reader.result;
          const img = new Image();
          img.onload = () => {
            const vec = computeImageBiometricVector(img);
            setTempImage(dataUrl);
            setTempVector(vec);
            setCaptured(true);
          };
          img.src = dataUrl;
        };
        reader.readAsDataURL(file);
      };

      const handleSave = () => {
        if (!selectedId || !tempImage) return;
        const newSig = `BIO-FACE-${selectedId.slice(-5)}-${Math.random().toString(16).slice(2, 6).toUpperCase()}`;
        setUsers((prev) =>
          prev.map((u) =>
            u.id === selectedId
              ? { ...u, photo: tempImage, faceSignature: newSig, faceVector: tempVector, isRealEnrolled: true }
              : u
          )
        );
        onClose();
      };

      return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#0f1523] border border-slate-800 rounded-3xl p-6 w-full max-w-md space-y-4 text-xs">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2 font-bold text-white text-sm">
                <Camera className="w-4 h-4 text-indigo-400" />
                <span>Biometric Face Photo Enrollment</span>
              </div>
              <button type="button" onClick={onClose} className="text-slate-400 hover:text-white font-bold text-sm cursor-pointer">
                ✕
              </button>
            </div>

            <div className="space-y-1">
              <label className="text-slate-400">Student Profile:</label>
              <select
                value={selectedId}
                disabled={lockStudentSelection}
                onChange={(e) => {
                  setSelectedId(e.target.value);
                  setCaptured(false);
                  setTempImage(null);
                  setTempVector(null);
                }}
                className="w-full p-2.5 bg-[#070a12] border border-slate-800 rounded-xl text-white font-semibold disabled:opacity-75"
              >
                {students.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.roll || s.id})
                  </option>
                ))}
              </select>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="user"
              onChange={handleFileUpload}
              className="hidden"
            />

            <div className="relative aspect-[4/3] sm:aspect-video max-h-[340px] w-full bg-black rounded-2xl border border-slate-800 overflow-hidden flex items-center justify-center">
              {!captured ? (
                <>
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className={`w-full h-full ${fitMode === 'contain' ? 'object-contain' : 'object-cover'} ${isMirrored ? 'scale-x-[-1]' : ''}`}
                  />
                  {cameraActive && (
                    <div className="absolute inset-6 border-2 border-dashed border-emerald-400/80 rounded-full pointer-events-none" />
                  )}
                  <CameraControlOverlay
                    facingMode={facingMode}
                    devices={devices}
                    cameraActive={cameraActive}
                    cameraLoading={cameraLoading}
                    cameraError={cameraError}
                    activeLabel={activeLabel}
                    resolutionText={resolutionText}
                    fitMode={fitMode}
                    toggleFitMode={toggleFitMode}
                    selectFrontCamera={selectFrontCamera}
                    selectBackCamera={selectBackCamera}
                    cycleNextCamera={cycleNextCamera}
                    retryCamera={retryCamera}
                  />
                </>
              ) : (
                <img src={tempImage} alt="Captured baseline preview" className="w-full h-full object-contain bg-black" />
              )}
            </div>

            {!captured ? (
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleCapture}
                  className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-indigo-600/30"
                >
                  <Camera className="w-4 h-4" /> Capture Reference Photo
                </button>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-3.5 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold rounded-xl flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <Upload className="w-4 h-4" /> Upload
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setCaptured(false);
                    setTempImage(null);
                    setTempVector(null);
                  }}
                  className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl cursor-pointer"
                >
                  Retake
                </button>
                <button
                  type="button"
                  onClick={handleSave}
                  className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl cursor-pointer"
                >
                  Save Reference Photo
                </button>
              </div>
            )}
          </div>
        </div>
      );
    }

    function SidebarItem({ icon: Icon, label, active, onClick }) {
      return (
        <button
          type="button"
          onClick={onClick}
          className={`w-full p-2.5 rounded-xl flex items-center gap-3 font-semibold transition text-xs cursor-pointer text-left ${
            active ? 'bg-[#5852f2] text-white shadow-lg shadow-indigo-600/30' : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
          }`}
        >
          <Icon className="w-4 h-4" />
          <span className="truncate">{label}</span>
        </button>
      );
    }

    // =========================================================================
    // 12. ADMIN PORTAL COMPONENTS
    // =========================================================================
    function AdminUserDirectory({ users, setUsers, onResetFace, onResetDemoData }) {
      const [showPassMap, setShowPassMap] = useState({});
      const [showAddModal, setShowAddModal] = useState(false);
      const [confirmDeleteId, setConfirmDeleteId] = useState(null);
      const [editingUserId, setEditingUserId] = useState(null);
      const [editNameValue, setEditNameValue] = useState('');
      const [newUser, setNewUser] = useState({ name: '', id: '', email: '', role: 'student', pass: 'Mu@2026', dept: 'ICT Sem 3' });

      const togglePass = (id) => {
        setShowPassMap((prev) => ({ ...prev, [id]: !prev[id] }));
      };

      const startEditingName = (userObj) => {
        setEditingUserId(userObj.id);
        setEditNameValue(userObj.name);
        setConfirmDeleteId(null);
      };

      const saveEditedName = (id) => {
        const trimmed = editNameValue.trim();
        if (!trimmed) return;
        setUsers((prev) => prev.map((u) => (u.id === id ? { ...u, name: trimmed } : u)));
        setEditingUserId(null);
        setEditNameValue('');
      };

      const handleAddUser = (e) => {
        e.preventDefault();
        const sig = `BIO-FACE-${newUser.id.slice(-5)}-${Math.random().toString(16).slice(2, 6).toUpperCase()}`;
        setUsers([
          ...users,
          {
            ...newUser,
            roll: newUser.id,
            faceSignature: newUser.role === 'student' ? sig : null,
            faceVector: null,
            isRealEnrolled: false,
            photo: null
          }
        ]);
        setShowAddModal(false);
        setNewUser({ name: '', id: '', email: '', role: 'student', pass: 'Mu@2026', dept: 'ICT Sem 3' });
      };

      const handleDeleteUser = (id) => {
        setUsers((prev) => prev.filter((u) => u.id !== id));
        setConfirmDeleteId(null);
      };

      return (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-white uppercase tracking-wider">User Directory & Keys</h2>
              <p className="text-xs text-slate-400">Manage registered Admin, Faculty, and Student credentials, names & biometric photos</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onResetDemoData}
                className="px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Reset Demo Data
              </button>
              <button
                type="button"
                onClick={() => setShowAddModal(true)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold flex items-center gap-2 shadow cursor-pointer"
              >
                <Plus className="w-4 h-4" /> Add New User
              </button>
            </div>
          </div>

          <div className="bg-[#0e1422] border border-slate-800/80 rounded-2xl p-4 shadow-xl overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#06080e] text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="p-3">USER</th>
                  <th className="p-3">ROLE</th>
                  <th className="p-3">ID / ROLL NO</th>
                  <th className="p-3">UNIVERSITY EMAIL</th>
                  <th className="p-3">CREATED PASSWORD</th>
                  <th className="p-3">ACTIONS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/20">
                    <td className="p-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-slate-800 overflow-hidden flex items-center justify-center font-bold text-slate-300 border border-slate-700 shrink-0">
                          {u.photo ? <img src={u.photo} alt={u.name} className="w-full h-full object-cover" /> : u.name.charAt(0)}
                        </div>
                        {editingUserId === u.id ? (
                          <div className="flex items-center gap-1.5">
                            <input
                              type="text"
                              value={editNameValue}
                              onChange={(e) => setEditNameValue(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') saveEditedName(u.id);
                                if (e.key === 'Escape') setEditingUserId(null);
                              }}
                              autoFocus
                              className="px-2.5 py-1 bg-[#070a12] border border-indigo-500 rounded-lg text-white font-semibold text-xs focus:outline-none w-44"
                            />
                            <button
                              type="button"
                              onClick={() => saveEditedName(u.id)}
                              className="px-2 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-[10px] font-bold cursor-pointer"
                            >
                              Save
                            </button>
                            <button
                              type="button"
                              onClick={() => setEditingUserId(null)}
                              className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-[10px] font-bold cursor-pointer"
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <div>
                            <div className="font-semibold text-slate-200 flex items-center gap-1.5">
                              <span>{u.name}</span>
                              {u.isRealEnrolled && (
                                <span className="px-1.5 py-0.5 bg-emerald-950 border border-emerald-800 text-emerald-400 rounded text-[9px] font-mono">
                                  ENROLLED
                                </span>
                              )}
                            </div>
                            {u.faceSignature && <div className="text-[10px] font-mono text-indigo-400">{u.faceSignature}</div>}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="p-3">
                      <span
                        className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                          u.role === 'admin'
                            ? 'bg-amber-950 text-amber-300 border border-amber-800'
                            : u.role === 'faculty'
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                            : 'bg-indigo-950 text-indigo-300 border border-indigo-800'
                        }`}
                      >
                        {u.role.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-slate-400">{u.roll || u.id}</td>
                    <td className="p-3 font-mono text-slate-400">{u.email}</td>
                    <td className="p-3 font-mono text-slate-300">
                      <div className="flex items-center gap-2">
                        <span className="text-cyan-300">{showPassMap[u.id] ? u.pass : '••••••••'}</span>
                        <button type="button" onClick={() => togglePass(u.id)} className="text-slate-500 hover:text-slate-300 cursor-pointer">
                          {showPassMap[u.id] ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    </td>
                    <td className="p-3">
                      {u.role !== 'admin' ? (
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => startEditingName(u)}
                            className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-cyan-300 rounded-lg text-[11px] font-semibold flex items-center gap-1 transition cursor-pointer"
                          >
                            <Edit3 className="w-3 h-3" /> Edit Name
                          </button>

                          {u.role === 'student' && (
                            <button
                              type="button"
                              onClick={() => onResetFace(u)}
                              className="px-2.5 py-1 bg-indigo-950 hover:bg-indigo-900 border border-indigo-800 text-indigo-300 rounded-lg text-[11px] font-semibold flex items-center gap-1 transition cursor-pointer"
                            >
                              <Camera className="w-3 h-3" /> Enroll Face
                            </button>
                          )}

                          {confirmDeleteId === u.id ? (
                            <div className="flex items-center gap-1 bg-red-950/90 border border-red-800 px-2 py-1 rounded-lg">
                              <span className="text-[10px] text-red-200 font-semibold mr-1">Delete?</span>
                              <button
                                type="button"
                                onClick={() => handleDeleteUser(u.id)}
                                className="px-2 py-0.5 bg-red-600 hover:bg-red-500 text-white rounded text-[10px] font-bold cursor-pointer"
                              >
                                Yes
                              </button>
                              <button
                                type="button"
                                onClick={() => setConfirmDeleteId(null)}
                                className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[10px] font-bold cursor-pointer"
                              >
                                No
                              </button>
                            </div>
                          ) : (
                            <button
                              type="button"
                              onClick={() => setConfirmDeleteId(u.id)}
                              className="px-2.5 py-1 bg-red-950/70 hover:bg-red-900 border border-red-800/80 text-red-300 rounded-lg text-[11px] font-semibold flex items-center gap-1 transition cursor-pointer"
                            >
                              <Trash2 className="w-3 h-3" /> Delete
                            </button>
                          )}
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => startEditingName(u)}
                          className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-amber-300 rounded-lg text-[11px] font-semibold flex items-center gap-1 transition cursor-pointer"
                        >
                          <Edit3 className="w-3 h-3" /> Edit Name
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {showAddModal && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
              <form onSubmit={handleAddUser} className="bg-[#0f1523] border border-slate-800 rounded-3xl p-6 w-full max-w-md space-y-4 text-xs">
                <h3 className="text-sm font-bold text-white">Create New User Account</h3>
                <input required placeholder="Full Name" value={newUser.name} onChange={(e) => setNewUser({ ...newUser, name: e.target.value })} className="w-full p-3 bg-[#070a12] border border-slate-800 rounded-xl text-white" />
                <input required placeholder="Enrollment No / Staff ID" value={newUser.id} onChange={(e) => setNewUser({ ...newUser, id: e.target.value })} className="w-full p-3 bg-[#070a12] border border-slate-800 rounded-xl text-white font-mono" />
                <input required placeholder="Email Address" value={newUser.email} onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} className="w-full p-3 bg-[#070a12] border border-slate-800 rounded-xl text-white font-mono" />
                <select value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })} className="w-full p-3 bg-[#070a12] border border-slate-800 rounded-xl text-white">
                  <option value="student">Student</option>
                  <option value="faculty">Faculty</option>
                  <option value="admin">Admin</option>
                </select>
                <input required placeholder="Assign Password" value={newUser.pass} onChange={(e) => setNewUser({ ...newUser, pass: e.target.value })} className="w-full p-3 bg-[#070a12] border border-slate-800 rounded-xl text-white font-mono" />

                <div className="flex gap-2">
                  <button type="button" onClick={() => setShowAddModal(false)} className="flex-1 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl cursor-pointer">
                    Cancel
                  </button>
                  <button type="submit" className="flex-1 py-2.5 bg-indigo-600 text-white font-bold rounded-xl cursor-pointer">
                    Register Account
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      );
    }

    function AdminAnalytics({ users, attendance, mismatchLogs }) {
      return (
        <div className="space-y-6 text-xs">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">System Analytics Overview</h2>
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="bg-[#0e1422] border border-slate-800 p-4 rounded-2xl">
              <div className="text-slate-400 font-semibold">Total Registered Users</div>
              <div className="text-2xl font-bold text-white mt-1">{users.length}</div>
            </div>
            <div className="bg-[#0e1422] border border-slate-800 p-4 rounded-2xl">
              <div className="text-slate-400 font-semibold">Overall Attendance Avg</div>
              <div className="text-2xl font-bold text-emerald-400 mt-1">84.2%</div>
            </div>
            <div className="bg-[#0e1422] border border-slate-800 p-4 rounded-2xl">
              <div className="text-slate-400 font-semibold">Defaulter Students (&lt;75%)</div>
              <div className="text-2xl font-bold text-red-400 mt-1">1</div>
            </div>
            <div className="bg-[#0e1422] border border-slate-800 p-4 rounded-2xl">
              <div className="text-slate-400 font-semibold">Biometric & QR Mismatches</div>
              <div className="text-2xl font-bold text-amber-400 mt-1">{mismatchLogs.length} Alerts</div>
            </div>
          </div>
        </div>
      );
    }

    function AdminDefaulters({ attendance, users }) {
      const [dispatched, setDispatched] = useState(false);
      const shivanag = users.find((u) => u.id === '92500133026') || { name: 'M. Shivanag', roll: '92500133026' };
      return (
        <div className="space-y-4 text-xs">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">Defaulter Alerts (&lt;75%)</h2>
          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-4">
            <div className="p-3 bg-red-950/40 border border-red-800/80 rounded-xl flex flex-wrap items-center justify-between gap-2 text-red-300">
              <div>
                <div className="font-bold">
                  {shivanag.name} ({shivanag.roll || shivanag.id})
                </div>
                <div className="text-[11px] text-slate-400">Current Attendance: 57.1% (PWP: 60%, DMGT: 53%)</div>
              </div>
              <button
                type="button"
                onClick={() => setDispatched(true)}
                className="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white font-bold rounded-lg cursor-pointer"
              >
                {dispatched ? '✓ Warning Dispatched' : 'Dispatch Warning Letter'}
              </button>
            </div>
          </div>
        </div>
      );
    }

    function AdminBiometricSensitivity({ biometricThreshold, setBiometricThreshold }) {
      return (
        <div className="space-y-4 text-xs max-w-md">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">Biometric Sensitivity Controls</h2>
          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-4 space-y-3">
            <label className="text-slate-300 font-semibold">
              Adaptive Face Matching Confidence Threshold: <strong className="text-indigo-400">{biometricThreshold}%</strong>
            </label>
            <input
              type="range"
              min="65"
              max="92"
              value={biometricThreshold}
              onChange={(e) => setBiometricThreshold(Number(e.target.value))}
              className="w-full accent-indigo-500"
            />
            <p className="text-[11px] text-slate-400">
              Recommended: <strong>72%–78%</strong>. Balances classroom lighting/head-angle tolerance for enrolled students while blocking different individuals.
            </p>
          </div>
        </div>
      );
    }

    function AdminClassroomAllocator({ users }) {
      const fac1 = users.find((u) => u.id === 'FAC01')?.name || 'Prof. Kawal Kaur';
      const fac2 = users.find((u) => u.id === 'FAC02')?.name || 'Prof. Biswajit';
      return (
        <div className="space-y-4 text-xs">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">Classroom Location Allocator</h2>
          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-4 space-y-2">
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl flex justify-between">
              <span className="font-bold text-white">Lab ICT 301</span>
              <span className="text-slate-400">{fac1} (PWP - Python Web Programming)</span>
            </div>
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl flex justify-between">
              <span className="font-bold text-white">Hall ICT 204</span>
              <span className="text-slate-400">{fac2} (DMGT - Discrete Math)</span>
            </div>
          </div>
        </div>
      );
    }

    function AdminMasterCurriculum() {
      return (
        <div className="space-y-4 text-xs">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">Master Curriculum Tracker</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-[#0e1422] border border-slate-800 p-4 rounded-2xl">
              <div className="font-bold text-indigo-300 text-sm">PWP - Python Web Programming</div>
              <div className="text-slate-400 mt-1">Modules: Django, Flask, REST APIs, ORM Database Layer</div>
            </div>
            <div className="bg-[#0e1422] border border-slate-800 p-4 rounded-2xl">
              <div className="font-bold text-indigo-300 text-sm">DMGT - Discrete Math & Graph Theory</div>
              <div className="text-slate-400 mt-1">Modules: Combinatorics, Euler Graphs, Propositional Logic</div>
            </div>
          </div>
        </div>
      );
    }

    function AdminActivityLogs({ mismatchLogs }) {
      return (
        <div className="space-y-4 text-xs">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">System Security & Activity Logs</h2>
          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-4 space-y-2 font-mono">
            <div className="text-emerald-400">[SYSTEM] Multi-factor 30s dynamic class QR & adaptive biometric engine initialized cleanly</div>
            {mismatchLogs.length === 0 && <div className="text-slate-400">[INFO] No expired QR, duplicate scan, or face mismatch incidents recorded yet.</div>}
            {mismatchLogs.map((log, idx) => (
              <div key={idx} className="text-red-400">
                [SECURITY MISMATCH @ {log.time}] {log.student}
              </div>
            ))}
          </div>
        </div>
      );
    }

    // =========================================================================
    // 13. FACULTY PORTAL COMPONENTS
    // =========================================================================
    function FacultyLiveAttendance({
      facultyUser,
      users,
      setUsers,
      activeQrSession,
      qrCountdown,
      rotateQrTokenNow,
      attendance,
      setAttendance,
      mismatchLogs,
      setMismatchLogs,
      studentSessionMarks,
      setStudentSessionMarks,
      classSessionRecords,
      setClassSessionRecords,
      isSessionLive,
      setIsSessionLive,
      liveSessionDate,
      setLiveSessionDate,
      liveSessionSubject,
      setLiveSessionSubject,
      liveSessionStartTime,
      setLiveSessionStartTime,
      biometricThreshold,
      onOpenRecordedSessions
    }) {
      const [selectedStudent, setSelectedStudent] = useState('92500133046');
      const [statusMsg, setStatusMsg] = useState(null);
      const [photoComparison, setPhotoComparison] = useState(null);
      const [activeMode, setActiveMode] = useState('all');
      const [projectorModalOpen, setProjectorModalOpen] = useState(false);
      const [sessionSavedNotice, setSessionSavedNotice] = useState(null);
      const [setupSubject, setSetupSubject] = useState(liveSessionSubject || facultyUser.subject || 'PWP');
      const [setupDate, setSetupDate] = useState(() => liveSessionDate || new Date().toISOString().split('T')[0]);
      const [setupStartTime, setSetupStartTime] = useState(() =>
        new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      );
      const videoRef = useRef(null);

      const students = users.filter((u) => u.role === 'student');
      const targetStudentObj = students.find((u) => u.id === selectedStudent) || students[0];
      const activeSubjectCode = isSessionLive
        ? liveSessionSubject || facultyUser.subject || 'PWP'
        : setupSubject || facultyUser.subject || 'PWP';
      const sessionToken = activeQrSession.token;
      const activeClassQrPayload = `MU-CLASS-QR|${sessionToken}|${activeSubjectCode}|${activeQrSession.validUntil}`;

      const scannedStudentsList = students.filter((s) => {
        const mark = studentSessionMarks[s.id];
        if (!mark || mark.status !== 'Marked as Present') return false;
        const src = String(mark.source || '');
        return src.includes('QR') || src.includes('Face');
      });
      const scannedQrStudents = students.filter((s) => {
        const mark = studentSessionMarks[s.id];
        return mark?.status === 'Marked as Present' && String(mark.source || '').includes('QR');
      });
      const scannedFaceStudents = students.filter((s) => {
        const mark = studentSessionMarks[s.id];
        return mark?.status === 'Marked as Present' && String(mark.source || '').includes('Face');
      });
      const presentStudentsList = students.filter((s) => studentSessionMarks[s.id]?.status === 'Marked as Present');
      const absentStudentsList = students.filter((s) => studentSessionMarks[s.id]?.status !== 'Marked as Present');

      const formatDisplayDate = (isoDate) => {
        try {
          if (!isoDate) return new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
          const parsed = new Date(isoDate + 'T00:00:00');
          if (isNaN(parsed.getTime())) return isoDate;
          return parsed.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
        } catch (e) {
          return isoDate;
        }
      };

      const handleStartLiveSession = (e) => {
        e.preventDefault();
        const chosenTime = setupStartTime.trim() || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const chosenDate = setupDate || new Date().toISOString().split('T')[0];
        const chosenSubject = setupSubject || facultyUser.subject || 'PWP';

        setLiveSessionSubject(chosenSubject);
        setLiveSessionDate(chosenDate);
        setLiveSessionStartTime(chosenTime);
        setStudentSessionMarks({});
        setStatusMsg(null);
        setPhotoComparison(null);
        setSessionSavedNotice(null);
        rotateQrTokenNow();
        setIsSessionLive(true);
      };

      const handleStopLiveSessionAndSaveRecord = () => {
        const endTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const startTime = liveSessionStartTime || endTime;
        const dateStr = formatDisplayDate(liveSessionDate);
        const subj = activeSubjectCode;

        const studentBreakdown = students.map((s) => {
          const mark = studentSessionMarks[s.id];
          const isPresent = mark?.status === 'Marked as Present';
          return {
            id: s.id,
            roll: s.roll,
            name: s.name,
            status: isPresent ? 'Present' : 'Absent',
            source: isPresent ? mark.source : 'Unscanned / Absent',
            time: isPresent ? mark.time : '-'
          };
        });

        const newRecord = {
          id: 'SES-' + Date.now(),
          facultyName: facultyUser.name,
          subject: subj,
          date: dateStr,
          startTime,
          endTime,
          totalStudents: students.length,
          presentCount: presentStudentsList.length,
          qrScannedCount: scannedQrStudents.length,
          absentCount: absentStudentsList.length,
          students: studentBreakdown
        };

        setClassSessionRecords((prev) => [newRecord, ...prev]);
        setSessionSavedNotice(
          `Live Session Stopped & Saved! ${subj} (${dateStr}, ${startTime} to ${endTime}): ${presentStudentsList.length} Present (${scannedQrStudents.length} QR Scanned) & ${absentStudentsList.length} Absent.`
        );

        setStudentSessionMarks({});
        setStatusMsg(null);
        setPhotoComparison(null);
        setProjectorModalOpen(false);
        setIsSessionLive(false);
        setSetupStartTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
      };

      const {
        facingMode,
        devices,
        cameraActive,
        cameraLoading,
        cameraError,
        activeLabel,
        resolutionText,
        isMirrored,
        fitMode,
        toggleFitMode,
        selectFrontCamera,
        selectBackCamera,
        cycleNextCamera,
        retryCamera
      } = useReliableCamera({
        videoRef,
        initialFacingMode: 'user',
        enabled: isSessionLive && (activeMode === 'all' || activeMode === 'face')
      });

      const markStudentAttendance = (studentId, isPresent, source = 'Faculty Manual / Face') => {
        const subj = activeSubjectCode;
        setAttendance((prev) => {
          const studentAtt = prev[studentId] || { [subj]: { present: 0, total: 0 } };
          const currentSubj = studentAtt[subj] || { present: 0, total: 0 };
          return {
            ...prev,
            [studentId]: {
              ...studentAtt,
              [subj]: {
                present: currentSubj.present + (isPresent ? 1 : 0),
                total: currentSubj.total + 1
              }
            }
          };
        });
        setStudentSessionMarks((prev) => ({
          ...prev,
          [studentId]: {
            status: isPresent ? 'Marked as Present' : 'Marked Absent',
            source,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        }));
      };

      const handleFaceVerification = () => {
        if (!targetStudentObj) return;
        const video = videoRef.current;

        if (!video || video.videoWidth === 0 || video.videoHeight === 0) {
          setStatusMsg({
            type: 'error',
            text: 'Camera feed inactive. Please allow camera access or switch between Front Cam and Back Cam.'
          });
          return;
        }

        const { avgLuminance, contrastRange } = computeFrameBrightnessAndContrast(video);
        if (avgLuminance < 18 || contrastRange < 20) {
          setStatusMsg({
            type: 'error',
            text: 'Camera Lens Covered / Too Dark! Please uncover the camera and face the lens clearly.'
          });
          return;
        }

        const snapCanvas = document.createElement('canvas');
        snapCanvas.width = video.videoWidth;
        snapCanvas.height = video.videoHeight;
        const snapCtx = snapCanvas.getContext('2d');
        if (isMirrored) {
          snapCtx.translate(snapCanvas.width, 0);
          snapCtx.scale(-1, 1);
        }
        snapCtx.drawImage(video, 0, 0, snapCanvas.width, snapCanvas.height);
        const scannedPhotoDataUrl = snapCanvas.toDataURL('image/jpeg', 0.88);

        const liveVec = computeImageBiometricVector(snapCanvas);
        if (!liveVec) {
          setStatusMsg({
            type: 'error',
            text: 'Unable to extract facial features from scanned photo. Please hold steady and try again.'
          });
          return;
        }

        if (!targetStudentObj.faceVector) {
          setStatusMsg({
            type: 'error',
            text: `${targetStudentObj.name} (${targetStudentObj.roll}) does not have an enrolled reference photo yet. Please enroll in Admin Portal first.`
          });
          return;
        }

        let bestMatchStudent = null;
        let bestScore = -1;
        let targetScore = computeCosineSimilarity(liveVec, targetStudentObj.faceVector) ?? 0;

        students.forEach((s) => {
          if (s.faceVector) {
            const sim = computeCosineSimilarity(liveVec, s.faceVector);
            if (sim !== null && sim > bestScore) {
              bestScore = sim;
              bestMatchStudent = s;
            }
          }
        });

        const thresholdDecimal = (biometricThreshold || 75) / 100;

        if (
          bestMatchStudent &&
          bestMatchStudent.id !== targetStudentObj.id &&
          bestScore >= thresholdDecimal &&
          bestScore > targetScore + 0.06
        ) {
          setPhotoComparison({
            enrolledPhoto: targetStudentObj.photo,
            scannedPhoto: scannedPhotoDataUrl,
            similarityPct: Math.round(targetScore * 100),
            matched: false
          });
          setStatusMsg({
            type: 'error',
            text: `MISMATCH! Enrolled photo is ${targetStudentObj.name} (${targetStudentObj.roll}), but scanned photo matches ${bestMatchStudent.name} (${bestMatchStudent.roll}). Attendance rejected!`
          });
          setMismatchLogs((prev) => [
            ...prev,
            {
              student: `Face Photo Mismatch: Target ${targetStudentObj.name} (${targetStudentObj.roll}) | Scanned ${bestMatchStudent.name} (${bestMatchStudent.roll})`,
              time: new Date().toLocaleTimeString()
            }
          ]);
          return;
        }

        if (targetScore >= thresholdDecimal) {
          const blendedVec = targetStudentObj.faceVector.map((val, idx) => 0.8 * val + 0.2 * liveVec[idx]);
          setUsers((prev) =>
            prev.map((u) => (u.id === targetStudentObj.id ? { ...u, faceVector: blendedVec } : u))
          );

          const simPct = Math.round(targetScore * 100);
          setPhotoComparison({
            enrolledPhoto: targetStudentObj.photo,
            scannedPhoto: scannedPhotoDataUrl,
            similarityPct: simPct,
            matched: true
          });
          setStatusMsg({
            type: 'success',
            text: `Marked as Present! Background photo comparison matched ${targetStudentObj.name} (${targetStudentObj.roll}) with ${simPct}% similarity.`
          });
          markStudentAttendance(targetStudentObj.id, true, 'Faculty Face Photo Match');
        } else {
          const simPct = Math.round(targetScore * 100);
          setPhotoComparison({
            enrolledPhoto: targetStudentObj.photo,
            scannedPhoto: scannedPhotoDataUrl,
            similarityPct: simPct,
            matched: false
          });
          setStatusMsg({
            type: 'error',
            text: `Mismatch! Scanned photo did not match ${targetStudentObj.name}'s enrolled photo (${simPct}% similarity < ${biometricThreshold}% required).`
          });
          setMismatchLogs((prev) => [
            ...prev,
            {
              student: `Face Photo Mismatch: Target ${targetStudentObj.name} (${targetStudentObj.roll}) — Similarity ${simPct}%`,
              time: new Date().toLocaleTimeString()
            }
          ]);
        }
      };

      const handleDownloadQrPng = () => {
        const qrContainer = document.getElementById('faculty-qr-box');
        const canvas = qrContainer?.querySelector('canvas');
        if (canvas) {
          const link = document.createElement('a');
          link.download = `Class_QR_${activeSubjectCode}_${sessionToken}.png`;
          link.href = canvas.toDataURL('image/png');
          link.click();
        }
      };

      const handleExportCsv = () => {
        const subj = facultyUser.subject || 'PWP';
        const rows = [['Roll No', 'Student Name', 'Subject', 'Present', 'Total', 'Percentage', 'Session Status']];
        students.forEach((s) => {
          const rec = attendance[s.id]?.[subj] || { present: 0, total: 0 };
          const pct = rec.total > 0 ? Math.round((rec.present / rec.total) * 100) : 100;
          const st = studentSessionMarks[s.id]?.status || 'Pending';
          rows.push([s.roll, s.name, subj, rec.present, rec.total, `${pct}%`, st]);
        });
        const csvContent = 'data:text/csv;charset=utf-8,' + rows.map((r) => r.join(',')).join('\n');
        const link = document.createElement('a');
        link.href = encodeURI(csvContent);
        link.download = `MU_ICT_${subj}_Attendance.csv`;
        link.click();
      };

      const progressBarPct = Math.max(0, Math.min(100, Math.round((qrCountdown / 30) * 100)));

      return (
        <div className="space-y-6 text-xs">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-white uppercase tracking-wider">Live Attendance Engine</h2>
              <p className="text-slate-400">
                Faculty: <strong className="text-indigo-400">{facultyUser.name}</strong> ({facultyUser.dept})
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={onOpenRecordedSessions}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-cyan-300 rounded-xl font-bold flex items-center gap-1.5 cursor-pointer"
              >
                <Clock className="w-3.5 h-3.5" /> Recorded Sessions & Student List ({classSessionRecords.length})
              </button>
              {isSessionLive ? (
                <div className="px-3 py-1.5 bg-emerald-950/80 border border-emerald-700 rounded-xl text-emerald-300 font-mono font-bold flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> LIVE SESSION ACTIVE
                </div>
              ) : (
                <div className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-xl text-slate-400 font-mono font-bold flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-slate-500" /> SESSION STOPPED
                </div>
              )}
            </div>
          </div>

          {sessionSavedNotice && (
            <div className="p-4 rounded-2xl bg-emerald-950/90 border border-emerald-700 text-emerald-200 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2 font-semibold">
                <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{sessionSavedNotice}</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={onOpenRecordedSessions}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-[11px] font-bold cursor-pointer"
                >
                  Open Recorded Sessions →
                </button>
                <button
                  type="button"
                  onClick={() => setSessionSavedNotice(null)}
                  className="text-emerald-300 hover:text-white font-bold px-2 cursor-pointer"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          {!isSessionLive ? (
            <div className="max-w-xl mx-auto bg-[#0e1422] border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-5 shadow-2xl">
              <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
                <div className="w-11 h-11 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
                  <Video className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Start New Live Class Session</h3>
                  <p className="text-[11px] text-slate-400">
                    QR Scanner, AI Face Recognition, and Manual Attendance stay hidden until you start a live session.
                  </p>
                </div>
              </div>

              <form onSubmit={handleStartLiveSession} className="space-y-4">
                <div className="space-y-1">
                  <label className="text-slate-300 font-semibold block">Subject / Lecture:</label>
                  <select
                    value={setupSubject}
                    onChange={(e) => setSetupSubject(e.target.value)}
                    className="w-full p-3 bg-[#070a12] border border-slate-800 rounded-xl text-white font-semibold"
                  >
                    <option value="PWP">PWP — Python Web Programming</option>
                    <option value="DMGT">DMGT — Discrete Math & Graph Theory</option>
                    <option value="COA">COA — Computer Organization & Architecture</option>
                    <option value="DSC">DSC — Data Structures in C</option>
                  </select>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-slate-300 font-semibold block">Session Date:</label>
                    <input
                      type="date"
                      required
                      value={setupDate}
                      onChange={(e) => setSetupDate(e.target.value)}
                      className="w-full p-3 bg-[#070a12] border border-slate-800 rounded-xl text-white font-mono"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-slate-300 font-semibold block">Session Start Time:</label>
                    <input
                      type="text"
                      required
                      value={setupStartTime}
                      onChange={(e) => setSetupStartTime(e.target.value)}
                      placeholder="e.g., 10:00 AM"
                      className="w-full p-3 bg-[#070a12] border border-slate-800 rounded-xl text-white font-mono"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-3.5 bg-[#5852f2] hover:bg-indigo-600 text-white font-bold rounded-xl text-sm flex items-center justify-center gap-2 shadow-xl shadow-indigo-600/30 cursor-pointer"
                >
                  <Video className="w-4 h-4" /> Start Live Session
                </button>
              </form>

              <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400">
                <span>Need to edit previous attendance or view class records?</span>
                <button
                  type="button"
                  onClick={onOpenRecordedSessions}
                  className="text-cyan-400 hover:text-cyan-300 font-bold underline cursor-pointer"
                >
                  Go to Recorded Sessions & Student List →
                </button>
              </div>
            </div>
          ) : (
            <>
              <div className="bg-indigo-950/40 border border-indigo-500/40 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="px-3 py-1 bg-indigo-600 text-white font-bold rounded-xl text-xs">
                    {activeSubjectCode}
                  </span>
                  <div className="text-xs text-slate-200 font-mono">
                    Date: <strong className="text-white">{formatDisplayDate(liveSessionDate)}</strong> • Start Time:{' '}
                    <strong className="text-cyan-300">{liveSessionStartTime}</strong>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleStopLiveSessionAndSaveRecord}
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-red-600/30 cursor-pointer"
                >
                  <CalendarCheck className="w-4 h-4" /> Stop Live Session & Save Record
                </button>
              </div>

              <div className="grid grid-cols-3 gap-2 bg-[#0e1422] p-2 rounded-2xl border border-slate-800">
                <button
                  type="button"
                  onClick={() => setActiveMode('all')}
                  className={`py-2.5 px-3 rounded-xl font-bold flex items-center justify-center gap-2 transition cursor-pointer ${
                    activeMode === 'all' ? 'bg-[#5852f2] text-white shadow-lg shadow-indigo-600/30' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Layers className="w-4 h-4" /> All Modes
                </button>
                <button
                  type="button"
                  onClick={() => setActiveMode('face')}
                  className={`py-2.5 px-3 rounded-xl font-bold flex items-center justify-center gap-2 transition cursor-pointer ${
                    activeMode === 'face' ? 'bg-[#5852f2] text-white shadow-lg shadow-indigo-600/30' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Video className="w-4 h-4 text-emerald-400" /> Face Recognition
                </button>
                <button
                  type="button"
                  onClick={() => setActiveMode('manual')}
                  className={`py-2.5 px-3 rounded-xl font-bold flex items-center justify-center gap-2 transition cursor-pointer ${
                    activeMode === 'manual' ? 'bg-[#5852f2] text-white shadow-lg shadow-indigo-600/30' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <UserCheck className="w-4 h-4 text-cyan-400" /> Manual Attendance Roster
                </button>
              </div>

              <div className="max-w-2xl mx-auto bg-[#0e1422] border border-indigo-500/30 rounded-2xl p-6 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div>
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <QrCode className="w-4 h-4 text-indigo-400" /> Dynamic 30-Second Class QR Code ({activeSubjectCode})
                    </h3>
                    <p className="text-[11px] text-slate-400">
                      Single class QR code — pattern refreshes automatically every 30s. Any student can scan once while active.
                    </p>
                  </div>
                  <div className="px-3 py-1 bg-indigo-950 border border-indigo-800 rounded-xl text-[11px] font-mono text-indigo-300 flex items-center gap-2">
                    <span>Token: <strong>{sessionToken}</strong></span>
                    <span className={`px-2 py-0.5 rounded-md font-bold text-white ${qrCountdown <= 8 ? 'bg-red-600 animate-pulse' : 'bg-indigo-600'}`}>
                      {qrCountdown}s
                    </span>
                  </div>
                </div>

                <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${qrCountdown <= 8 ? 'bg-red-500' : 'bg-emerald-500'}`}
                    style={{ width: `${progressBarPct}%` }}
                  />
                </div>

                <div className="p-6 rounded-2xl bg-[#070a12] border border-indigo-500/50 shadow-lg shadow-indigo-600/15 flex flex-col items-center text-center space-y-3">
                  <div className="px-3 py-1 bg-slate-900 border border-slate-800 rounded-xl text-xs font-semibold text-cyan-300">
                    Faculty: {facultyUser.name} ({activeSubjectCode}) • Valid for {qrCountdown}s
                  </div>

                  <div className="bg-white p-3 rounded-2xl shadow-lg border-4 border-indigo-500/30">
                    <RealScannableQrCode id="faculty-qr-box" value={activeClassQrPayload} size={196} />
                  </div>

                  <div className="text-[11px] font-mono text-slate-400">{sessionToken}</div>

                  <div className="flex flex-wrap items-center justify-center gap-2">
                    <button
                      type="button"
                      onClick={rotateQrTokenNow}
                      className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-[11px] font-bold flex items-center gap-1.5 cursor-pointer"
                    >
                      <RefreshCw className="w-3.5 h-3.5" /> Generate New QR Pattern Now
                    </button>
                    <button
                      type="button"
                      onClick={() => setProjectorModalOpen(true)}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-xl text-[11px] font-bold flex items-center gap-1.5 cursor-pointer"
                    >
                      <Maximize2 className="w-3.5 h-3.5 text-indigo-400" /> Full-Screen Projector
                    </button>
                    <button
                      type="button"
                      onClick={handleDownloadQrPng}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-xl text-[11px] font-bold flex items-center gap-1.5 cursor-pointer"
                    >
                      <Download className="w-3.5 h-3.5 text-emerald-400" /> Save QR PNG
                    </button>
                  </div>

                  <p className="text-[11px] text-slate-400">
                    Any student can scan this QR from their Student Portal within {qrCountdown}s (one scan per student per pattern).
                  </p>
                </div>
              </div>

              {(activeMode === 'all' || activeMode === 'face') && (
                <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-6 space-y-4 max-w-2xl mx-auto">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <span className="font-bold text-white text-sm block">AI Face Photo Scanner ({facultyUser.name})</span>
                      <span className="text-[11px] text-slate-400">
                        Compares enrolled reference photo against scanned live photo in background (Threshold: {biometricThreshold}%)
                      </span>
                    </div>
                    <span className="px-2.5 py-1 bg-amber-950 border border-amber-800 text-amber-300 rounded-lg text-[10px] font-bold">
                      Target: {targetStudentObj?.roll}
                    </span>
                  </div>

                  <div className="space-y-1">
                    <label className="text-slate-400 text-[11px]">Target Student for Face Verification:</label>
                    <select
                      value={selectedStudent}
                      onChange={(e) => {
                        setSelectedStudent(e.target.value);
                        setStatusMsg(null);
                        setPhotoComparison(null);
                      }}
                      className="w-full p-2.5 bg-[#070a12] border border-slate-800 rounded-xl text-white font-semibold"
                    >
                      {students.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name} ({s.roll}) {s.faceVector ? '• Enrolled Photo Ready' : '• Enrollment Needed'}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="relative aspect-[4/3] sm:aspect-video max-h-[380px] w-full bg-black rounded-2xl border border-slate-800 flex items-center justify-center overflow-hidden">
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      muted
                      className={`w-full h-full ${fitMode === 'contain' ? 'object-contain' : 'object-cover'} ${isMirrored ? 'scale-x-[-1]' : ''}`}
                    />
                    {cameraActive && (
                      <div className="absolute inset-8 border-2 border-dashed border-indigo-400/70 rounded-full pointer-events-none" />
                    )}
                    {targetStudentObj?.photo && (
                      <div className="absolute top-2.5 left-2.5 bg-slate-900/90 border border-slate-700 p-1.5 rounded-xl flex items-center gap-2 z-10">
                        <img src={targetStudentObj.photo} alt="Ref" className="w-8 h-8 rounded-lg object-cover border border-indigo-500" />
                        <div className="text-[10px] leading-tight">
                          <div className="text-slate-400">Enrolled Photo</div>
                          <div className="font-bold text-white">{targetStudentObj.name}</div>
                        </div>
                      </div>
                    )}
                    <CameraControlOverlay
                      facingMode={facingMode}
                      devices={devices}
                      cameraActive={cameraActive}
                      cameraLoading={cameraLoading}
                      cameraError={cameraError}
                      activeLabel={activeLabel}
                      resolutionText={resolutionText}
                      fitMode={fitMode}
                      toggleFitMode={toggleFitMode}
                      selectFrontCamera={selectFrontCamera}
                      selectBackCamera={selectBackCamera}
                      cycleNextCamera={cycleNextCamera}
                      retryCamera={retryCamera}
                    />
                  </div>

                  {photoComparison && (
                    <div className="p-3.5 rounded-2xl bg-[#070a12] border border-slate-800 space-y-2">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="font-bold text-slate-300">Background Photo Comparison</span>
                        <span
                          className={`font-mono font-bold ${
                            photoComparison.matched ? 'text-emerald-400' : 'text-red-400'
                          }`}
                        >
                          {photoComparison.similarityPct}% Similarity ({photoComparison.matched ? 'MATCH' : 'MISMATCH'})
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-center">
                        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-2">
                          <div className="text-[10px] text-slate-400 font-semibold mb-1">1. Enrolled Photo</div>
                          {photoComparison.enrolledPhoto ? (
                            <img
                              src={photoComparison.enrolledPhoto}
                              alt="Enrolled"
                              className="w-full h-24 object-cover rounded-lg border border-slate-700"
                            />
                          ) : (
                            <div className="w-full h-24 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400">
                              No Photo
                            </div>
                          )}
                        </div>
                        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-2">
                          <div className="text-[10px] text-slate-400 font-semibold mb-1">2. Scanned Photo</div>
                          <img
                            src={photoComparison.scannedPhoto}
                            alt="Scanned"
                            className="w-full h-24 object-cover rounded-lg border border-slate-700"
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {statusMsg && (
                    <div
                      className={`p-3 rounded-xl border text-xs font-bold flex items-start gap-2 ${
                        statusMsg.type === 'success'
                          ? 'bg-emerald-950/90 border-emerald-800 text-emerald-300'
                          : 'bg-red-950/90 border-red-800 text-red-300'
                      }`}
                    >
                      {statusMsg.type === 'success' ? (
                        <CheckCircle className="w-4 h-4 shrink-0 mt-0.5" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                      )}
                      <span>{statusMsg.text}</span>
                    </div>
                  )}

                  <button
                    type="button"
                    onClick={handleFaceVerification}
                    className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 cursor-pointer"
                  >
                    <Camera className="w-4 h-4" /> Scan & Compare Photo
                  </button>
                </div>
              )}

              {/* LIVE SESSION SCAN & ATTENDANCE SUMMARY */}
              <div className="max-w-2xl mx-auto bg-[#0e1422] border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <BarChart2 className="w-4 h-4 text-emerald-400" /> Live Session Scan & Attendance Summary
                    </h3>
                    <p className="text-[11px] text-slate-400 font-mono">
                      {formatDisplayDate(liveSessionDate)} • Started at <strong className="text-cyan-300">{liveSessionStartTime}</strong>
                    </p>
                  </div>
                  <span className="px-2.5 py-1 bg-emerald-950 border border-emerald-800 text-emerald-300 rounded-lg text-[10px] font-bold flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" /> LIVE COUNTS
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="p-3.5 rounded-xl bg-indigo-950/40 border border-indigo-800/80">
                    <div className="text-[10px] text-indigo-300 font-semibold">TOTAL SCANNED</div>
                    <div className="text-2xl font-extrabold text-indigo-400 mt-0.5">{scannedStudentsList.length}</div>
                    <div className="text-[9px] text-indigo-300/80 font-mono">
                      {scannedQrStudents.length} QR • {scannedFaceStudents.length} Face
                    </div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-800/80">
                    <div className="text-[10px] text-emerald-300 font-semibold">TOTAL PRESENT</div>
                    <div className="text-2xl font-extrabold text-emerald-400 mt-0.5">{presentStudentsList.length}</div>
                    <div className="text-[9px] text-emerald-300/80 font-mono">Out of {students.length}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-800/80">
                    <div className="text-[10px] text-red-300 font-semibold">TOTAL ABSENT</div>
                    <div className="text-2xl font-extrabold text-red-400 mt-0.5">{absentStudentsList.length}</div>
                    <div className="text-[9px] text-red-300/80 font-mono">Unscanned / Absent</div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/80 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
                      Students Who Scanned QR / Face ({scannedStudentsList.length} Scanned)
                    </span>
                  </div>

                  {scannedStudentsList.length === 0 ? (
                    <div className="p-3 rounded-xl bg-[#070a12] border border-slate-800 text-[11px] text-slate-400">
                      No students have scanned the QR code or completed Face Recognition yet. As soon as a student scans, their name and <strong className="text-emerald-400">Marked as Present</strong> badge will appear here live.
                    </div>
                  ) : (
                    <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-700/70 space-y-2">
                      <div className="text-[10px] font-bold text-emerald-300 uppercase">
                        Verified Scans — Marked as Present ({scannedStudentsList.length}):
                      </div>
                      <div className="space-y-1.5">
                        {scannedStudentsList.map((s) => {
                          const mark = studentSessionMarks[s.id];
                          const isFace = String(mark?.source || '').includes('Face');
                          return (
                            <div
                              key={s.id}
                              className="flex flex-wrap items-center justify-between gap-2 px-3 py-2 rounded-xl bg-[#070a12] border border-emerald-700/60"
                            >
                              <div className="flex items-center gap-2.5">
                                <div className="w-7 h-7 rounded-full bg-emerald-900/60 border border-emerald-600/60 overflow-hidden flex items-center justify-center font-bold text-emerald-200 shrink-0">
                                  {s.photo ? <img src={s.photo} alt={s.name} className="w-full h-full object-cover" /> : s.name.charAt(0)}
                                </div>
                                <div>
                                  <div className="text-xs font-bold text-white">{s.name}</div>
                                  <div className="text-[10px] font-mono text-slate-400">
                                    Roll: {s.roll} • {isFace ? 'Face Recognition' : 'QR Code Scan'} at {mark?.time}
                                  </div>
                                </div>
                              </div>
                              <span className="px-2.5 py-1 rounded-lg bg-emerald-600 text-white text-[10px] font-bold shadow">
                                ✓ Marked as Present
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="p-3 rounded-xl bg-emerald-950/25 border border-emerald-800/60 space-y-2">
                      <div className="text-[10px] font-bold text-emerald-400 uppercase flex items-center justify-between">
                        <span>Present Students ({presentStudentsList.length})</span>
                        <span>PRESENT</span>
                      </div>
                      {presentStudentsList.length === 0 ? (
                        <div className="text-[11px] text-slate-500 italic">No students marked present yet.</div>
                      ) : (
                        <div className="space-y-1.5">
                          {presentStudentsList.map((s) => {
                            const mark = studentSessionMarks[s.id];
                            return (
                              <div
                                key={s.id}
                                className="flex items-center justify-between gap-2 px-2.5 py-1.5 rounded-lg bg-[#070a12] border border-slate-800"
                              >
                                <div className="truncate">
                                  <div className="text-[11px] font-bold text-white truncate">{s.name}</div>
                                  <div className="text-[9px] font-mono text-slate-400">
                                    {s.roll} • {mark?.source}
                                  </div>
                                </div>
                                <span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-400 text-[9px] font-bold shrink-0">
                                  Marked as Present
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>

                    <div className="p-3 rounded-xl bg-red-950/25 border border-red-800/60 space-y-2">
                      <div className="text-[10px] font-bold text-red-400 uppercase flex items-center justify-between">
                        <span>Absent Students ({absentStudentsList.length})</span>
                        <span>ABSENT</span>
                      </div>
                      {absentStudentsList.length === 0 ? (
                        <div className="text-[11px] text-emerald-400 font-semibold">All students are present!</div>
                      ) : (
                        <div className="space-y-1.5">
                          {absentStudentsList.map((s) => (
                            <div
                              key={s.id}
                              className="flex items-center justify-between gap-2 px-2.5 py-1.5 rounded-lg bg-[#070a12] border border-slate-800"
                            >
                              <div className="truncate">
                                <div className="text-[11px] font-bold text-slate-200 truncate">{s.name}</div>
                                <div className="text-[9px] font-mono text-slate-500">{s.roll}</div>
                              </div>
                              <span className="px-2 py-0.5 rounded bg-red-950 border border-red-800 text-red-400 text-[9px] font-bold shrink-0">
                                Absent
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {(activeMode === 'all' || activeMode === 'manual') && (
                <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-6 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                    <div>
                      <h3 className="text-sm font-bold text-white flex items-center gap-2">
                        <UserCheck className="w-4 h-4 text-cyan-400" /> Live Manual Attendance Roster ({activeSubjectCode})
                      </h3>
                      <p className="text-[11px] text-slate-400">
                        Automatically updates on QR/Face scan or override manually during the live session
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={handleExportCsv}
                        className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-bold rounded-xl text-[11px] flex items-center gap-1.5 cursor-pointer"
                      >
                        <Download className="w-3.5 h-3.5" /> Export CSV
                      </button>
                      <button
                        type="button"
                        onClick={() => students.forEach((s) => markStudentAttendance(s.id, true, 'Faculty Bulk Present'))}
                        className="px-3 py-1.5 bg-emerald-950 hover:bg-emerald-900 border border-emerald-800 text-emerald-300 font-bold rounded-xl text-[11px] cursor-pointer"
                      >
                        Mark All Present
                      </button>
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-[#06080e] text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="p-3">STUDENT</th>
                          <th className="p-3">ROLL NO</th>
                          <th className="p-3">CURRENT {activeSubjectCode} %</th>
                          <th className="p-3">LIVE ATTENDANCE STATUS</th>
                          <th className="p-3 text-right">MANUAL OVERRIDE</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {students.map((s) => {
                          const subj = activeSubjectCode;
                          const rec = attendance[s.id]?.[subj] || { present: 0, total: 0 };
                          const pct = rec.total > 0 ? Math.round((rec.present / rec.total) * 100) : 100;
                          const sessionRecord = studentSessionMarks[s.id];

                          return (
                            <tr key={s.id} className="hover:bg-slate-800/20">
                              <td className="p-3 flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-slate-800 overflow-hidden border border-slate-700 flex items-center justify-center font-bold text-slate-300">
                                  {s.photo ? <img src={s.photo} alt={s.name} className="w-full h-full object-cover" /> : s.name.charAt(0)}
                                </div>
                                <span className="font-semibold text-white">{s.name}</span>
                              </td>
                              <td className="p-3 font-mono text-slate-400">{s.roll}</td>
                              <td className="p-3 font-mono">
                                <span className={`font-bold ${pct < 75 ? 'text-red-400' : 'text-emerald-400'}`}>{pct}%</span>{' '}
                                <span className="text-slate-500">
                                  ({rec.present}/{rec.total})
                                </span>
                              </td>
                              <td className="p-3">
                                {sessionRecord ? (
                                  <div className="space-y-0.5">
                                    <span
                                      className={`px-2.5 py-0.5 rounded text-[10px] font-bold inline-block ${
                                        sessionRecord.status === 'Marked as Present'
                                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                          : 'bg-red-950 text-red-400 border border-red-800'
                                      }`}
                                    >
                                      {sessionRecord.status.toUpperCase()}
                                    </span>
                                    <div className="text-[10px] text-slate-400 font-mono">
                                      via {sessionRecord.source} ({sessionRecord.time})
                                    </div>
                                  </div>
                                ) : (
                                  <span className="text-slate-500 text-[11px]">Awaiting Student QR / Face Scan</span>
                                )}
                              </td>
                              <td className="p-3 text-right">
                                <div className="inline-flex gap-2">
                                  <button
                                    type="button"
                                    onClick={() => markStudentAttendance(s.id, true, 'Faculty Manual Roster')}
                                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-[11px] cursor-pointer"
                                  >
                                    Present
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => markStudentAttendance(s.id, false, 'Faculty Manual Roster')}
                                    className="px-3 py-1.5 bg-red-600/80 hover:bg-red-600 text-white font-bold rounded-lg text-[11px] cursor-pointer"
                                  >
                                    Absent
                                  </button>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {projectorModalOpen && (
                <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center p-4 z-50">
                  <div className="bg-[#0f1523] border border-slate-800 rounded-3xl p-8 max-w-md w-full text-center space-y-4">
                    <div className="flex items-center justify-between">
                      <span className={`text-xs font-mono font-bold ${qrCountdown <= 8 ? 'text-red-400 animate-pulse' : 'text-indigo-400'}`}>
                        NEW QR PATTERN IN {qrCountdown}s
                      </span>
                      <button type="button" onClick={() => setProjectorModalOpen(false)} className="text-slate-400 hover:text-white font-bold cursor-pointer">
                        ✕ Close
                      </button>
                    </div>
                    <h3 className="text-lg font-extrabold text-white">{facultyUser.name} — {activeSubjectCode}</h3>
                    <p className="text-xs font-mono text-slate-400">Active Token: {sessionToken}</p>
                    <div className="bg-white p-4 rounded-2xl inline-block shadow-2xl">
                      <RealScannableQrCode id="projector-qr-box" value={activeClassQrPayload} size={240} />
                    </div>
                    <p className="text-[11px] text-slate-400">Any student can scan once while active</p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      );
    }

    function FacultyRecordedSessionsDashboard({
      facultyUser,
      users,
      attendance,
      setAttendance,
      classSessionRecords,
      setClassSessionRecords,
      onBackToLive
    }) {
      const students = users.filter((u) => u.role === 'student');
      const subjectsList = ['PWP', 'DMGT', 'COA', 'DSC'];
      const [selectedRecordId, setSelectedRecordId] = useState(() =>
        classSessionRecords.length > 0 ? classSessionRecords[0].id : null
      );
      const [masterSubjectFilter, setMasterSubjectFilter] = useState(facultyUser.subject || 'PWP');
      const [updateBanner, setUpdateBanner] = useState('');

      useEffect(() => {
        if (!selectedRecordId && classSessionRecords.length > 0) {
          setSelectedRecordId(classSessionRecords[0].id);
        } else if (selectedRecordId && !classSessionRecords.some((r) => r.id === selectedRecordId)) {
          setSelectedRecordId(classSessionRecords.length > 0 ? classSessionRecords[0].id : null);
        }
      }, [classSessionRecords, selectedRecordId]);

      const activeRecord = classSessionRecords.find((r) => r.id === selectedRecordId) || null;

      const triggerCsvDownload = (rows, filename) => {
        const csvString = rows
          .map((row) =>
            row
              .map((cell) => `"${String(cell ?? '').replace(/"/g, '""')}"`)
              .join(',')
          )
          .join('\n');
        const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
      };

      const handleDownloadAllClassesReport = () => {
        const rows = [
          [
            'Roll Number',
            'Student Name',
            'Department',
            'PWP (Present/Total)',
            'DMGT (Present/Total)',
            'COA (Present/Total)',
            'DSC (Present/Total)',
            'Total Classes Attended',
            'Total Classes Conducted',
            'Overall Attendance Percentage (%)',
            'Eligibility Status'
          ]
        ];

        students.forEach((s) => {
          const stuAtt = attendance[s.id] || {};
          let totalPresent = 0;
          let totalConducted = 0;
          const subjectCols = subjectsList.map((sub) => {
            const rec = stuAtt[sub] || { present: 0, total: 0 };
            totalPresent += rec.present;
            totalConducted += rec.total;
            return `${rec.present}/${rec.total}`;
          });
          const overallPct =
            totalConducted > 0 ? ((totalPresent / totalConducted) * 100).toFixed(2) : '100.00';
          rows.push([
            s.roll,
            s.name,
            s.dept || 'ICT Sem 3',
            ...subjectCols,
            totalPresent,
            totalConducted,
            `${overallPct}%`,
            Number(overallPct) >= 75 ? 'ELIGIBLE (>=75%)' : 'DEFAULTER (<75%)'
          ]);
        });

        triggerCsvDownload(rows, 'MU_ICT_All_Student_Classes_Attendance_Report.csv');
      };

      const handleDownloadRecordedSessionReport = (rec, e) => {
        if (e) e.stopPropagation();
        if (!rec) return;
        const rows = [
          ['Recorded Session ID', rec.id],
          ['Subject', rec.subject],
          ['Faculty', rec.facultyName],
          ['Date', rec.date],
          ['Session Time', `${rec.startTime} - ${rec.endTime}`],
          ['Present Count', rec.presentCount],
          ['Absent Count', rec.absentCount],
          ['Total Students', rec.totalStudents],
          [],
          ['Roll Number', 'Student Name', 'Status', 'Verification Source', 'Timestamp']
        ];

        rec.students.forEach((st) => {
          rows.push([st.roll, st.name, st.status, st.source, st.time]);
        });

        const safeDate = String(rec.date || 'Session').replace(/[^a-zA-Z0-9_-]/g, '_');
        triggerCsvDownload(rows, `Recorded_Session_${rec.subject}_${safeDate}_${rec.id}.csv`);
      };

      const handleToggleStudentStatusInRecord = (recordId, studentId, newStatus) => {
        const targetRecord = classSessionRecords.find((r) => r.id === recordId);
        if (!targetRecord) return;
        const targetStudent = targetRecord.students.find((st) => st.id === studentId);
        if (!targetStudent || targetStudent.status === newStatus) return;

        const subj = targetRecord.subject || facultyUser.subject || 'PWP';
        const deltaPresent = newStatus === 'Present' ? 1 : -1;

        setClassSessionRecords((prev) =>
          prev.map((rec) => {
            if (rec.id !== recordId) return rec;
            const updatedStudents = rec.students.map((st) =>
              st.id === studentId
                ? {
                    ...st,
                    status: newStatus,
                    source: newStatus === 'Present' ? 'Faculty Record Edit (Present)' : 'Faculty Record Edit (Absent)',
                    time:
                      newStatus === 'Present'
                        ? st.time && st.time !== '-'
                          ? st.time
                          : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                        : '-'
                  }
                : st
            );
            const newPresentCount = updatedStudents.filter((st) => st.status === 'Present').length;
            const newAbsentCount = updatedStudents.length - newPresentCount;
            return {
              ...rec,
              presentCount: newPresentCount,
              absentCount: newAbsentCount,
              students: updatedStudents
            };
          })
        );

        setAttendance((prev) => {
          const stuAtt = prev[studentId] || { [subj]: { present: 0, total: 1 } };
          const subRec = stuAtt[subj] || { present: 0, total: 1 };
          const adjustedPresent = Math.max(0, Math.min(subRec.total, subRec.present + deltaPresent));
          return {
            ...prev,
            [studentId]: {
              ...stuAtt,
              [subj]: {
                present: adjustedPresent,
                total: subRec.total
              }
            }
          };
        });

        setUpdateBanner(`Updated ${targetStudent.name} (${targetStudent.roll}) to ${newStatus.toUpperCase()} in ${subj} session record.`);
        setTimeout(() => setUpdateBanner(''), 3000);
      };

      const handleMasterAttendanceAdjust = (studentId, deltaPresent, deltaTotal) => {
        const subj = masterSubjectFilter;
        const stuObj = students.find((s) => s.id === studentId);
        setAttendance((prev) => {
          const stuAtt = prev[studentId] || { [subj]: { present: 0, total: 0 } };
          const cur = stuAtt[subj] || { present: 0, total: 0 };
          const nextTotal = Math.max(0, cur.total + deltaTotal);
          const nextPresent = Math.max(0, Math.min(nextTotal, cur.present + deltaPresent));
          return {
            ...prev,
            [studentId]: {
              ...stuAtt,
              [subj]: {
                present: nextPresent,
                total: nextTotal
              }
            }
          };
        });
        if (stuObj) {
          setUpdateBanner(
            `Updated ${stuObj.name}'s ${subj} attendance (${deltaPresent > 0 ? '+1 Present' : '+1 Absent'}).`
          );
          setTimeout(() => setUpdateBanner(''), 2500);
        }
      };

      return (
        <div className="space-y-6 text-xs">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-white uppercase tracking-wider">Recorded Sessions & Student Attendance List</h2>
              <p className="text-slate-400">
                Download overall student classes attendance report with percentage or download & edit any recorded session report
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={handleDownloadAllClassesReport}
                className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold flex items-center gap-1.5 shadow-lg shadow-emerald-600/25 cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" /> Download All Classes Attendance Report (%)
              </button>
              <button
                type="button"
                onClick={onBackToLive}
                className="px-3.5 py-2 bg-[#5852f2] hover:bg-indigo-600 text-white rounded-xl font-bold flex items-center gap-1.5 shadow-lg shadow-indigo-600/25 cursor-pointer"
              >
                <Video className="w-3.5 h-3.5" /> Go to Live Attendance Engine
              </button>
            </div>
          </div>

          {updateBanner && (
            <div className="p-3 rounded-xl bg-emerald-950/90 border border-emerald-700 text-emerald-300 font-bold flex items-center gap-2">
              <CheckCircle className="w-4 h-4 shrink-0" />
              <span>{updateBanner}</span>
            </div>
          )}

          {/* ALL STUDENT CLASSES ATTENDANCE REPORT WITH ATTENDANCE PERCENTAGE (ABOVE RECORDED SESSIONS) */}
          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-5 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-emerald-400" /> All Student Classes Attendance Report (With Attendance %)
                </h3>
                <p className="text-[11px] text-slate-400">
                  Cumulative attendance across all subjects (PWP, DMGT, COA, DSC) and overall attendance percentage
                </p>
              </div>
              <button
                type="button"
                onClick={handleDownloadAllClassesReport}
                className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold text-[11px] flex items-center gap-1.5 cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" /> Download CSV Report
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#06080e] text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="p-3">STUDENT</th>
                    <th className="p-3">ROLL NO</th>
                    <th className="p-3">PWP</th>
                    <th className="p-3">DMGT</th>
                    <th className="p-3">COA</th>
                    <th className="p-3">DSC</th>
                    <th className="p-3">TOTAL CLASSES</th>
                    <th className="p-3">ATTENDANCE %</th>
                    <th className="p-3 text-right">STATUS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {students.map((s) => {
                    const stuAtt = attendance[s.id] || {};
                    let totPresent = 0;
                    let totConducted = 0;
                    subjectsList.forEach((sub) => {
                      const rec = stuAtt[sub] || { present: 0, total: 0 };
                      totPresent += rec.present;
                      totConducted += rec.total;
                    });
                    const overallPct =
                      totConducted > 0 ? Math.round((totPresent / totConducted) * 1000) / 10 : 100;

                    return (
                      <tr key={s.id} className="hover:bg-slate-800/20">
                        <td className="p-3 flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-full bg-slate-800 overflow-hidden border border-slate-700 flex items-center justify-center font-bold text-slate-300 shrink-0">
                            {s.photo ? <img src={s.photo} alt={s.name} className="w-full h-full object-cover" /> : s.name.charAt(0)}
                          </div>
                          <span className="font-semibold text-white">{s.name}</span>
                        </td>
                        <td className="p-3 font-mono text-slate-400">{s.roll}</td>
                        {subjectsList.map((sub) => {
                          const rec = stuAtt[sub] || { present: 0, total: 0 };
                          return (
                            <td key={sub} className="p-3 font-mono text-slate-300">
                              {rec.present}/{rec.total}
                            </td>
                          );
                        })}
                        <td className="p-3 font-mono text-slate-200 font-semibold">
                          {totPresent} / {totConducted}
                        </td>
                        <td className="p-3 font-mono">
                          <span className={`font-extrabold ${overallPct < 75 ? 'text-red-400' : 'text-emerald-400'}`}>
                            {overallPct}%
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <span
                            className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                              overallPct >= 75
                                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                : 'bg-red-950 text-red-400 border border-red-800'
                            }`}
                          >
                            {overallPct >= 75 ? 'ELIGIBLE' : 'DEFAULTER'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* RECORDED SESSIONS & SESSION STUDENT LIST */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <div className="lg:col-span-5 bg-[#0e1422] border border-slate-800 rounded-2xl p-5 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Clock className="w-4 h-4 text-indigo-400" /> Recorded Sessions ({classSessionRecords.length})
                </h3>
              </div>

              {classSessionRecords.length === 0 ? (
                <div className="p-4 rounded-xl bg-[#070a12] border border-slate-800 text-slate-400 text-center space-y-2">
                  <p>No recorded sessions saved yet.</p>
                  <button
                    type="button"
                    onClick={onBackToLive}
                    className="px-3 py-1.5 bg-indigo-600 text-white rounded-lg font-bold text-[11px] cursor-pointer"
                  >
                    Start a Live Session
                  </button>
                </div>
              ) : (
                <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
                  {classSessionRecords.map((rec) => {
                    const isSelected = rec.id === activeRecord?.id;
                    return (
                      <div
                        key={rec.id}
                        onClick={() => setSelectedRecordId(rec.id)}
                        className={`w-full text-left p-4 rounded-xl border transition cursor-pointer space-y-2 ${
                          isSelected
                            ? 'bg-indigo-950/50 border-indigo-500 shadow-lg shadow-indigo-600/15'
                            : 'bg-[#070a12] border-slate-800 hover:border-slate-700'
                        }`}
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <span className="px-2.5 py-0.5 rounded bg-indigo-950 border border-indigo-800 text-indigo-300 font-bold text-[10px]">
                            {rec.subject}
                          </span>
                          <span className="font-mono text-[11px] text-cyan-300 font-semibold">
                            {rec.date} • {rec.startTime} to {rec.endTime}
                          </span>
                        </div>
                        <div className="font-bold text-white text-xs">
                          <span className="text-emerald-400">{rec.presentCount} Present</span> •{' '}
                          <span className="text-red-400">{rec.absentCount} Absent</span>{' '}
                          <span className="text-slate-400 font-normal">({rec.totalStudents} Total)</span>
                        </div>
                        <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                          <span className="text-[10px] text-slate-500">
                            Faculty: {rec.facultyName}
                          </span>
                          <button
                            type="button"
                            onClick={(e) => handleDownloadRecordedSessionReport(rec, e)}
                            className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-[10px] font-bold flex items-center gap-1 cursor-pointer"
                          >
                            <Download className="w-3 h-3" /> Download Report
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="lg:col-span-7 bg-[#0e1422] border border-slate-800 rounded-2xl p-5 space-y-4">
              {activeRecord ? (
                <>
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                    <div>
                      <h3 className="text-sm font-bold text-white flex items-center gap-2">
                        <Users className="w-4 h-4 text-cyan-400" /> Session Student List — {activeRecord.subject}
                      </h3>
                      <p className="text-[11px] text-slate-400 font-mono">
                        {activeRecord.date} • {activeRecord.startTime} to {activeRecord.endTime} •{' '}
                        <span className="text-emerald-400 font-bold">{activeRecord.presentCount} Present</span> /{' '}
                        <span className="text-red-400 font-bold">{activeRecord.absentCount} Absent</span>
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => handleDownloadRecordedSessionReport(activeRecord, e)}
                      className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-[11px] flex items-center gap-1.5 cursor-pointer"
                    >
                      <Download className="w-3.5 h-3.5" /> Download Session Report (CSV)
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-[#06080e] text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="p-3">STUDENT</th>
                          <th className="p-3">ROLL NO</th>
                          <th className="p-3">RECORDED STATUS</th>
                          <th className="p-3">TIME / METHOD</th>
                          <th className="p-3 text-right">CHANGE ATTENDANCE</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {activeRecord.students.map((st) => {
                          const userProfile = students.find((u) => u.id === st.id);
                          const isPresent = st.status === 'Present';
                          return (
                            <tr key={st.id} className="hover:bg-slate-800/20">
                              <td className="p-3 flex items-center gap-2.5">
                                <div className="w-7 h-7 rounded-full bg-slate-800 overflow-hidden border border-slate-700 flex items-center justify-center font-bold text-slate-300 shrink-0">
                                  {userProfile?.photo ? (
                                    <img src={userProfile.photo} alt={st.name} className="w-full h-full object-cover" />
                                  ) : (
                                    st.name.charAt(0)
                                  )}
                                </div>
                                <span className="font-semibold text-white">{st.name}</span>
                              </td>
                              <td className="p-3 font-mono text-slate-400">{st.roll}</td>
                              <td className="p-3">
                                <span
                                  className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                                    isPresent
                                      ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                      : 'bg-red-950 text-red-400 border border-red-800'
                                  }`}
                                >
                                  {st.status.toUpperCase()}
                                </span>
                              </td>
                              <td className="p-3 text-[10px] font-mono text-slate-400">
                                {st.time} • {st.source}
                              </td>
                              <td className="p-3 text-right">
                                <div className="inline-flex gap-1.5">
                                  <button
                                    type="button"
                                    onClick={() => handleToggleStudentStatusInRecord(activeRecord.id, st.id, 'Present')}
                                    className={`px-2.5 py-1 rounded-lg text-[11px] font-bold cursor-pointer ${
                                      isPresent
                                        ? 'bg-emerald-600 text-white shadow'
                                        : 'bg-slate-800 hover:bg-emerald-700 text-slate-300 hover:text-white'
                                    }`}
                                  >
                                    Present
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => handleToggleStudentStatusInRecord(activeRecord.id, st.id, 'Absent')}
                                    className={`px-2.5 py-1 rounded-lg text-[11px] font-bold cursor-pointer ${
                                      !isPresent
                                        ? 'bg-red-600 text-white shadow'
                                        : 'bg-slate-800 hover:bg-red-700 text-slate-300 hover:text-white'
                                    }`}
                                  >
                                    Absent
                                  </button>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </>
              ) : (
                <div className="p-8 text-center text-slate-400">
                  Select a recorded session on the left to view and edit its student list.
                </div>
              )}
            </div>
          </div>

          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <UserCheck className="w-4 h-4 text-emerald-400" /> Master Student Attendance List ({masterSubjectFilter})
                </h3>
                <p className="text-[11px] text-slate-400">
                  Review overall student attendance percentages or adjust cumulative Present / Absent counts directly
                </p>
              </div>
              <div className="flex items-center gap-2">
                <label className="text-slate-400 text-[11px]">Subject:</label>
                <select
                  value={masterSubjectFilter}
                  onChange={(e) => setMasterSubjectFilter(e.target.value)}
                  className="px-3 py-1.5 bg-[#070a12] border border-slate-800 rounded-xl text-white font-bold"
                >
                  <option value="PWP">PWP</option>
                  <option value="DMGT">DMGT</option>
                  <option value="COA">COA</option>
                  <option value="DSC">DSC</option>
                </select>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#06080e] text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="p-3">STUDENT</th>
                    <th className="p-3">ROLL NO</th>
                    <th className="p-3">ATTENDED / TOTAL</th>
                    <th className="p-3">ATTENDANCE %</th>
                    <th className="p-3 text-right">ADJUST ATTENDANCE</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {students.map((s) => {
                    const rec = attendance[s.id]?.[masterSubjectFilter] || { present: 0, total: 0 };
                    const pct = rec.total > 0 ? Math.round((rec.present / rec.total) * 100) : 100;
                    return (
                      <tr key={s.id} className="hover:bg-slate-800/20">
                        <td className="p-3 flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-slate-800 overflow-hidden border border-slate-700 flex items-center justify-center font-bold text-slate-300">
                            {s.photo ? <img src={s.photo} alt={s.name} className="w-full h-full object-cover" /> : s.name.charAt(0)}
                          </div>
                          <span className="font-semibold text-white">{s.name}</span>
                        </td>
                        <td className="p-3 font-mono text-slate-400">{s.roll}</td>
                        <td className="p-3 font-mono text-slate-200">
                          {rec.present} / {rec.total} Sessions
                        </td>
                        <td className="p-3 font-mono">
                          <span className={`font-bold ${pct < 75 ? 'text-red-400' : 'text-emerald-400'}`}>{pct}%</span>
                        </td>
                        <td className="p-3 text-right">
                          <div className="inline-flex gap-2">
                            <button
                              type="button"
                              onClick={() => handleMasterAttendanceAdjust(s.id, 1, 1)}
                              className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-[11px] cursor-pointer"
                            >
                              + Present
                            </button>
                            <button
                              type="button"
                              onClick={() => handleMasterAttendanceAdjust(s.id, 0, 1)}
                              className="px-3 py-1.5 bg-red-600/80 hover:bg-red-600 text-white font-bold rounded-lg text-[11px] cursor-pointer"
                            >
                              + Absent
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      );
    }

    function FacultyUpdatesManager({ facultyUser, campusUpdates, setCampusUpdates }) {
      const [category, setCategory] = useState('Assignment');
      const [subject, setSubject] = useState(facultyUser.subject || 'PWP');
      const [title, setTitle] = useState('');
      const [date, setDate] = useState('2026-11-25');
      const [details, setDetails] = useState('');

      const handlePublish = (e) => {
        e.preventDefault();
        if (!title.trim()) return;
        const newEntry = {
          id: 'UPD-' + Math.floor(100 + Math.random() * 900),
          category,
          subject: category === 'Holiday' ? 'ALL' : subject,
          title: title.trim(),
          date,
          details: details.trim() || 'Published by ' + facultyUser.name,
          postedBy: facultyUser.name
        };
        setCampusUpdates([newEntry, ...campusUpdates]);
        setTitle('');
        setDetails('');
      };

      const handleDeleteUpdate = (id) => {
        setCampusUpdates((prev) => prev.filter((item) => item.id !== id));
      };

      return (
        <div className="space-y-6 text-xs">
          <div>
            <h2 className="text-base font-bold text-white uppercase tracking-wider">Assignments, Holidays & Campus Events</h2>
            <p className="text-slate-400">Publish new assignments, university holidays, or ICT events directly to the Student Dashboard</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <form onSubmit={handlePublish} className="bg-[#0e1422] border border-slate-800 rounded-2xl p-6 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Plus className="w-4 h-4 text-indigo-400" /> Add New Student Update
              </h3>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Update Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full p-2.5 bg-[#070a12] border border-slate-800 rounded-xl text-white font-semibold"
                  >
                    <option value="Assignment">Assignment</option>
                    <option value="Holiday">Holiday</option>
                    <option value="Event">Campus / Dept Event</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Subject / Scope</label>
                  <select
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    disabled={category === 'Holiday'}
                    className="w-full p-2.5 bg-[#070a12] border border-slate-800 rounded-xl text-white font-semibold disabled:opacity-50"
                  >
                    <option value="PWP">PWP</option>
                    <option value="DMGT">DMGT</option>
                    <option value="COA">COA</option>
                    <option value="DSC">DSC</option>
                    <option value="ICT Dept">ICT Department</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Unit 4 Graph Theory Problem Set / TechFest 2026"
                  className="w-full p-3 bg-[#070a12] border border-slate-800 rounded-xl text-white"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Date / Due Date</label>
                <input
                  type="date"
                  required
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  className="w-full p-3 bg-[#070a12] border border-slate-800 rounded-xl text-white font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Description & Instructions</label>
                <textarea
                  rows="3"
                  value={details}
                  onChange={(e) => setDetails(e.target.value)}
                  placeholder="Enter instructions, venue, or holiday notice details..."
                  className="w-full p-3 bg-[#070a12] border border-slate-800 rounded-xl text-white"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3 bg-[#5852f2] hover:bg-indigo-600 text-white font-bold rounded-xl shadow-lg shadow-indigo-600/30 cursor-pointer"
              >
                Publish to Student Dashboard
              </button>
            </form>

            <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-6 space-y-3">
              <h3 className="text-sm font-bold text-white">Published Items ({campusUpdates.length})</h3>
              <div className="space-y-2.5 max-h-[420px] overflow-y-auto pr-1">
                {campusUpdates.map((item) => (
                  <div key={item.id} className="p-3.5 bg-[#070a12] border border-slate-800 rounded-xl flex items-start justify-between gap-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            item.category === 'Assignment'
                              ? 'bg-indigo-950 text-indigo-300 border border-indigo-800'
                              : item.category === 'Holiday'
                              ? 'bg-amber-950 text-amber-300 border border-amber-800'
                              : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          }`}
                        >
                          {item.category.toUpperCase()}
                        </span>
                        <span className="text-[10px] font-mono text-slate-400">{item.date}</span>
                      </div>
                      <div className="font-bold text-white text-xs">{item.title}</div>
                      <p className="text-[11px] text-slate-400">{item.details}</p>
                      <div className="text-[10px] text-slate-500">Posted by {item.postedBy}</div>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleDeleteUpdate(item.id)}
                      className="p-1.5 bg-red-950/70 hover:bg-red-900 border border-red-800/80 text-red-300 rounded-lg cursor-pointer"
                      title="Remove item"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      );
    }

    function FacultyGradeEntry({ users, results, setResults }) {
      const [savedBanner, setSavedBanner] = useState(false);

      const handleGradeChange = (studentId, field, value) => {
        setResults((prev) => {
          const cur = prev[studentId] || { sgpa: { 'Sem 1': 8.0, 'Sem 2': 8.0, 'Sem 3': 8.0 }, cgpa: 8.0, backlogs: 0, subjects: {} };
          if (field === 'sem3') {
            return { ...prev, [studentId]: { ...cur, sgpa: { ...cur.sgpa, 'Sem 3': Number(value) } } };
          }
          if (field === 'cgpa') {
            return { ...prev, [studentId]: { ...cur, cgpa: Number(value) } };
          }
          return { ...prev, [studentId]: { ...cur, backlogs: Number(value) } };
        });
        setSavedBanner(true);
        setTimeout(() => setSavedBanner(false), 2000);
      };

      return (
        <div className="space-y-4 text-xs">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white uppercase tracking-wider">Grade & Result Entry</h2>
            {savedBanner && <span className="text-emerald-400 font-bold">✓ Synced to Student Transcripts</span>}
          </div>
          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-4 overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-[#06080e] text-slate-400">
                <tr>
                  <th className="p-3">STUDENT</th>
                  <th className="p-3">SGPA (SEM 3)</th>
                  <th className="p-3">CGPA</th>
                  <th className="p-3">ACTIVE BACKLOGS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {users
                  .filter((u) => u.role === 'student')
                  .map((s) => (
                    <tr key={s.id}>
                      <td className="p-3 font-semibold text-white">{s.name}</td>
                      <td className="p-3 font-mono">
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          max="10"
                          value={results[s.id]?.sgpa['Sem 3'] ?? 8.5}
                          onChange={(e) => handleGradeChange(s.id, 'sem3', e.target.value)}
                          className="w-20 p-1.5 bg-[#070a12] border border-slate-700 rounded-lg text-cyan-400 font-bold"
                        />
                      </td>
                      <td className="p-3 font-mono">
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          max="10"
                          value={results[s.id]?.cgpa ?? 8.5}
                          onChange={(e) => handleGradeChange(s.id, 'cgpa', e.target.value)}
                          className="w-20 p-1.5 bg-[#070a12] border border-slate-700 rounded-lg text-emerald-400 font-bold"
                        />
                      </td>
                      <td className="p-3 font-mono">
                        <input
                          type="number"
                          min="0"
                          max="10"
                          value={results[s.id]?.backlogs ?? 0}
                          onChange={(e) => handleGradeChange(s.id, 'backlogs', e.target.value)}
                          className="w-16 p-1.5 bg-[#070a12] border border-slate-700 rounded-lg text-amber-400 font-bold"
                        />
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    function FacultyLiveQuizPoll({ livePoll, setLivePoll }) {
      const [question, setQuestion] = useState('What is the average time complexity of searching in a Binary Search Tree?');
      const [optionsText, setOptionsText] = useState('O(log n), O(n^2), O(1), O(n!)');

      const handleLaunch = () => {
        const opts = optionsText.split(',').map((o) => o.trim()).filter(Boolean);
        if (!question.trim() || opts.length < 2) return;
        setLivePoll({
          id: Date.now(),
          question: question.trim(),
          options: opts,
          votes: {}
        });
      };

      const totalVotes = livePoll ? Object.keys(livePoll.votes || {}).length : 0;

      return (
        <div className="space-y-4 text-xs max-w-lg">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">Live Class 1-Min Quiz Runner</h2>
          <div className="bg-[#0e1422] border border-slate-800 p-5 rounded-2xl space-y-3">
            <div>
              <label className="text-slate-400 block mb-1">Quiz Question:</label>
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="w-full p-2.5 bg-[#070a12] border border-slate-800 rounded-xl text-white"
              />
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Options (comma-separated):</label>
              <input
                type="text"
                value={optionsText}
                onChange={(e) => setOptionsText(e.target.value)}
                className="w-full p-2.5 bg-[#070a12] border border-slate-800 rounded-xl text-white"
              />
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleLaunch}
                className="flex-1 py-2.5 bg-[#5852f2] hover:bg-indigo-600 text-white font-bold rounded-xl cursor-pointer"
              >
                Launch Live Poll to Students
              </button>
              {livePoll && (
                <button
                  type="button"
                  onClick={() => setLivePoll(null)}
                  className="px-4 py-2.5 bg-slate-800 text-slate-300 font-bold rounded-xl cursor-pointer"
                >
                  End Poll
                </button>
              )}
            </div>

            {livePoll && (
              <div className="pt-3 border-t border-slate-800 space-y-2">
                <div className="font-bold text-emerald-400">Live Responses ({totalVotes} votes):</div>
                {livePoll.options.map((opt, idx) => {
                  const count = Object.values(livePoll.votes || {}).filter((v) => v === idx).length;
                  const pct = totalVotes > 0 ? Math.round((count / totalVotes) * 100) : 0;
                  return (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-200">{opt}</span>
                        <span className="font-mono text-indigo-300">{count} ({pct}%)</span>
                      </div>
                      <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                        <div className="h-full bg-indigo-500" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      );
    }

    function FacultyPlagiarismCheck() {
      return (
        <div className="space-y-4 text-xs">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">Assignment Plagiarism & Similarity Checker</h2>
          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-4 space-y-2">
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl flex justify-between items-center">
              <div>
                <div className="font-bold text-white">Django REST API Microservices</div>
                <div className="text-[11px] text-slate-400">38 Student Submissions Processed</div>
              </div>
              <span className="px-2.5 py-1 bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono rounded-lg">12% Low Risk</span>
            </div>
          </div>
        </div>
      );
    }

    function FacultyMassAlerts({ attendance, users }) {
      const [sent, setSent] = useState(false);
      return (
        <div className="space-y-4 text-xs">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">Low Attendance Mass Alerts</h2>
          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-4">
            <button
              type="button"
              onClick={() => setSent(true)}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl cursor-pointer"
            >
              {sent ? '✓ Alerts Sent to Defaulters (<75%)' : 'Send Alert Reminders to All Defaulters (<75%)'}
            </button>
          </div>
        </div>
      );
    }

    // =========================================================================
    // 14. STUDENT PORTAL COMPONENTS
    // =========================================================================
    function StudentDashboardOverview({
      studentUser,
      attendance,
      results,
      campusUpdates,
      studentSessionMarks,
      livePoll,
      setLivePoll,
      onNavigate
    }) {
      const subjects = attendance
        ? Object.entries(attendance)
        : [
            ['PWP', { present: 28, total: 30 }],
            ['DMGT', { present: 25, total: 28 }],
            ['COA', { present: 26, total: 26 }],
            ['DSC', { present: 24, total: 27 }]
          ];

      const totalPresent = subjects.reduce((acc, [, d]) => acc + d.present, 0);
      const totalSessions = subjects.reduce((acc, [, d]) => acc + d.total, 0);
      const overallPct = totalSessions > 0 ? Math.round((totalPresent / totalSessions) * 1000) / 10 : 100;
      const safeMisses = Math.max(0, Math.floor(totalPresent / 0.75 - totalSessions));
      const requiredClasses = overallPct < 75 ? Math.ceil((0.75 * totalSessions - totalPresent) / 0.25) : 0;

      const assignmentCount = campusUpdates.filter((u) => u.category === 'Assignment').length;
      const holidayEventCount = campusUpdates.filter((u) => u.category !== 'Assignment').length;

      const handleVote = (optionIdx) => {
        if (!livePoll) return;
        setLivePoll({
          ...livePoll,
          votes: { ...(livePoll.votes || {}), [studentUser.id]: optionIdx }
        });
      };

      return (
        <div className="space-y-6 text-xs">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-white uppercase tracking-wider">Student Dashboard</h2>
              <p className="text-slate-400">
                Welcome back, <strong className="text-white">{studentUser.name}</strong> ({studentUser.roll} • {studentUser.dept})
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={() => onNavigate('scan')}
                className="px-4 py-2 bg-[#5852f2] hover:bg-indigo-600 text-white font-bold rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-600/30 cursor-pointer"
              >
                <QrCode className="w-4 h-4" /> Scan Live Faculty QR
              </button>
            </div>
          </div>

          {livePoll && (
            <div className="bg-indigo-950/50 border border-indigo-600/60 rounded-2xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-indigo-300 uppercase text-[11px]">Live Class Quiz Poll</span>
                <span className="text-[10px] font-mono text-emerald-400">Active Now</span>
              </div>
              <div className="font-bold text-white text-sm">{livePoll.question}</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {livePoll.options.map((opt, idx) => {
                  const chosen = livePoll.votes?.[studentUser.id] === idx;
                  return (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleVote(idx)}
                      className={`p-2.5 rounded-xl border text-left font-semibold cursor-pointer ${
                        chosen
                          ? 'bg-indigo-600 border-indigo-400 text-white'
                          : 'bg-[#070a12] border-slate-800 text-slate-300 hover:border-indigo-500'
                      }`}
                    >
                      {opt} {chosen && '✓'}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="bg-[#0e1422] border border-slate-800 p-4 rounded-2xl">
              <div className="text-slate-400 font-semibold">Overall Attendance</div>
              <div className={`text-2xl font-extrabold mt-1 ${overallPct < 75 ? 'text-red-400' : 'text-emerald-400'}`}>
                {overallPct}%
              </div>
              <div className="text-[10px] text-slate-500 mt-1">
                {totalPresent} / {totalSessions} Sessions Attended
              </div>
            </div>

            <div className="bg-[#0e1422] border border-slate-800 p-4 rounded-2xl">
              <div className="text-slate-400 font-semibold">Current CGPA</div>
              <div className="text-2xl font-extrabold text-cyan-400 mt-1">{results?.cgpa || '8.63'}</div>
              <div className="text-[10px] text-slate-500 mt-1">Active Backlogs: {results?.backlogs ?? 0}</div>
            </div>

            <div className="bg-[#0e1422] border border-slate-800 p-4 rounded-2xl">
              <div className="text-slate-400 font-semibold">Pending Assignments</div>
              <div className="text-2xl font-extrabold text-indigo-400 mt-1">{assignmentCount}</div>
              <button
                type="button"
                onClick={() => onNavigate('assignments')}
                className="text-[10px] text-indigo-300 hover:underline mt-1 cursor-pointer"
              >
                Open Assignments Hub →
              </button>
            </div>

            <div className="bg-[#0e1422] border border-slate-800 p-4 rounded-2xl">
              <div className="text-slate-400 font-semibold">Holidays & Events</div>
              <div className="text-2xl font-extrabold text-amber-400 mt-1">{holidayEventCount}</div>
              <button
                type="button"
                onClick={() => onNavigate('holidays-events')}
                className="text-[10px] text-amber-300 hover:underline mt-1 cursor-pointer"
              >
                View Calendar Notices →
              </button>
            </div>
          </div>

          <div
            className={`p-4 rounded-2xl border flex items-center justify-between gap-3 ${
              overallPct >= 75
                ? 'bg-emerald-950/40 border-emerald-800/80 text-emerald-300'
                : 'bg-red-950/40 border-red-800/80 text-red-300'
            }`}
          >
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5 shrink-0" />
              <div>
                <div className="font-bold">AI Attendance Defaulter Guard</div>
                <div className="text-[11px] opacity-90">
                  {overallPct >= 75
                    ? `Safe Zone: You can safely miss ${safeMisses} more sessions while staying above the mandatory 75% threshold.`
                    : `Defaulter Warning: Attend the next ${requiredClasses} consecutive classes to recover above 75%.`}
                </div>
              </div>
            </div>
            {studentSessionMarks[studentUser.id]?.status === 'Marked as Present' && (
              <span className="px-3 py-1 bg-emerald-600 text-white font-bold rounded-xl text-[10px] shrink-0">
                Today's Session: PRESENT
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-5 space-y-3">
              <h3 className="text-sm font-bold text-white">Subject-Wise Attendance</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {subjects.map(([subj, data]) => {
                  const pct = data.total > 0 ? Math.round((data.present / data.total) * 100) : 100;
                  return (
                    <div key={subj} className="p-3.5 bg-[#070a12] border border-slate-800 rounded-xl flex items-center justify-between">
                      <div>
                        <div className="font-bold text-white">{subj}</div>
                        <div className="text-[11px] text-slate-400">
                          {data.present} / {data.total} Sessions
                        </div>
                      </div>
                      <span className={`text-sm font-extrabold font-mono ${pct < 75 ? 'text-red-400' : 'text-cyan-400'}`}>
                        {pct}%
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Latest Faculty Updates</h3>
                <button
                  type="button"
                  onClick={() => onNavigate('holidays-events')}
                  className="text-[11px] text-indigo-400 hover:underline cursor-pointer"
                >
                  View All
                </button>
              </div>
              <div className="space-y-2.5">
                {campusUpdates.slice(0, 3).map((item) => (
                  <div key={item.id} className="p-3 bg-[#070a12] border border-slate-800 rounded-xl space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-indigo-300 uppercase">{item.category}</span>
                      <span className="text-[10px] font-mono text-slate-500">{item.date}</span>
                    </div>
                    <div className="font-bold text-white">{item.title}</div>
                    <div className="text-[10px] text-slate-400">By {item.postedBy}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      );
    }

    function StudentQrScanner({
      studentUser,
      users,
      activeQrSession,
      usedQrTokensByStudent,
      setUsedQrTokensByStudent,
      setAttendance,
      setMismatchLogs,
      setStudentSessionMarks
    }) {
      const [selectedSubject, setSelectedSubject] = useState('PWP');
      const [scanResult, setScanResult] = useState(null);
      const [isAutoScanning, setIsAutoScanning] = useState(true);
      const [scanStatusHint, setScanStatusHint] = useState('Align Faculty QR code inside frame...');
      const videoRef = useRef(null);
      const qrFileInputRef = useRef(null);
      const isDecodingRef = useRef(false);

      const {
        facingMode,
        devices,
        cameraActive,
        cameraLoading,
        cameraError,
        activeLabel,
        resolutionText,
        isMirrored,
        fitMode,
        toggleFitMode,
        selectFrontCamera,
        selectBackCamera,
        cycleNextCamera,
        retryCamera
      } = useReliableCamera({
        videoRef,
        initialFacingMode: 'environment',
        enabled: !scanResult
      });

      const activeFaculty = users.find((u) => u.role === 'faculty' && u.subject === selectedSubject) || users.find((u) => u.role === 'faculty');

      useEffect(() => {
        setScanResult(null);
        setIsAutoScanning(true);
        setScanStatusHint('Align Faculty QR code inside frame...');
      }, [studentUser.id]);

      const markPresentForClassQr = (scannedToken, qrSubject) => {
        const subjectToMark = qrSubject || selectedSubject;
        const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        setUsedQrTokensByStudent((prev) => {
          const prevList = prev[studentUser.id] || [];
          return {
            ...prev,
            [studentUser.id]: Array.from(new Set([...prevList, scannedToken]))
          };
        });

        setAttendance((prev) => {
          const stu = prev[studentUser.id] || { [subjectToMark]: { present: 0, total: 0 } };
          const sub = stu[subjectToMark] || { present: 0, total: 0 };
          return {
            ...prev,
            [studentUser.id]: {
              ...stu,
              [subjectToMark]: {
                present: sub.present + 1,
                total: sub.total + 1
              }
            }
          };
        });

        setStudentSessionMarks((prev) => ({
          ...prev,
          [studentUser.id]: {
            status: 'Marked as Present',
            source: `Optical QR (${subjectToMark})`,
            time: nowTime
          }
        }));

        setIsAutoScanning(false);
        setScanResult({
          type: 'success',
          title: 'Marked as Present!',
          text: `QR Code Verified (${scannedToken})! ${studentUser.name} (${studentUser.roll}) is now Marked as Present for ${subjectToMark}.`
        });
      };

      const validateAndProcessDecodedQr = (rawText) => {
        if (!rawText) return;
        const trimmed = String(rawText).trim();

        if (!trimmed.startsWith('MU-CLASS-QR|')) {
          setIsAutoScanning(false);
          setScanResult({
            type: 'error',
            title: 'Invalid QR Code',
            text: 'Invalid QR Code — Unrecognized QR pattern. Please scan the live QR code shown by your faculty.'
          });
          setMismatchLogs((prev) => [
            ...prev,
            {
              student: `Invalid QR: ${studentUser.name} (${studentUser.roll}) scanned unrecognized QR`,
              time: new Date().toLocaleTimeString()
            }
          ]);
          return;
        }

        const parts = trimmed.split('|');
        const scannedToken = (parts[1] || '').trim();
        const qrSubject = (parts[2] || selectedSubject).trim();
        const validUntilMs = Number(parts[3] || 0);
        const nowMs = Date.now();

        const studentUsedList = usedQrTokensByStudent[studentUser.id] || [];
        if (studentUsedList.includes(scannedToken)) {
          setIsAutoScanning(false);
          setScanResult({
            type: 'error',
            title: 'Invalid QR Code',
            text: `Invalid QR Code — You have already scanned this QR code (${scannedToken}). Each QR pattern can only be used once per student.`
          });
          setMismatchLogs((prev) => [
            ...prev,
            {
              student: `Reused QR Blocked: ${studentUser.name} (${studentUser.roll}) re-scanned ${scannedToken}`,
              time: new Date().toLocaleTimeString()
            }
          ]);
          return;
        }

        const currentEpoch = Math.floor(nowMs / 30000);
        const currentEpochToken = computeRollingQrForEpoch(currentEpoch, activeQrSession.manualOffset).token;
        const gracePrevToken =
          nowMs % 30000 <= 2500
            ? computeRollingQrForEpoch(currentEpoch - 1, activeQrSession.manualOffset).token
            : null;

        const isPatternStillActive =
          scannedToken === activeQrSession.token ||
          scannedToken === currentEpochToken ||
          (gracePrevToken !== null && scannedToken === gracePrevToken) ||
          (validUntilMs > 0 && nowMs <= validUntilMs + 2500);

        if (!isPatternStillActive) {
          setIsAutoScanning(false);
          setScanResult({
            type: 'error',
            title: 'Invalid QR Code',
            text: 'Invalid QR Code — The QR code pattern changed before it was scanned. Please scan the faculty\'s new active QR code.'
          });
          setMismatchLogs((prev) => [
            ...prev,
            {
              student: `Expired QR Pattern: ${studentUser.name} (${studentUser.roll}) scanned outdated token (${scannedToken})`,
              time: new Date().toLocaleTimeString()
            }
          ]);
          return;
        }

        markPresentForClassQr(scannedToken, qrSubject);
      };

      const decodeFromCanvasOrVideo = async (sourceEl, isManualClick = false) => {
        if (isDecodingRef.current && !isManualClick) return;
        const w = sourceEl?.videoWidth || sourceEl?.naturalWidth || sourceEl?.width;
        const h = sourceEl?.videoHeight || sourceEl?.naturalHeight || sourceEl?.height;
        if (!w || !h) {
          if (isManualClick) {
            setScanResult({
              type: 'error',
              title: 'No Camera Feed',
              text: 'Camera feed is not ready. Please allow camera permissions or upload a QR screenshot.'
            });
          }
          return;
        }

        isDecodingRef.current = true;
        try {
          const canvas = document.createElement('canvas');
          canvas.width = w;
          canvas.height = h;
          const ctx = canvas.getContext('2d', { willReadFrequently: true });
          ctx.drawImage(sourceEl, 0, 0, w, h);
          const imgData = ctx.getImageData(0, 0, w, h);

          let sum = 0, min = 255, max = 0;
          for (let i = 0; i < imgData.data.length; i += 16) {
            const lum = 0.299 * imgData.data[i] + 0.587 * imgData.data[i + 1] + 0.114 * imgData.data[i + 2];
            sum += lum;
            if (lum < min) min = lum;
            if (lum > max) max = lum;
          }
          const avgLum = sum / (imgData.data.length / 16);
          const contrast = max - min;

          if (avgLum < 18 || contrast < 25) {
            setScanStatusHint('Camera covered / dark screen — point at Faculty QR');
            if (isManualClick) {
              setScanResult({
                type: 'error',
                title: 'No QR Code Detected',
                text: 'No QR Code Detected — Point camera at the Faculty\'s QR code screen.'
              });
            }
            return;
          }

          setScanStatusHint('Scanning live frame for QR pattern...');

          if ('BarcodeDetector' in window) {
            try {
              const detector = new window.BarcodeDetector({ formats: ['qr_code'] });
              const barcodes = await detector.detect(canvas);
              if (barcodes && barcodes.length > 0 && barcodes[0].rawValue) {
                validateAndProcessDecodedQr(barcodes[0].rawValue);
                return;
              }
            } catch (err) {}
          }

          if (window.jsQR) {
            const code = window.jsQR(imgData.data, w, h, { inversionAttempts: 'attemptBoth' });
            if (code && code.data) {
              validateAndProcessDecodedQr(code.data);
              return;
            }
          }

          if (isManualClick) {
            setScanResult({
              type: 'error',
              title: 'No QR Code Detected',
              text: 'No QR Code Detected — Point camera at the Faculty\'s QR code screen.'
            });
          }
        } finally {
          isDecodingRef.current = false;
        }
      };

      useEffect(() => {
        if (!isAutoScanning || scanResult) return;
        const interval = setInterval(() => {
          if (videoRef.current && videoRef.current.videoWidth > 0) {
            decodeFromCanvasOrVideo(videoRef.current, false);
          }
        }, 250);
        return () => clearInterval(interval);
      }, [isAutoScanning, scanResult, studentUser.id, selectedSubject, activeQrSession]);

      const handleQrImageUpload = (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
          const img = new Image();
          img.onload = () => decodeFromCanvasOrVideo(img, true);
          img.src = reader.result;
        };
        reader.readAsDataURL(file);
        e.target.value = '';
      };

      return (
        <div className="space-y-6 text-xs max-w-md mx-auto">
          <div className="text-center">
            <h2 className="text-base font-bold text-white uppercase tracking-wider">Scan Faculty Live QR Code</h2>
            <p className="text-slate-400 mt-0.5">
              Point your camera at the active QR code displayed by your teacher
            </p>
          </div>

          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-6 text-center space-y-4 shadow-2xl">
            <div className="flex items-center justify-between bg-[#070a12] border border-slate-800 p-3 rounded-xl text-left">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-indigo-600/30 border border-indigo-500/40 overflow-hidden flex items-center justify-center font-bold text-indigo-300">
                  {studentUser.photo ? (
                    <img src={studentUser.photo} alt={studentUser.name} className="w-full h-full object-cover" />
                  ) : (
                    studentUser.name.charAt(0)
                  )}
                </div>
                <div>
                  <div className="font-bold text-white text-xs">{studentUser.name}</div>
                  <div className="text-[10px] font-mono text-slate-400">Roll: {studentUser.roll}</div>
                </div>
              </div>
              <span className="px-2 py-1 bg-indigo-950 border border-indigo-800 text-indigo-300 rounded-lg text-[10px] font-bold">
                Scanner Ready
              </span>
            </div>

            <div className="text-left">
              <label className="text-slate-400 text-[10px] block mb-1">Active Subject & Faculty:</label>
              <select
                value={selectedSubject}
                onChange={(e) => {
                  setSelectedSubject(e.target.value);
                  setScanResult(null);
                  setIsAutoScanning(true);
                }}
                className="w-full p-2.5 bg-[#070a12] border border-slate-800 rounded-xl text-white font-semibold"
              >
                <option value="PWP">PWP — Prof. R. K. Sharma / Kawal Kaur</option>
                <option value="DMGT">DMGT — Prof. Biswajit</option>
                <option value="COA">COA — Prof. Vijay Dubey</option>
                <option value="DSC">DSC — Prof. Alam</option>
              </select>
            </div>

            <input
              ref={qrFileInputRef}
              type="file"
              accept="image/*"
              onChange={handleQrImageUpload}
              className="hidden"
            />

            <div className="relative aspect-[4/3] sm:aspect-video max-h-[380px] w-full bg-black rounded-2xl border border-slate-800 overflow-hidden flex items-center justify-center">
              {!scanResult ? (
                <>
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className={`w-full h-full ${fitMode === 'contain' ? 'object-contain' : 'object-cover'} ${isMirrored ? 'scale-x-[-1]' : ''}`}
                  />
                  {cameraActive && (
                    <div className="absolute inset-6 border-2 border-dashed border-indigo-500 rounded-2xl pointer-events-none animate-pulse" />
                  )}
                  <div className="absolute top-2.5 left-2.5 px-2.5 py-1 bg-slate-900/90 border border-slate-700 rounded-lg text-[10px] font-mono text-indigo-300 z-10">
                    {activeFaculty?.name || 'Faculty'} Live QR
                  </div>
                  <div className="absolute bottom-2.5 left-2.5 px-2 py-1 bg-slate-950/85 border border-slate-800 rounded-lg text-[9px] text-slate-300 max-w-[50%] truncate z-10">
                    {scanStatusHint}
                  </div>
                  <CameraControlOverlay
                    facingMode={facingMode}
                    devices={devices}
                    cameraActive={cameraActive}
                    cameraLoading={cameraLoading}
                    cameraError={cameraError}
                    activeLabel={activeLabel}
                    resolutionText={resolutionText}
                    fitMode={fitMode}
                    toggleFitMode={toggleFitMode}
                    selectFrontCamera={selectFrontCamera}
                    selectBackCamera={selectBackCamera}
                    cycleNextCamera={cycleNextCamera}
                    retryCamera={retryCamera}
                  />
                </>
              ) : scanResult.type === 'success' ? (
                <div className="p-4 flex flex-col items-center gap-2 text-emerald-400 font-bold">
                  <CheckCircle className="w-12 h-12" />
                  <span className="text-sm">{scanResult.title}</span>
                  <span className="text-[11px] text-slate-300 font-normal leading-relaxed">{scanResult.text}</span>
                </div>
              ) : (
                <div className="p-4 flex flex-col items-center gap-2 text-red-400 font-bold">
                  <AlertTriangle className="w-12 h-12" />
                  <span className="text-sm">{scanResult.title}</span>
                  <span className="text-[11px] text-red-200 font-normal leading-relaxed">{scanResult.text}</span>
                </div>
              )}
            </div>

            {!scanResult ? (
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => decodeFromCanvasOrVideo(videoRef.current, true)}
                  className="flex-1 py-3 px-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20 cursor-pointer"
                >
                  <QrCode className="w-4 h-4" /> Capture & Verify QR Frame
                </button>
                <button
                  type="button"
                  onClick={() => qrFileInputRef.current?.click()}
                  className="px-3.5 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold rounded-xl flex items-center justify-center gap-1.5 cursor-pointer"
                  title="Upload QR Screenshot"
                >
                  <Upload className="w-4 h-4" /> Upload QR
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => {
                  setScanResult(null);
                  setIsAutoScanning(true);
                  setScanStatusHint('Align Faculty QR code inside frame...');
                }}
                className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold rounded-xl cursor-pointer"
              >
                Reset & Scan Again
              </button>
            )}
          </div>
        </div>
      );
    }

    function StudentTimetableSchedule({ users }) {
      const f1 = users.find((u) => u.id === 'FAC01')?.name || 'Prof. Kawal Kaur';
      const f2 = users.find((u) => u.id === 'FAC02')?.name || 'Prof. Biswajit';
      const f3 = users.find((u) => u.id === 'FAC03')?.name || 'Prof. Vijay Dubey';
      const f4 = users.find((u) => u.id === 'FAC04')?.name || 'Prof. Alam';

      const schedule = [
        { time: '09:00 AM - 10:00 AM', subject: 'PWP (Python Web Programming)', faculty: f1, room: 'Lab ICT 301', type: 'Lab' },
        { time: '10:00 AM - 11:00 AM', subject: 'DMGT (Discrete Math & Graph Theory)', faculty: f2, room: 'Hall ICT 204', type: 'Lecture' },
        { time: '11:15 AM - 12:15 PM', subject: 'COA (Computer Organization & Arch)', faculty: f3, room: 'Hall ICT 204', type: 'Lecture' },
        { time: '01:00 PM - 02:00 PM', subject: 'DSC (Data Structures in C)', faculty: f4, room: 'Lab ICT 302', type: 'Lab' }
      ];

      return (
        <div className="space-y-4 text-xs">
          <div>
            <h2 className="text-base font-bold text-white uppercase tracking-wider">Timetable & Schedule</h2>
            <p className="text-slate-400">Daily ICT Sem 3 class slots, assigned faculty, and laboratory rooms</p>
          </div>
          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-4 space-y-2.5">
            {schedule.map((slot, i) => (
              <div key={i} className="p-3.5 bg-[#070a12] border border-slate-800 rounded-xl flex flex-wrap items-center justify-between gap-2">
                <div>
                  <div className="font-mono text-indigo-400 font-bold text-[11px]">{slot.time}</div>
                  <div className="font-bold text-white text-sm mt-0.5">{slot.subject}</div>
                  <div className="text-slate-400 text-[11px]">{slot.faculty}</div>
                </div>
                <div className="text-right">
                  <span className="px-2.5 py-1 bg-slate-900 border border-slate-700 rounded-lg font-mono text-cyan-300 font-semibold">
                    {slot.room}
                  </span>
                  <div className="text-[10px] text-slate-500 mt-1">{slot.type}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    function StudentAssignmentsHub({ campusUpdates }) {
      const [submittedIds, setSubmittedIds] = useState({});
      const assignments = campusUpdates.filter((u) => u.category === 'Assignment');

      return (
        <div className="space-y-4 text-xs">
          <div>
            <h2 className="text-base font-bold text-white uppercase tracking-wider">Assignments Hub</h2>
            <p className="text-slate-400">Live coursework and lab assignments published by faculty</p>
          </div>
          <div className="space-y-3">
            {assignments.length === 0 && (
              <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-6 text-slate-400">
                No active assignments published by faculty yet.
              </div>
            )}
            {assignments.map((a) => {
              const isSubmitted = !!submittedIds[a.id];
              return (
                <div key={a.id} className="bg-[#0e1422] border border-slate-800 rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
                  <div className="space-y-1 max-w-xl">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 bg-indigo-950 border border-indigo-800 text-indigo-300 rounded font-bold text-[10px]">
                        {a.subject}
                      </span>
                      <span className="text-slate-400 font-mono text-[11px]">Due: {a.date}</span>
                    </div>
                    <div className="font-bold text-white text-sm">{a.title}</div>
                    <p className="text-slate-400 text-[11px]">{a.details}</p>
                    <div className="text-[10px] text-slate-500">Assigned by {a.postedBy}</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSubmittedIds((prev) => ({ ...prev, [a.id]: true }))}
                    className={`px-4 py-2 rounded-xl font-bold cursor-pointer ${
                      isSubmitted
                        ? 'bg-emerald-950 border border-emerald-800 text-emerald-400'
                        : 'bg-[#5852f2] hover:bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
                    }`}
                  >
                    {isSubmitted ? '✓ Submitted' : 'Submit Work'}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      );
    }

    function StudentResultsTranscript({ studentUser, results }) {
      const [downloaded, setDownloaded] = useState(false);

      const handleDownloadTranscript = () => {
        const lines = [
          'MARWADI UNIVERSITY - DEPARTMENT OF ICT',
          'OFFICIAL ACADEMIC TRANSCRIPT (SEMESTER 3)',
          '-----------------------------------------',
          `Student Name : ${studentUser.name}`,
          `Enrollment No: ${studentUser.roll}`,
          `CGPA         : ${results?.cgpa || '8.63'}`,
          `Backlogs     : ${results?.backlogs ?? 0}`,
          '',
          'SGPA SUMMARY:',
          ...Object.entries(results?.sgpa || {}).map(([sem, val]) => `  ${sem}: ${val}`),
          '',
          'SUBJECT GRADES:',
          ...Object.entries(results?.subjects || {}).map(([sub, grd]) => `  ${sub}: ${grd}`)
        ];
        const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `Transcript_${studentUser.roll}.txt`;
        link.click();
        setDownloaded(true);
      };

      return (
        <div className="space-y-4 text-xs">
          <h2 className="text-base font-bold text-white uppercase tracking-wider">Results & Transcript (Sem 3)</h2>
          <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex flex-wrap justify-between items-center gap-3 border-b border-slate-800 pb-3">
              <div>
                <div className="text-lg font-extrabold text-white">CGPA: {results?.cgpa || '8.63'}</div>
                <div className="text-slate-400">
                  Student: {studentUser.name} ({studentUser.roll}) • Active Backlogs: {results?.backlogs ?? 0}
                </div>
              </div>
              <button
                type="button"
                onClick={handleDownloadTranscript}
                className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl flex items-center gap-1.5 cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" /> {downloaded ? '✓ Transcript Downloaded' : 'Download Transcript'}
              </button>
            </div>
            <div className="grid grid-cols-3 gap-3 text-center font-mono">
              {results &&
                Object.entries(results.sgpa).map(([sem, val]) => (
                  <div key={sem} className="bg-[#070a12] border border-slate-800 p-3 rounded-xl">
                    <div className="text-[10px] text-slate-400">{sem}</div>
                    <div className="font-bold text-cyan-400 text-base mt-0.5">{val}</div>
                  </div>
                ))}
            </div>
            {results?.subjects && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2">
                {Object.entries(results.subjects).map(([sub, grade]) => (
                  <div key={sub} className="p-2.5 bg-slate-900 border border-slate-800 rounded-xl flex justify-between items-center font-mono">
                    <span className="text-slate-300 font-bold">{sub}</span>
                    <span className="text-emerald-400 font-extrabold">{grade}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      );
    }

    function StudentCurriculumProgress({ users }) {
      const f1 = users.find((u) => u.id === 'FAC01')?.name || 'Prof. Kawal Kaur';
      const f2 = users.find((u) => u.id === 'FAC02')?.name || 'Prof. Biswajit';
      const f3 = users.find((u) => u.id === 'FAC03')?.name || 'Prof. Vijay Dubey';
      const f4 = users.find((u) => u.id === 'FAC04')?.name || 'Prof. Alam';

      const courses = [
        { code: 'PWP', name: 'Python Web Programming', progress: 82, units: '4 / 5 Units Completed', faculty: f1 },
        { code: 'DMGT', name: 'Discrete Math & Graph Theory', progress: 75, units: '3 / 4 Units Completed', faculty: f2 },
        { code: 'COA', name: 'Computer Organization & Architecture', progress: 90, units: '4.5 / 5 Units Completed', faculty: f3 },
        { code: 'DSC', name: 'Data Structures in C', progress: 80, units: '4 / 5 Units Completed', faculty: f4 }
      ];

      return (
        <div className="space-y-4 text-xs">
          <div>
            <h2 className="text-base font-bold text-white uppercase tracking-wider">Curriculum Progress</h2>
            <p className="text-slate-400">Real-time syllabus completion across ICT Semester 3 subjects</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {courses.map((c) => (
              <div key={c.code} className="bg-[#0e1422] border border-slate-800 rounded-2xl p-5 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-bold text-white text-sm">
                      {c.code} — {c.name}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      {c.faculty} • {c.units}
                    </div>
                  </div>
                  <span className="font-mono font-extrabold text-indigo-400">{c.progress}%</span>
                </div>
                <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                  <div className="h-full bg-[#5852f2] rounded-full" style={{ width: `${c.progress}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    function StudentHolidaysEvents({ campusUpdates }) {
      const items = campusUpdates.filter((u) => u.category === 'Holiday' || u.category === 'Event');
      return (
        <div className="space-y-4 text-xs">
          <div>
            <h2 className="text-base font-bold text-white uppercase tracking-wider">Holidays & Events</h2>
            <p className="text-slate-400">Official Marwadi University holidays, hackathons, and ICT events posted by faculty</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {items.length === 0 && (
              <div className="bg-[#0e1422] border border-slate-800 rounded-2xl p-6 text-slate-400">
                No upcoming holidays or events posted yet.
              </div>
            )}
            {items.map((item) => (
              <div key={item.id} className="bg-[#0e1422] border border-slate-800 rounded-2xl p-5 space-y-2">
                <div className="flex items-center justify-between">
                  <span
                    className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                      item.category === 'Holiday'
                        ? 'bg-amber-950 text-amber-300 border border-amber-800'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                    }`}
                  >
                    {item.category.toUpperCase()}
                  </span>
                  <span className="text-slate-400 font-mono text-[11px]">{item.date}</span>
                </div>
                <div className="font-bold text-white text-sm">{item.title}</div>
                <p className="text-slate-400 text-[11px]">{item.details}</p>
                <div className="text-[10px] text-slate-500 pt-1">Published by {item.postedBy}</div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(<App />);
  </script>
</body>
</html>"""

class FullAppHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/sync"):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            key = query.get("key", [None])[0]
            with STATE_LOCK:
                found = key in SHARED_STORE
                val = SHARED_STORE.get(key)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(json.dumps({"found": found, "value": val}).encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(FULL_WEBSITE_CODE.encode("utf-8"))

    def do_POST(self):
        if self.path == "/api/sync":
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode("utf-8")
            try:
                payload = json.loads(raw_body)
                key = payload.get("key")
                if key:
                    with STATE_LOCK:
                        SHARED_STORE[key] = payload.get("value")
                        save_store_to_disk()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as exc:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(exc)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    print(f"Marwadi University ICT Full System running at http://localhost:{PORT}")
    threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    with ThreadedHTTPServer(("", PORT), FullAppHandler) as httpd:
        httpd.serve_forever()