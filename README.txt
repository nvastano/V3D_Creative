V3D CREATIVE - COMPLETE SITE PACKAGE
====================================

FOLDER STRUCTURE:
- index.html (homepage with product grid)
- product-desk-hook.html
- product-bunny.html
- product-hello-spring.html
- product-hello-spring-circle.html
- product-minecraft.html
- about.html
- google-script.js (for Google Apps Script)
- images/ (all product photos and logo)

SETUP INSTRUCTIONS:

1. GOOGLE SHEETS SETUP:
   - Open your Google Sheet
   - Go to Extensions → Apps Script
   - Delete any existing code
   - Copy ALL code from google-script.js
   - Paste into the editor
   - Save (💾)
   - Deploy → New deployment → Web app
   - Execute as: Me
   - Who has access: Anyone
   - Deploy → Copy the URL

2. UPDATE HTML FILES:
   You need to add your Google Script URL to ALL 5 product pages:
   
   - product-desk-hook.html (line with SCRIPT_URL)
   - product-bunny.html (line with SCRIPT_URL)
   - product-hello-spring.html (line with SCRIPT_URL)
   - product-hello-spring-circle.html (line with SCRIPT_URL)
   - product-minecraft.html (line with SCRIPT_URL)
   
   Replace: const SCRIPT_URL = 'YOUR_GOOGLE_SCRIPT_URL_HERE';
   With: const SCRIPT_URL = 'YOUR_ACTUAL_GOOGLE_SCRIPT_URL';

3. UPLOAD TO GITHUB:
   - Use GitHub Desktop (easiest)
   - Or use command line: git add . && git commit -m "New site" && git push
   
4. GOOGLE SHEET - ONE CENTRAL SHEET:
   All orders from all products go into ONE sheet called "All Orders"
   
   Columns:
   1. Timestamp
   2. Product (which product)
   3. Name (customer name)
   4. Email
   5. Item Details (colors, text, etc.)
   6. Price Per Unit
   7. Notes
   8. Status
   
   Each physical item gets its own row!

PRODUCTS:
1. Desk Hook - $5 single / $7 dual
2. Bunny Silhouette - $4
3. Hello Spring Sign - $5
4. Hello Spring Circle - $6
5. Minecraft Name Plate - $7

Need help? Ask Claude!
