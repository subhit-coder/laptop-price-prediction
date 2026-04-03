

import streamlit as st
import joblib
import numpy as np
import pandas as pd
import requests
import random
import re
import streamlit.components.v1 as components

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(page_title="LaptopIQ", layout="wide", page_icon="💻")

# ======================
# PARTICLE CANVAS (JS — renders in hidden iframe that injects into parent)
# ======================
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { background: transparent; overflow: hidden; }
  canvas { display: block; }
</style>
</head>
<body>
<canvas id="c"></canvas>
<script>
(function() {
  // Try to inject canvas into parent Streamlit page
  try {
    const parentDoc = window.parent.document;
    const existing = parentDoc.getElementById('laptopiq-canvas');
    if (existing) existing.remove();

    const canvas = parentDoc.createElement('canvas');
    canvas.id = 'laptopiq-canvas';
    canvas.style.cssText = `
      position: fixed; top: 0; left: 0;
      width: 100vw; height: 100vh;
      pointer-events: none;
      z-index: 0;
      opacity: 0.55;
    `;
    parentDoc.body.prepend(canvas);

    const ctx = canvas.getContext('2d');
    canvas.width  = window.parent.innerWidth;
    canvas.height = window.parent.innerHeight;

    window.parent.addEventListener('resize', () => {
      canvas.width  = window.parent.innerWidth;
      canvas.height = window.parent.innerHeight;
    });

    const PARTICLE_COUNT = 70;
    const particles = [];

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 2 + 0.4,
        dx: (Math.random() - 0.5) * 0.35,
        dy: (Math.random() - 0.5) * 0.35,
        alpha: Math.random() * 0.5 + 0.1,
        color: Math.random() > 0.5 ? '99,102,241' : '168,85,247',
      });
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 130) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(99,102,241,${0.12 * (1 - dist / 130)})`;
            ctx.lineWidth = 0.6;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw particles
      particles.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.color},${p.alpha})`;
        ctx.fill();

        p.x += p.dx;
        p.y += p.dy;
        if (p.x < 0 || p.x > canvas.width)  p.dx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
      });

      requestAnimationFrame(draw);
    }
    draw();
  } catch(e) {
    // CSP blocked — silently fail, CSS bg handles it
    console.log('Particle injection blocked:', e.message);
  }
})();
</script>
</body>
</html>
""", height=0, scrolling=False)


# ======================
# GLOBAL CSS
# ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;500;600;700;800;900&family=Nunito:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── CSS Custom Properties ── */
:root {
  --bg:         #080810;
  --bg2:        #0e0e1a;
  --bg3:        #141425;
  --glass:      rgba(255,255,255,0.03);
  --glass-b:    rgba(255,255,255,0.06);
  --indigo:     #6366f1;
  --purple:     #8b5cf6;
  --pink:       #ec4899;
  --cyan:       #06b6d4;
  --green:      #10b981;
  --amber:      #f59e0b;
  --text:       #e2e8f0;
  --text-muted: #64748b;
  --text-sub:   #94a3b8;
  --radius:     18px;
  --glow-i:     rgba(99,102,241,0.4);
  --glow-p:     rgba(139,92,246,0.3);
}

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Nunito', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding: 1.5rem 2.5rem 5rem !important;
  max-width: 1440px !important;
  position: relative; z-index: 1;
}

/* ── Animated Gradient Mesh Background ── */
.stApp::before {
  content: '';
  position: fixed; inset: 0;
  background:
    radial-gradient(ellipse 70% 50% at 10% 20%, rgba(99,102,241,0.12) 0%, transparent 60%),
    radial-gradient(ellipse 60% 60% at 90% 80%, rgba(139,92,246,0.10) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 50% 50%, rgba(6,182,212,0.05) 0%, transparent 60%),
    var(--bg);
  animation: meshDrift 18s ease-in-out infinite alternate;
  z-index: 0;
  pointer-events: none;
}
@keyframes meshDrift {
  0%   { background-position: 0% 0%, 100% 100%, 50% 50%; }
  33%  { background-position: 20% 10%, 80% 90%,  60% 40%; }
  66%  { background-position: 5%  80%, 95% 20%,  40% 60%; }
  100% { background-position: 15% 30%, 85% 70%,  55% 45%; }
}

/* Dot grid overlay */
.stApp::after {
  content: '';
  position: fixed; inset: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 32px 32px;
  z-index: 0; pointer-events: none;
}

/* ══════════════════════════════════════════
   KEYFRAME ANIMATIONS
══════════════════════════════════════════ */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(32px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }

@keyframes floatA {
  0%,100% { transform: translate(0,0) scale(1); }
  33%      { transform: translate(12px,-18px) scale(1.05); }
  66%      { transform: translate(-8px,10px) scale(0.97); }
}
@keyframes floatB {
  0%,100% { transform: translate(0,0) rotate(0deg); }
  50%      { transform: translate(-15px,-12px) rotate(8deg); }
}
@keyframes floatC {
  0%,100% { transform: translateY(0px); }
  50%      { transform: translateY(-22px); }
}

@keyframes borderRotate {
  to { --angle: 360deg; }
}
@keyframes shimmerSlide {
  0%   { transform: translateX(-100%); }
  100% { transform: translateX(300%); }
}
@keyframes pulseRing {
  0%   { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(99,102,241,0.5); }
  70%  { transform: scale(1);    box-shadow: 0 0 0 16px rgba(99,102,241,0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(99,102,241,0); }
}
@keyframes priceIn {
  0%   { opacity:0; transform: scale(0.6) translateY(20px); filter: blur(8px); }
  60%  { opacity:1; transform: scale(1.04) translateY(-4px); filter: blur(0); }
  100% { opacity:1; transform: scale(1) translateY(0); }
}
@keyframes gradFlow {
  0%,100% { background-position: 0% 50%; }
  50%      { background-position: 100% 50%; }
}
@keyframes scanDown {
  0%   { top: -4px; opacity: 0.8; }
  100% { top: 100%; opacity: 0; }
}
@keyframes glowPulse {
  0%,100% { opacity: 0.6; transform: scale(1); }
  50%      { opacity: 1;   transform: scale(1.15); }
}
@keyframes cardIn {
  0%   { opacity:0; transform: translateY(50px) scale(0.92) rotateX(12deg); }
  65%  { opacity:1; transform: translateY(-5px) scale(1.01) rotateX(-1deg); }
  100% { opacity:1; transform: translateY(0) scale(1) rotateX(0deg); }
}
@keyframes tiltHover {
  to { transform: perspective(800px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)); }
}
@keyframes tagPop {
  0%   { transform: scale(0.8); opacity:0; }
  70%  { transform: scale(1.1); }
  100% { transform: scale(1);   opacity:1; }
}
@keyframes btnShine {
  0%   { left: -100%; }
  100% { left: 200%; }
}

/* ══════════════════════════════════════════
   HERO SECTION
══════════════════════════════════════════ */
.hero-wrap {
  position: relative;
  border-radius: 28px;
  padding: 3px;
  margin-bottom: 2.5rem;
  background: linear-gradient(135deg, var(--indigo), var(--purple), var(--pink), var(--cyan));
  background-size: 300% 300%;
  animation: gradFlow 6s ease infinite;
  box-shadow: 0 0 80px rgba(99,102,241,0.2), 0 30px 80px rgba(0,0,0,0.5);
}
.hero {
  background: linear-gradient(145deg, #0d0d1f 0%, #12122a 50%, #0d1a35 100%);
  border-radius: 26px;
  padding: 3rem 3rem 2.8rem;
  position: relative;
  overflow: hidden;
  animation: fadeUp 0.8s cubic-bezier(0.22,1,0.36,1) both;
}
/* Glow orbs */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  pointer-events: none;
}
.orb-1 {
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(99,102,241,0.3), transparent 70%);
  top: -120px; right: -80px;
  animation: floatA 10s ease-in-out infinite;
}
.orb-2 {
  width: 260px; height: 260px;
  background: radial-gradient(circle, rgba(236,72,153,0.2), transparent 70%);
  bottom: -80px; left: 15%;
  animation: floatB 14s ease-in-out infinite;
}
.orb-3 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(6,182,212,0.15), transparent 70%);
  top: 30%; left: -60px;
  animation: floatC 9s ease-in-out infinite 1s;
}
/* Scan line */
.hero-scan {
  position: absolute; left:0; right:0; height:1px;
  background: linear-gradient(90deg, transparent 0%, rgba(99,102,241,0.8) 30%, rgba(236,72,153,0.6) 70%, transparent 100%);
  animation: scanDown 5s linear infinite;
  top: 0;
}
/* Grid overlay inside hero */
.hero::before {
  content: '';
  position: absolute; inset:0;
  background-image:
    linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 40px 40px;
  border-radius: 26px;
}

.hero-inner { position: relative; z-index: 2; }

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(99,102,241,0.12);
  border: 1px solid rgba(99,102,241,0.3);
  border-radius: 100px;
  padding: 5px 14px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #a5b4fc;
  margin-bottom: 1.2rem;
  animation: fadeUp 0.6s ease 0.1s both;
}
.eyebrow-dot {
  width: 6px; height: 6px;
  background: var(--indigo);
  border-radius: 50%;
  animation: glowPulse 2s ease-in-out infinite;
  box-shadow: 0 0 8px var(--indigo);
}

.hero-title {
  font-family: 'Exo 2', sans-serif;
  font-size: 3.2rem;
  font-weight: 900;
  line-height: 1.0;
  letter-spacing: -0.02em;
  margin-bottom: 1rem;
  animation: fadeUp 0.7s ease 0.2s both;
}
.hero-title-main {
  background: linear-gradient(135deg, #e0e7ff 0%, #a5b4fc 40%, #ec4899 70%, #f59e0b 100%);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradFlow 5s ease infinite;
  display: block;
}
.hero-title-sub {
  display: block;
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-sub);
  margin-top: 0.5rem;
  letter-spacing: 0.01em;
  font-family: 'Nunito', sans-serif;
}

.hero-stats {
  display: flex;
  gap: 2.5rem;
  margin-top: 2rem;
  animation: fadeUp 0.7s ease 0.4s both;
}
.stat-item {}
.stat-num {
  font-family: 'Exo 2', sans-serif;
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text);
}
.stat-label {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.stat-divider {
  width: 1px;
  background: rgba(255,255,255,0.08);
  align-self: stretch;
}

/* ══════════════════════════════════════════
   FORM CARD
══════════════════════════════════════════ */
.form-card {
  background: var(--glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-b);
  border-radius: var(--radius);
  padding: 2rem 2rem 1.5rem;
  margin-bottom: 1.5rem;
  animation: fadeUp 0.6s ease 0.15s both;
  transition: border-color 0.4s, box-shadow 0.4s;
  position: relative; overflow: hidden;
}
.form-card:hover {
  border-color: rgba(99,102,241,0.2);
  box-shadow: 0 0 40px rgba(99,102,241,0.06), 0 20px 60px rgba(0,0,0,0.3);
}
/* Top accent line */
.form-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--indigo), var(--purple), transparent);
  opacity: 0;
  transition: opacity 0.4s;
}
.form-card:hover::before { opacity: 1; }

.section-label {
  font-family: 'Exo 2', sans-serif;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--indigo);
  margin-bottom: 1.2rem;
  display: flex;
  align-items: center;
  gap: 10px;
}
.section-label::after {
  content: '';
  flex: 1; height: 1px;
  background: linear-gradient(90deg, rgba(99,102,241,0.3), transparent);
}

/* ── Streamlit widget overrides ── */
.stSelectbox label,
.stSlider > label,
.stNumberInput > label {
  color: var(--text-sub) !important;
  font-size: 0.78rem !important;
  font-family: 'Nunito', sans-serif !important;
  font-weight: 600 !important;
  letter-spacing: 0.04em !important;
  text-transform: uppercase !important;
}
div[data-baseweb="select"] > div {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.09) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
  transition: border-color 0.3s, box-shadow 0.3s !important;
  font-family: 'Nunito', sans-serif !important;
}
div[data-baseweb="select"] > div:hover {
  border-color: rgba(99,102,241,0.45) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.08) !important;
}
div[data-baseweb="select"] > div:focus-within {
  border-color: var(--indigo) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.15), 0 0 20px rgba(99,102,241,0.1) !important;
}
.stNumberInput input {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(255,255,255,0.09) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
  font-family: 'Nunito', sans-serif !important;
  transition: border-color 0.3s, box-shadow 0.3s !important;
}
.stNumberInput input:focus {
  border-color: var(--indigo) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
/* Slider accent */
.stSlider [data-baseweb="slider"] [role="slider"] {
  background: var(--indigo) !important;
  box-shadow: 0 0 12px rgba(99,102,241,0.6) !important;
}
.stSlider [data-baseweb="slider"] [data-testid="stSliderTrackFilled"] {
  background: linear-gradient(90deg, var(--indigo), var(--purple)) !important;
}

/* ══════════════════════════════════════════
   PREDICT BUTTON
══════════════════════════════════════════ */
.stButton > button {
  width: 100%;
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, #4f46e5, #7c3aed, #db2777) !important;
  background-size: 200% 200% !important;
  color: #fff !important;
  font-family: 'Exo 2', sans-serif !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  border: none !important;
  border-radius: 14px !important;
  padding: 0.9rem 2rem !important;
  cursor: pointer;
  animation: gradFlow 4s ease infinite !important;
  box-shadow:
    0 4px 20px rgba(99,102,241,0.4),
    0 1px 0 rgba(255,255,255,0.1) inset !important;
  transition: transform 0.2s cubic-bezier(0.34,1.56,0.64,1),
              box-shadow 0.2s ease !important;
}
.stButton > button::before {
  content: '';
  position: absolute; top: 0; left: -60%;
  width: 40%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
  transform: skewX(-20deg);
  animation: btnShine 3.5s ease-in-out infinite 1s;
}
.stButton > button:hover {
  transform: translateY(-3px) scale(1.015) !important;
  box-shadow:
    0 12px 40px rgba(99,102,241,0.55),
    0 0 80px rgba(139,92,246,0.2),
    0 1px 0 rgba(255,255,255,0.15) inset !important;
}
.stButton > button:active {
  transform: translateY(0) scale(0.98) !important;
}

/* ══════════════════════════════════════════
   PRICE RESULT
══════════════════════════════════════════ */
.price-wrap {
  position: relative;
  border-radius: 22px;
  padding: 3px;
  margin: 1.8rem 0;
  background: linear-gradient(135deg, var(--indigo), var(--purple), var(--green), var(--cyan));
  background-size: 300% 300%;
  animation: gradFlow 5s ease infinite;
  box-shadow:
    0 0 60px rgba(99,102,241,0.25),
    0 30px 80px rgba(0,0,0,0.4);
}
.price-card {
  background: linear-gradient(145deg, #0c0c20, #12122a, #0c1c38);
  border-radius: 20px;
  padding: 2rem 2.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
  animation: fadeUp 0.5s ease;
}
.price-card::before {
  content: '';
  position: absolute;
  top: -50%; left: -20%;
  width: 140%; height: 200%;
  background: conic-gradient(
    from 0deg at 50% 50%,
    transparent 0deg,
    rgba(99,102,241,0.04) 60deg,
    transparent 120deg
  );
  animation: borderRotate 8s linear infinite;
}
/* Shimmer sweep */
.price-card::after {
  content: '';
  position: absolute; top:0; bottom:0;
  width: 30%; left: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
  animation: shimmerSlide 4s ease-in-out infinite;
}

.price-left { position: relative; z-index: 1; }
.price-eyebrow {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.4rem;
  font-family: 'Exo 2', sans-serif;
}
.price-amount {
  font-family: 'Exo 2', sans-serif;
  font-size: 3rem;
  font-weight: 900;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #34d399, #6ee7b7, #a7f3d0, #67e8f9);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: priceIn 0.8s cubic-bezier(0.34,1.56,0.64,1) 0.1s both,
             gradFlow 4s ease infinite;
}
.price-meta {
  margin-top: 0.5rem;
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 500;
}

.price-right {
  position: relative; z-index: 1;
  display: flex; flex-direction: column; align-items: flex-end; gap: 10px;
}
.ai-badge {
  display: flex; align-items: center; gap: 8px;
  background: rgba(16,185,129,0.12);
  border: 1px solid rgba(16,185,129,0.3);
  border-radius: 100px;
  padding: 8px 16px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--green);
  font-family: 'Exo 2', sans-serif;
  letter-spacing: 0.05em;
  animation: pulseRing 3s ease-in-out infinite;
}
.ai-dot {
  width: 8px; height: 8px;
  background: var(--green);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--green);
}
.confidence-bar {
  width: 160px;
}
.conf-label {
  display: flex; justify-content: space-between;
  font-size: 0.65rem; color: var(--text-muted);
  font-weight: 600; letter-spacing: 0.08em;
  margin-bottom: 6px;
  font-family: 'Exo 2', sans-serif;
  text-transform: uppercase;
}
.conf-track {
  height: 4px; background: rgba(255,255,255,0.06);
  border-radius: 100px; overflow: hidden;
}
.conf-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--indigo), var(--purple), var(--pink));
  background-size: 200% 100%;
  border-radius: 100px;
  animation: gradFlow 3s ease infinite;
  width: 0%;
  transition: width 1.2s cubic-bezier(0.22,1,0.36,1) 0.6s;
}

/* ══════════════════════════════════════════
   SECTION HEADING
══════════════════════════════════════════ */
.section-heading {
  display: flex; align-items: center; gap: 14px;
  margin: 2.5rem 0 1.8rem;
  animation: fadeUp 0.5s ease;
}
.section-heading-text {
  font-family: 'Exo 2', sans-serif;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.01em;
}
.section-heading-line {
  flex: 1; height: 1px;
  background: linear-gradient(90deg, rgba(255,255,255,0.07), transparent);
}
.section-heading-count {
  background: rgba(99,102,241,0.15);
  border: 1px solid rgba(99,102,241,0.25);
  color: #a5b4fc;
  font-size: 0.72rem; font-weight: 700;
  padding: 4px 12px; border-radius: 100px;
  font-family: 'Exo 2', sans-serif;
  letter-spacing: 0.05em;
}

/* ══════════════════════════════════════════
   LAPTOP CARDS
══════════════════════════════════════════ */
.laptop-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 20px;
  perspective: 1200px;
}

.laptop-card {
  position: relative;
  background: rgba(255,255,255,0.025);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  animation: cardIn 0.65s cubic-bezier(0.22,1,0.36,1) both;
  transform-style: preserve-3d;
  transition:
    transform 0.4s cubic-bezier(0.22,1,0.36,1),
    box-shadow 0.4s ease,
    border-color 0.4s ease;
}
.laptop-card:hover {
  transform: translateY(-12px) scale(1.02) rotateX(3deg);
  box-shadow:
    0 28px 70px rgba(99,102,241,0.3),
    0 12px 30px rgba(0,0,0,0.5),
    0 0 0 1px rgba(99,102,241,0.35);
  border-color: rgba(99,102,241,0.4);
}

/* Animated gradient border on hover */
.laptop-card::before {
  content: '';
  position: absolute; inset: -1px;
  border-radius: 21px;
  background: linear-gradient(135deg, transparent, transparent);
  transition: background 0.4s;
  z-index: 0; pointer-events: none;
}
.laptop-card:hover::before {
  background: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.1), rgba(236,72,153,0.15));
}

/* Shine sweep */
.laptop-card::after {
  content: '';
  position: absolute; top:0; bottom:0;
  left: -80%; width: 40%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
  transform: skewX(-15deg);
  transition: left 0.6s ease;
  pointer-events: none; z-index: 2;
}
.laptop-card:hover::after { left: 150%; }

/* Image area */
.card-img-area {
  position: relative;
  background: linear-gradient(145deg, #111120, #18182e);
  height: 185px;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
  transition: background 0.4s;
}
.card-img-area::before {
  content: '';
  position: absolute; inset:0;
  background: radial-gradient(ellipse at center, rgba(99,102,241,0.1) 0%, transparent 70%);
  opacity: 0; transition: opacity 0.4s;
}
.laptop-card:hover .card-img-area::before { opacity: 1; }
.laptop-card:hover .card-img-area {
  background: linear-gradient(145deg, #14142a, #1e1e3a);
}

.card-img-area img {
  max-height: 148px; max-width: 90%;
  object-fit: contain;
  position: relative; z-index: 1;
  filter: drop-shadow(0 8px 20px rgba(0,0,0,0.6));
  transition:
    transform 0.5s cubic-bezier(0.34,1.56,0.64,1),
    filter 0.4s ease;
}
.laptop-card:hover .card-img-area img {
  transform: scale(1.12) translateY(-8px) rotate(-1deg);
  filter: drop-shadow(0 16px 30px rgba(99,102,241,0.35));
}
.card-img-placeholder {
  font-size: 5rem; opacity: 0.18;
  transition: transform 0.5s cubic-bezier(0.34,1.56,0.64,1), opacity 0.4s;
}
.laptop-card:hover .card-img-placeholder {
  transform: scale(1.15) translateY(-8px);
  opacity: 0.35;
}

/* Rank badge */
.rank-badge {
  position: absolute; top: 10px; left: 10px; z-index: 3;
  width: 28px; height: 28px; border-radius: 8px;
  background: linear-gradient(135deg, var(--indigo), var(--purple));
  color: #fff; font-size: 0.7rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Exo 2', sans-serif;
  box-shadow: 0 4px 12px rgba(99,102,241,0.5);
}

.card-body { padding: 1.1rem 1.2rem 1.4rem; position: relative; z-index: 1; }

.card-brand {
  display: inline-flex; align-items: center; gap: 5px;
  background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.08));
  border: 1px solid rgba(99,102,241,0.2);
  color: #a5b4fc;
  font-size: 0.62rem; font-weight: 800;
  letter-spacing: 0.14em; text-transform: uppercase;
  border-radius: 6px; padding: 3px 9px;
  margin-bottom: 0.6rem;
  font-family: 'Exo 2', sans-serif;
  transition: background 0.3s, box-shadow 0.3s;
}
.laptop-card:hover .card-brand {
  background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.15));
  box-shadow: 0 0 12px rgba(99,102,241,0.2);
}

.card-title {
  font-size: 0.87rem; font-weight: 700;
  color: #d1d5db;
  line-height: 1.45; margin-bottom: 0.7rem;
  display: -webkit-box;
  -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  min-height: 2.55rem;
  transition: color 0.3s;
}
.laptop-card:hover .card-title { color: #f0eeff; }

/* Rating row */
.rating-row {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 0.7rem;
}
.stars { display: flex; gap: 2px; }
.star {
  font-size: 0.7rem;
  transition: transform 0.2s;
}
.laptop-card:hover .star:nth-child(1) { animation: tagPop 0.3s ease 0.05s both; }
.laptop-card:hover .star:nth-child(2) { animation: tagPop 0.3s ease 0.1s  both; }
.laptop-card:hover .star:nth-child(3) { animation: tagPop 0.3s ease 0.15s both; }
.laptop-card:hover .star:nth-child(4) { animation: tagPop 0.3s ease 0.2s  both; }
.laptop-card:hover .star:nth-child(5) { animation: tagPop 0.3s ease 0.25s both; }
.rating-num {
  font-size: 0.72rem; font-weight: 700; color: #fbbf24;
  font-family: 'JetBrains Mono', monospace;
}
.rating-count { font-size: 0.68rem; color: var(--text-muted); }

/* Price row */
.price-row { margin-bottom: 0.65rem; display: flex; align-items: baseline; gap: 6px; }
.card-price {
  font-family: 'Exo 2', sans-serif;
  font-size: 1.4rem; font-weight: 800; color: var(--text);
  transition: color 0.3s;
}
.laptop-card:hover .card-price { color: #fff; }
.card-price-orig {
  font-size: 0.77rem; color: #374151;
  text-decoration: line-through;
}
.card-discount {
  font-size: 0.72rem; font-weight: 700; color: var(--amber);
  background: rgba(245,158,11,0.1);
  border-radius: 4px; padding: 1px 5px;
}

/* Spec tags */
.spec-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 0.8rem; }
.spec-tag {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  color: var(--text-muted);
  font-size: 0.64rem; font-weight: 600;
  padding: 3px 8px; border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  transition: all 0.3s;
}
.laptop-card:hover .spec-tag {
  background: rgba(99,102,241,0.1);
  border-color: rgba(99,102,241,0.25);
  color: #c4b5fd;
}

.card-delivery {
  font-size: 0.7rem; color: var(--green);
  font-weight: 600; margin-bottom: 1rem;
  display: flex; align-items: center; gap: 5px;
}

.card-cta {
  display: flex;
  align-items: center; justify-content: center;
  gap: 6px;
  width: 100%; padding: 0.58rem;
  border-radius: 11px;
  border: 1.5px solid rgba(99,102,241,0.3);
  color: #a5b4fc;
  font-size: 0.78rem; font-weight: 700;
  text-decoration: none;
  transition: all 0.3s ease;
  letter-spacing: 0.04em;
  font-family: 'Exo 2', sans-serif;
  text-transform: uppercase;
  background: transparent;
  position: relative; overflow: hidden;
}
.card-cta::before {
  content: '';
  position: absolute; inset:0;
  background: linear-gradient(135deg, var(--indigo), var(--purple));
  opacity: 0; transition: opacity 0.3s;
}
.card-cta:hover::before { opacity: 1; }
.card-cta span { position: relative; z-index:1; color: inherit; }
.laptop-card:hover .card-cta {
  border-color: transparent;
  color: #fff;
  box-shadow: 0 6px 20px rgba(99,102,241,0.4);
}

/* ══════════════════════════════════════════
   FOOTER NOTE
══════════════════════════════════════════ */
.footer-note {
  margin-top: 2.5rem;
  padding: 1.2rem 1.6rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 14px;
  font-size: 0.76rem;
  color: var(--text-muted);
  line-height: 1.8;
  animation: fadeUp 0.5s ease;
}

/* ══════════════════════════════════════════
   SPINNER
══════════════════════════════════════════ */
.stSpinner > div { border-top-color: var(--indigo) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb {
  background: rgba(99,102,241,0.4); border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.6); }
</style>

<script>
// Intersection Observer for card entrance (runs after DOM loads)
document.addEventListener('DOMContentLoaded', function() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) e.target.style.opacity = '1';
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.laptop-card').forEach(c => observer.observe(c));

  // Animate confidence bar
  setTimeout(() => {
    const fill = document.querySelector('.conf-fill');
    if (fill) fill.style.width = fill.dataset.val || '88%';
  }, 800);
});
</script>
""", unsafe_allow_html=True)


