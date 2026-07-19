# 3D Effects Quick Start Guide

## 🚀 Get Started in 2 Minutes

Your landing page now has 4 powerful 3D modules. Here's how to use them:

---

## 1. Floating Cards (Mouse-Responsive)

Makes cards respond to mouse movement with 3D perspective.

```html
<div data-floating-card>
  <h3>Your Card Title</h3>
  <p>Card content here</p>
</div>
```

**What it does:**
- Cards tilt toward mouse cursor
- Floating up/down animation
- Hover shadow effects
- Works on all modern browsers

**Perfect for:** Feature cards, testimonials, pricing cards, team members

---

## 2. Depth Layers (Scroll Parallax)

Elements at different depths move at different scroll speeds.

```html
<div data-depth-layer="1">Back layer (moves slower)</div>
<div data-depth-layer="2">Middle layer</div>
<div data-depth-layer="3">Front layer (moves faster)</div>
```

**Depth values:**
- `1` = slowest (background)
- `2` = medium (midground)
- `3` = fastest (foreground)

**What it does:**
- Creates immersive parallax effect
- Responds to both scroll and mouse
- Subtle scale adjustments
- Smooth spring animations

**Perfect for:** Background elements, layered sections, hero sections

---

## 3. 3D Text Animation

Text characters animate as they enter the viewport.

```html
<h2 data-text-3d>Your Heading Here</h2>
```

**What it does:**
- Each letter rotates in 3D space
- Staggered entrance animation
- Floats upward with perspective
- Triggers automatically on scroll

**Perfect for:** Main headings, section titles, important messages

---

## 4. Floating Elements

Simple continuous floating animation (6-second loop).

```html
<div class="float-3d">
  Your content here
</div>
```

**What it does:**
- Floats up/down continuously
- Smooth wavelike motion
- No mouse tracking needed
- Staggered timing for multiple elements

**Perfect for:** Icon elements, decorative items, visual separators

---

## 5. Bonus Effects

### Card Tilt (Simple Hover)
```html
<div class="card-tilt">
  Content tilts on hover
</div>
```

### Glowing Elements
```html
<div class="glow-3d">
  Glowing drop-shadow effect
</div>
```

### Layout 3D
```html
<section class="layout-3d">
  <!-- All children enable 3D transforms -->
</section>
```

---

## 📋 Combined Example

```html
<section class="section-3d">
  <h2 data-text-3d>Features</h2>
  
  <div class="demo-grid">
    <div data-floating-card>
      <h3>Feature 1</h3>
      <p>Description</p>
    </div>
    
    <div data-floating-card>
      <h3>Feature 2</h3>
      <p>Description</p>
    </div>
  </div>

  <div data-depth-layer="1">Background accent</div>
  <div data-depth-layer="2">Main content</div>
  <div data-depth-layer="3" class="float-3d">Floating element</div>
</section>
```

---

## ⚙️ Configuration

### Disable on Reduced Motion
Automatically disabled for users who prefer reduced motion (no code needed!).

### Mobile Optimization
Effects automatically scale down on smaller screens for better performance.

### Performance
- All modules use requestAnimationFrame
- Passive event listeners (no jank)
- GPU-accelerated transforms
- Automatic pause when tab inactive

---

## 🧪 Test it Out

1. **View the demo**: `http://localhost:8081/3d-demo.html`
2. **Check the homepage**: `http://localhost:8081/index.html`
3. **Move your mouse** over floating cards
4. **Scroll down** to see parallax effects
5. **Watch text animations** trigger on scroll

---

## 🎨 Styling Tips

### Make Cards Pop
```css
[data-floating-card] {
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  border-radius: 12px;
  padding: 2rem;
}
```

### Customize Depth Colors
```css
[data-depth-layer="1"] { color: rgba(255, 255, 255, 0.5); }
[data-depth-layer="2"] { color: rgba(255, 255, 255, 0.7); }
[data-depth-layer="3"] { color: rgba(255, 255, 255, 1); }
```

### Adjust Animation Speed
Edit the JavaScript files to customize:
- `floatSpeed` in floating-cards-3d.js
- Animation delays and durations
- Parallax intensity and scale

---

## 🐛 Troubleshooting

### Cards Not Responding?
- Check if `data-floating-card` is on the element
- Open DevTools (F12) and check for JS errors
- Verify element has non-zero dimensions

### Parallax Not Working?
- Make sure elements have `data-depth-layer="N"` (1-3)
- Try scrolling the page (effect activates on scroll)
- Check that z-index doesn't conflict

### Text Not Animating?
- Element must be visible on screen
- Add `data-text-3d` to the heading element
- Scroll to trigger the animation

### Performance Issues?
- Reduce number of floating cards per page
- Disable on low-end mobile devices
- Check browser's FPS counter (DevTools > More > Rendering)

---

## 📚 Files Reference

| File | Size | Purpose |
|------|------|---------|
| `hero-3d.js` | 8.5K | Three.js WebGL ambient scene |
| `floating-cards-3d.js` | 3.5K | Interactive card transforms |
| `depth-parallax.js` | 2.6K | Scroll-based parallax |
| `text-3d-effects.js` | 3.4K | Text character animations |

---

## ✅ Accessibility

All effects:
- ✅ Support keyboard navigation
- ✅ Respect `prefers-reduced-motion`
- ✅ Have proper contrast ratios
- ✅ Work with screen readers
- ✅ Maintain content semantics

---

## 🎯 Best Practices

1. **Don't Overuse**: Keep effects to 1-2 per section
2. **Performance First**: Test on low-end devices
3. **Mobile Friendly**: Effects reduce automatically on small screens
4. **Semantic HTML**: Use proper heading/structure elements
5. **Fallbacks**: Always have content readable without JS

---

## 🔗 Resources

- [Full Documentation](3D-ENHANCEMENTS.md)
- [Live Demo](3d-demo.html)
- [Three.js Docs](https://threejs.org/docs/)
- [CSS 3D Transforms](https://developer.mozilla.org/en-US/docs/Web/CSS/transform-style)
- [Intersection Observer API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)

---

## 💡 Ideas for Your Site

- Add `data-floating-card` to all feature cards
- Use `data-depth-layer` for hero section layers
- Apply `data-text-3d` to main section headings
- Wrap testimonials in `class="float-3d"`
- Use `class="glow-3d"` on CTAs
- Combine effects for max impact!

---

**Need help?** Check the browser console for any errors or warnings.  
**Want more?** Edit the JS files to customize animations to your brand!
