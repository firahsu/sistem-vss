/**
 * Google Apps Script untuk otomatisasi submit data Google Form ke Webhook
 * 
 * Instalasi:
 * 1. Buka Google Sheet yang menampilkan response Google Form
 * 2. Extensions → Apps Script → Copy paste kode ini
 * 3. Ganti WEBHOOK_URL sesuai server Anda
 * 4. Set trigger: onFormSubmit() → On form submit
 * 5. Authorize script untuk access sheet dan network
 * 
 * Asumsi kolom Sheet (sesuaikan index jika diperlukan):
 * [0] Timestamp (otomatis dari Google Form)
 * [1] Nama Mahasiswa
 * [2] Jurusan/Program Studi
 * [3] Judul Skripsi
 * [4] Abstrak Skripsi
 * [5] Tahun Akademik
 */

// ============================================================================
// KONFIGURASI
// ============================================================================
// GANTI dengan URL server webhook Anda (contoh: http://localhost:8000/webhook atau https://domain.com/webhook)
const WEBHOOK_URL = "http://localhost:8000/webhook";

// Set true hanya saat debugging (akan banyak log di Apps Script)
const DEBUG = false;


// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Mengambil data dari baris terakhir di sheet.
 * Mengasumsikan kolom urutan sesuai di atas.
 * 
 * @return {Object} Data object dengan key: {nama, jurusan, judul, abstrak, tahun}
 */
function getLatestSubmission() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName("Form Responses"); // Nama sheet di Google Form
  
  if (!sheet) {
    throw new Error("Sheet 'Form Responses' tidak ditemukan. Silakan periksa nama sheet.");
  }
  
  const lastRow = sheet.getLastRow();
  
  if (lastRow < 2) {
    // Header hanya (row 1), tidak ada submission baru
    Logger.log("[Apps Script] Tidak ada submission baru (sheet masih kosong atau hanya header)");
    return null;
  }
  
  // Ambil data baris terakhir (20 kolom untuk jaga-jaga)
  const range = sheet.getRange(lastRow, 1, 1, 20); // Range dari kolom 1-20
  const values = range.getValues();
  const row = values[0];
  
  // DEBUG: Log seluruh row untuk melihat struktur asli
  if (DEBUG) {
    Logger.log("[DEBUG] Seluruh row array:");
    for (let i = 0; i < 15; i++) {
      Logger.log(`[${i}] = ${row[i]}`);
    }
  }
  
  // Mapping kolom sesuai urutan Google Sheet (hasil debug):
  // [0]=Row#, [1]=Empty, [2]=Timestamp, [3]=Email, [4]=Nama, [5]=NIM, [6]=Jurusan, [7]=Periode, 
  // [8]=Alamat, [9]=HP, [10]=Judul, [11]=Abstrak, [12]=File, [13]=Tahun
  const data = {
    timestamp: row[2] || "",
    nama: row[4] || "",           // Kolom E - Nama Mahasiswa
    jurusan: row[6] || "",        // Kolom G - Jurusan/Prodi
    judul: row[10] || "",         // Kolom K - Judul Skripsi
    abstrak: row[11] || "",       // Kolom L - Abstrak Skripsi
    tahun: row[13] || "",         // Kolom N - Tahun Skripsi
  };
  
  Logger.log("[Apps Script] Data mapping: " + JSON.stringify(data));
  return data;
}


/**
 * Kirim data ke webhook via HTTP POST.
 */
function sendToWebhook(data) {
  Logger.log("[Apps Script] === ENTERING sendToWebhook ===");
  
  if (!data) {
    Logger.log("[Apps Script] ERROR: Data is null/undefined");
    throw new Error("Data kosong");
  }
  
  Logger.log("[Apps Script] Data received: " + JSON.stringify(data));
  
  const payload = {
    nama: data.nama.toString().trim(),
    judul: data.judul.toString().trim(),
    abstrak: data.abstrak.toString().trim(),
    jurusan: data.jurusan.toString().trim(),
    tahun: data.tahun.toString().trim(),
  };
  
  Logger.log("[Apps Script] Payload: " + JSON.stringify(payload));
  
  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: false,
    timeout: 30,
  };
  
  try {
    Logger.log("[Apps Script] Sending to: " + WEBHOOK_URL);
    const response = UrlFetchApp.fetch(WEBHOOK_URL, options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    Logger.log("[Apps Script] Response code: " + responseCode);
    Logger.log("[Apps Script] Response: " + responseText);
    
    if (responseCode === 200) {
      Logger.log("[Apps Script] ✓ SUCCESS");
      return JSON.parse(responseText);
    } else {
      Logger.log("[Apps Script] ERROR: Status " + responseCode);
      throw new Error("Status " + responseCode);
    }
  } catch (error) {
    Logger.log("[Apps Script] CATCH: " + error.toString());
    throw error;
  }
}


