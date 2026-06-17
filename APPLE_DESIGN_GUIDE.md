# 🍎 CursorOS — Apple-Inspired Design System
## *Design philosophy, visual language, and interaction patterns to make CursorOS feel like it came from Cupertino*

---

## 📐 Table of Contents

1. [The Apple Design Philosophy](#1-the-apple-design-philosophy)
2. [Spatial Design — The Overlay as a "Space"](#2-spatial-design--the-overlay-as-a-space)
3. [Typography — San Francisco, Everywhere](#3-typography--san-francisco-everywhere)
4. [Color System — Light & Dark, Alive](#4-color-system--light--dark-alive)
5. [Materials — Frosted Glass, Layers, Depth](#5-materials--frosted-glass-layers-depth)
6. [Motion — Physics That Feel Real](#6-motion--physics-that-feel-real)
7. [Sound Design — The Silent Detail](#7-sound-design--the-silent-detail)
8. [Iconography — SF Symbols Philosophy](#8-iconography--sf-symbols-philosophy)
9. [Component Redesigns — Apple-Grade UI](#9-component-redesigns--apple-grade-ui)
10. [Complete CSS Design Tokens](#10-complete-css-design-tokens)
11. [Implementation Code — React Components](#11-implementation-code--react-components)
12. [Screens & Flows — How It All Comes Together](#12-screens--flows--how-it-all-comes-together)

---

## 1. The Apple Design Philosophy

Before writing a single line of CSS, you need to internalize *why* Apple software feels the way it does:

### The 7 Principles

| Principle | What It Means for CursorOS |
|---|---|
| **Clarity** | Every element has a purpose. No decorative noise. The user's query and the AI's response are the *only* things that matter. |
| **Deference** | The UI serves the content, never competes with it. The overlay should feel like a lens painted on glass, not a window. |
| **Depth** | Layers of frosted glass create a real sense of z-space. Background is *behind*, content is *in front*, input is *closest*. |
| **Restraint** | One accent color. Two font weights. Three levels of opacity. If you need to add something, remove something first. |
| **Continuity** | Every animation has physical meaning — momentum, friction, spring. Nothing just "appears." |
| **Immersive** | When CursorOS is active, the desktop fades away. The overlay *becomes* the world. |
| **Honest** | No fake skeuomorphism. No unnecessary chrome. A button looks like a button. A divider looks like a divider. |

### What "Apple-Feels-Like" Actually Means

It's not about copying macOS visually. It's about the **quality of attention to detail**:

- **Pixel-perfect alignment** — every padding value is a multiple of 4 (Apple's grid unit)
- **Sub-pixel rendering** — text uses `-webkit-font-smoothing: antialiased` aggressively
- **Intentional whitespace** — Apple uses more padding than you think. Elements breathe.
- **Opacity hierarchy** — primary text is never "white," it's `rgba(255,255,255,0.97)`. Secondary is `0.6`. Tertiary is `0.3`.
- **Rounded corners on everything** — but the radius is *calculated*, not arbitrary. Apple uses `continuity corners` (slightly squircle, not perfect circles)
- **No visible borders** — Apple separates elements with whitespace and subtle shadows, not lines

---

## 2. Spatial Design — The Overlay as a "Space"

### Think in Layers (Z-Axis)

```
┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
│  Desktop (blurred 40px, darkened 60%)              │
│                                                     │
│   ┌─────────────────────────────────────────────┐   │
│   │  Layer 0 — Frosted Glass Panel              │   │
│   │  background: rgba(255,255,255,0.05)         │   │
│   │  backdrop-filter: blur(60px) saturate(1.8)  │   │
│   │  border: 1px solid rgba(255,255,255,0.08)   │   │
│   │                                             │   │
│   │   ┌───────────────────────────────────┐     │   │
│   │   │  Layer 1 — Content Area           │     │   │
│   │   │  (tasks, results, messages)       │     │   │
│   │   └───────────────────────────────────┘     │   │
│   │                                             │   │
│   │   ┌───────────────────────────────────┐     │   │
│   │   │  Layer 2 — Input Bar              │     │   │
│   │   │  (closest to the user)            │     │   │
│   │   │  Inner glow: rgba(255,255,255,0.1) │     │   │
│   │   └───────────────────────────────────┘     │   │
│   └─────────────────────────────────────────────┘   │
└ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘
```

### Spacing System (4px grid)

Apple's design language is built on a **4px base unit**. Every spacing value is a multiple:

```
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-5: 20px
--space-6: 24px
--space-8: 32px
--space-10: 40px
--space-12: 48px
```

Applied to CursorOS:
- Input bar padding: `var(--space-3) var(--space-4)` (12px 16px)
- Task item padding: `var(--space-2) var(--space-4)` (8px 16px)
- Result card internal padding: `var(--space-3) var(--space-4)` (12px 16px)
- Section gaps: `var(--space-4)` (16px)
- Panel internal padding: `var(--space-5)` (20px)

### Dimensions

| Element | Current (Tkinter) | Apple Target | Rationale |
|---|---|---|---|
| Overlay width | 650px | 640px | Multiple of 4, close to Apple.alert width |
| Overlay height (expanded) | 480px | 500px | Rounded, breathing room |
| Overlay corner radius | 0 (sharp) | 20px | macOS Sonoma big sur style |
| Input corner radius | 0 (sharp) | 12px | Pill-shaped for warm feel |
| Result card radius | 0 (sharp) | 12px | Consistent with input |
| Pill indicator height | 4px | 4px | Keep — it's subtle and good |
| Pill indicator width | 120px | 120px | Keep — proportion is right |

---

## 3. Typography — San Francisco, Everywhere

### Font Stack

```css
font-family:
  -apple-system,           /* SF Pro on macOS */
  BlinkMacSystemFont,      /* Chrome on macOS */
  'SF Pro Display',        /* Explicit SF */
  'SF Pro Text',           /* SF Text variant */
  'Segoe UI Variable',     /* Windows Fluent */
  'Segoe UI',              /* Windows fallback */
  system-ui,               /* System default */
  -apple-system,
  sans-serif;
```

### Type Scale

Apple uses **specific, non-linear** sizes. Don't use a mathematical scale — use Apple's actual values:

```css
/* Display — Never used in overlay, but for reference */
--text-display: 34px;
--text-display-weight: 700;

/* Large Title — Overlay title if any */
--text-large-title: 28px;
--text-large-title-weight: 600;

/* Title 1 — Main heading */
--text-title-1: 24px;
--text-title-1-weight: 600;

/* Title 2 — Section heading */
--text-title-2: 20px;
--text-title-2-weight: 600;

/* Title 3 — Subsection */
--text-title-3: 17px;
--text-title-3-weight: 600;

/* Headline — Emphasized body */
--text-headline: 15px;
--text-headline-weight: 600;

/* Body — Primary text (results, descriptions) */
--text-body: 15px;
--text-body-weight: 400;
--text-body-line-height: 1.47059; /* Apple's exact body line-height */

/* Callout — Input text, emphasized */
--text-callout: 14px;
--text-callout-weight: 400;

/* Subheadline — Secondary info */
--text-subhead: 13px;
--text-subhead-weight: 400;

/* Footnote — Timestamps, metadata */
--text-footnote: 12px;
--text-footnote-weight: 400;

/* Caption — Micro labels */
--text-caption: 11px;
--text-caption-weight: 500;
--text-caption-letter-spacing: 0.02em;
--text-caption-text-transform: uppercase;
```

### Applied to CursorOS

| Element | Size | Weight | Opacity |
|---|---|---|---|
| Input text | `--text-callout` (14px) | 500 | 0.97 (primary) |
| Placeholder text | `--text-callout` (14px) | 400 | 0.3 (tertiary) |
| Result filename | `--text-body` (15px) | 600 | 0.97 |
| Result path | `--text-footnote` (12px) | 400 | 0.45 |
| Task description | `--text-subhead` (13px) | 400 | 0.6 (inactive) / 0.97 (active) |
| Mode label | `--text-caption` (11px) | 600 | 0.6 + letter-spacing |
| Section title | `--text-caption` (11px) | 600 | 0.3 + uppercase |
| AI response text | `--text-body` (15px) | 400 | 0.8 |
| Button text | `--text-subhead` (13px) | 600 | 0.97 |

### Trackpad/Keyboard Hint Style

Apple's signature `⌘` style command hints:
```
[⌘ ⇧ Space] to activate
```

Implement with:
```css
.key-hint {
  font-family: SF Mono, 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.05em;
  opacity: 0.35;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  padding: 1px 6px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
```

---

## 4. Color System — Light & Dark, Alive

### Apple's Dynamic Color Philosophy

Apple doesn't use flat hex colors. Every color is an **opacity over the background**, creating depth through layering. In dark mode (which CursorOS should default to):

### Dark Mode Tokens

```css
:root {
  /* ── Background Layers ── */
  --bg-panel:           rgba(30, 30, 30, 0.72);    /* Primary glass panel */
  --bg-panel-solid:     #1e1e1e;                     /* Non-transparent fallback */
  --bg-elevated:        rgba(50, 50, 50, 0.60);      /* Elevated surfaces */
  --bg-input:           rgba(0, 0, 0, 0.30);         /* Input field background */
  --bg-card:            rgba(255, 255, 255, 0.04);   /* Result cards default */
  --bg-card-hover:      rgba(255, 255, 255, 0.08);   /* Result cards hover */
  --bg-button:          rgba(255, 255, 255, 0.10);   /* Secondary buttons */
  --bg-button-hover:    rgba(255, 255, 255, 0.15);   /* Secondary buttons hover */
  --bg-fill-tertiary:   rgba(255, 255, 255, 0.04);   /* Subtle fill */

  /* ── Text ── */
  --text-primary:       rgba(255, 255, 255, 0.97);   /* Headlines, active states */
  --text-secondary:     rgba(255, 255, 255, 0.60);   /* Body text, descriptions */
  --text-tertiary:      rgba(255, 255, 255, 0.30);   /* Placeholders, hints */
  --text-quaternary:    rgba(255, 255, 255, 0.15);   /* Disabled */

  /* ── Separators (not borders!) ── */
  --separator-opaque:   rgba(255, 255, 255, 0.12);   /* Visible dividers */
  --separator-non-opaque: rgba(255, 255, 255, 0.06); /* Hairline */

  /* ── Accent — Apple System Blue ── */
  --accent:             #0A84FF;                      /* Vibrant dark-mode blue */
  --accent-hover:       #409CFF;                      /* Lighter on hover */
  --accent-pressed:     #0066CC;                      /* Darker on press */
  --accent-glow:        rgba(10, 132, 255, 0.25);     /* Subtle glow halo */
  --accent-fill:        rgba(10, 132, 255, 0.15);     /* Tinted backgrounds */

  /* ── Semantic — Apple's exact values ── */
  --success:            #30D158;                      /* System Green */
  --success-fill:       rgba(48, 209, 88, 0.15);
  --warning:            #FFD60A;                      /* System Yellow */
  --warning-fill:       rgba(255, 214, 10, 0.15);
  --error:              #FF453A;                      /* System Red */
  --error-fill:         rgba(255, 69, 58, 0.15);

  /* ── Overlays ── */
  --bg-scrim:           rgba(0, 0, 0, 0.32);         /* Background scrim */
}
```

### Light Mode (for completeness)

```css
.light {
  --bg-panel:           rgba(255, 255, 255, 0.72);
  --bg-panel-solid:     #ffffff;
  --bg-elevated:        rgba(255, 255, 255, 0.60);
  --bg-card:            rgba(0, 0, 0, 0.03);
  --bg-card-hover:      rgba(0, 0, 0, 0.06);
  --text-primary:       rgba(0, 0, 0, 0.97);
  --text-secondary:     rgba(0, 0, 0, 0.60);
  --text-tertiary:      rgba(0, 0, 0, 0.30);
  --separator-opaque:   rgba(0, 0, 0, 0.12);
  --separator-non-opaque: rgba(0, 0, 0, 0.06);
  --accent:             #007AFF;       /* Light-mode blue */
}
```

### The Key Insight About Apple Colors

**Apple never uses pure white (#FFFFFF) or pure black (#000000) as backgrounds.** Even macOS's "dark" mode uses `#1e1e1e` (not `#000`), and "light" mode uses `#ffffff` with opacity for glass panels. This creates the feeling of **depth** rather than flatness.

---

## 5. Materials — Frosted Glass, Layers, Depth

### The Glass Panel (macOS Sonoma / Control Center Style)

This is the **single most important visual element**. Your overlay IS the glass panel.

```css
.glass-panel {
  /* ── Base ── */
  background: rgba(30, 30, 30, 0.72);

  /* ── Frost Engine ── */
  backdrop-filter:
    blur(60px)                    /* Heavy blur for desktop behind */
    saturate(1.8)                 /* Boost colors beneath */
    brightness(1.1);              /* Slight brightness lift */
  -webkit-backdrop-filter:
    blur(60px)
    saturate(1.8)
    brightness(1.1);

  /* ── Edge highlight (the "lip" that catches light) ── */
  border: 1px solid rgba(255, 255, 255, 0.08);

  /* ── Shape ── */
  border-radius: 20px;

  /* ── Shadow (multi-layer for realism) ── */
  box-shadow:
    /* Outer ambient shadow */
    0 22px 70px 4px rgba(0, 0, 0, 0.56),
    /* Mid shadow */
    0 8px 24px rgba(0, 0, 0, 0.32),
    /* Inner edge highlight (top) */
    inset 0 0.5px 0 0 rgba(255, 255, 255, 0.10),
    /* Inner edge highlight (bottom) */
    inset 0 -0.5px 0 0 rgba(255, 255, 255, 0.04);
}
```

### Input Field (Vibrancy Style)

Apple's input fields have a distinctive inner glow:

```css
.apple-input {
  background: rgba(0, 0, 0, 0.30);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow:
    inset 0 1px 0 0 rgba(255, 255, 255, 0.06),
    inset 0 -1px 0 0 rgba(255, 255, 255, 0.02),
    0 1px 2px rgba(0, 0, 0, 0.12);
}

.apple-input:focus {
  border-color: rgba(10, 132, 255, 0.4);
  box-shadow:
    inset 0 1px 0 0 rgba(255, 255, 255, 0.06),
    inset 0 -1px 0 0 rgba(255, 255, 255, 0.02),
    0 0 0 3px rgba(10, 132, 255, 0.15),  /* Focus ring */
    0 1px 2px rgba(0, 0, 0, 0.12);
}
```

### Mode Pill (Segmented Control Style)

```css
.apple-segment {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  padding: 4px 12px;
  color: rgba(255, 255, 255, 0.6);
  transition: all 0.2s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.apple-segment:hover {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.10);
}
```

---

## 6. Motion — Physics That Feel Real

### Apple's Animation Curve

Apple's signature easing curve is:

```css
cubic-bezier(0.25, 0.1, 0.25, 1.0)
```

This is **not** `ease-in-out`. It starts slightly fast, then decelerates naturally. Use this as your default timing function.

### Animation Timing Scale

| Speed | Duration | Use Case |
|---|---|---|
| **Instant** | 0ms | State toggles (checkbox, icon change) |
| **Fast** | 150ms | Hover states, micro-interactions |
| **Normal** | 250ms | Focus changes, dropdowns |
| **Slow** | 400ms | Panel expand/collapse |
| **Dramatic** | 600ms | Overlay entrance/exit |

### Framer Motion Presets for CursorOS

```jsx
// ── Pill → Panel Expand (the hero animation) ──
const expandAnimation = {
  initial: {
    opacity: 0,
    scale: 0.85,
    y: -10,
    filter: 'blur(10px)',
  },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    filter: 'blur(0px)',
  },
  exit: {
    opacity: 0,
    scale: 0.92,
    y: -6,
    filter: 'blur(6px)',
  },
  transition: {
    duration: 0.5,
    ease: [0.25, 0.1, 0.25, 1.0],
  },
};

// ── Item Stagger (for task list, results) ──
const staggerItem = (index) => ({
  initial: { opacity: 0, y: 8, scale: 0.98 },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      delay: index * 0.06,
      duration: 0.35,
      ease: [0.25, 0.1, 0.25, 1.0],
    },
  },
});

// ── Task Status Dot Pulse ──
const pulseAnimation = {
  animate: {
    scale: [1, 1.5, 1],
    opacity: [0.6, 1, 0.6],
  },
  transition: {
    duration: 1.2,
    repeat: Infinity,
    ease: 'easeInOut',
  },
};

// ── Spinner (Apple-style, not full rotation) ──
const spinnerAnimation = {
  animate: {
    rotate: [0, 320], // Not 360 — Apple's spinner has a gap
  },
  transition: {
    duration: 1.0,
    repeat: Infinity,
    ease: 'linear',
  },
};

// ── Background Dim (entire desktop) ──
const backdropAnimation = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1.0] },
};
```

### The Blur Transition Secret

Apple's transitions almost always include a **blur filter** in addition to opacity/scale. This creates the feeling of something coming into focus:

```css
/* Element arriving */
@keyframes apple-enter {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.98);
    filter: blur(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0px);
  }
}

/* Element departing */
@keyframes apple-exit {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0px);
  }
  to {
    opacity: 0;
    transform: translateY(-4px) scale(0.98);
    filter: blur(6px);
  }
}
```

---

## 7. Sound Design — The Silent Detail

Apple pays extreme attention to sound. For CursorOS, subtle audio cues should accompany:

| Event | Sound Type | Character |
|---|---|---|
| Overlay appears | Soft "thud" | Like setting a glass on a table |
| Query submitted | Subtle "click" | Mechanical, satisfying |
| Task completes | Gentle "ding" | Single tone, positive |
| Error | Soft "buzz" | Two low tones |
| Overlay closes | Reverse "thud" | Fading, like lifting glass |
| Result appears | Micro "pop" | Almost subliminal |

### Implementation

```js
// Use Web Audio API for zero-dependency sounds
class AppleSound {
  constructor() {
    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
  }

  play(kind) {
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.connect(gain);
    gain.connect(this.ctx.destination);

    const configs = {
      appear:   { freq: 120, duration: 0.08, type: 'sine', vol: 0.06 },
      submit:   { freq: 800, duration: 0.02, type: 'sine', vol: 0.03 },
      complete: { freq: 523, duration: 0.12, type: 'sine', vol: 0.05 },
      error:    { freq: 200, duration: 0.15, type: 'sawtooth', vol: 0.04 },
      close:    { freq: 100, duration: 0.10, type: 'sine', vol: 0.04 },
    };

    const cfg = configs[kind];
    osc.type = cfg.type;
    osc.frequency.setValueAtTime(cfg.freq, this.ctx.currentTime);
    gain.gain.setValueAtTime(cfg.vol, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + cfg.duration);

    osc.start();
    osc.stop(this.ctx.currentTime + cfg.duration);
  }
}
```

---

## 8. Iconography — SF Symbols Philosophy

### Icon System Rules

1. **Use SF Symbols** when possible (via `sf-symbols-web` or similar)
2. **Fallback to Lucide React** — it's the closest open-source equivalent
3. **All icons are line-based, not filled** — Apple uses outlines almost exclusively
4. **Consistent weight** — use `strokeWidth: 1.5` for all icons
5. **Color = meaning, not decoration**

### Icon Mapping

| Context | Icon | Notes |
|---|---|---|
| Send / Submit | `ArrowUp` inside circle | Apple-style circular button |
| File | `File` | Outline, not filled |
| Folder | `Folder` | Outline, warm color |
| Command / Mode | `Terminal` or `Sparkles` | Contextual |
| Search | `Search` | In the input field (left or right) |
| Loading | Custom spinner | Apple arc, not full circle |
| Success | `CheckCircle2` | Green, animated checkmark |
| Error | `XCircle` | Red, maybe with shake animation |
| Settings | `Settings` (gear) | In tray menu |
| Quit | `Power` | In tray menu |

### Spinner Component (Apple-Style)

```jsx
function AppleSpinner({ size = 16, color = 'rgba(255,255,255,0.5)' }) {
  return (
    <motion.svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      animate={{ rotate: 320 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear',
      }}
    >
      <circle
        cx="12" cy="12" r="9"
        fill="none"
        stroke={color}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeDasharray="40 14"
      />
    </motion.svg>
  );
}
```

---

## 9. Component Redesigns — Apple-Grade UI

### 9.1 The Overlay Container

```
┌──────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ ╭─────╮                                                      │ │
│ │ │Auto │  ┌─────────────────────────────────────┐  ┌──────┐  │ │
│ │ ╰─────╯  │ Ask anything...                     │  │  ↑   │  │ │
│ │          └─────────────────────────────────────┘  └──────┘  │ │
│ │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │ │
│ │                                                               │ │
│ │  ●  Analyzing your request...                                │ │
│ │  ✓  Searching for files...                                   │ │
│ │                                                               │ │
│ │  ┌─────────────────────────────────────────────────────────┐ │ │
│ │  │ 📄  project_report.pdf                                  │ │ │
│ │  │     C:\Users\Kurian\Documents\Work\project_report.pdf   │ │ │
│ │  └─────────────────────────────────────────────────────────┘ │ │
│ │  ┌─────────────────────────────────────────────────────────┐ │ │
│ │  │ 📁  Assets                                              │ │ │
│ │  │     C:\Users\Kurian\Documents\Work\Assets               │ │ │
│ │  └─────────────────────────────────────────────────────────┘ │ │
│ │                                                               │ │
│ │                                    ┌──────────────────────┐  │ │
│ │                                    │   ▶  Execute Plan    │  │ │
│ │                                    └──────────────────────┘  │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 9.2 Input Bar (Biggest Visual Upgrade from Tkinter)

The input bar is the **hero element** — it should feel premium:

```jsx
// AppleInput.jsx
<div className="relative">
  {/* Glow ring that appears on focus */}
  <motion.div
    className="absolute -inset-[1px] rounded-[10px] pointer-events-none"
    animate={{
      boxShadow: focused
        ? '0 0 0 3px rgba(10, 132, 255, 0.15)'
        : '0 0 0 0px transparent',
    }}
  />

  <div
    className={`
      flex items-center gap-3 rounded-[10px] px-4 py-2.5
      bg-[rgba(0,0,0,0.30)]
      border border-[rgba(255,255,255,0.06)]
      transition-all duration-200
      ${focused ? 'border-[rgba(10,132,255,0.3)]' : ''}
    `}
    style={{
      boxShadow: focused
        ? 'inset 0 1px 0 0 rgba(255,255,255,0.08), 0 1px 3px rgba(0,0,0,0.15)'
        : 'inset 0 1px 0 0 rgba(255,255,255,0.04), 0 1px 2px rgba(0,0,0,0.10)',
    }}
  >
    <Search size={15} className="opacity-30 shrink-0" />

    <input
      ref={inputRef}
      type="text"
      value={value}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      onChange={(e) => setValue(e.target.value)}
      onKeyDown={handleKeyDown}
      placeholder={placeholder}
      className="flex-1 bg-transparent border-none outline-none text-[14px] font-medium text-[rgba(255,255,255,0.97)] placeholder-[rgba(255,255,255,0.25)] caret-[#0A84FF]"
    />

    {value.trim() && (
      <motion.button
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0, opacity: 0 }}
        transition={{ type: 'spring', stiffness: 600, damping: 25 }}
        onClick={handleSubmit}
        className="w-7 h-7 rounded-full bg-[#0A84FF] flex items-center justify-center hover:bg-[#409CFF] active:bg-[#0066CC] transition-colors"
      >
        <ArrowUp size={14} className="text-white" strokeWidth={2.5} />
      </motion.button>
    )}
  </div>
</div>
```

### 9.3 File Result Cards (Apple List Style)

```jsx
<motion.div
  initial={{ opacity: 0, y: 6 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ delay: index * 0.05, duration: 0.3 }}
  whileHover={{ backgroundColor: 'rgba(255,255,255,0.07)' }}
  onClick={() => onSelect(item)}
  className="group flex items-center gap-3 px-3 py-2.5 rounded-[10px] cursor-pointer transition-colors duration-150"
>
  {/* File icon container */}
  <div className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
    style={{ backgroundColor: `${iconColor}18` }}
  >
    <Icon size={18} style={{ color: iconColor }} />
  </div>

  {/* Text */}
  <div className="flex-1 min-w-0">
    <div className="text-[13px] font-semibold text-[rgba(255,255,255,0.95)] truncate group-hover:text-white transition-colors">
      {filename}
    </div>
    <div className="text-[11px] text-[rgba(255,255,255,0.35)] truncate mt-0.5">
      {path}
    </div>
  </div>

  {/* Chevron (Apple always shows disclosure) */}
  <ChevronRight size={14} className="opacity-0 group-hover:opacity-25 transition-opacity shrink-0" />
</motion.div>
```

### 9.4 Task Status List (Progress Style)

```jsx
{tasks.map((task, i) => (
  <motion.div
    key={task.id}
    initial={{ opacity: 0, x: -8 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay: i * 0.08, duration: 0.3 }}
    className="flex items-center gap-3 py-2"
  >
    {/* Status indicator */}
    <div className="w-4 h-4 flex items-center justify-center">
      {task.status === 'in-progress' && <AppleSpinner size={14} />}
      {task.status === 'completed' && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 600, damping: 20 }}
        >
          <CheckCircle2 size={14} className="text-[#30D158]" />
        </motion.div>
      )}
      {task.status === 'failed' && (
        <XCircle size={14} className="text-[#FF453A]" />
      )}
      {task.status === 'pending' && (
        <div className="w-1.5 h-1.5 rounded-full bg-[rgba(255,255,255,0.15)]" />
      )}
    </div>

    {/* Description */}
    <span
      className="text-[13px] transition-colors duration-200"
      style={{
        color: task.status === 'in-progress'
          ? 'rgba(255,255,255,0.95)'
          : 'rgba(255,255,255,0.45)',
        fontWeight: task.status === 'in-progress' ? 500 : 400,
      }}
    >
      {task.description}
    </span>
  </motion.div>
))}
```

### 9.5 AI Response (Markdown Renderer)

```jsx
<motion.div
  initial={{ opacity: 0, y: 10, filter: 'blur(4px)' }}
  animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
  transition={{ duration: 0.4 }}
  className="py-3 px-1"
>
  <div
    className="text-[14px] leading-relaxed text-[rgba(255,255,255,0.75)]"
    style={{ lineHeight: 1.6 }}
  >
    {/* Render markdown content here */}
    {message}
  </div>
</motion.div>
```

### 9.6 The Pill Indicator (Collapsed State)

The pill should be more elegant than Tkinter's flat rectangle:

```jsx
<motion.div
  className="w-[100px] h-[4px] rounded-full mx-auto cursor-pointer"
  style={{
    background: 'linear-gradient(90deg, rgba(10,132,255,0.4), rgba(10,132,255,0.8), rgba(10,132,255,0.4))',
    boxShadow: '0 0 12px rgba(10, 132, 255, 0.3)',
  }}
  whileHover={{
    width: 120,
    boxShadow: '0 0 20px rgba(10, 132, 255, 0.5)',
  }}
  onClick={onShow}
/>
```

---

## 10. Complete CSS Design Tokens

Single file to copy-paste: `src/renderer/styles/apple-tokens.css`

```css
:root {
  /* ═══════════════════════════════════════════
     APPLE DESIGN TOKEN SYSTEM — CursorOS
     ═══════════════════════════════════════════ */

  /* ── Grid ── */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;

  /* ── Typography ── */
  --font-sf: -apple-system, BlinkMacSystemFont,
    'SF Pro Display', 'SF Pro Text',
    'Segoe UI Variable', 'Segoe UI',
    system-ui, sans-serif;
  --font-sf-mono: 'SF Mono', 'JetBrains Mono', 'Fira Code', monospace;

  --text-34: 34px; --w-34: 700;
  --text-28: 28px; --w-28: 700;
  --text-24: 24px; --w-24: 600;
  --text-20: 20px; --w-20: 600;
  --text-17: 17px; --w-17: 600;
  --text-15: 15px; --w-15: 400;
  --text-14: 14px; --w-14: 400;
  --text-13: 13px; --w-13: 400;
  --text-12: 12px; --w-12: 400;
  --text-11: 11px; --w-11: 500;

  /* ── Colors — Dark Mode ── */
  --bg-glass: rgba(30, 30, 30, 0.72);
  --bg-elevated: rgba(50, 50, 50, 0.60);
  --bg-input: rgba(0, 0, 0, 0.30);
  --bg-card: rgba(255, 255, 255, 0.04);
  --bg-card-hover: rgba(255, 255, 255, 0.08);
  --bg-button: rgba(255, 255, 255, 0.10);
  --bg-button-hover: rgba(255, 255, 255, 0.15);

  --text-1: rgba(255, 255, 255, 0.97);
  --text-2: rgba(255, 255, 255, 0.60);
  --text-3: rgba(255, 255, 255, 0.30);
  --text-4: rgba(255, 255, 255, 0.15);

  --separator: rgba(255, 255, 255, 0.10);
  --separator-hairline: rgba(255, 255, 255, 0.06);

  --blue: #0A84FF;
  --blue-hover: #409CFF;
  --blue-pressed: #0066CC;
  --blue-glow: rgba(10, 132, 255, 0.20);
  --blue-fill: rgba(10, 132, 255, 0.12);

  --green: #30D158;
  --green-fill: rgba(48, 209, 88, 0.12);
  --red: #FF453A;
  --red-fill: rgba(255, 69, 58, 0.12);
  --yellow: #FFD60A;
  --yellow-fill: rgba(255, 214, 10, 0.12);

  /* ── Radius ── */
  --radius-panel: 20px;
  --radius-card: 12px;
  --radius-input: 10px;
  --radius-button: 8px;
  --radius-pill: 6px;
  --radius-full: 9999px;

  /* ── Shadows ── */
  --shadow-panel:
    0 22px 70px 4px rgba(0, 0, 0, 0.56),
    0 8px 24px rgba(0, 0, 0, 0.32),
    inset 0 0.5px 0 0 rgba(255, 255, 255, 0.10);
  --shadow-card:
    0 2px 8px rgba(0, 0, 0, 0.20);
  --shadow-input:
    inset 0 1px 0 0 rgba(255, 255, 255, 0.06),
    0 1px 2px rgba(0, 0, 0, 0.12);

  /* ── Blur ── */
  --blur-panel: blur(60px) saturate(1.8) brightness(1.1);
  --blur-light: blur(20px) saturate(1.4);

  /* ── Animation ── */
  --ease-apple: cubic-bezier(0.25, 0.1, 0.25, 1.0);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1.0);
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --duration-dramatic: 600ms;
}

/* ── Global Resets ── */
*, *::before, *::after {
  box-sizing: border-box;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

html, body, #root {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: transparent;
  font-family: var(--font-sf);
  color: var(--text-1);
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

/* ── Glass Panel ── */
.apple-glass {
  background: var(--bg-glass);
  backdrop-filter: var(--blur-panel);
  -webkit-backdrop-filter: var(--blur-panel);
  border: 1px solid var(--separator-hairline);
  border-radius: var(--radius-panel);
  box-shadow: var(--shadow-panel);
}

/* ── Apple Scrollbar ── */
.apple-scroll::-webkit-scrollbar {
  width: 6px;
  background: transparent;
}
.apple-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.apple-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 3px;
}
.apple-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.20);
}
```

---

## 11. Implementation Code — React Components

### 11.1 Complete Overlay Component (Apple Style)

```jsx
// AppleOverlay.jsx
import { motion, AnimatePresence } from 'framer-motion';
import AppleInput from './AppleInput';
import AppleTaskList from './AppleTaskList';
import AppleResults from './AppleResults';
import AppleActionBar from './AppleActionBar';
import AppleSpinner from './AppleSpinner';

export default function AppleOverlay({
  mode, onModeToggle, onSubmit, onSelect,
  onExecute, onConfirmOrg,
  tasks, results, orgPreview, planReady, message
}) {
  return (
    <motion.div
      className="apple-glass w-full h-full flex flex-col overflow-hidden"
      initial={{ opacity: 0, scale: 0.88, y: -12, filter: 'blur(10px)' }}
      animate={{ opacity: 1, scale: 1, y: 0, filter: 'blur(0px)' }}
      exit={{ opacity: 0, scale: 0.92, y: -6, filter: 'blur(6px)' }}
      transition={{ duration: 0.45, ease: [0.25, 0.1, 0.25, 1.0] }}
    >
      {/* ── Header ── */}
      <div className="flex items-center gap-3 px-5 py-3.5 shrink-0">
        {/* Mode Pill */}
        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
          onClick={onModeToggle}
          className="px-3 py-1.5 rounded-[6px] text-[11px] font-semibold tracking-[0.02em] cursor-pointer select-none transition-colors duration-150"
          style={{
            color: 'rgba(255,255,255,0.55)',
            background: 'rgba(255,255,255,0.06)',
            border: '1px solid rgba(255,255,255,0.04)',
          }}
        >
          {mode}
        </motion.button>

        {/* Input */}
        <AppleInput onSubmit={onSubmit} />
      </div>

      {/* ── Separator (hairline, not a border) ── */}
      <div
        className="h-px mx-5 shrink-0"
        style={{ background: 'var(--separator)' }}
      />

      {/* ── Content ── */}
      <div className="flex-1 overflow-y-auto apple-scroll px-4 py-2">
        <AppleTaskList tasks={tasks} />

        <AnimatePresence>
          {results && (
            <AppleResults items={results} onSelect={onSelect} />
          )}
        </AnimatePresence>

        {orgPreview && (
          <AppleOrgPreview proposal={orgPreview} onConfirm={onConfirmOrg} />
        )}

        {message && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
            className="py-3 px-1"
          >
            <p className="text-[14px] leading-relaxed text-[rgba(255,255,255,0.7)]">
              {message}
            </p>
          </motion.div>
        )}
      </div>

      {/* ── Action Bar ── */}
      <AnimatePresence>
        {planReady && (
          <AppleActionBar onExecute={onExecute} />
        )}
      </AnimatePresence>
    </motion.div>
  );
}
```

### 11.2 Action Bar (Apple Style)

```jsx
// AppleActionBar.jsx
import { motion } from 'framer-motion';
import { Play } from 'lucide-react';

export default function AppleActionBar({ onExecute }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 12 }}
      transition={{ duration: 0.35 }}
      className="px-5 py-3.5 shrink-0 flex justify-end"
      style={{ borderTop: '1px solid var(--separator)' }}
    >
      <motion.button
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        onClick={onExecute}
        className="flex items-center gap-2 px-5 py-2 rounded-[8px] text-[13px] font-semibold text-white cursor-pointer"
        style={{
          background: 'linear-gradient(180deg, #0A84FF 0%, #006EE6 100%)',
          boxShadow: '0 2px 8px rgba(10, 132, 255, 0.3), inset 0 1px 0 0 rgba(255,255,255,0.15)',
        }}
      >
        <Play size={13} fill="white" />
        Execute Plan
      </motion.button>
    </motion.div>
  );
}
```

### 11.3 Animated Sentences for AI Responses

Apple often reveals AI text word-by-word. Here's how:

```jsx
// TypewriterText.jsx
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export default function TypewriterText({ text, speed = 30 }) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);

  useEffect(() => {
    let i = 0;
    setDisplayed('');
    setDone(false);
    const interval = setInterval(() => {
      if (i < text.length) {
        setDisplayed(text.slice(0, i + 1));
        i++;
      } else {
        setDone(true);
        clearInterval(interval);
      }
    }, speed);
    return () => clearInterval(interval);
  }, [text, speed]);

  return (
    <span>
      {displayed}
      {!done && (
        <motion.span
          animate={{ opacity: [1, 0] }}
          transition={{ repeat: Infinity, duration: 0.5 }}
          className="inline-block w-[2px] h-[14px] bg-[#0A84FF] ml-0.5 align-middle"
        />
      )}
    </span>
  );
}
```

---

## 12. Screens & Flows — How It All Comes Together

### Flow 1: Quick Search

```
Time    Screen                           Notes
─────   ──────────────────────────────   ───────────────────
0ms     [Desktop visible]                User presses ⌘⇧Space
80ms     ┌─── ··· ───┐                   Blue pill glows, appears top-center
         └───────────┘
