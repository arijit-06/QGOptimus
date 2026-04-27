import { useEffect, useRef } from 'react'

/**
 * Full-page particle background.
 *
 * Left half  → ordered lattice (classical / deterministic)
 * Right half → chaotic brownian network (quantum / probabilistic)
 *
 * The two regions blur into each other near the centre, mirroring the
 * classical-vs-quantum theme of the app.
 */
export default function ParticleBackground() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const dpr = window.devicePixelRatio || 1

    /* ── resize helper ─────────────────────────────────────────── */
    function resize() {
      const w = window.innerWidth
      const h = window.innerHeight
      canvas.width = w * dpr
      canvas.height = h * dpr
      canvas.style.width = `${w}px`
      canvas.style.height = `${h}px`
      ctx.scale(dpr, dpr)
      return { w, h }
    }

    let { w, h } = resize()

    /* ── colour palette ────────────────────────────────────────── */
    // Classical side  → cool blue-cyan
    // Quantum side    → warm violet-magenta
    const CLASSICAL_HUE = 195  // cyan-ish
    const QUANTUM_HUE   = 270  // violet

    /* ── Particle class ────────────────────────────────────────── */
    class Particle {
      constructor(x, y, ordered) {
        this.x = x
        this.y = y
        this.ox = x          // original / anchor position
        this.oy = y
        this.ordered = ordered
        this.size = ordered ? 1.8 : 1.5
        this.vx = (Math.random() - 0.5) * 1.8
        this.vy = (Math.random() - 0.5) * 1.8
        this.influence = 0   // how much chaos bleeds into this ordered particle
        this.neighbors = []
        // t drives a gentle breathing oscillation for ordered particles
        this.phase = Math.random() * Math.PI * 2
      }

      update(t) {
        if (this.ordered) {
          /* ordered: tries to return home, but neighbours pull it away */
          const dx = this.ox - this.x
          const dy = this.oy - this.y

          let cx = 0, cy = 0, maxInf = 0
          for (const nb of this.neighbors) {
            if (nb.ordered) continue
            const d = Math.hypot(this.x - nb.x, this.y - nb.y)
            const str = Math.max(0, 1 - d / 120)
            cx += nb.vx * str
            cy += nb.vy * str
            if (str > maxInf) maxInf = str
          }

          const blend = this.influence
          this.x += dx * 0.04 * (1 - blend) + cx * blend * 0.6
          this.y += dy * 0.04 * (1 - blend) + cy * blend * 0.6
          this.influence = Math.max(maxInf, this.influence * 0.985)

          /* subtle breathing oscillation so the ordered side feels alive */
          this.x += Math.sin(t * 0.015 + this.phase) * 0.18
          this.y += Math.cos(t * 0.013 + this.phase) * 0.18
        } else {
          /* chaotic: brownian walk with wall reflection */
          this.vx += (Math.random() - 0.5) * 0.45
          this.vy += (Math.random() - 0.5) * 0.45
          this.vx *= 0.94
          this.vy *= 0.94
          this.x += this.vx
          this.y += this.vy

          if (this.x < w / 2) { this.vx = Math.abs(this.vx); this.x = w / 2 }
          if (this.x > w)     { this.vx = -Math.abs(this.vx); this.x = w }
          if (this.y < 0)     { this.vy = Math.abs(this.vy);  this.y = 0 }
          if (this.y > h)     { this.vy = -Math.abs(this.vy); this.y = h }
        }
      }

      /* fractional position across full width (0 = left edge, 1 = right edge) */
      get frac() { return this.x / w }

      /* blended hue between classical and quantum based on x position */
      get hue() {
        const t = Math.min(1, Math.max(0, (this.x / w - 0.35) / 0.3))
        return CLASSICAL_HUE + (QUANTUM_HUE - CLASSICAL_HUE) * t
      }

      draw() {
        const alpha = this.ordered
          ? 0.75 - this.influence * 0.45
          : 0.7
        const sat = this.ordered ? 70 : 85
        const lit = this.ordered ? 72 : 68
        ctx.fillStyle = `hsla(${this.hue}, ${sat}%, ${lit}%, ${alpha})`
        ctx.beginPath()
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
        ctx.fill()
      }
    }

    /* ── build particle grid ───────────────────────────────────── */
    let particles = []

    function buildParticles() {
      particles = []

      /* ordered lattice – left half */
      const cols = Math.round(w / 2 / 38)
      const rows = Math.round(h / 38)
      const sx   = (w / 2) / cols
      const sy   = h / rows
      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          particles.push(new Particle(sx * i + sx / 2, sy * j + sy / 2, true))
        }
      }

      /* chaotic particles – right half */
      const area   = (w / 2) * h
      const count  = Math.round(area / 1400)
      for (let k = 0; k < count; k++) {
        particles.push(new Particle(
          w / 2 + Math.random() * w / 2,
          Math.random() * h,
          false
        ))
      }
    }

    buildParticles()

    /* ── neighbour update (cheap spatial) ─────────────────────── */
    const NEIGHBOUR_DIST = 130

    function updateNeighbors() {
      for (const p of particles) p.neighbors = []
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const a = particles[i], b = particles[j]
          const d = Math.hypot(a.x - b.x, a.y - b.y)
          if (d < NEIGHBOUR_DIST) {
            a.neighbors.push(b)
            b.neighbors.push(a)
          }
        }
      }
    }
    updateNeighbors()

    /* ── animation loop ────────────────────────────────────────── */
    let t = 0
    let raf

    function animate() {
      const W = window.innerWidth
      const H = window.innerHeight
      ctx.clearRect(0, 0, W, H)

      /* update neighbours every 25 frames */
      if (t % 25 === 0) updateNeighbors()

      /* draw edges first */
      const EDGE_DIST = 55
      for (const p of particles) {
        for (const nb of p.neighbors) {
          if (nb === p) continue
          const d = Math.hypot(p.x - nb.x, p.y - nb.y)
          if (d < EDGE_DIST) {
            const alpha = 0.18 * (1 - d / EDGE_DIST)
            // hue at midpoint
            const mx = (p.x + nb.x) / 2
            const t2 = Math.min(1, Math.max(0, (mx / W - 0.35) / 0.3))
            const hue = CLASSICAL_HUE + (QUANTUM_HUE - CLASSICAL_HUE) * t2
            ctx.strokeStyle = `hsla(${hue}, 75%, 70%, ${alpha})`
            ctx.lineWidth = 0.6
            ctx.beginPath()
            ctx.moveTo(p.x, p.y)
            ctx.lineTo(nb.x, nb.y)
            ctx.stroke()
          }
        }
      }

      /* update and draw particles */
      for (const p of particles) {
        p.update(t)
        p.draw()
      }

      /* soft divider line */
      const grad = ctx.createLinearGradient(W / 2, 0, W / 2, H)
      grad.addColorStop(0,   'hsla(230, 60%, 80%, 0)')
      grad.addColorStop(0.3, 'hsla(230, 60%, 80%, 0.12)')
      grad.addColorStop(0.7, 'hsla(230, 60%, 80%, 0.12)')
      grad.addColorStop(1,   'hsla(230, 60%, 80%, 0)')
      ctx.strokeStyle = grad
      ctx.lineWidth = 0.8
      ctx.beginPath()
      ctx.moveTo(W / 2, 0)
      ctx.lineTo(W / 2, H)
      ctx.stroke()

      t++
      raf = requestAnimationFrame(animate)
    }

    animate()

    /* ── resize handler ────────────────────────────────────────── */
    function onResize() {
      const dims = resize()
      w = dims.w
      h = dims.h
      buildParticles()
      updateNeighbors()
    }
    window.addEventListener('resize', onResize)

    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', onResize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        inset: 0,
        width: '100vw',
        height: '100vh',
        zIndex: 0,
        display: 'block',
        background: 'linear-gradient(135deg, #070b18 0%, #0d0f26 55%, #130b22 100%)',
      }}
    />
  )
}
