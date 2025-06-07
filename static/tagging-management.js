/**
 * Tagging Management JavaScript
 * Handles authentication and data display for the tagging management interface
 */

let isAuthenticated = false;

/**
 * Authenticate user for tagging management access
 */
async function authenticate() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const authError = document.getElementById("authError");
  const authBtn = document.getElementById("authBtn");

  if (!username || !password) {
    authError.innerHTML = '<div class="error">Please enter both username and password.</div>';
    return;
  }

  authBtn.disabled = true;
  authBtn.textContent = "Authenticating...";

  try {
    authError.innerHTML = '<div class="loading">Authenticating...</div>';

    const response = await fetch("/auth-report", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      if (data.success) {
        isAuthenticated = true;
        document.getElementById("authSection").style.display = "none";
        document.getElementById("managementContent").style.display = "block";
        loadTaggingStats();
      } else {
        authError.innerHTML = '<div class="error">Authentication failed</div>';
      }
    } else {
      const errorData = await response.json();
      authError.innerHTML = `<div class="error">${errorData.detail || "Authentication failed"}</div>`;
    }
  } catch (error) {
    console.error("Authentication error:", error);
    authError.innerHTML = '<div class="error">Connection error. Please try again.</div>';
  } finally {
    authBtn.disabled = false;
    authBtn.textContent = "Login";
  }
}

/**
 * Load and display tagging statistics
 */
async function loadTaggingStats() {
  const loading = document.getElementById("loading");
  const error = document.getElementById("error");
  const tableBody = document.getElementById("managementTableBody");

  // Show loading state
  loading.style.display = "block";
  error.style.display = "none";
  tableBody.innerHTML = "";

  try {
    const response = await fetch("/tagging-stats");
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Update summary statistics
    updateSummaryStats(data.summary);

    // Populate table
    populateTable(data.data);

  } catch (err) {
    console.error("Error loading tagging stats:", err);
    error.innerHTML = '<div class="error">Failed to load tagging statistics. Please try again.</div>';
    error.style.display = "block";
  } finally {
    loading.style.display = "none";
  }
}

/**
 * Update summary statistics cards
 */
function updateSummaryStats(summary) {
  document.getElementById("totalTopics").textContent = summary.total_topics;
  document.getElementById("totalNarratives").textContent = summary.total_narratives;
  document.getElementById("totalDoneNarratives").textContent = summary.total_done_narratives;
  document.getElementById("totalMissingNarratives").textContent = summary.total_missing_narratives;
  document.getElementById("totalInitial").textContent = summary.total_initial;
  document.getElementById("totalYes").textContent = summary.total_yes;
  document.getElementById("totalNo").textContent = summary.total_no;
  document.getElementById("totalTooObvious").textContent = summary.total_too_obvious;
  document.getElementById("totalProblem").textContent = summary.total_problem;
}

/**
 * Populate the management table with data
 */
function populateTable(data) {
  const tableBody = document.getElementById("managementTableBody");
  
  if (data.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: 20px; color: #999;">
          No tagging data available
        </td>
      </tr>
    `;
    return;
  }

  // Sort data by sheet then by narrative
  data.sort((a, b) => {
    const sheetCompare = a.sheet.localeCompare(b.sheet);
    if (sheetCompare !== 0) return sheetCompare;
    return a.narrative.localeCompare(b.narrative);
  });

  const rows = data.map(item => {
    const missingDisplay = item.missing > 0 ? item.missing : '';
    
    // Generate styled numbers - show empty cells for zero values
    const initialNumber = item.initial_count > 0 ? 
      `<span class="initial-number">${item.initial_count}</span>` : '';
    const yesNumber = item.yes_count > 0 ? 
      `<span class="yes-number">${item.yes_count}</span>` : '';
    const noNumber = item.no_count > 0 ? 
      `<span class="no-number">${item.no_count}</span>` : '';
    const obviousNumber = item.too_obvious_count > 0 ? 
      `<span class="too-obvious-number">${item.too_obvious_count}</span>` : '';
    const problemNumber = item.problem_count > 0 ? 
      `<span class="problem-number">${item.problem_count}</span>` : '';
    const missingNumber = item.missing > 0 ? 
      `<span class="missing-number">${missingDisplay}</span>` : 
      missingDisplay;
    
    return `
      <tr>
        <td>${escapeHtml(item.sheet)}</td>
        <td class="narrative-cell" title="${escapeHtml(item.narrative)}">
          ${escapeHtml(item.narrative)}
        </td>
        <td class="number-cell">${initialNumber}</td>
        <td class="number-cell">${yesNumber}</td>
        <td class="number-cell">${noNumber}</td>
        <td class="number-cell">${obviousNumber}</td>
        <td class="number-cell">${problemNumber}</td>
        <td class="number-cell">${missingNumber}</td>
      </tr>
    `;
  }).join('');

  tableBody.innerHTML = rows;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Handle Enter key press in password field
 */
document.addEventListener('DOMContentLoaded', function() {
  const passwordField = document.getElementById('password');
  const usernameField = document.getElementById('username');
  
  [passwordField, usernameField].forEach(field => {
    if (field) {
      field.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
          authenticate();
        }
      });
    }
  });
});
