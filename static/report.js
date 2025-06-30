// Report functionality
let isAuthenticated = false;

// Protocol-agnostic API utility functions (from tagger.js)
function getBaseUrl() {
  return window.location.origin;
}

async function apiCall(endpoint, options = {}) {
  const url = `${getBaseUrl()}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || `Server error: ${response.status}`;
      throw new Error(errorMessage);
    }

    return response;
  } catch (error) {
    console.error(`API call failed for ${endpoint}:`, error);
    throw error;
  }
}

async function authenticate() {
  const username = document.getElementById("authUsername").value.trim();
  const password = document.getElementById("authPassword").value.trim();
  const authMessage = document.getElementById("authMessage");

  if (!username || !password) {
    authMessage.innerHTML =
      '<div class="error">Please enter both username and password.</div>';
    return;
  }

  try {
    authMessage.innerHTML = '<div class="loading">Authenticating...</div>';

    const response = await apiCall("/auth-report", {
      method: "POST",
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    const result = await response.json();

    if (result.success) {
      isAuthenticated = true;
      document.getElementById("authSection").style.display = "none";
      document.getElementById("reportSection").style.display = "block";
      await loadTaggedRecords();
    }
  } catch (error) {
    authMessage.innerHTML = `<div class="error">Authentication failed: ${error.message}</div>`;
  }
}

async function loadTaggedRecords() {
  const loadingMessage = document.getElementById("loadingMessage");
  const errorMessage = document.getElementById("errorMessage");
  const tableContainer = document.getElementById("tableContainer");
  const statsInfo = document.getElementById("statsInfo");

  try {
    const response = await apiCall("/tagged-records");
    const records = await response.json();

    loadingMessage.style.display = "none";

    if (records.length === 0) {
      tableContainer.innerHTML = "<p>No tagged records found.</p>";
      return;
    }

    // Calculate statistics
    const totalRecords = records.length;
    const tagger1Count = records.filter(
      (r) => r.Tagger_1 && r.Tagger_1 !== ""
    ).length;
    
    // Count unique narratives that have been tagged (individual narratives, not records)
    const uniqueNarrativesTagged = new Set(
      records
        .filter(r => r.Narrative && r.Narrative.trim() !== "" && r.Tagger_1 && r.Tagger_1 !== "")
        .map(r => r.Narrative.trim())
    ).size;
    
    // Count unique taggers
    const uniqueTaggers = new Set(
      records
        .filter(r => r.Tagger_1 && r.Tagger_1 !== "")
        .map(r => r.Tagger_1)
    ).size;
    
    // Count narratives with more than 5 "Yes" records
    const narrativeYesCounts = {};
    records.forEach(record => {
      if (record.Narrative && record.Narrative.trim() !== "" && 
          (record.Tagger_1_Result === 1 || record.Tagger_1_Result === "1")) {
        const narrative = record.Narrative.trim();
        narrativeYesCounts[narrative] = (narrativeYesCounts[narrative] || 0) + 1;
      }
    });
    
    const fullNarrativesTagged = Object.values(narrativeYesCounts).filter(count => count > 5).length;

    // Display statistics
    statsInfo.innerHTML = `
      <div class="stat-card">
        <div class="stat-number">${uniqueNarrativesTagged}</div>
        <div class="stat-label">Narratives Tagged</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">${fullNarrativesTagged}</div>
        <div class="stat-label">Full Narratives Tagged</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">${uniqueTaggers}</div>
        <div class="stat-label">Taggers</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">${tagger1Count}</div>
        <div class="stat-label">Tagged Records</div>
      </div>
    `;

    // Create table
    let tableHTML = `
      <table class="records-table">
        <thead>
          <tr>
            <th>Sheet</th>
            <th>Video Link</th>
            <th>Narrative</th>
            <th>Story</th>
            <th>Tagger</th>
            <th>Result</th>
          </tr>
        </thead>
        <tbody>
    `;

    records.forEach((record) => {
      // Helper function to get result label with color class
      function getResultLabel(result) {
        // If result is null, undefined, empty string, or 0, keep as "Not Tagged"
        if (
          result === null ||
          result === undefined ||
          result === "" ||
          result === 0 ||
          result === "0"
        ) {
          return '<span class="result-init">Not Tagged</span>';
        }

        // Map values to labels with color classes
        const resultMapping = {
          1: '<span class="result-yes">Yes</span>',
          2: '<span class="result-no">No</span>',
          3: '<span class="result-obvious">Too Obvious</span>',
          4: '<span class="result-problem">Problem</span>',
          "1": '<span class="result-yes">Yes</span>',
          "2": '<span class="result-no">No</span>',
          "3": '<span class="result-obvious">Too Obvious</span>',
          "4": '<span class="result-problem">Problem</span>',
        };

        // Return colored label or original value if not found
        return resultMapping[result] || result;
      }

      tableHTML += `
        <tr>
          <td>${record.Sheet || ""}</td>
          <td><a href="${
            record.Link || ""
          }" target="_blank" class="video-link">${(record.Link || "").substring(
        0,
        50
      )}${(record.Link || "").length > 50 ? "..." : ""}</a></td>
          <td class="narrative-cell" title="${record.Narrative || ""}">${
        record.Narrative || ""
      }</td>
          <td class="story-cell" title="${record.Story || ""}">${
        record.Story || ""
      }</td>
          <td>${record.Tagger_1 || "Not Tagged"}</td>
          <td>${getResultLabel(record.Tagger_1_Result)}</td>
        </tr>
      `;
    });

    tableHTML += `
        </tbody>
      </table>
    `;

    tableContainer.innerHTML = tableHTML;
  } catch (error) {
    loadingMessage.style.display = "none";
    errorMessage.innerHTML = `<div class="error">Error loading records: ${error.message}</div>`;
  }
}

// Refresh functions
async function refreshData() {
  const refreshDataBtn = document.getElementById("refreshDataBtn");
  const originalText = refreshDataBtn.textContent;
  
  try {
    refreshDataBtn.textContent = "🔄 Refreshing...";
    refreshDataBtn.disabled = true;
    
    const response = await apiCall("/refresh-data", {
      method: "POST"
    });
    
    const result = await response.json();
    
    // Show success message
    showRefreshMessage(`✅ ${result.message} (${result.total_records} records)`, 'success');
    
    // Reload the report data
    if (isAuthenticated) {
      loadTaggedRecords();
    }
    
  } catch (error) {
    showRefreshMessage(`❌ Failed to refresh data: ${error.message}`, 'error');
  } finally {
    refreshDataBtn.textContent = originalText;
    refreshDataBtn.disabled = false;
  }
}

async function refreshApp() {
  const refreshAppBtn = document.getElementById("refreshAppBtn");
  const originalText = refreshAppBtn.textContent;
  
  try {
    refreshAppBtn.textContent = "♻️ Refreshing...";
    refreshAppBtn.disabled = true;
    
    const response = await apiCall("/refresh-app", {
      method: "POST"
    });
    
    const result = await response.json();
    
    // Show success message
    showRefreshMessage(`✅ ${result.message} (${result.total_records} records)`, 'success');
    
    // Reload the entire page to ensure fresh state
    setTimeout(() => {
      if (isAuthenticated) {
        loadTaggedRecords();
      }
    }, 1000);
    
  } catch (error) {
    showRefreshMessage(`❌ Failed to refresh app: ${error.message}`, 'error');
  } finally {
    refreshAppBtn.textContent = originalText;
    refreshAppBtn.disabled = false;
  }
}

function showRefreshMessage(message, type) {
  // Create or update message element
  let messageEl = document.getElementById("refreshMessage");
  if (!messageEl) {
    messageEl = document.createElement("div");
    messageEl.id = "refreshMessage";
    messageEl.style.cssText = `
      margin: 10px 0;
      padding: 10px;
      border-radius: 4px;
      font-weight: bold;
    `;
    
    // Insert after refresh buttons
    const refreshButtons = document.querySelector(".refresh-buttons");
    refreshButtons.parentNode.insertBefore(messageEl, refreshButtons.nextSibling);
  }
  
  messageEl.className = type;
  messageEl.textContent = message;
  
  if (type === 'success') {
    messageEl.style.cssText += `
      background-color: #d4edda;
      color: #155724;
      border: 1px solid #c3e6cb;
    `;
  } else {
    messageEl.style.cssText += `
      background-color: #f8d7da;
      color: #721c24;
      border: 1px solid #f5c6cb;
    `;
  }
  
  // Auto-hide after 5 seconds
  setTimeout(() => {
    if (messageEl) {
      messageEl.style.opacity = '0';
      setTimeout(() => {
        if (messageEl && messageEl.parentNode) {
          messageEl.parentNode.removeChild(messageEl);
        }
      }, 300);
    }
  }, 5000);
}

// Allow Enter key to submit authentication
document.addEventListener("DOMContentLoaded", function () {
  const authInputs = document.querySelectorAll("#authUsername, #authPassword");
  authInputs.forEach((input) => {
    input.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        authenticate();
      }
    });
  });
});