200ms    ┌──────────────────────────┐     Glass panel expands
         │ Auto │ Ask anything...  ↑│     Input auto-focused
         │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │     
         │                          │     Empty state, breathing
         └──────────────────────────┘     
350ms    │ Auto │ find...          ↑│     User types
         │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │     
         │  ○  Searching files...  │     Task step appears (stagger)
         └──────────────────────────┘     
600ms    │ Auto │ find...          ↑│     
         │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │     Results appear one by one
         │  ✓  Searching files...  │     (each with 50ms delay)
         │ ┌──────────────────────┐│     
         │ │ 📄 report.pdf        ││     
         │ └──────────────────────┘│     
         │ ┌──────────────────────┐│     
         │ │ 📄 summary.docx      ││     
         │ └──────────────────────┘│     
         └──────────────────────────┘     
```

### Flow 2: Organization Plan

```
Time    Screen                           Notes
─────   ──────────────────────────────   ───────────────────
0ms     │ Plan │ organize downloads↑│    Plan mode active
        │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │     
        │  ◉  Analyzing folder... │     Spinner animating
        └──────────────────────────┘     
400ms   │  ✓  Analyzing folder... │     Checkmark (spring)
        │  ○  Scanning files...   │     Next task starts
        └──────────────────────────┘     
800ms   │  ✓  Analyzing folder... │     
        │  ✓  Scanning files...   │     
        │                          │     Org preview appears
        │  ┌─ Organization Plan ─┐ │     With edit boxes
        │  │ photo.jpg → Images │ │     
        │  │ notes.txt → Docs   │ │     
        │  └────────────────────┘ │     
        │              [▶ Execute] │     Blue button pulses once
        └──────────────────────────┘     
