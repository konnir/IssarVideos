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
    console.log('Fetching tagging stats...');
    const response = await fetch("/tagging-stats");
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Received tagging stats data:', data);

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
  document.getElementById("totalSheets").textContent = summary.total_sheets;
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
  
  console.log('Populating table with data:', data);
  
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
    console.log('Processing table row item:', item);
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

  console.log('Generated table rows HTML:', rows);
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
async function showAddNarrativeModal() {
  if (!isAuthenticated) {
    alert('Please authenticate first');
    return;
  }
  
  document.getElementById('addNarrativeModal').style.display = 'block';
  
  // Reset to single form line
  resetFormContainer();
  
  // Always reload sheets list when modal opens to ensure fresh data
  await loadAllTopics();
  
  // Load all available narratives as backup
  await loadAllNarratives();
  
  // Clear any previous messages
  document.getElementById('addNarrativeError').style.display = 'none';
  
  // Focus on the first sheet input to make it ready for user interaction
  const firstSheetInput = document.getElementById('sheet1');
  if (firstSheetInput) {
    setTimeout(() => firstSheetInput.focus(), 100);
  }
}

/**
 * Hide the Add Narrative modal
 */
function hideAddNarrativeModal() {
  // Hide the modal
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
  
  // Add event listeners for the first line's sheet input
  addTopicEventListeners(1);
}

/**
 * Create HTML for a new form line
 */
