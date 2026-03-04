function doPost(e) {
  try {
    // Open your specific spreadsheet by ID
    const SHEET_ID = '1RQiL0eK7GkGiLzXqt93QXh_n1ZAtk1k4Prog1m_gqXk';
    const spreadsheet = SpreadsheetApp.openById(SHEET_ID);
    
    // Parse the incoming data
    const data = JSON.parse(e.postData.contents);
    
    // Handle all orders in one central sheet
    handleOrder(spreadsheet, data);
    
    // Return success response
    return ContentService.createTextOutput(JSON.stringify({
      'status': 'success',
      'message': 'Order received successfully'
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    // Return error response
    return ContentService.createTextOutput(JSON.stringify({
      'status': 'error',
      'message': error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function handleOrder(spreadsheet, data) {
  // Get or create "All Orders" sheet
  let sheet = spreadsheet.getSheetByName('All Orders');
  
  if (!sheet) {
    sheet = spreadsheet.insertSheet('All Orders');
    
    // Create headers
    sheet.appendRow([
      'Timestamp',
      'Product',
      'Name',
      'Email',
      'Quantity Ordered',
      'Item Details',
      'Price Per Unit',
      'Notes',
      'Status'
    ]);
    
    // Format header row
    const headerRange = sheet.getRange(1, 1, 1, 9);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#667eea');
    headerRange.setFontColor('#ffffff');
    
    // Freeze header row
    sheet.setFrozenRows(1);
  }
  
  // Determine product type and add rows accordingly
  const productName = data.productName;
  
  if (productName === 'Minecraft Custom Name Plate') {
    // One row per nameplate
    const plates = JSON.parse(data.plates);
    plates.forEach(plate => {
      sheet.appendRow([
        data.timestamp,
        productName,
        data.name,
        data.email,
        1,  // Always 1 - each row is one item
        `Name: ${plate.name}, Color: ${plate.color}`,
        data.pricePerUnit,
        data.notes,
        'New Order'
      ]);
    });
    
  } else if (productName === 'Headphone/Backpack/Purse Desk Hook') {
    // One row per hook
    const hooks = JSON.parse(data.hooks);
    const isSingleColor = data.colorType.includes('Single');
    
    hooks.forEach(hook => {
      const details = isSingleColor 
        ? `Color: ${hook.color}`
        : `Primary: ${hook.primaryColor}, Secondary: ${hook.secondaryColor}`;
      
      sheet.appendRow([
        data.timestamp,
        productName,
        data.name,
        data.email,
        1,  // Always 1 - each row is one item
        details,
        data.pricePerUnit,
        data.notes,
        'New Order'
      ]);
    });
    
  } else if (productName === 'Bunny Silhouette' || 
             productName === 'Hello Spring Sign' || 
             productName === 'Hello Spring Circle Sign' ||
             productName === 'Brick Letter Name Plate') {
    // One row per item (bunny, sign, or brick plate)
    let items;
    if (productName === 'Bunny Silhouette') {
      items = JSON.parse(data.bunnies);
    } else if (productName === 'Brick Letter Name Plate') {
      items = JSON.parse(data.plates);
    } else {
      items = JSON.parse(data.signs);
    }
    
    items.forEach(item => {
      const details = productName === 'Brick Letter Name Plate'
        ? `Name: ${item.name}, Color: ${item.color}`
        : `Color: ${item.color}`;
      
      sheet.appendRow([
        data.timestamp,
        productName,
        data.name,
        data.email,
        1,  // Always 1 - each row is one item
        details,
        data.pricePerUnit,
        data.notes,
        'New Order'
      ]);
    });
  }
  
  // Auto-resize columns
  sheet.autoResizeColumns(1, 9);
}

// Test function
function testOrder() {
  const testData = {
    postData: {
      contents: JSON.stringify({
        timestamp: new Date().toLocaleString(),
        productName: 'Minecraft Custom Name Plate',
        name: 'Test Customer',
        email: 'test@example.com',
        plates: JSON.stringify([
          { name: 'STEVE', color: 'Blue' },
          { name: 'ALEX', color: 'Pink' }
        ]),
        pricePerUnit: '$7',
        notes: 'Test order'
      })
    }
  };
  
  const result = doPost(testData);
  Logger.log(result.getContent());
}
