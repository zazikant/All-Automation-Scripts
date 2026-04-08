## Mailster Template Creation Guide

### Element Identification
*   **Text Areas:** Black color blocks - Use `<single>` or `<multi>` tags
*   **Images:** Grey color blocks - Use `<img>` tags with `editable=""` attribute and **MANDATORY** `height="auto"`
*   **Buttons:** Yellow color blocks - Use Mailster `<buttons>` template structure

### Basic Structure
- **Base width:** 600px total (24px + 552px + 24px)
- **Table-based layout** for email compatibility
- **Modules:** Each section wrapped in `<module>` tags

### Workflow
1. **Look at skeleton image** - Identify all elements in each bordered section
2. **Measure proportions** - Calculate dimensions based on 600px width
3. **Match visual sizes exactly** - Grey boxes = image dimensions, Black boxes = text area dimensions
4. **Create todo list** - One item per section with exact measurements
5. **Build section by section** - Complete one fully before next

### ⚠️ Critical Size Matching Rule
- **Grey boxes (images)**: Image width/height must match the visual size in skeleton
- **Black boxes (text)**: Text area must match the visual height/width in skeleton
- Don't use standard sizes - measure what you actually see in the image

### ⚠️ Critical Visual Analysis Rule
**SCAN EACH BORDERED SECTION COMPLETELY - Look for ALL elements within each border**

**Common mistakes to avoid:**
- Missing stacked elements (images below images, text below text)
- Assuming first visible element is the only element in section
- Not noticing border outlines that indicate separate images
- Confusing which section elements belong to (check border boundaries)

**Proper scanning technique:**
1. Identify border boundaries of each section
2. Within each border, scan TOP TO BOTTOM
3. Count ALL grey blocks, black blocks, yellow blocks
4. Note stacking (vertical arrangement) vs side-by-side (horizontal arrangement)
5. Measure each element separately

### Spacing
```html
<tr>
    <td height="12" colspan="3"></td>
</tr>
```

### Button Template
```html
<div class="btn">
    <buttons data-tmpl="...">
        <table class="textbutton" align="center" role="presentation">
            <tbody>
                <tr>
                    <td align="center" width="120">
                        <a href="" editable="" label="Button Text">Button Text</a>
                    </td>
                </tr>
            </tbody>
        </table>
    </buttons>
</div>
```

### ⚠️ CRITICAL STRUCTURE RULES

**NEVER use multiple `<module>` tags - Use single table structure!**

### Template Structure Rules
- **Single table structure** - One main table, all sections as `<tr>` rows
- **Width calculations**: 
  - Total content: 552px
  - 2 columns: (552-24)/2 = 264px each
  - 3 columns: (552-48)/3 = 168px each
  - 4 columns: (552-72)/4 = 120px each
- **Use `o-fix` class** for nested tables
- **MANDATORY: All images MUST have `height="auto"`** - Never use fixed heights
- **Simple buttons** - Direct `<table class="textbutton">` without complex wrappers

### Complete Template Structure
```html
<table width="600" cellpadding="0" cellspacing="0" role="presentation" style="background-color: white">
    <tbody>
        <!-- Section 1 -->
        <tr>
            <td height="24" colspan="3"></td>
        </tr>
        <tr>
            <td width="24" class="padd">&zwnj;</td>
            <td width="552" valign="top" align="center">
                <!-- Section content -->
            </td>
            <td width="24" class="padd">&zwnj;</td>
        </tr>
        
        <!-- Section 2 -->
        <tr>
            <td height="24" colspan="3"></td>
        </tr>
        <tr>
            <td width="24" class="padd">&zwnj;</td>
            <td width="552" valign="top">
                <table cellpadding="0" cellspacing="0" class="o-fix" role="presentation">
                    <!-- Multi-column content -->
                </table>
            </td>
            <td width="24" class="padd">&zwnj;</td>
        </tr>
        
        <!-- Continue pattern for all sections -->
    </tbody>
</table>
```

### Simple Button Structure
```html
<table class="textbutton" align="center" role="presentation">
    <tbody>
        <tr>
            <td align="center" width="120">
                <a href="" editable="" label="Button Text">Button Text</a>
            </td>
        </tr>
    </tbody>
</table>
```