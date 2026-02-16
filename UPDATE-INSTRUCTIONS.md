# V3D Creative Website Update Instructions

## Changes Made

### 1. New Logo (logo.svg)
- Created a wider, more prominent logo that spans more across the banner
- Features a 3D cube icon with gradient "V3D Creative" text
- Includes "CUSTOM 3D PRINTS" tagline
- More professional and eye-catching design

### 2. Updated Home Page (index.html)
- Restructured to show a **product gallery/thumbnail view**
- Currently displays the Minecraft name plate as a clickable card
- Clean, modern design with hover effects
- Ready to add more products easily
- Each product card links to its detailed product page

### 3. Minecraft Product Page (product-minecraft-nameplate.html)
- Dedicated page for the Minecraft name plate product
- Includes image gallery (3 photos)
- Full product description and features list
- Complete order form with all customization options
- Venmo payment information with QR code
- "Back to All Products" button for easy navigation

## How to Upload to GitHub

### Method 1: Using GitHub Web Interface (Easiest)

1. Go to https://github.com/nvastano/V3D_Creative

2. **Upload the new logo.svg:**
   - Click on the existing `logo.svg` file
   - Click the pencil icon (Edit this file)
   - Delete all content
   - Copy the contents from the new `logo.svg` file I created
   - Paste it into the editor
   - Scroll down and click "Commit changes"
   - Add commit message: "Update logo to wider design"
   - Click "Commit changes"

3. **Upload the new index.html:**
   - Click on the existing `index.html` file
   - Click the pencil icon (Edit this file)
   - Select all (Cmd+A or Ctrl+A) and delete
   - Copy the contents from the new `index.html` file I created
   - Paste it into the editor
   - Scroll down and click "Commit changes"
   - Add commit message: "Restructure home page to product gallery"
   - Click "Commit changes"

4. **Upload/Update product-minecraft-nameplate.html:**
   - Go back to the main repository page
   - Click on the existing `product-minecraft-nameplate.html` file (if it exists)
   - Click the pencil icon (Edit this file)
   - Replace all content with the new version I created
   - OR if the file doesn't exist:
     - Click "Add file" → "Create new file"
     - Name it: `product-minecraft-nameplate.html`
     - Paste the contents
   - Scroll down and click "Commit changes"
   - Add commit message: "Update Minecraft product page with full details"
   - Click "Commit changes"

### Method 2: Upload Multiple Files at Once

1. Go to https://github.com/nvastano/V3D_Creative
2. Click "Add file" → "Upload files"
3. Drag and drop the three files (logo.svg, index.html, product-minecraft-nameplate.html)
4. Add commit message: "Update site with new logo and product gallery layout"
5. Click "Commit changes"

## After Upload

1. Wait 1-2 minutes for GitHub Pages to rebuild
2. Visit your site: https://nvastano.github.io/V3D_Creative/
3. You should see:
   - Larger, more professional logo in the header
   - Home page showing product thumbnail(s)
   - Click on Minecraft product to see the detailed page with form

## Adding More Products Later

To add more products in the future:

1. **Add a new product card to index.html** in the `products-grid` section:
```html
<a href="product-YOUR-PRODUCT.html" class="product-card">
    <div class="product-images">
        <img src="your-product-image.jpg" alt="Your Product" class="product-image">
    </div>
    <h2>Your Product Name</h2>
    <div class="product-price">$XX</div>
    <p class="product-description">
        Description of your product...
    </p>
    <span class="view-details-btn">View Details & Order →</span>
</a>
```

2. **Create a new product page** by copying and modifying `product-minecraft-nameplate.html`

## Need Help?

If you have any questions or issues uploading the files, let me know and I can guide you through it!
