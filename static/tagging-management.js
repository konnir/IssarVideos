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

/**
 * Add Narrative Modal Functions
 */

// Global counter for form lines
let formLineCounter = 1;

/**
 * Show the Add Narrative modal
 */
function showAddNarrativeModal() {
  if (!isAuthenticated) {
    alert('Please authenticate first');
    return;
  }
  
  document.getElementById('addNarrativeModal').style.display = 'block';
  
  // Reset to single form line
  resetFormContainer();
  
  // Load available topics into dropdown
  loadTopics();
  
  // Clear any previous messages
  document.getElementById('addNarrativeError').style.display = 'none';
}

/**
 * Hide the Add Narrative modal
 */
function hideAddNarrativeModal() {
  document.getElementById('addNarrativeModal').style.display = 'none';
}

/**
 * Reset form container to single line
 */
function resetFormContainer() {
  const container = document.getElementById('narrativeFormContainer');
  formLineCounter = 1;
  
  // Clear container and add first line
  container.innerHTML = createFormLineHTML(1);
}

/**
 * Create HTML for a new form line
 */
function createFormLineHTML(lineId, copyTopic = '', copyNarrative = '') {
  return `
    <div class="narrative-form-line" id="formLine${lineId}" data-line-id="${lineId}">
      <div class="form-row" style="display: grid !important; grid-template-columns: 1.5fr 1.5fr 2fr 1fr auto !important; grid-template-rows: 1fr !important; gap: 30px !important; align-items: start !important; background: #2d2d2d !important; border: 2px solid #404040 !important; border-radius: 12px !important; padding: 20px !important; width: 100% !important; min-width: 0 !important; overflow: visible !important; flex-direction: row !important; flex-wrap: nowrap !important; margin-bottom: 20px !important;">
        <div class="form-field" style="grid-column: 1 !important; grid-row: 1 !important; display: flex !important; flex-direction: column !important; min-width: 0 !important; width: 100% !important;">
          <label for="sheet${lineId}">Topic:</label>
          <input type="text" id="sheet${lineId}" class="form-input topic-input" placeholder="Enter Topic" value="${copyTopic}" list="topicsList"/>
        </div>
        <div class="form-field" style="grid-column: 2 !important; grid-row: 1 !important; display: flex !important; flex-direction: column !important; min-width: 0 !important; width: 100% !important;">
          <label for="narrative${lineId}">Narrative:</label>
          <input type="text" id="narrative${lineId}" class="form-input narrative-input" placeholder="Enter narrative text" value="${copyNarrative}" />
        </div>
        <div class="form-field form-field-story" style="grid-column: 3 !important; grid-row: 1 !important; display: flex !important; flex-direction: column !important; min-width: 0 !important; width: 100% !important;">
          <label for="story${lineId}">Story:</label>
          <textarea id="story${lineId}" class="form-textarea story-input" placeholder="Enter story content" rows="4"></textarea>
          <div class="story-buttons">
            <button class="suggest-story-btn" onclick="suggestStory(${lineId})" data-line-id="${lineId}" type="button">✨ Suggest Story</button>
            <button class="edit-prompt-btn" onclick="editPrompt(${lineId})" data-line-id="${lineId}" type="button">📝 Edit Prompt</button>
          </div>
        </div>
        <div class="form-field" style="grid-column: 4 !important; grid-row: 1 !important; display: flex !important; flex-direction: column !important; min-width: 0 !important; width: 100% !important;">
          <label for="link${lineId}">Link:</label>
          <input type="url" id="link${lineId}" class="form-input link-input" placeholder="https://example.com" />
        </div>
        <div class="form-field form-field-button" style="grid-column: 5 !important; grid-row: 1 !important; display: flex !important; flex-direction: column !important; align-items: flex-start !important; padding-bottom: 0 !important;">
          <label>Actions:</label>
          <div class="button-group" style="display: flex; gap: 5px; align-items: center;">
            <button class="add-btn-inline" onclick="addSingleNarrative(${lineId})" data-line-id="${lineId}">Add</button>
            <button class="plus-btn" onclick="addNewFormLine(${lineId})" title="Add new line">+</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

/**
 * Add a new form line, copying topic and narrative if filled
 */
function addNewFormLine(sourceLineId) {
  formLineCounter++;
  const newLineId = formLineCounter;
  
  // Get values to copy from source line - Topic and Narrative only
  const sourceTopic = document.getElementById(`sheet${sourceLineId}`).value.trim();
  const sourceNarrative = document.getElementById(`narrative${sourceLineId}`).value.trim();
  
  // Copy custom prompt if it exists for the source line
  if (customPrompts[sourceLineId]) {
    customPrompts[newLineId] = customPrompts[sourceLineId];
  }
  
  // Create new form line HTML
  const newLineHTML = createFormLineHTML(newLineId, sourceTopic, sourceNarrative);
  
  // Add new line to container
  const container = document.getElementById('narrativeFormContainer');
  container.insertAdjacentHTML('beforeend', newLineHTML);
  
  // Update edit button appearance if custom prompt was copied
  if (customPrompts[newLineId]) {
    const editBtn = document.querySelector(`[data-line-id="${newLineId}"].edit-prompt-btn`);
    editBtn.textContent = '📝 Prompt Edited ✓';
    editBtn.style.background = '#357abd'; // Darker blue to indicate custom
  }
  
  // Focus on the story field of the new line (since Topic and Narrative are pre-filled)
  document.getElementById(`story${newLineId}`).focus();
}

/**
 * Add a single narrative from the specified form line
 */
async function addSingleNarrative(lineId) {
  const errorDiv = document.getElementById('addNarrativeError');
  
  // Clear previous messages
  errorDiv.style.display = 'none';
  
  // Get form values for this specific line
  const sheet = document.getElementById(`sheet${lineId}`).value.trim();
  const narrative = document.getElementById(`narrative${lineId}`).value.trim();
  const story = document.getElementById(`story${lineId}`).value.trim();
  const link = document.getElementById(`link${lineId}`).value.trim();
  
  // Validate required fields
  if (!sheet || !narrative || !story || !link) {
    errorDiv.innerHTML = '<div class="error">Please fill in all fields</div>';
    errorDiv.style.display = 'block';
    return;
  }
  
  // Validate URL format
  try {
    new URL(link);
  } catch {
    errorDiv.innerHTML = '<div class="error">Please enter a valid URL</div>';
    errorDiv.style.display = 'block';
    return;
  }
  
  // Get the specific Add button for this line
  const addBtn = document.querySelector(`[data-line-id="${lineId}"].add-btn-inline`);
  addBtn.disabled = true;
  addBtn.textContent = 'Adding...';
  
  try {
    const response = await fetch('/add-narrative', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        Sheet: sheet,
        Narrative: narrative,
        Story: story,
        Link: link
      }),
    });
    
    if (response.ok) {
      const result = await response.json();
      
      // Change button to "Added ✓" and keep it disabled
      addBtn.textContent = 'Added ✓';
      addBtn.disabled = true;
      
      // Refresh the stats table
      await loadTaggingStats();
      
      // Keep all fields intact after successful submission for potential reuse
      // User can manually clear fields if needed
      
    } else {
      const errorData = await response.json();
      let errorMessage = errorData.detail || 'Failed to add narrative';
      
      // Check for duplicate link error and provide user-friendly message
      if (errorMessage.toLowerCase().includes('link already exists') || 
          errorMessage.toLowerCase().includes('record with this link already exists')) {
        errorMessage = '🔗 This link is already in the database. Please choose a different link.';
      }
      
      errorDiv.innerHTML = `<div class="error">${errorMessage}</div>`;
      errorDiv.style.display = 'block';
      // Reset button on failure
      addBtn.disabled = false;
      addBtn.textContent = 'Add';
    }
  } catch (error) {
    console.error('Error adding narrative:', error);
    errorDiv.innerHTML = '<div class="error">Connection error. Please try again.</div>';
    errorDiv.style.display = 'block';
    // Reset button only on error
    addBtn.disabled = false;
    addBtn.textContent = 'Add';
  }
}

/**
 * Suggest a story based on the narrative using AI
 */
async function suggestStory(lineId) {
  const narrative = document.getElementById(`narrative${lineId}`).value.trim();
  const errorDiv = document.getElementById('addNarrativeError');
  
  // Clear previous messages
  errorDiv.style.display = 'none';
  
  // Validate that narrative is filled
  if (!narrative) {
    errorDiv.innerHTML = '<div class="error">Please enter a narrative first to generate a story suggestion</div>';
    errorDiv.style.display = 'block';
    return;
  }
  
  // Get the suggest button for this line
  const suggestBtn = document.querySelector(`[data-line-id="${lineId}"].suggest-story-btn`);
  const storyTextarea = document.getElementById(`story${lineId}`);
  
  // Set loading state
  suggestBtn.disabled = true;
  suggestBtn.textContent = '✨ Generating...';
  
  try {
    // Check if this line has a custom prompt
    const hasCustomPrompt = customPrompts[lineId];
    let response;
    
    if (hasCustomPrompt) {
      // Use custom prompt endpoint
      response = await fetch('/generate-story-custom-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          narrative: narrative,
          custom_prompt: customPrompts[lineId],
          style: 'engaging'
        }),
      });
    } else {
      // Use default endpoint
      response = await fetch('/generate-story', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          narrative: narrative,
          style: 'engaging',
          additional_context: ''
        }),
      });
    }
    
    if (response.ok) {
      const result = await response.json();
      
      // Set the generated story in the textarea
      storyTextarea.value = result.story;
      
      // Reset button
      suggestBtn.disabled = false;
      suggestBtn.textContent = '✨ Suggest Story';
      
      // Show success message briefly
      errorDiv.innerHTML = '<div class="success">Story generated successfully! You can edit it before adding.</div>';
      errorDiv.style.display = 'block';
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        errorDiv.style.display = 'none';
      }, 3000);
      
    } else {
      const errorData = await response.json();
      let errorMessage = errorData.detail || 'Failed to generate story';
      
      errorDiv.innerHTML = `<div class="error">Story generation failed: ${errorMessage}</div>`;
      errorDiv.style.display = 'block';
      
      // Reset button
      suggestBtn.disabled = false;
      suggestBtn.textContent = '✨ Suggest Story';
    }
  } catch (error) {
    console.error('Error generating story:', error);
    errorDiv.innerHTML = '<div class="error">Connection error. Please try again.</div>';
    errorDiv.style.display = 'block';
    
    // Reset button
    suggestBtn.disabled = false;
    suggestBtn.textContent = '✨ Suggest Story';
  }
}

/**
 * Edit Prompt Modal Functions
 */

// Global storage for custom prompts per form line
let customPrompts = {};
let currentEditingLineId = null;

// Default prompt template
const DEFAULT_PROMPT = `Create a brief story concept (2-3 sentences) that incorporates this hidden narrative:

Hidden Narrative: "{narrative}"

Provide only a concise story idea that:
1. Subtly includes the hidden narrative
2. Is suitable for short video content
3. Can be expanded into a full video later

Keep it short and focused on the core concept only.`;

/**
 * Edit prompt for a specific line
 */
function editPrompt(lineId) {
  // Check if narrative field exists and has content
  const narrativeField = document.getElementById(`narrative${lineId}`);
  const narrative = narrativeField ? narrativeField.value.trim() : '';
  
  if (!narrative) {
    // Show error message using the same error div as other validation errors
    const errorDiv = document.getElementById('addNarrativeError');
    errorDiv.innerHTML = '<div class="error">Please enter a narrative first before editing the prompt</div>';
    errorDiv.style.display = 'block';
    
    // Hide error after 3 seconds
    setTimeout(() => {
      errorDiv.style.display = 'none';
    }, 3000);
    
    return; // Don't open the modal
  }
  
  currentEditingLineId = lineId;
  
  // Get existing custom prompt or use default
  const existingPrompt = customPrompts[lineId] || DEFAULT_PROMPT;
  
  // Show modal and populate with existing prompt
  document.getElementById('editPromptModal').style.display = 'block';
  document.getElementById('customPrompt').value = existingPrompt;
  
  // Clear any previous messages
  document.getElementById('editPromptError').style.display = 'none';
  document.getElementById('promptTestResult').style.display = 'none';
  
  // Update modal title to show the narrative being edited
  const modalHeader = document.querySelector('#editPromptModal .modal-header h3');
  const truncatedNarrative = narrative.length > 50 ? narrative.substring(0, 50) + '...' : narrative;
  modalHeader.textContent = `Edit Story Prompt (${truncatedNarrative})`;
}

/**
 * Hide the edit prompt modal
 */
function hideEditPromptModal() {
  document.getElementById('editPromptModal').style.display = 'none';
  currentEditingLineId = null;
}

/**
 * Save the custom prompt for the current line
 */
function saveCustomPrompt() {
  if (!currentEditingLineId) return;
  
  const promptText = document.getElementById('customPrompt').value.trim();
  const errorDiv = document.getElementById('editPromptError');
  
  // Clear previous messages
  errorDiv.style.display = 'none';
   // Validate prompt
  if (!promptText) {
    errorDiv.innerHTML = '<div class="error">Prompt cannot be empty</div>';
    errorDiv.style.display = 'block';
    return;
  }

  if (!promptText.includes('{narrative}')) {
    errorDiv.innerHTML = '<div class="error">Prompt must include {narrative} placeholder</div>';
    errorDiv.style.display = 'block';
    return;
  }

  // Check if the prompt is actually different from the default
  if (promptText === DEFAULT_PROMPT) {
    // If it's the same as default, remove any custom prompt and reset button
    delete customPrompts[currentEditingLineId];
    
    const editBtn = document.querySelector(`[data-line-id="${currentEditingLineId}"].edit-prompt-btn`);
    editBtn.textContent = '📝 Edit Prompt';
    editBtn.style.background = '#4a90e2'; // Original blue
    
    errorDiv.innerHTML = '<div class="success">Prompt is using default settings</div>';
    errorDiv.style.display = 'block';
    
    // Hide modal after short delay
    setTimeout(() => {
      hideEditPromptModal();
    }, 1500);
    return;
  }

  // Save the custom prompt (only if it's different from default)
  customPrompts[currentEditingLineId] = promptText;
  
  // Update the edit button to show it has a custom prompt with checkmark
  const editBtn = document.querySelector(`[data-line-id="${currentEditingLineId}"].edit-prompt-btn`);
  editBtn.textContent = '📝 Prompt Edited ✓';
  editBtn.style.background = '#357abd'; // Darker blue to indicate custom
  
  // Show success message
  errorDiv.innerHTML = '<div class="success">Custom prompt saved successfully!</div>';
  errorDiv.style.display = 'block';
  
  // Hide modal after short delay
  setTimeout(() => {
    hideEditPromptModal();
  }, 1500);
}

/**
 * Reset to default prompt
 */
function resetToDefaultPrompt() {
  if (!currentEditingLineId) return;
  
  // Remove custom prompt
  delete customPrompts[currentEditingLineId];
  
  // Reset button appearance
  const editBtn = document.querySelector(`[data-line-id="${currentEditingLineId}"].edit-prompt-btn`);
  editBtn.textContent = '📝 Edit Prompt';
  editBtn.style.background = '#4a90e2'; // Original blue
  
  // Update textarea with default prompt
  document.getElementById('customPrompt').value = DEFAULT_PROMPT;
  
  // Show success message
  const errorDiv = document.getElementById('editPromptError');
  errorDiv.innerHTML = '<div class="success">Reset to default prompt!</div>';
  errorDiv.style.display = 'block';
  
  // Hide message after delay
  setTimeout(() => {
    errorDiv.style.display = 'none';
  }, 2000);
}

/**
 * Test the custom prompt with the current narrative
 */
async function testCustomPrompt() {
  if (!currentEditingLineId) return;
  
  const narrative = document.getElementById(`narrative${currentEditingLineId}`).value.trim();
  const customPrompt = document.getElementById('customPrompt').value.trim();
  const resultDiv = document.getElementById('promptTestResult');
  const errorDiv = document.getElementById('editPromptError');
  
  // Clear previous messages
  errorDiv.style.display = 'none';
  resultDiv.style.display = 'none';
  
  // Validate inputs
  if (!narrative) {
    errorDiv.innerHTML = '<div class="error">Please enter a narrative in the form first to test the prompt</div>';
    errorDiv.style.display = 'block';
    return;
  }
  
  if (!customPrompt) {
    errorDiv.innerHTML = '<div class="error">Please enter a custom prompt to test</div>';
    errorDiv.style.display = 'block';
    return;
  }
  
  if (!customPrompt.includes('{narrative}')) {
    errorDiv.innerHTML = '<div class="error">Prompt must include {narrative} placeholder</div>';
    errorDiv.style.display = 'block';
    return;
  }
  
  // Disable test button and show loading
  const testBtn = document.querySelector('.modal-btn.secondary:last-child');
  const originalText = testBtn.textContent;
  testBtn.disabled = true;
  testBtn.textContent = '🧪 Testing...';
  
  try {
    const response = await fetch('/generate-story-custom-prompt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        narrative: narrative,
        custom_prompt: customPrompt,
        style: 'engaging'
      }),
    });
    
    if (response.ok) {
      const result = await response.json();
      
      // Show test result
      resultDiv.className = 'prompt-test-result success';
      resultDiv.innerHTML = `
        <h4>✅ Test Successful</h4>
        <p><strong>Generated Story:</strong></p>
        <pre>${result.story}</pre>
      `;
      resultDiv.style.display = 'block';
      
    } else {
      const errorData = await response.json();
      let errorMessage = errorData.detail || 'Failed to test prompt';
      
      resultDiv.className = 'prompt-test-result error';
      resultDiv.innerHTML = `
        <h4>❌ Test Failed</h4>
        <p><strong>Error:</strong> ${errorMessage}</p>
      `;
      resultDiv.style.display = 'block';
    }
    
  } catch (error) {
    console.error('Error testing prompt:', error);
    resultDiv.className = 'prompt-test-result error';
    resultDiv.innerHTML = `
      <h4>❌ Connection Error</h4>
      <p>Failed to connect to the server. Please try again.</p>
    `;
    resultDiv.style.display = 'block';
  } finally {
    // Reset test button
    testBtn.disabled = false;
    testBtn.textContent = originalText;
  }
}

/**
 * Close modal when clicking outside of it
 */
document.addEventListener('DOMContentLoaded', function() {
  // Handle add narrative modal
  const addModal = document.getElementById('addNarrativeModal');
  if (addModal) {
    addModal.addEventListener('click', function(e) {
      if (e.target === addModal) {
        hideAddNarrativeModal();
      }
    });
  }
  
  // Handle edit prompt modal
  const editModal = document.getElementById('editPromptModal');
  if (editModal) {
    editModal.addEventListener('click', function(e) {
      if (e.target === editModal) {
        hideEditPromptModal();
      }
    });
  }
});

/**
 * Load all available topics into the dropdown
 */
async function loadTopics() {
  try {
    const response = await fetch('/topics');
    if (response.ok) {
      const data = await response.json();
      const topicsList = document.getElementById('topicsList');
      
      // Clear existing options
      topicsList.innerHTML = '';
      
      // Add options for each topic
      data.topics.forEach(topic => {
        const option = document.createElement('option');
        option.value = topic;
        topicsList.appendChild(option);
      });
    } else {
      console.error('Failed to load topics:', response.statusText);
    }
  } catch (error) {
    console.error('Error loading topics:', error);
  }
}

// Load topics on initial page load
document.addEventListener('DOMContentLoaded', function() {
  loadTopics();
});
