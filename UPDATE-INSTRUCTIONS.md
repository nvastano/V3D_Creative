# V3D Creative - Setup Instructions (Updated)

## 📁 New Folder Structure

Your site now has proper organization:
- `images/` - All photos, logos, QR codes
- `css/` - For future CSS files (currently in HTML)
- `js/` - For future JavaScript files (currently in HTML)
- HTML files in the root

This makes it easier to manage and is best practice!

---

## 🚀 Quick Upload to GitHub Pages

### Step 1: Go to Your Repository
https://github.com/nvastano/v3d-creative (or your repo name)

### Step 2: Delete Old Files (Important!)
Since we reorganized, you need to delete the old flat structure:
1. In GitHub, click on each old image file (logo.svg, minecraft-1.jpg, etc.)
2. Click the trash icon to delete
3. Do this for all image files in the root
4. Commit the deletions

### Step 3: Upload New Structure
1. Click "Add file" → "Upload files"
2. Drag the ENTIRE `v3d-site` folder contents:
   - All HTML files
   - The `images` folder (with all images inside)
   - The `google-script.js` file
   - The README.md file
3. Make sure the folder structure is preserved!
4. Click "Commit changes"

GitHub Pages will automatically serve from the root, so:
- `index.html` will be your homepage
- `images/logo.svg` will be at `/images/logo.svg`

---

## 🔗 Google Sheets Connection

### Step 1: Open Google Apps Script
1. Go to your Google Sheet
2. Click **Extensions** → **Apps Script**

### Step 2: Paste the Script
1. Delete any existing code
2. Open `google-script.js`
3. Copy ALL the code
4. Paste into Apps Script editor
5. Save (💾)

### Step 3: Deploy
1. Click **Deploy** → **New deployment**
2. Select **Web app**
3. Settings:
   - **Execute as**: Me
   - **Who has access**: Anyone
4. Click **Deploy**
5. **Copy the URL** (looks like `https://script.google.com/macros/s/...`)

### Step 4: Update HTML Files
You need to update 2 files with your Google Script URL:

**File 1: index.html**
- Line ~775: Find `const SCRIPT_URL = 'YOUR_GOOGLE_SCRIPT_URL_HERE';`
- Replace with your actual URL

**File 2: contact.html**  
- Line ~280: Find `const SCRIPT_URL = 'YOUR_GOOGLE_SCRIPT_URL_HERE';`
- Replace with your actual URL

**Then re-upload these 2 files to GitHub!**

---

## ✅ Testing Checklist

After uploading everything:

1. ✅ Visit your site: `https://YOUR-USERNAME.github.io/v3d-creative/`
2. ✅ Check that logo appears in header
3. ✅ Check that all product images load
4. ✅ Click "Order Headphone Hook" - form should expand
5. ✅ Click "Order Minecraft Name Plate" - form should expand
6. ✅ Test submitting an order - should appear in Google Sheet
7. ✅ Check Venmo QR code displays

---

## 🐛 Troubleshooting

### Images not loading?
- Make sure you uploaded the `images/` folder, not just the files
- Check that folder structure is preserved in GitHub
- Paths should be `images/logo.svg` not just `logo.svg`

### Forms not submitting?
- Did you update the SCRIPT_URL in both `index.html` and `contact.html`?
- Is your Google Script deployed as "Anyone" can access?
- Check your Google Sheet for new tabs

### Logo too small/big?
- Edit `index.html`, `about.html`, `contact.html`
- Find: `style="height: 80px"`
- Change to desired size (e.g., `100px` for bigger)

---

## 🎨 Future Improvements

Want to make changes? Here's what you can do:

### Add New Products
Tell me and I'll add them to `index.html`

### Change Colors
Tell me what colors you want and I'll update the CSS

### Add Pages
Need a new page? I can create it and add it to the nav

---

## 📊 Google Sheet Tabs

Your orders will appear in:
- **Headphone Hook Orders** - Hook orders with color choices
- **Minecraft Orders** - Nameplate orders with plate details
- **Custom Requests** - Contact form submissions

Update the "Status" column as you process orders!

---

## 💡 Pro Tips

1. Keep all images in the `images/` folder
2. When adding new images, upload them to the `images/` folder in GitHub
3. Use descriptive file names: `product-name-1.jpg`
4. Optimize images before uploading (keep under 500KB each)
5. Check your Google Sheet daily for new orders

---

Good luck! Your site is organized and ready to go! 🚀
