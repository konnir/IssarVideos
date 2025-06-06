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
      (r) => r.Tagger_1 && r.Tagger_1 !== "Init"
    ).length;

    // Display statistics
    statsInfo.innerHTML = `
      <div class="stat-card">
        <div class="stat-number">${totalRecords}</div>
        <div class="stat-label">Total Tagged</div>
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
            <th>Tagger</th>
            <th>Result</th>
          </tr>
        </thead>
        <tbody>
    `;

    records.forEach((record) => {
      // Helper function to get result label with color class
      function getResultLabel(result) {
        // If result is null, undefined, empty string, "Init", or 0, keep as "Init"
        if (
          result === null ||
          result === undefined ||
          result === "" ||
          result === "Init" ||
          result === 0 ||
          result === "0"
        ) {
          return '<span class="result-init">Init</span>';
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
          <td>${record.Tagger_1 || "Init"}</td>
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