// ============================================================================
// MAIN HANDLER
// ============================================================================

/**
 * Trigger function yang dipanggil otomatis saat Google Form menerima submission.
 * Diset via: Resources → Triggers → Add trigger → On form submit
 * 
 * @param {GoogleAppsScript.Events.FormSubmitEvent} e - Event object dari Google Form
 */
function onFormSubmit(e) {
  try {
    Logger.log("[Apps Script] ===== STARTED onFormSubmit() =====");
    Logger.log("[Apps Script] Getting latest submission...");
    
    // Ambil data submission terbaru dari sheet
    const data = getLatestSubmission();
    Logger.log("[Apps Script] getLatestSubmission() returned");
    
    if (!data) {
      Logger.log("[Apps Script] Tidak ada data baru, skip processing");
      return;
    }
    
    Logger.log("[Apps Script] Data obtained: " + JSON.stringify(data));
    Logger.log("[Apps Script] About to call sendToWebhook()...");
    
    // Kirim ke webhook
    const result = sendToWebhook(data);
    Logger.log("[Apps Script] sendToWebhook() returned successfully");
    
    // Log success
    Logger.log("[Apps Script] ✓ SUCCESS");
    Logger.log("[Apps Script] Response: " + JSON.stringify(result));
    Logger.log(
      `[Apps Script] Dokumen ID: ${result.id}, Status: ${result.status}, Pesan: ${result.pesan}`
    );
    Logger.log("[Apps Script] ===== FINISHED (SUCCESS) =====");
    
  } catch (error) {
    // Log error - wrap in try-catch to ensure logging happens
    try {
      Logger.log("[Apps Script] ===== ERROR OCCURRED =====");
      Logger.log("[Apps Script] Error type: " + error.constructor.name);
      Logger.log("[Apps Script] Error message: " + error.message);
      Logger.log("[Apps Script] Error string: " + error.toString());
      if (error.stack) {
        Logger.log("[Apps Script] Stack trace: " + error.stack);
      }
    } catch (logError) {
      Logger.log("[Apps Script] Could not log error details: " + logError.toString());
    }
  }
}


// ============================================================================
// MANUAL TEST (optional, panggil dari editor)
// ============================================================================

/**
 * Test function (optional, panggil dari editor untuk debug)
 * Gunakan untuk testing tanpa Google Form submit.
 */
function testWebhookManual() {
  Logger.log("[Apps Script] ===== testWebhookManual() STARTED =====");
  
  try {
    Logger.log("[Apps Script] Step 1: Getting latest submission...");
    const data = getLatestSubmission();
    Logger.log("[Apps Script] Step 2: Got data back");
    
    if (!data) {
      Logger.log("[Apps Script] ERROR: data is null!");
      return;
    }
    
    Logger.log("[Apps Script] Step 3: Data is valid, about to call sendToWebhook()");
    Logger.log("[Apps Script] Data: " + JSON.stringify(data));
    
    const result = sendToWebhook(data);
    Logger.log("[Apps Script] Step 4: Got result from sendToWebhook()");
    Logger.log("[Apps Script] RESULT: " + JSON.stringify(result));
    
    Logger.log("[Apps Script] ===== testWebhookManual() FINISHED (SUCCESS) =====");
    
  } catch (error) {
    Logger.log("[Apps Script] ===== ERROR in testWebhookManual() =====");
    Logger.log("[Apps Script] Error: " + error.toString());
    Logger.log("[Apps Script] Message: " + error.message);
  }
}