function createFormLineHTML(lineId, copyTopic = '', copyNarrative = '') {
  return `
    <div class="narrative-form-line" id="formLine${lineId}" data-line-id="${lineId}">
      <div class="form-row" style="display: grid !important; grid-template-columns: 1.5fr 2fr 2fr 1fr auto !important; grid-template-rows: 1fr !important; gap: 30px !important; align-items: start !important; background: #2d2d2d !important; border: 2px solid #404040 !important; border-radius: 12px !important; padding: 20px !important; width: 100% !important; min-width: 0 !important; overflow: visible !important; flex-direction: row !important; flex-wrap: nowrap !important; margin-bottom: 20px !important;">
        <div class="form-field" style="grid-column: 1 !important; grid-row: 1 !important; display: flex !important; flex-direction: column !important; min-width: 0 !important; width: 100% !important;">
          <label for="sheet${lineId}">Sheet:</label>
          <input type="text" id="sheet${lineId}" class="form-input topic-input" placeholder="Enter or select Sheet" value="${copyTopic}" list="topicsList" autocomplete="off"/>
        </div>
        <div class="form-field" style="grid-column: 2 !important; grid-row: 1 !important; display: flex !important; flex-direction: column !important; min-width: 0 !important; width: 100% !important;">
          <label for="narrative${lineId}">Narrative:</label>
          <input type="text" id="narrative${lineId}" class="form-input narrative-input" placeholder="Enter or select narrative text" value="${copyNarrative}" list="narrativesList" autocomplete="off"/>
        </div>
        <div class="form-field form-field-story" style="grid-column: 3 !important; grid-row: 1 !important; display: flex !important; flex-direction: column !important; min-width: 0 !important; width: 100% !important;">
          <label for="story${lineId}">Story:</label>
          <textarea id="story${lineId}" class="form-textarea story-input" placeholder="Enter story content" rows="4"></textarea>
          <div class="story-buttons">
            <button class="suggest-story-btn" onclick="suggestStory(${lineId})" data-line-id="${lineId}" type="button">✨ Suggest Story</button>
            <button class="edit-prompt-btn" onclick="editPrompt(${lineId})" data-line-id="${lineId}" type="button">📝 Edit Prompt</button>
            <button class="youtube-search-btn" onclick="openYouTubeSearch(${lineId})" data-line-id="${lineId}" type="button">🎬 Search YouTube</button>
          </div>
        </div>
        <div class="form-field" style="grid-column: 4 !important; grid-row: 1 !important; display: flex !important; flex-direction: column !important; min-width: 0 !important; width: 100% !important;">
          <label for="link${lineId}">Link:</label>
          <input type="url" id="link${lineId}" class="form-input link-input" placeholder="https://example.com" />
          <div id="video-info-${lineId}" class="video-info" style="margin-top: 8px; padding: 8px; background: #404040; color: #fff; border-radius: 4px; font-size: 12px; display: none;"></div>
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
 * Add a new form line, copying sheet, narrative, and story if filled
 */
function addNewFormLine(sourceLineId) {
  formLineCounter++;
  const newLineId = formLineCounter;
  
  // Get values to copy from source line - Sheet, Narrative, and Story
  const sourceTopic = document.getElementById(`sheet${sourceLineId}`).value.trim();
  const sourceNarrative = document.getElementById(`narrative${sourceLineId}`).value.trim();
  const sourceStory = document.getElementById(`story${sourceLineId}`).value.trim();
  
  // Copy custom prompt if it exists for the source line
  if (customPrompts[sourceLineId]) {
    customPrompts[newLineId] = customPrompts[sourceLineId];
  }
  
  // Create new form line HTML
  const newLineHTML = createFormLineHTML(newLineId, sourceTopic, sourceNarrative);
  
  // Add new line to container
  const container = document.getElementById('narrativeFormContainer');
  container.insertAdjacentHTML('beforeend', newLineHTML);
  
  // Copy the story content to the new line if it exists
  if (sourceStory) {
    const newStoryTextarea = document.getElementById(`story${newLineId}`);
    if (newStoryTextarea) {
      newStoryTextarea.value = sourceStory;
    }
  }
  
  // Add event listeners for the new sheet input
  addTopicEventListeners(newLineId);
  
  // Update edit button appearance if custom prompt was copied
  if (customPrompts[newLineId]) {
    const editBtn = document.querySelector(`[data-line-id="${newLineId}"].edit-prompt-btn`);
    editBtn.textContent = '📝 Prompt Edited ✓';
    editBtn.style.background = '#357abd'; // Darker blue to indicate custom
  }
  
  // Focus on the link field of the new line (since Sheet, Narrative, and Story are pre-filled)
  document.getElementById(`link${newLineId}`).focus();
}

/**
 * Add a single narrative from the specified form line
 */
async function addSingleNarrative(lineId) {
  const errorDiv = document.getElementById('addNarrativeError');
  
  // Clear previous messages
  errorDiv.style.display = 'none';
  
  // Get form values for this specific line
  const topic = document.getElementById(`sheet${lineId}`).value.trim();
  const narrative = document.getElementById(`narrative${lineId}`).value.trim();
  const story = document.getElementById(`story${lineId}`).value.trim();
  const link = document.getElementById(`link${lineId}`).value.trim();
  
  // Validate required fields
  if (!topic || !narrative || !story || !link) {
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
        Sheet: topic,
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
 * Load all available sheets for the sheet dropdown
 */
async function loadAllTopics() {
  try {
    console.log('Loading all sheets...');
    const response = await fetch('/topics');
    if (response.ok) {
      const data = await response.json();
      
      console.log('Sheets received:', data.topics);
      
      // Ensure sheets datalist exists
      let topicsList = document.getElementById('topicsList');
      if (!topicsList) {
        console.log('Creating new sheets datalist element');
        topicsList = document.createElement('datalist');
        topicsList.id = 'topicsList';
        // Add it to the modal body so it's always available
        const modalBody = document.querySelector('#addNarrativeModal .modal-body');
        if (modalBody) {
          modalBody.appendChild(topicsList);
        } else {
          console.error('Modal body not found');
          return;
        }
      }
      
      // Always clear and rebuild the options to ensure fresh data
      topicsList.innerHTML = '';
      
      // Add options for each sheet
      data.topics.forEach(topic => {
        const option = document.createElement('option');
        option.value = topic;
        option.textContent = topic; // Ensure text content is set
        topicsList.appendChild(option);
        console.log('Added sheet option:', topic);
      });
      
      console.log('All sheets loaded successfully, total options:', topicsList.children.length);
      
      // Store the topics globally for easy access
      window.availableSheets = data.topics;
      
    } else {
      console.error('Failed to load sheets:', response.statusText);
    }
  } catch (error) {
    console.error('Error loading sheets:', error);
  }
}

/**
 * Load narratives for a specific sheet
 */
async function loadNarratives(topic) {
  if (!topic || topic.trim() === '') {
    return;
  }
  
  try {
    console.log('Loading narratives for sheet:', topic);
    const response = await fetch(`/narratives/${encodeURIComponent(topic)}`);
    if (response.ok) {
      const data = await response.json();
      
      console.log('Narratives received for sheet:', topic, data.narratives);
      
      // Ensure narratives datalist exists
      let narrativesList = document.getElementById('narrativesList');
      if (!narrativesList) {
        console.log('Creating new narratives datalist element');
        narrativesList = document.createElement('datalist');
        narrativesList.id = 'narrativesList';
        // Add it to the modal body so it's always available
        const modalBody = document.querySelector('#addNarrativeModal .modal-body');
        if (modalBody) {
          modalBody.appendChild(narrativesList);
        } else {
          console.error('Modal body not found');
          return;
        }
      }
      
      // Clear existing options
      narrativesList.innerHTML = '';
      
      // Add options for each narrative
      data.narratives.forEach(narrative => {
        const option = document.createElement('option');
        option.value = narrative;
        narrativesList.appendChild(option);
        console.log('Added narrative option for sheet:', narrative);
      });
      
      console.log('Narratives loaded successfully for sheet:', topic, 'total options:', narrativesList.children.length);
    } else {
      console.error('Failed to load narratives for sheet:', topic, response.statusText);
    }
  } catch (error) {
    console.error('Error loading narratives for sheet:', topic, error);
  }
}

/**
 * Load all available narratives
 */
async function loadAllNarratives() {
  try {
    console.log('Loading all narratives...');
    const response = await fetch('/all-records');
    if (response.ok) {
      const data = await response.json();
      
      // Extract unique narratives from all records
      const narratives = [...new Set(data.map(record => record.Narrative).filter(narrative => narrative && narrative.trim() !== ''))];
      console.log('All narratives received:', narratives);
      
      // Ensure narratives datalist exists
      let narrativesList = document.getElementById('narrativesList');
      if (!narrativesList) {
        console.log('Creating new narratives datalist element');
        narrativesList = document.createElement('datalist');
        narrativesList.id = 'narrativesList';
        // Add it to the modal body so it's always available
        const modalBody = document.querySelector('#addNarrativeModal .modal-body');
        if (modalBody) {
          modalBody.appendChild(narrativesList);
        } else {
          console.error('Modal body not found');
          return;
        }
      }
      
      // Clear existing options
      narrativesList.innerHTML = '';
      
      // Add options for each narrative
      narratives.forEach(narrative => {
        const option = document.createElement('option');
        option.value = narrative;
        narrativesList.appendChild(option);
        console.log('Added narrative option:', narrative);
      });
      
      console.log('All narratives loaded successfully, total options:', narrativesList.children.length);
    } else {
      console.error('Failed to load narratives:', response.statusText);
    }
  } catch (error) {
    console.error('Error loading narratives:', error);
  }
}

/**
 * Add event listeners to a form line for sheet selection
 */
function addTopicEventListeners(lineId) {
  const topicInput = document.getElementById(`sheet${lineId}`);
  if (topicInput) {
    let timeoutId;
    
    // Handle input change with debouncing to avoid interfering with dropdown
    topicInput.addEventListener('input', function() {
      const selectedTopic = this.value.trim();
      
      // Clear previous timeout
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      
      // Only load narratives if there's a complete sheet name and after a short delay
      if (selectedTopic.length > 0) {
        timeoutId = setTimeout(() => {
          // Check if the value is still the same and appears to be a complete selection
          if (this.value.trim() === selectedTopic) {
            loadNarratives(selectedTopic);
          }
        }, 500); // Wait 500ms before loading narratives
      }
    });
    
    // Handle change event (when user definitely selects from dropdown)
    topicInput.addEventListener('change', function() {
      const selectedTopic = this.value.trim();
      if (selectedTopic) {
        // Clear any pending timeout
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        // Load narratives immediately on selection
        loadNarratives(selectedTopic);
      }
    });
    
    // Handle focus event to ensure the full list is available
    topicInput.addEventListener('focus', function() {
      // Clear any pending timeout when focusing
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      // Make sure the sheets list is fully loaded
      loadAllTopics();
    });
  }
}

// Load all topics on initial page load
document.addEventListener('DOMContentLoaded', function() {
  loadAllTopics();
});

/**
 * Open YouTube search using API and populate link field
 */
async function openYouTubeSearch(lineId) {
  const storyTextarea = document.getElementById(`story${lineId}`);
  const linkInput = document.getElementById(`link${lineId}`);
  const videoInfoDiv = document.getElementById(`video-info-${lineId}`);
  
  if (!storyTextarea) {
    alert('Story field not found');
    return;
  }
  
  const storyContent = storyTextarea.value.trim();
  if (!storyContent) {
    alert('Please enter a story first to search on YouTube');
    return;
  }
  
  try {
    // Show loading state
    if (videoInfoDiv) {
      videoInfoDiv.style.display = 'block';
      videoInfoDiv.innerHTML = '<div style="text-align: center;">🔄 Generating search query...</div>';
    }
    
    // Step 1: Generate video keywords from the story
    const keywordsResponse = await fetch('/generate-video-keywords', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        story: storyContent,
        max_keywords: 5
      })
    });
    
    if (!keywordsResponse.ok) {
      throw new Error(`Failed to generate keywords: ${keywordsResponse.status}`);
    }
    
    const keywordsData = await keywordsResponse.json();
    const searchQuery = keywordsData.search_query;
    
    if (!searchQuery) {
      throw new Error('No search query generated from the story');
    }
    
    // Update loading state
    if (videoInfoDiv) {
      videoInfoDiv.innerHTML = '<div style="text-align: center;">🔍 Searching for videos...</div>';
    }
    
    // Step 2: Search for videos using the generated query
    const searchResponse = await fetch(`/search-videos?query=${encodeURIComponent(searchQuery)}&max_results=1&max_duration=300`, {
      method: 'POST'
    });
    
    if (!searchResponse.ok) {
      throw new Error(`Failed to search videos: ${searchResponse.status}`);
    }
    
    const searchData = await searchResponse.json();
    
    if (!searchData.videos || !Array.isArray(searchData.videos)) {
      throw new Error('Invalid response format from video search');
    }
    
    if (searchData.videos && searchData.videos.length > 0) {
      const video = searchData.videos[0];
      
      // Set the URL in the link input field
      if (linkInput) {
        linkInput.value = video.url;
      }
      
      // Display video information
      if (videoInfoDiv) {
        const duration = Math.floor(video.duration / 60) + ':' + String(video.duration % 60).padStart(2, '0');
        videoInfoDiv.innerHTML = `
          <div style="
            background: #3a3a3a;
            border: 1px solid #555;
            border-radius: 8px;
            padding: 12px;
            margin: 4px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          ">
            <div style="
              background: rgba(255,255,255,0.05);
              border-radius: 6px;
              padding: 8px;
              margin-bottom: 8px;
            ">
              <div style="
                color: #60a5fa;
                font-weight: 600;
                margin-bottom: 4px;
                line-height: 1.3;
                font-size: 12px;
                cursor: pointer;
                transition: color 0.2s ease;
              " 
              onclick="openVideoInPopup('${video.url.replace(/'/g, "\\'")}', '${video.title.replace(/'/g, "\\'")}')"
              onmouseover="this.style.color='#3b82f6'"
              onmouseout="this.style.color='#60a5fa'"
              title="Click to open video in popup window"
              >${video.title}</div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px;">
              <div style="
                background: rgba(255,255,255,0.03);
                padding: 6px 8px;
                border-radius: 4px;
                border-left: 3px solid #60a5fa;
              ">
                <div style="color: #9ca3af; margin-bottom: 2px;">📺 Channel</div>
                <div style="color: #e5e7eb; font-weight: 500;">${video.uploader}</div>
              </div>
              
              <div style="
                background: rgba(255,255,255,0.03);
                padding: 6px 8px;
                border-radius: 4px;
                border-left: 3px solid #f59e0b;
              ">
                <div style="color: #9ca3af; margin-bottom: 2px;">⏱️ Duration</div>
                <div style="color: #e5e7eb; font-weight: 500;">${duration}</div>
              </div>
              
              <div style="
                background: rgba(255,255,255,0.03);
                padding: 6px 8px;
                border-radius: 4px;
                border-left: 3px solid #ef4444;
              ">
                <div style="color: #9ca3af; margin-bottom: 2px;">👁️ Views</div>
                <div style="color: #e5e7eb; font-weight: 500;">${video.view_count?.toLocaleString() || 'N/A'}</div>
              </div>
              
              <div style="
                background: rgba(255,255,255,0.03);
                padding: 6px 8px;
                border-radius: 4px;
                border-left: 3px solid #8b5cf6;
              ">
                <div style="color: #9ca3af; margin-bottom: 2px;">🔍 Query</div>
                <div style="color: #e5e7eb; font-weight: 500;">"${searchQuery}"</div>
              </div>
            </div>
          </div>
        `;
        videoInfoDiv.style.display = 'block';
      }
    } else {
      if (videoInfoDiv) {
        videoInfoDiv.innerHTML = '<div style="color: #ff6b6b; text-align: center;">No videos found for this story</div>';
        videoInfoDiv.style.display = 'block';
      }
    }
    
  } catch (error) {
    console.error('Error in YouTube search:', error);
    if (videoInfoDiv) {
      videoInfoDiv.innerHTML = `<div style="color: #ff6b6b; text-align: center;">Error: ${error.message}</div>`;
      videoInfoDiv.style.display = 'block';
    }
    alert(`Error searching YouTube: ${error.message}`);
  }
}

/**
 * Open TikTok search in a popup window with the story content
 */
function openTikTokSearch(lineId) {
  const storyTextarea = document.getElementById(`story${lineId}`);
  if (!storyTextarea) {
    alert('Story field not found');
    return;
  }
  
  const storyContent = storyTextarea.value.trim();
  if (!storyContent) {
    alert('Please enter a story first to search on TikTok');
    return;
  }
  
  // Encode the story content for URL
  const searchQuery = encodeURIComponent(storyContent);
  const tiktokSearchUrl = `https://www.tiktok.com/search?q=${searchQuery}`;
  
  // Get screen dimensions for 90% size and center positioning
  const screenWidth = window.screen.availWidth;
  const screenHeight = window.screen.availHeight;
  const popupWidth = Math.floor(screenWidth * 0.9);
  const popupHeight = Math.floor(screenHeight * 0.9);
  
  // Calculate center position
  const left = Math.floor((screenWidth - popupWidth) / 2) + window.screen.availLeft;
  const top = Math.floor((screenHeight - popupHeight) / 2) + window.screen.availTop;
  
  // Open TikTok search in popup window
  const popup = window.open(
    tiktokSearchUrl,
    'tiktokSearch',
    `width=${popupWidth},height=${popupHeight},left=${left},top=${top},scrollbars=yes,resizable=yes,toolbar=yes,location=yes,menubar=no,status=no`
  );
  
  if (popup) {
    popup.focus();
  } else {
    // Fallback if popup is blocked
    alert('Popup blocked. Please allow popups and try again, or manually search TikTok for: ' + storyContent);
  }
}

