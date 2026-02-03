# V3D Creative - Google Sheets Setup Instructions

## Quick Setup (10 minutes)

Follow these steps to connect your order forms to your Google Sheet.

---

## Step 1: Open Your Google Sheet

Go to: https://docs.google.com/spreadsheets/d/1RQiL0eK7GkGiLzXqt93QXh_n1ZAtk1k4Prog1m_gqXk/edit?usp=sharing

Make sure you're logged into the Google account that owns this sheet.

---

## Step 2: Open Apps Script

1. In your Google Sheet, click **Extensions** → **Apps Script**
2. A new tab will open with the Apps Script editor

---

## Step 3: Add the Script

1. **Delete** any code that's already in the editor
2. Open the file `google-script.js` (I provided this)
3. **Copy ALL the code** from that file
4. **Paste** it into the Apps Script editor
5. Click the **Save icon** (💾) or press Ctrl+S
6. Name your project: "V3D Order Handler"

---

## Step 4: Deploy as Web App

1. Click **Deploy** button (top right) → **New deployment**
2. Click the **gear icon** ⚙️ next to "Select type"
3. Choose **Web app**
4. Configure:
   - **Description**: "V3D Order Form"
   - **Execute as**: **Me** (your email)
   - **Who has access**: **Anyone**
5. Click **Deploy**

### Authorization (First Time Only)
6. Click **Authorize access**
7. Choose your Google account
8. Click **Advanced** → **Go to V3D Order Handler (unsafe)**
9. Click **Allow**

### ⭐ IMPORTANT: Copy the Web App URL
10. You'll see a URL like: `https://script.google.com/macros/s/AKfycby.../exec`
11. **COPY THIS URL** - you'll need it in the next step!

---

## Step 5: Update Your Website Files

You need to add your Web App URL to TWO files:

### File 1: index.html
1. Open `index.html`
2. Press Ctrl+F (or Cmd+F on Mac) and search for: `YOUR_GOOGLE_SCRIPT_URL_HERE`
3. Replace it with your Web App URL from Step 4.10
4. **Save the file**

### File 2: contact.html
1. Open `contact.html`
2. Press Ctrl+F and search for: `YOUR_GOOGLE_SCRIPT_URL_HERE`
3. Replace it with your Web App URL
4. **Save the file**

---

## Step 6: Test It! (Optional but Recommended)

Before uploading your site, test the script:

1. Go back to Apps Script editor
2. Select **testProductOrder** from the dropdown at the top
3. Click the **Run** button ▶️
4. Check your Google Sheet - you should see a new tab called "Product Orders" with a test order!
5. If it works, **delete the test row**

---

## Step 7: Upload Your Website to GitHub Pages

### Create GitHub Account
1. Go to **github.com** and sign up (it's free)

### Create Repository
1. Click the **"+"** button (top right) → **"New repository"**
2. Name it: **v3d-creative**
3. Make it **Public**
4. Click **"Create repository"**

### Upload Files
1. Click **"uploading an existing file"**
2. Drag and drop ALL these files:
   - index.html
   - about.html
   - contact.html
   - logo.svg
   - hudson-venmo.png
   - minecraft-1.jpg
   - minecraft-2.jpg
   - minecraft-3.jpg
   - family-photo.jpg
3. Click **"Commit changes"**

### Enable GitHub Pages
1. Go to **Settings** (tab at top)
2. Click **Pages** (left sidebar)
3. Under "Source", select **main** branch
4. Click **Save**
5. Wait 2-3 minutes

### Your Site is Live! 🎉
Your site will be at: `https://YOUR-USERNAME.github.io/v3d-creative/`

---

## How It Works

### When Someone Orders:
1. Customer fills out the form on your site
2. Clicks "Place Order"
3. Data goes to your Google Sheet in the "Product Orders" tab
4. Customer sees the Venmo QR code and pays Hudson directly
5. You check your sheet for new orders and process them!

### Google Sheet Columns:
- Timestamp
- Product
- First Name
- Last Name
- Email
- Name/Text (what they want printed)
- Color
- Quantity
- Price Per Unit
- Total Price
- Notes
- Status (update this as you work on orders!)

---

## Troubleshooting

### Orders not showing up?
- Double-check you pasted the Web App URL in BOTH `index.html` AND `contact.html`
- Make sure you deployed as "Anyone" can access
- Try re-deploying: Deploy → Manage deployments → Edit → New version

### Can't authorize the script?
- Run the test function first
- Complete authorization
- Then deploy

### Images not showing?
- Make sure all image files are uploaded to GitHub
- Check that file names match exactly (case-sensitive!)

---

## What's Next?

1. Check your Google Sheet daily for new orders
2. Update the "Status" column as you work (New Order → In Progress → Completed)
3. When you want to add more products, just tell me and I'll add them to the site!

---

## Need Help?

If something isn't working, double-check:
- ✅ You copied the full Web App URL
- ✅ You updated BOTH index.html and contact.html
- ✅ All files are uploaded to GitHub
- ✅ Script is deployed as "Anyone" can access

Good luck! 🚀