```

### Flow 3: AI Chat Response

```
Time    Screen                           Notes
─────   ──────────────────────────────   ───────────────────
0ms     │ Auto │ summarize this   ↑│    Content peek query
        │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │     
        │  ○  Reading file...     │     
        └──────────────────────────┘     
500ms   │  ✓  Reading file...     │     
        │  ○  Analyzing content...│     Typing indicator
        └──────────────────────────┘     
800ms   │  ✓  Reading file...     │     AI response appears
        │  ✓  Analyzing content...│     word by word with
        │                          │     blinking cursor
        │  This Q3 report covers   │     
        │  revenue growth of 23%.. │ ▌   
        └──────────────────────────┘     
```

---

## 🎯 Summary: The Apple Checklist

Every time you work on a component, run through this:

- [ ] **No pure white/black** — use `rgba()` with slight color temperature
- [ ] **4px grid** — all padding/margins are multiples of 4
- [ ] **Corners are calculated** — panel 20px, cards 12px, inputs 10px
- [ ] **Typography is SF** — correct sizes, correct weights, correct opacity
- [ ] **No visible borders** — separate with whitespace, shadows, hairlines
- [ ] **Animations have physics** — ease `[0.25, 0.1, 0.25, 1.0]`, springs, blur transitions
- [ ] **Blur filter on enter/exit** — things come into focus, not just appear
- 