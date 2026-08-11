---
name: Obsidian Glass
colors:
  surface: '#111417'
  surface-dim: '#111417'
  surface-bright: '#37393d'
  surface-container-lowest: '#0c0e12'
  surface-container-low: '#191c1f'
  surface-container: '#1d2023'
  surface-container-high: '#282a2e'
  surface-container-highest: '#323539'
  on-surface: '#e1e2e7'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#e1e2e7'
  inverse-on-surface: '#2e3134'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#4cd7f6'
  on-secondary: '#003640'
  secondary-container: '#03b5d3'
  on-secondary-container: '#00424e'
  tertiary: '#d0bcff'
  on-tertiary: '#3c0091'
  tertiary-container: '#a078ff'
  on-tertiary-container: '#340080'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d0bcff'
  on-tertiary-fixed: '#23005c'
  on-tertiary-fixed-variant: '#5516be'
  background: '#111417'
  on-background: '#e1e2e7'
  surface-variant: '#323539'
typography:
  display:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: '1'
    letterSpacing: 0.05em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 0.5rem
  sm: 1rem
  md: 1.5rem
  lg: 2.5rem
  xl: 4rem
  gutter: 24px
  margin: 40px
---

## Brand & Style

This design system is built on a foundation of **Glassmorphism** and **Minimalism**, tailored for a high-performance desktop web environment. The brand personality is technical, sophisticated, and immersive, designed to make data feel like it is floating in a deep, digital space.

The aesthetic leverages high-transparency layers, extreme background blurs, and vibrant accent glows to create depth without physical shadows. The user interface should evoke a sense of "digital precision"—clean, futuristic, and unobtrusive, allowing the content to remain the primary focus while the container provides a premium, tactile feel.

## Colors

The palette is centered on a deep **Obsidian (#05070A)** base, which acts as the canvas for all glass effects. 

- **Primary & Secondary:** Indigo and Cyan are used for interactive states and as the source colors for ambient background blurs.
- **Accents:** Violet is reserved for secondary highlights, such as specialized status indicators or rare action buttons.
- **Surface Strategy:** Surfaces are never fully opaque. They use a semi-transparent dark slate with a `backdrop-filter: blur(20px)` to create the frosted effect. 
- **Border Strategy:** To define edges in a dark environment, use 1px solid borders with 10% white opacity. This simulates the catch-light on the edge of a glass pane.

## Typography

The typographic system utilizes **Geist** for high-impact headings to maintain a technical, clean-cut look. **Inter** handles all body copy for maximum legibility against dark, translucent backgrounds. **JetBrains Mono** is introduced for labels and metadata to reinforce the application's "AI/Technical" DNA.

- **Contrast:** Always use pure white (#FFFFFF) for primary text and 70% white (#A1A1AA) for secondary text.
- **Hierarchy:** Use tight letter-spacing for large displays to maintain a compact, "designed" feel. Labels should always be uppercase when using the monospaced font.

## Layout & Spacing

This design system employs a **Fluid Grid** model with generous safe areas to enhance the minimalist feel.

- **Grid:** A 12-column system for desktop, transitioning to a stack-based layout for mobile.
- **Rhythm:** Spacing follows a 4px baseline, but internal card padding should lean towards `md` (24px) or `lg` (40px) to allow the glass background to breathe.
- **Floating Containers:** Layout modules should rarely touch the edges of the viewport; they should appear as floating islands against the obsidian background with its ambient gradient glows.

## Elevation & Depth

Depth is achieved through **Backdrop Filtering** and **Tonal Layering** rather than traditional drop shadows.

1.  **Level 0 (Background):** Pure #05070A with large, low-opacity (15%) Indigo and Cyan blurs moving slowly in the background.
2.  **Level 1 (Default Surface):** `rgba(255, 255, 255, 0.03)` with `blur(16px)`. This is used for sidebars and secondary navigation.
3.  **Level 2 (Active Surface/Cards):** `rgba(255, 255, 255, 0.06)` with `blur(24px)` and a `1px` border of `rgba(255, 255, 255, 0.1)`.
4.  **Level 3 (Popovers/Modals):** `rgba(255, 255, 255, 0.1)` with `blur(32px)`. Increase border opacity to `0.2` for these elements.

## Shapes

The design uses a **Rounded (Level 2)** shape language. This softens the technical nature of the Geist typeface and creates a more approachable, premium feel.

- **Standard Buttons & Inputs:** 0.5rem (8px) corner radius.
- **Cards & Main Containers:** 1rem (16px) corner radius.
- **Large Sections/Modals:** 1.5rem (24px) corner radius.
- **Interactive States:** Hovering over elements should trigger a subtle expansion or a brightening of the internal glass tint.

## Components

### Buttons
- **Primary:** Solid Indigo background with a subtle Cyan-to-Indigo linear gradient (45deg). No border.
- **Secondary (Glass):** Transparent background with `blur(12px)` and a 1px white border (15% opacity).
- **Micro-interaction:** On hover, buttons should increase their glow (box-shadow: 0 0 20px rgba(99, 102, 241, 0.4)).

### Input Fields
- **Default:** `rgba(255, 255, 255, 0.05)` background, 1px border.
- **Focus:** Border color changes to Cyan (#06B6D4) with a subtle outer glow.
- **Typography:** Labels use the `label-md` (JetBrains Mono) style for a technical aesthetic.

### Cards
- Always implement `backdrop-filter: blur(20px)`.
- Use a "Top-Light" effect: A subtle white-to-transparent linear gradient on the border to simulate light hitting the top edge of the glass.

### Chips & Tags
- Pill-shaped with a very low opacity Indigo or Cyan tint (`rgba(6, 182, 212, 0.1)`).
- Use `label-sm` typography.

### Progress Bars
- Background track is `rgba(255, 255, 255, 0.1)`.
- Fill is a Cyan-to-Violet gradient.
- Add a small 4px glow at the leading edge of the progress fill.