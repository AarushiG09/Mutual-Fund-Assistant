---
name: Groww AI Assistant
colors:
  surface: '#0d1511'
  surface-dim: '#0d1511'
  surface-bright: '#333b37'
  surface-container-lowest: '#08100c'
  surface-container-low: '#161d19'
  surface-container: '#1a211d'
  surface-container-high: '#242c28'
  surface-container-highest: '#2f3732'
  on-surface: '#dce5de'
  on-surface-variant: '#bacac1'
  inverse-surface: '#dce5de'
  inverse-on-surface: '#2a322e'
  outline: '#85948c'
  outline-variant: '#3c4a43'
  surface-tint: '#2fe0aa'
  primary: '#44edb7'
  on-primary: '#003828'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#006c4f'
  secondary: '#4edeab'
  on-secondary: '#003827'
  secondary-container: '#06b686'
  on-secondary-container: '#00402d'
  tertiary: '#ffc8a3'
  on-tertiary: '#502500'
  tertiary-container: '#ffa15b'
  on-tertiary-container: '#733800'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#6ffbc5'
  secondary-fixed-dim: '#4edeab'
  on-secondary-fixed: '#002115'
  on-secondary-fixed-variant: '#00513a'
  tertiary-fixed: '#ffdcc6'
  tertiary-fixed-dim: '#ffb785'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#713700'
  background: '#0d1511'
  on-background: '#dce5de'
  surface-variant: '#2f3732'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-xl:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-xl-mobile:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Outfit
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-xs:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 80px
---

## Brand & Style

The design system is engineered to feel like a premium, intelligent financial advisor—sophisticated, precise, and transparent. It caters to modern investors who value both high-tech efficiency and institutional-grade reliability. 

The aesthetic is a fusion of **Glassmorphism** and **Corporate Modern**. It leverages deep, multi-dimensional dark backgrounds with luminous accents to create a sense of focused immersion. The UI avoids the starkness of pure black, opting instead for a deep oceanic palette that reduces eye strain during long research sessions. Visual hierarchy is established through "light-emitting" primary elements and frosted glass surfaces that suggest depth and digital materiality.

## Colors

The palette is anchored by the signature "Groww Teal" gradient, representing growth and financial vitality. 

- **Primary Gradient:** A linear flow from `#00d09c` to `#00b585`, used for primary actions, success states, and key AI highlights.
- **Background:** A foundational deep grey-blue (`#080c14`). Implement subtle, large-scale radial mesh gradients in very low-opacity cyan (2-5% opacity) in the corners to prevent the dark mode from feeling "flat."
- **Glass Surfaces:** Containers use a semi-transparent slate (`rgba(15, 23, 42, 0.65)`) to allow the background mesh gradients to ghost through.
- **Compliance/Warning:** Amber (`#fbbf24`) is reserved strictly for regulatory disclaimers, risk warnings, and critical account alerts to ensure high visibility against the cool-toned base.

## Typography

This design system utilizes a dual-font strategy to balance character with utility.

**Outfit** is used for all "Display" and "Headline" roles. Its geometric construction provides a modern, tech-forward feel that excels in metrics and financial figures. Keep tracking slightly tight on larger sizes to maintain a premium "editorial" look.

**Inter** is the functional workhorse for body copy, labels, and chat messages. Its high x-height and neutral character ensure maximum legibility for complex financial FAQs. Use Medium (500) or SemiBold (600) weights for labels to maintain clarity against glass backgrounds.

## Layout & Spacing

The system follows a strict **8px grid** (half-step 4px for fine-tuning) to ensure mathematical harmony across all components.

- **Desktop:** 12-column fluid grid with a maximum content width of 1440px. Use 24px gutters to allow the glassmorphism cards enough breathing room to avoid visual clutter.
- **Mobile:** 4-column fluid grid with 16px side margins. 
- **Spacing Rhythm:** Use `lg` (40px) for section vertical spacing and `md` (24px) for padding within glass containers. Internal component spacing (like icon-to-text) should stick to `xs` or `base`.

Prioritize whitespace to highlight the "intelligence" of the AI—dense layouts should be avoided in favor of a clean, progressive disclosure model.

## Elevation & Depth

Hierarchy is defined through light and transparency rather than traditional heavy shadows.

1.  **Level 0 (Base):** The deep background (`#080c14`) with mesh gradients.
2.  **Level 1 (Surfaces):** Glassmorphism cards with a `12px` backdrop-blur. Every card must have a 1px solid border at 10% opacity, using a white-to-teal gradient stroke to define the edges.
3.  **Level 2 (Interaction):** On hover, glass cards should increase their border opacity to 30% and emit a soft, localized ambient glow (`box-shadow`) using the primary teal color with a 20px blur and low (15%) opacity.
4.  **Floating Elements:** Modals or tooltips use a higher blur (20px) and a slightly darker fill to pop against the standard surface cards.

## Shapes

The design system employs a **Rounded** language (12px / 0.75rem base) to feel approachable and modern. 

- **Standard Components:** Buttons, input fields, and small cards use the `rounded` (12px) setting.
- **Large Containers:** Main chat windows and dashboard modules use `rounded-lg` (16px).
- **Search/AI Input:** The primary AI prompt bar should use a `rounded-xl` (24px) or semi-pill shape to distinguish it from static data cards.

Avoid sharp 90-degree corners entirely to maintain the "soft-tech" friendly persona of an assistant.

## Components

### Buttons
- **Primary:** Gradient fill (#00d09c to #00b585) with white text. Apply a soft teal drop-glow on hover.
- **Secondary:** Transparent with a 1px teal border. 
- **Ghost:** No border or fill, teal text, subtle background highlight on hover.

### AI Chat Bubbles
- **Assistant:** Glass surface (slate/65) with a teal left-accent border.
- **User:** Deep indigo-slate fill to distinguish from the AI's responses.

### Input Fields
- Dark slate fill (10% opacity) with a 1px border. On focus, the border transitions to the primary teal gradient and the backdrop blur increases.

### Cards
- Standard glassmorphism styling. Use `Outfit` for the card titles and `Inter` for metadata. Ensure all cards have the 1px subtle border to prevent "bleeding" into the dark background.

### Icons & Imagery
- **Icons:** Use **Material Symbols Outlined**. Keep stroke weight consistent (200 or 300) to match the thin borders of the glass cards. 
- **Data Viz:** Charts should use the primary teal for growth lines, with the secondary teal for historical data. Use the Amber accent for specific data points that require caution.