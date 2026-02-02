// Google Apps Script for 3D Printing Store
// This script receives all form submissions and adds them to your Google Sheet

function doPost(e) {
  try {
    // Open your specific spreadsheet by ID
    const SHEET_ID = '1RQiL0eK7GkGiLzXqt93QXh_n1ZAtk1k4Prog1m_gqXk';
    const spreadsheet = SpreadsheetApp.openById(SHEET_ID);
    
    // Parse the incoming data
    const data = JSON.parse(e.postData.contents);
    
    // Determine which type of form was submitted
    if (data.productName) {
      // Product order form
      handleProductOrder(spreadsheet, data);
    } else if (data.formType === 'Custom Print Request') {
      // Custom print request form
      handleCustomRequest(spreadsheet, data);
    }
    
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

function handleProductOrder(spreadsheet, data) {
  // Get or create "Product Orders" sheet
  let sheet = spreadsheet.getSheetByName('Product Orders');
  
  if (!sheet) {
    sheet = spreadsheet.insertSheet('Product Orders');
    
    // Create headers
    sheet.appendRow([
      'Timestamp',
      'Product',
      'First Name',
      'Last Name',
      'Email',
      'Phone',
      'Name/Text',
      'Color',
      'Quantity',
      'Price Per Unit',
      'Total Price',
      'Notes',
      'Status'
    ]);
    
    // Format header row
    const headerRange = sheet.getRange(1, 1, 1, 13);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#667eea');
    headerRange.setFontColor('#ffffff');
  }
  
  // Add the order data
  sheet.appendRow([
    data.timestamp,
    data.productName,
    data.firstName,
    data.lastName,
    data.email,
    data.phone,
    data.nameText,
    data.color,
    data.quantity,
    data.pricePerUnit,
    data.totalPrice,
    data.notes,
    'New Order'
  ]);
  
  // Auto-resize columns
  sheet.autoResizeColumns(1, 13);
}

function handleCustomRequest(spreadsheet, data) {
  // Get or create "Custom Requests" sheet
  let sheet = spreadsheet.getSheetByName('Custom Requests');
  
  if (!sheet) {
    sheet = spreadsheet.insertSheet('Custom Requests');
    
    // Create headers
    sheet.appendRow([
      'Timestamp',
      'First Name',
      'Last Name',
      'Email',
      'Phone',
      'Project Description',
      'Has File?',
      'Preferred Color',
      'Quantity',
      'Timeline',
      'Additional Notes',
      'Status'
    ]);
    
    // Format header row
    const headerRange = sheet.getRange(1, 1, 1, 12);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#667eea');
    headerRange.setFontColor('#ffffff');
  }
  
  // Add the request data
  sheet.appendRow([
    data.timestamp,
    data.firstName,
    data.lastName,
    data.email,
    data.phone,
    data.projectDescription,
    data.hasFile,
    data.preferredColor,
    data.quantity,
    data.timeline,
    data.additionalNotes,
    'New Request'
  ]);
  
  // Auto-resize columns
  sheet.autoResizeColumns(1, 12);
}

// Test function for product orders
function testProductOrder() {
  const testData = {
    postData: {
      contents: JSON.stringify({
        timestamp: new Date().toLocaleString(),
        productName: 'Minecraft Custom Name Plate',
        firstName: 'Test',
        lastName: 'Customer',
        email: 'test@example.com',
        phone: '555-1234',
        nameText: 'STEVE',
        color: 'Green',
        quantity: '2',
        pricePerUnit: '$7',
        totalPrice: '$14',
        notes: 'This is a test order'
      })
    }
  };
  
  const result = doPost(testData);
  Logger.log(result.getContent());
}

// Test function for custom requests
function testCustomRequest() {
  const testData = {
    postData: {
      contents: JSON.stringify({
        timestamp: new Date().toLocaleString(),
        formType: 'Custom Print Request',
        firstName: 'Test',
        lastName: 'Customer',
        email: 'test@example.com',
        phone: '555-1234',
        projectDescription: 'I need a custom phone stand',
        hasFile: 'No - need help designing',
        preferredColor: 'Black',
        quantity: '1',
        timeline: 'Within 2 weeks',
        additionalNotes: 'This is a test request'
      })
    }
  };
  
  const result = doPost(testData);
  Logger.log(result.getContent());
}
