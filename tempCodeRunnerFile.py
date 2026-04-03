
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