/**
 * Close YouTube search section and restore modal to normal size
 */
function closeYouTubeSearch() {
  const youtubeSection = document.getElementById('youtubeSection');
  const youtubeFrame = document.getElementById('youtubeFrame');
  const modalContent = document.querySelector('.modal-content');
  const modalBody = document.getElementById('modalBody');
  
  if (youtubeSection) {
    youtubeSection.style.display = 'none';
  }
  
  if (youtubeFrame) {
    youtubeFrame.src = ''; // Clear the iframe
    youtubeFrame.srcdoc = ''; // Clear the iframe content
  }
  
  if (modalContent) {
    // Restore modal to normal size
    modalContent.style.maxHeight = '';
    modalContent.style.height = '';
    modalContent.style.display = '';
    modalContent.style.flexDirection = '';
  }
  
  if (modalBody) {
    // Restore modal body styling
    modalBody.style.flex = '';
    modalBody.style.overflowY = '';
    modalBody.style.maxHeight = '';
  }
}

/**
 * Open video in a popup window (75% screen size, centered)
 */
function openVideoInPopup(videoUrl, videoTitle) {
  // Get screen dimensions for 75% size and center positioning
  const screenWidth = window.screen.availWidth;
  const screenHeight = window.screen.availHeight;
  const popupWidth = Math.floor(screenWidth * 0.75);
  const popupHeight = Math.floor(screenHeight * 0.75);
  
  // Calculate center position
  const left = Math.floor((screenWidth - popupWidth) / 2) + window.screen.availLeft;
  const top = Math.floor((screenHeight - popupHeight) / 2) + window.screen.availTop;
  
  // Create popup window name (remove special characters for valid window name)
  const windowName = 'videoPopup_' + Date.now();
  
  // Open video in popup window
  const popup = window.open(
    videoUrl,
    windowName,
    `width=${popupWidth},height=${popupHeight},left=${left},top=${top},scrollbars=yes,resizable=yes,toolbar=yes,location=yes,menubar=no,status=no`
  );
  
  if (popup) {
    popup.focus();
    // Optional: Set the popup title if possible
    try {
      popup.document.title = videoTitle || 'Video Player';
    } catch (e) {
      // Cross-origin restrictions may prevent this, but it's not critical
      console.log('Could not set popup title due to cross-origin restrictions');
    }
  } else {
    // Fallback if popup is blocked
    alert('Popup blocked. Please allow popups and try again, or manually open: ' + videoUrl);
  }
}
