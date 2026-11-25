# Pentagon Layout in Webflow - Step by Step Guide

## 📐 Overview

This guide shows you how to create a pentagon layout (5 items arranged in a perfect circle around a central SVG) in Webflow.

## 🎯 Visual Structure

```
        Item 1 (Top)
             |
  Item 5 ----SVG---- Item 2
             |
      Item 4   Item 3
```

---

## Step 1: Create the Container Structure

### 1.1 Main Wrapper
1. Add a **Div Block**
2. Name it: `pentagon-wrapper`
3. Settings:
   - Position: `Relative`
   - Width: `500px` (or your preferred size)
   - Height: `500px` (same as width)
   - Margin: `Auto` (to center it)

### 1.2 SVG Container (Center)
1. Inside `pentagon-wrapper`, add a **Div Block**
2. Name it: `pentagon-center`
3. Settings:
   - Position: `Absolute`
   - Top: `50%`
   - Left: `50%`
   - Width: `220px`
   - Height: `220px`
   - Transform: `translate(-50%, -50%)`
   - Z-index: `10`

4. Inside `pentagon-center`, add another **Div Block** for your SVG
   - Give it an ID: `myShapeSVG` (you'll need this for rotation)
   - Add class: `svgContainer`

---

## Step 2: Add the 5 Pentagon Items

For EACH of the 5 items, repeat these steps:

### 2.1 Create Item
1. Inside `pentagon-wrapper` (NOT inside pentagon-center), add a **Div Block**
2. Name it: `pentagon-item-1` (then 2, 3, 4, 5)
3. Give it a class: `pentagon-item`

### 2.2 Base Styling (Apply to ALL items via class)
1. Select class `pentagon-item`
2. Settings:
   - Position: `Absolute`
   - Top: `50%`
   - Left: `50%`
   - Width: `130px`
   - Padding: `16px 12px`
   - Background: `rgba(76, 175, 80, 0.15)` or your brand color
   - Border: `2px solid #4CAF50`
   - Border-radius: `10px`
   - Text-align: `Center`
   - Z-index: `5`
   - Cursor: `Pointer`

3. Add hover state:
   - Background: `rgba(76, 175, 80, 0.3)`
   - Transform: Scale `1.05`
   - Transition: `All 300ms ease`

### 2.3 Position Each Item (Individual Settings)

Now position each item individually using Transform (uses **percentages** for responsive design):

**Item 1 (Top - 0°):**
- Select `pentagon-item-1`
- Transform: `translate(-50%, -50%) translate(0%, -40%)`

**Item 2 (Right-Top - 72°):**
- Select `pentagon-item-2`
- Transform: `translate(-50%, -50%) translate(38%, -12.4%)`

**Item 3 (Right-Bottom - 144°):**
- Select `pentagon-item-3`
- Transform: `translate(-50%, -50%) translate(23.5%, 32.4%)`

**Item 4 (Left-Bottom - 216°):**
- Select `pentagon-item-4`
- Transform: `translate(-50%, -50%) translate(-23.5%, 32.4%)`

**Item 5 (Left-Top - 288°):**
- Select `pentagon-item-5`
- Transform: `translate(-50%, -50%) translate(-38%, -12.4%)`

> **💡 Tip:** These percentage values work at ANY screen size! Just paste them into Webflow's Transform → Move fields.
> **Note:** Type the percentages directly (e.g., `38` and `-12.4` for Item 2's X and Y)

---

## Step 3: Add Content to Items

Inside each `pentagon-item` div:

1. Add a **Text Block** with styling:
   - Font-size: `16px`
   - Font-weight: `Bold`
   - Color: `#4CAF50`
   - Display: `Block`
   - Margin-bottom: `4px`

2. Add another **Text Block** below it:
   - Font-size: `14px`
   - Color: `White`

Example:
```
pentagon-item-1
  ├─ Text: "Service 1" (bold)
  └─ Text: "Consulting"
```

---

## Step 4: Add Custom Attributes for Rotation

For each pentagon item, add custom attributes:

**Item 1:**
- Attribute: `data-rotate-target` | Value: `myShapeSVG`
- Attribute: `id` | Value: `0deg`

**Item 2:**
- Attribute: `data-rotate-target` | Value: `myShapeSVG`
- Attribute: `id` | Value: `72deg`

**Item 3:**
- Attribute: `data-rotate-target` | Value: `myShapeSVG`
- Attribute: `id` | Value: `144deg`

**Item 4:**
- Attribute: `data-rotate-target` | Value: `myShapeSVG`
- Attribute: `id` | Value: `216deg`

**Item 5:**
- Attribute: `data-rotate-target` | Value: `myShapeSVG`
- Attribute: `id` | Value: `288deg`

> **📍 Where to add:** Select element → Settings Panel (gear icon) → Custom Attributes → Add Attribute

---

## Step 5: Add the JavaScript

### 5.1 Add External Scripts

In **Project Settings** → **Custom Code** → **Head Code**, add:

```html
<!-- Vivus & Pathformer -->
<script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/dist/vivus.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vivus@0.4.4/src/pathformer.js"></script>
```

### 5.2 Upload Your Script

1. Go to **Assets** panel
2. Upload your `vivusObserver.js` file
3. Copy the file URL

### 5.3 Add Initialization Code

In **Page Settings** → **Before </body> tag**, add:

```html
<!-- Your custom script -->
<script src="YOUR_VIVUSOBSERVER_URL_HERE"></script>

<!-- Initialize -->
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const shapes = [{
      containerId: 'myShapeSVG',
      svgUrl: 'YOUR_SVG_URL_HERE',
      vivusOptions: { type: 'scenario-sync', duration: 36 },
      vivusInstance: null,
      isAnimated: false
    }];
    
    // Initialize animation
    initGlobalStaggerObserver(shapes, 0.5, false);
    
    // Initialize rotation
    initRotationControls(shapes, '[data-rotate-target]', 600, false);
  });
</script>
```

Replace:
- `YOUR_VIVUSOBSERVER_URL_HERE` with the uploaded file URL
- `YOUR_SVG_URL_HERE` with your SVG file URL from Assets

---

## Step 6: Add Accordion Content (Optional)

If you want content to appear below when clicked:

### 6.1 Create Content Sections

Below the `pentagon-wrapper`, add 5 **Div Blocks**:

1. Name them: `content-1`, `content-2`, etc.
2. Give them all a class: `accordion-content`
3. Settings for class:
   - Max-height: `0px`
   - Overflow: `Hidden`
   - Opacity: `0`
   - Padding: `0px 30px`
   - Background: `#2a2a2a`
   - Border-radius: `12px`
   - Margin-bottom: `20px`
   - Transition: `All 400ms ease`

### 6.2 Create Active State

1. Create a combo class: `accordion-content.active`
2. Settings:
   - Max-height: `500px`
   - Padding: `30px`
   - Opacity: `1`
   - Border: `2px solid #4CAF50`

### 6.3 Add Webflow Interaction

**Option A: Use Webflow Interactions** (No extra JS needed!)

1. Select `pentagon-item-1`
2. Add Interaction → **Element trigger** → **Click**
3. Create new animation:
   - **On 1st click:** 
     - Add class `active` to `content-1`
     - (Optional) Remove class `active` from other content divs
   - **On 2nd click:**
     - Remove class `active` from `content-1`

4. Repeat for all 5 items

**Option B: Use JavaScript**

Add this to your Before </body> tag script:

```javascript
// Accordion functionality
const pentagonItems = document.querySelectorAll('.pentagon-item');
const accordionContents = document.querySelectorAll('.accordion-content');

pentagonItems.forEach((item, index) => {
  item.addEventListener('click', function() {
    const wasActive = this.classList.contains('active');
    
    // Close all
    pentagonItems.forEach(i => i.classList.remove('active'));
    accordionContents.forEach(c => c.classList.remove('active'));
    
    // Open clicked one (if not already open)
    if (!wasActive) {
      this.classList.add('active');
      accordionContents[index].classList.add('active');
    }
  });
});
```

---

## 📱 Responsive Design

**Good news!** Using percentage-based positions means **you don't need to change the translate values** at different breakpoints. They scale automatically! 🎉

Just adjust these at each breakpoint:

### Desktop (Base):
- `pentagon-wrapper`: Width `100%`, Max-width: `600px`
- `pentagon-center`: Width/Height: `40%` (of wrapper)
- Item width: `22%`, Min-width: `90px`, Max-width: `140px`
- **Positions: Use the same % values from Step 2.3**

### Tablet (≤768px):
- `pentagon-wrapper`: Max-width: `500px`
- Item width: `25%`
- **Positions: No change needed!**

### Mobile (≤480px):
- `pentagon-wrapper`: Max-width: `350px`
- `pentagon-center`: Width/Height: `38%`
- Item width: `28%`, Min-width: `70px`
- **Positions: No change needed!**

> **💡 Key Point:** The percentage positions automatically scale with the container size. You only need to adjust container max-width and item sizing at breakpoints

---

## 🧮 Calculate Your Own Positions

If you want different spacing or radius percentage:

**Formula:**
```
angle = -90° + (360° / 5) × itemNumber
x = radiusPercent × cos(angle in radians)
y = radiusPercent × sin(angle in radians)
```

**JavaScript calculator (for percentage positions):**
```javascript
function calculatePercentagePositions(totalItems, radiusPercent) {
  console.log(`Pentagon positions for ${totalItems} items, ${radiusPercent}% radius:\n`);
  for (let i = 0; i < totalItems; i++) {
    const angleInDegrees = -90 + (360 / totalItems) * i;
    const angleInRadians = angleInDegrees * (Math.PI / 180);
    const x = (radiusPercent * Math.cos(angleInRadians)).toFixed(1);
    const y = (radiusPercent * Math.sin(angleInRadians)).toFixed(1);
    console.log(`Item ${i + 1}: translate(-50%, -50%) translate(${x}%, ${y}%)`);
  }
}

// Calculate for 5 items with 40% radius (default)
calculatePercentagePositions(5, 40);

// Try different radius: 35% for tighter circle
// calculatePercentagePositions(5, 35);

// Or 45% for wider circle
// calculatePercentagePositions(5, 45);
```

---

## ✅ Checklist

- [ ] Pentagon wrapper created (position: relative)
- [ ] SVG container centered (position: absolute, transform: translate(-50%, -50%))
- [ ] 5 pentagon items added with class `pentagon-item`
- [ ] Each item positioned using transform translate values
- [ ] Custom attributes added (`data-rotate-target` and `id` with angle)
- [ ] Vivus/Pathformer scripts added to Head
- [ ] vivusObserver.js uploaded and linked
- [ ] Initialization script added before </body>
- [ ] (Optional) Accordion content sections created
- [ ] (Optional) Webflow interactions or JS added for accordion
- [ ] Tested on all breakpoints

---

## 🎥 Quick Visual Guide

```
1. Container (100% width, max 600px, relative)
   └── Center SVG (40% size, absolute, centered)
   └── Item 1 (absolute, centered + translate(0%, -40%))
   └── Item 2 (absolute, centered + translate(38%, -12.4%))
   └── Item 3 (absolute, centered + translate(23.5%, 32.4%))
   └── Item 4 (absolute, centered + translate(-23.5%, 32.4%))
   └── Item 5 (absolute, centered + translate(-38%, -12.4%))
```

**Why percentages?**
- ✅ Responsive at any screen size
- ✅ No breakpoint adjustments needed for positions
- ✅ Scales proportionally with container
- ✅ Works in Webflow exactly the same way

---

## 🆘 Troubleshooting

**Items not in circle?**
- Check that wrapper has `position: relative`
- Check each item has `position: absolute`
- Verify transform values are exact (including negative signs)

**SVG not rotating?**
- Verify custom attributes are correct
- Check browser console for errors
- Make sure vivusObserver.js loaded
- Verify SVG container ID matches `data-rotate-target` value

**Accordion not working?**
- Check class names match exactly
- Verify interaction triggers are set up correctly
- Check JavaScript console for errors

---

## 📚 Additional Resources

- Live demo: `pentagon-accordion.html`
- Test page: `layout-options.html`
- Full documentation: `ROTATION.md`

---

**Made with ❤️ for Webflow**