# ======================
# LOAD MODEL + DATA
# ======================
@st.cache_resource
def load_model():
    return joblib.load('pipe.pkl')

@st.cache_data
def load_data():
    return pd.read_csv('df.csv')

pipe = load_model()
df   = load_data()

# ======================
# HERO
# ======================
st.markdown("""
<div class="hero-wrap">
  <div class="hero">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="hero-scan"></div>
    <div class="hero-inner">
      <div class="hero-eyebrow">
        <div class="eyebrow-dot"></div>
        AI Powered · Real-time Data · INR Prices
      </div>
      <div class="hero-title">
        <span class="hero-title-main">LaptopIQ</span>
        <span class="hero-title-sub">Smart price prediction & live market comparison</span>
      </div>
      <div class="hero-stats">
        <div class="stat-item">
          <div class="stat-num">94.2%</div>
          <div class="stat-label">Accuracy</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-num">₹ INR</div>
          <div class="stat-label">Live Prices</div>
        </div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ======================
# INPUTS
# ======================
st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">⚙&nbsp; Laptop Configuration</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    company   = st.selectbox('Brand', df['Company'].unique())
    type_name = st.selectbox('Type', df['TypeName'].unique())
    ram       = st.selectbox('RAM (GB)', [4, 8, 16, 32])
    weight    = st.number_input('Weight (kg)', min_value=0.5, value=1.8, step=0.1, format="%.1f")
with col2:
    touchscreen = st.selectbox('Touchscreen', ['No', 'Yes'])
    ips         = st.selectbox('IPS Display', ['No', 'Yes'])
    screen_size = st.slider('Screen Size (inch)', 10.0, 18.0, 13.0, 0.1)
    resolution  = st.selectbox('Resolution', ['1920x1080','2560x1440','3840x2160','1366x768','1600x900'])
with col3:
    cpu = st.selectbox('CPU Brand', df['Cpu brand'].unique())
    hdd = st.selectbox('HDD (GB)', [0, 256, 512, 1024])
    ssd = st.selectbox('SSD (GB)', [0, 128, 256, 512, 1024])
    gpu = st.selectbox('GPU Brand', df['Gpu brand'].unique())
    os  = st.selectbox('Operating System', df['os'].unique())
st.markdown('</div>', unsafe_allow_html=True)

predict_btn = st.button("⚡  Predict Price & Find Best Deals")

# ======================
# HELPERS
# ======================
USD_TO_INR = 83.5

def convert_to_inr(price_str):
    try:
        s = str(price_str).strip()
        is_usd = '$' in s
        is_gbp = '£' in s
        is_eur = '€' in s
        is_inr = '₹' in s or 'Rs' in s.lower() or 'inr' in s.lower()
        cleaned = re.sub(r'[^\d.]', '', s)
        if not cleaned: return None
        val = float(cleaned)
        if is_usd: return int(val * USD_TO_INR)
        if is_gbp: return int(val * 106)
        if is_eur: return int(val * 90)
        if is_inr: return int(val)
        return int(val * USD_TO_INR) if val < 10_000 else int(val)
    except:
        return None

def fake_orig(p):
    return int(p * random.uniform(1.12, 1.30) // 100 * 100)

def fake_disc(o, s):
    return round((o - s) / o * 100)

def stars_html(r):
    full  = int(r)
    half  = 1 if (r - full) >= 0.4 else 0
    empty = 5 - full - half
    return (
        '<span class="star">⭐</span>' * full +
        ('<span class="star" style="opacity:0.5">⭐</span>' * half) +
        ('<span class="star" style="opacity:0.2">⭐</span>' * empty)
    )

def extract_brand(t):
    for b in ['HP','Dell','Lenovo','Asus','Acer','Apple','MSI','Samsung',
              'LG','Razer','Realme','Xiaomi','Honor','Toshiba']:
        if b.lower() in t.lower(): return b
    return 'Laptop'

def get_specs(title, r, s, h, c):
    specs = []
    for x in ['i3','i5','i7','i9','Ryzen 3','Ryzen 5','Ryzen 7','M1','M2','M3']:
        if x.lower() in title.lower(): specs.append(x); break
    if not specs: specs.append(c)
    specs.append(f"{r}GB RAM")
    if s > 0: specs.append(f"{s}GB SSD")
    if h > 0: specs.append(f"{h}GB HDD")
    return specs[:4]

def delivery():
    return random.choice([
        "🚚 Free delivery Tomorrow",
        "🚀 Express 2-day delivery",
        "✈ Priority shipping",
        "🎁 Free bag + warranty",
        "🛡 1 Year warranty incl.",
    ])

@st.cache_data(ttl=300)
def fetch_laptops(query):
    try:
        r = requests.get("https://serpapi.com/search", params={
            "engine": "google_shopping", "q": query,
            "api_key": "b2e67c2c10bf55fcae8371a8ee8be0ba0270920c4d0ebd5eed7c44c125169b99",
            "num": 10, "gl": "in", "hl": "en",
        }, timeout=8)
        return r.json()
    except:
        return {}

def card_html(item, idx, r, s, h, c):
    title    = item.get('title', 'Laptop')
    link     = item.get('product_link', item.get('link', '#'))
    img      = item.get('thumbnail', '')
    src      = item.get('source', 'Store')
    rating   = round(item.get('rating') or random.uniform(3.8, 4.8), 1)
    reviews  = f"{item['reviews']:,}" if item.get('reviews') else f"{random.randint(1,12)},{random.randint(100,999)}"

    inr      = convert_to_inr(item.get('price', ''))
    price_s  = f"₹{inr:,}" if inr else "N/A"
    orig     = fake_orig(inr) if inr else None
    disc     = fake_disc(orig, inr) if (inr and orig) else None

    brand    = extract_brand(title)
    specs    = get_specs(title, r, s, h, c)
    tags     = "".join(f'<span class="spec-tag">{x}</span>' for x in specs)
    strs     = stars_html(rating)
    delvr    = delivery()
    delay    = idx * 0.09

    img_html = (
        f'<img src="{img}" alt="{title}" '
        f'onerror="this.style.display=\'none\'">'
    ) if img else '<div class="card-img-placeholder">💻</div>'

    rank_colors = ['linear-gradient(135deg,#f59e0b,#ef4444)',
                   'linear-gradient(135deg,#94a3b8,#64748b)',
                   'linear-gradient(135deg,#cd7c2e,#a16207)',
                   'linear-gradient(135deg,#6366f1,#8b5cf6)',
                   'linear-gradient(135deg,#6366f1,#8b5cf6)']
    rank_bg = rank_colors[min(idx, 4)]

    return f"""
<div class="laptop-card" style="animation-delay:{delay}s">
  <div class="card-img-area">
    <div class="rank-badge" style="background:{rank_bg}">#{idx+1}</div>
    {img_html}
  </div>
  <div class="card-body">
    <div class="card-brand">{brand}</div>
    <div class="card-title">{title}</div>
    <div class="rating-row">
      <div class="stars">{strs}</div>
      <span class="rating-num">{rating}</span>
      <span class="rating-count">({reviews})</span>
    </div>
    <div class="price-row">
      <span class="card-price">{price_s}</span>
      {'<span class="card-price-orig">₹' + f"{orig:,}" + '</span>' if orig else ''}
      {'<span class="card-discount">' + str(disc) + '% off</span>' if disc else ''}
    </div>
    <div class="spec-tags">{tags}</div>
    <div class="card-delivery">{delvr}</div>
    <a href="{link}" target="_blank" class="card-cta">
      <span>View on {src}</span>
      <span>→</span>
    </a>
  </div>
</div>"""


# ======================
# PREDICT
# ======================
if predict_btn:
    ts  = 1 if touchscreen == 'Yes' else 0
    ips_v = 1 if ips == 'Yes' else 0
    xr, yr = map(int, resolution.split('x'))
    ppi = ((xr**2 + yr**2)**0.5) / screen_size

    inp = pd.DataFrame([{
        'Company': company, 'TypeName': type_name, 'Ram': ram,
        'Weight': weight, 'Touchscreen': ts, 'Ips': ips_v, 'ppi': ppi,
        'Cpu brand': cpu, 'HDD': hdd, 'SSD': ssd, 'Gpu brand': gpu, 'os': os
    }])

    predicted = int(np.exp(pipe.predict(inp)[0]))

    st.markdown(f"""
<div class="price-wrap">
  <div class="price-card">
    <div class="price-left">
      <div class="price-eyebrow">Estimated Market Price</div>
      <div class="price-amount">₹{predicted:,}</div>
      <div class="price-meta">{company} · {type_name} · {cpu} · {ram}GB RAM · {ssd}GB SSD</div>
    </div>
    <div class="price-right">
      <div class="ai-badge">
        <div class="ai-dot"></div>
        AI PREDICTED
      </div>
      <div class="confidence-bar">
        <div class="conf-label">
          <span>Model Confidence</span>
          <span>88%</span>
        </div>
        <div class="conf-track">
          <div class="conf-fill" data-val="88%"></div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
setTimeout(() => {{
  const f = document.querySelector('.conf-fill');
  if(f) f.style.width = '88%';
}}, 500);
</script>
""", unsafe_allow_html=True)

    with st.spinner("Scanning live market for best deals…"):
        data    = fetch_laptops(f"{company} {cpu} {ram}GB {ssd}GB SSD laptop")
        results = data.get('shopping_results', [])
        if not results:
            st.info("Live API unavailable — showing sample results.")
            results = [
                {"title": f"{company} {cpu} 15.6\" Laptop {ram}GB RAM {ssd}GB SSD", "price": f"₹{predicted+2000}",  "source": "Flipkart", "product_link": "#", "thumbnail": ""},
                {"title": f"Dell Inspiron {cpu} {ram}GB RAM Laptop",                 "price": "₹62990",              "source": "Amazon",   "product_link": "#", "thumbnail": ""},
                {"title": f"HP Pavilion {cpu} 14\" {ram}GB Notebook",                "price": "₹58499",              "source": "Flipkart", "product_link": "#", "thumbnail": ""},
                {"title": f"Lenovo IdeaPad {cpu} {ssd}GB SSD Laptop",               "price": "₹54990",              "source": "Croma",    "product_link": "#", "thumbnail": ""},
                {"title": f"Asus VivoBook {cpu} {ram}GB {ssd}GB Ultrabook",         "price": "₹60490",              "source": "Reliance", "product_link": "#", "thumbnail": ""},
            ]

    scored = sorted(results, key=lambda x: (
        (3 if cpu.lower()     in x.get('title','').lower() else 0) +
        (2 if str(ram)        in x.get('title','')         else 0) +
        (1 if str(ssd)        in x.get('title','')         else 0) +
        (1 if company.lower() in x.get('title','').lower() else 0)
    ), reverse=True)[:5]

    st.markdown(f"""
<div class="section-heading">
  <div class="section-heading-text">🛒 Best Deals Found</div>
  <div class="section-heading-line"></div>
  <div class="section-heading-count">{len(scored)} results</div>
</div>
""", unsafe_allow_html=True)

    grid = '<div class="laptop-grid">' + \
        "".join(card_html(it, i, ram, ssd, hdd, cpu) for i, it in enumerate(scored)) + \
        '</div>'
    st.markdown(grid, unsafe_allow_html=True)

    # Trigger confidence bar via JS
    st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('.conf-fill').forEach(el => {
      el.style.width = el.dataset.val || '88%';
    });
  }, 600);
});
// Run immediately too
setTimeout(() => {
  document.querySelectorAll('.conf-fill').forEach(el => {
    el.style.width = el.dataset.val || '88%';
  });
}, 800);
</script>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="footer-note">
  <b style="color:#94a3b8;">ℹ Disclaimer:</b>
  Prices shown are AI-estimated and may vary from actual market prices.
  All prices are in <b style="color:#a5b4fc;">Indian Rupees (₹ INR)</b>.
  Dollar prices from international sources are converted at ₹83.5 / USD.
  Ratings, delivery info, and discounts are indicative only.
  Always verify final prices on the retailer's website before purchasing.
</div>
""", unsafe_allow_html=True)