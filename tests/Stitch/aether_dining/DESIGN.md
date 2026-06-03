---
name: Aether Dining
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e18'
  surface-container-low: '#171b26'
  surface-container: '#1c1f2a'
  surface-container-high: '#262a35'
  surface-container-highest: '#313540'
  on-surface: '#dfe2f1'
  on-surface-variant: '#e2bec0'
  inverse-surface: '#dfe2f1'
  inverse-on-surface: '#2c303b'
  outline: '#a9898b'
  outline-variant: '#5a4042'
  surface-tint: '#ffb2b8'
  primary: '#ffb2b8'
  on-primary: '#67001e'
  primary-container: '#ff506f'
  on-primary-container: '#5b0019'
  inverse-primary: '#ba1340'
  secondary: '#7bd0ff'
  on-secondary: '#00354a'
  secondary-container: '#00a6e0'
  on-secondary-container: '#00374d'
  tertiary: '#ffb3b3'
  on-tertiary: '#680015'
  tertiary-container: '#ff5260'
  on-tertiary-container: '#5b0011'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdadb'
  primary-fixed-dim: '#ffb2b8'
  on-primary-fixed: '#40000f'
  on-primary-fixed-variant: '#91002d'
  secondary-fixed: '#c4e7ff'
  secondary-fixed-dim: '#7bd0ff'
  on-secondary-fixed: '#001e2c'
  on-secondary-fixed-variant: '#004c69'
  tertiary-fixed: '#ffdad9'
  tertiary-fixed-dim: '#ffb3b3'
  on-tertiary-fixed: '#400009'
  on-tertiary-fixed-variant: '#920021'
  background: '#0f131d'
  on-background: '#dfe2f1'
  surface-variant: '#313540'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  metric-xl:
    fontFamily: Outfit
    fontSize: 36px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: -0.01em
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
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
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
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

The design system is engineered to evoke a sense of high-fidelity precision and culinary discovery. It targets a premium demographic that views food through the lens of data-driven luxury. The visual narrative combines the depth of space with the heat of the kitchen, using a "Galactic Gastronomy" aesthetic.

The style is a sophisticated blend of **Glassmorphism** and **High-Contrast Bold**. It utilizes deep, multi-layered backgrounds with mesh radial glows to simulate cosmic depth, while the core brand gradient provides a high-energy focal point. Interaction states are defined by glowing borders and ultra-smooth cubic-bezier transitions, creating a UI that feels responsive, ethereal, and state-of-the-art.

## Colors

The palette is anchored in a deep dark slate space, providing a high-contrast canvas for the AI-driven data. 

- **The Rose-Red Gradient**: Reserved for primary actions, branding elements, and AI "intelligence" highlights. It symbolizes heat, flavor, and the core identity.
- **Sky Blue**: Functionally assigned to metrics, price points, and cost indicators to provide clear visual separation from brand elements.
- **Glassmorphic Surface**: Used for secondary containers. It requires a backdrop-filter blur of at least 16px and a subtle 1px border using the `border_glow` or a low-opacity white to define edges.
- **Mesh Glows**: Implement radial gradients in the background (using primary and secondary colors at 5-10% opacity) to prevent the dark interface from feeling static.

## Typography

This design system uses a dual-font strategy to balance character with readability.

- **Outfit** is the voice of the system. It is used for all headers, numeric data, and high-impact metrics. Its geometric clarity ensures that AI-generated scores and restaurant names feel modern and authoritative.
- **Inter** handles the utility. It is used for descriptions, reviews, and UI labels. Its neutral construction ensures high legibility against complex glassmorphic backgrounds.
- **Numerical Data**: Always use Outfit for price points and ratings. For metrics, use a slightly tighter letter-spacing to emphasize precision.

## Layout & Spacing

The layout follows a **Fluid Grid** model with generous margins to allow the glassmorphic elements "room to breathe." 

- **Desktop**: A 12-column grid with 24px gutters. Use wide margins (40px+) to create a cinematic, widescreen feel.
- **Mobile**: A 4-column grid. Spacing is tighter (16px margins), and complex glass layers should be simplified to single-layer stacks to maintain performance.
- **Rhythm**: All spacing is derived from an 8px base unit. Component internal padding should favor the `md` (24px) scale to reinforce the premium, non-cramped feel of the dashboard.

## Elevation & Depth

Depth is communicated through **Glassmorphism** and **Tonal Layering** rather than traditional drop shadows.

1.  **Level 0 (Base)**: Deep dark slate (#0b0f19) with subtle mesh glows.
2.  **Level 1 (Cards/Panels)**: Glassmorphic slate (rgba(15, 23, 42, 0.65)) with a 16px-24px backdrop blur.
3.  **Level 2 (Modals/Popovers)**: Higher transparency glass with a 1px solid border (#ffffff 10%) and a soft, wide outer glow in the primary color (opacity 0.05).
4.  **Transitions**: All depth changes must use `cubic-bezier(0.4, 0, 0.2, 1)` transitions. Elements should appear to "float up" from the background when hovered, increasing the blur intensity of the layers beneath them.

## Shapes

The shape language is consistently **Rounded**, striking a balance between organic culinary forms and technical precision.

- **Standard Elements**: 0.5rem (8px) radius for inputs and small buttons.
- **Cards & Containers**: 1rem (16px) radius to soften the high-contrast dark theme.
- **Interactive Triggers**: Large buttons and AI recommendation chips should use 1.5rem (24px) or full pill shapes to indicate touch-friendly, high-importance actions.
- **Glow Borders**: Borders should follow the exact curvature of the parent element, with a 1px stroke weight to maintain a "razor-thin" technical appearance.

## Components

- **Buttons**: Primary buttons use the Rose-Red gradient with white text. On hover, apply a 10px outer glow in the primary color. Secondary buttons use a "ghost" style with a 1px Sky Blue border.
- **AI Recommendation Cards**: These are the "hero" components. Use a glassmorphic background, a subtle primary-color inner glow at the top edge, and Outfit Medium for the restaurant name.
- **Metric Chips**: Small, pill-shaped Sky Blue backgrounds with 10% opacity and 100% opacity Sky Blue text for costs and delivery times.
- **Input Fields**: Dark slate backgrounds (#0f1626) with a 1px border that glows Rose-Red on focus.
- **Glowing Borders**: For "AI-suggested" items, use a continuous CSS border-gradient animation that subtly rotates around the card.
- **Progress Bars**: Used for "Match Scores." Use the Sky Blue for the track and the Rose-Red gradient for the fill, creating a visual "heat map" of how well a restaurant matches the user's profile.