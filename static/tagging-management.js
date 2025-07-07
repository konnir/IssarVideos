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
  document.getElementById("totalSheets").textContent = summary.total_topics;
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
        <td colspan="9" style="text-align: center; padding: 20px; color: #999;">
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
        <td class="action-cell">
          <button class="add-row-btn" onclick="openAddNarrativeWithData('${escapeHtml(item.sheet).replace(/'/g, "\\'")}', '${escapeHtml(item.narrative).replace(/'/g, "\\'")}')">
            ➕
          </button>
        </td>
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
  
  // Reset Add All button state when modal is closed
  resetAddAllButton();
}

/**
 * Reset form container to single line
 */
function resetFormContainer() {
  const container = document.getElementById('narrativeFormContainer');
  formLineCounter = 1;
  
  // Clear container and add first line
  const newHTML = createFormLineHTML(1);
  container.innerHTML = newHTML;
  
  // Add event listeners for the first line's sheet input
  addTopicEventListeners(1);
  
  // Setup automatic story generation for narrative fields
  setupAutoStoryGeneration();
  
  // Reset Add All button to initial state
  resetAddAllButton();
  
  // Check initial validation state
  setTimeout(() => {
    checkAllLinesValid();
  }, 100);
}

/**
 * Create HTML for a new form line
 */
function createFormLineHTML(lineId, copyTopic = '', copyNarrative = '') {
  return `
    <div class="narrative-form-line" id="formLine${lineId}" data-line-id="${lineId}">
      <div class="form-row" style="display: grid !important; grid-template-columns: 1.5fr 2fr 2fr 1fr auto !important; grid-template-rows: 1fr !important; gap: 30px !important; align-items: start !important; background: #2d2d2d !important; border: 2px solid #404040 !important; border-radius: 12px !important; padding: 20px !important; width: 100% !important; min-width: 0 !important; overflow: visible !important; flex-direction: row !important; flex-wrap: nowrap !important; margin-bottom: 20px !important;">
        <div class="form-field" style="grid-column: 1 !important; grid-row: 1 !important; display: flex !important; flex-direction: column !important; min-width: 0 !important; width: 100% !important;">
          <label for="sheet${lineId}">Topic:</label>
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
          <div class="button-group" style="display: flex; flex-direction: column; gap: 5px; align-items: stretch;">
            <button class="add-btn-inline" onclick="addSingleNarrative(${lineId})" data-line-id="${lineId}">Add</button>
            <button class="plus-btn" onclick="addNewFormLine(${lineId})" title="Add new line">+</button>
            <button class="x10-btn" onclick="addTenFormLines(${lineId})" title="Add 9 duplicate lines" data-line-id="${lineId}">x10</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

/**
 * Add a new form line, copying sheet and narrative (story will be auto-generated)
 */
function addNewFormLine(sourceLineId) {
  formLineCounter++;
  const newLineId = formLineCounter;
  
  // Get values to copy from source line - Sheet and Narrative only
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
  
  // Don't copy story content - always generate fresh story if narrative exists
  if (sourceNarrative) {
    // If there's a narrative, trigger auto generation after a brief delay
    setTimeout(() => {
      autoGenerateStory(newLineId, false);
    }, 500); // Small delay to ensure DOM is fully updated
  }
  
  // Add event listeners for the new sheet input
  addTopicEventListeners(newLineId);
  
  // Update edit button appearance if custom prompt was copied
  if (customPrompts[newLineId]) {
    const editBtn = document.querySelector(`[data-line-id="${newLineId}"].edit-prompt-btn`);
    editBtn.textContent = '📝 Prompt Edited ✓';
    editBtn.style.background = '#357abd'; // Darker blue to indicate custom
  }
  
  // Check validation state after adding new line
  setTimeout(checkAllLinesValid, 200);
  
  // Note: Removed automatic focus to prevent scrolling when creating multiple lines during YouTube search
}

/**
 * Add nine form lines, copying sheet and narrative from source line (stories will be auto-generated)
 */
function addTenFormLines(sourceLineId) {
  // Get values to copy from source line - Sheet and Narrative only
  const sourceTopic = document.getElementById(`sheet${sourceLineId}`).value.trim();
  const sourceNarrative = document.getElementById(`narrative${sourceLineId}`).value.trim();
  
  // Get the x10 button for this line to show progress
  const x10Btn = document.querySelector(`[data-line-id="${sourceLineId}"].x10-btn`);
  const originalText = x10Btn.textContent;
  
  // Disable the button during processing
  x10Btn.disabled = true;
  x10Btn.textContent = 'Adding...';
  
  // Add 9 duplicate lines
  for (let i = 1; i <= 9; i++) {
    formLineCounter++;
    const newLineId = formLineCounter;
    
    // Copy custom prompt if it exists for the source line
    if (customPrompts[sourceLineId]) {
      customPrompts[newLineId] = customPrompts[sourceLineId];
    }
    
    // Create new form line HTML
    const newLineHTML = createFormLineHTML(newLineId, sourceTopic, sourceNarrative);
    
    // Add new line to container
    const container = document.getElementById('narrativeFormContainer');
    container.insertAdjacentHTML('beforeend', newLineHTML);
    
    // Don't copy story content - always generate fresh story if narrative exists
    if (sourceNarrative) {
      // If there's a narrative, trigger auto generation after a brief delay
      // Stagger the calls for multiple lines to avoid overwhelming the server
      setTimeout(() => {
        autoGenerateStory(newLineId, false);
      }, 500 + (i * 200)); // Stagger by 200ms per line
    }
    
    // Add event listeners for the new sheet input
    addTopicEventListeners(newLineId);
    
    // Update edit button appearance if custom prompt was copied
    if (customPrompts[newLineId]) {
      const editBtn = document.querySelector(`[data-line-id="${newLineId}"].edit-prompt-btn`);
      if (editBtn) {
        editBtn.textContent = '📝 Prompt Edited ✓';
        editBtn.style.background = '#357abd'; // Darker blue to indicate custom
      }
    }
  }
  
  // Re-enable the button and show completion
  x10Btn.disabled = false;
  x10Btn.textContent = originalText;
  
  // Show success message
  const errorDiv = document.getElementById('addNarrativeError');
  if (errorDiv) {
    errorDiv.innerHTML = '<div class="success">✅ Successfully added 9 duplicate lines!</div>';
    errorDiv.style.display = 'block';
    
    // Hide success message after 3 seconds
    setTimeout(() => {
      errorDiv.style.display = 'none';
    }, 3000);
  }
  
  // Check validation state after adding multiple lines
  setTimeout(checkAllLinesValid, 500);
}

/**
 * Show the Add Narrative modal with pre-filled Sheet and Narrative data
 */
async function openAddNarrativeWithData(sheetName, narrativeText) {
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
  
  // Wait for DOM to be updated after resetFormContainer
  setTimeout(() => {
    // Pre-fill the Sheet and Narrative fields
    const sheetInput = document.getElementById('sheet1');
    const narrativeInput = document.getElementById('narrative1');
    
    if (sheetInput) {
      sheetInput.value = sheetName;
    }
    
    if (narrativeInput) {
      narrativeInput.value = narrativeText;
    }
    
    // Verify the values were actually set
    setTimeout(() => {
      const finalSheetValue = document.getElementById('sheet1')?.value;
      const finalNarrativeValue = document.getElementById('narrative1')?.value;
    }, 50);
    
    // Clear any previous messages
    const errorElement = document.getElementById('addNarrativeError');
    if (errorElement) {
      errorElement.style.display = 'none';
    }
    
    // Trigger automatic story generation since narrative is pre-filled
    if (narrativeText && narrativeText.trim()) {
      setTimeout(() => {
        autoGenerateStory(1, false);
      }, 200); // Small delay to ensure DOM is fully updated and event listeners are attached
    }
    
    // Focus on the story input since Sheet and Narrative are already filled
    const storyInput = document.getElementById('story1');
    if (storyInput) {
      setTimeout(() => {
        storyInput.focus();
      }, 100);
    }
    
    // Check validation state after pre-filling
    setTimeout(() => {
      checkAllLinesValid();
    }, 400);
  }, 100); // Wait for DOM to be updated after innerHTML change
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
  
  // Disable ALL Add buttons to prevent multiple simultaneous operations
  const allAddBtns = document.querySelectorAll('.add-btn-inline');
  const buttonStates = new Map(); // Store original states
  
  allAddBtns.forEach(btn => {
    const btnLineId = btn.getAttribute('data-line-id');
    // Store the original state
    buttonStates.set(btnLineId, {
      disabled: btn.disabled,
      text: btn.textContent
    });
    
    // Only change the text for the current button being processed
    if (btnLineId === lineId.toString()) {
      btn.textContent = 'Adding...';
    }
    // Disable all buttons but don't change text for other buttons
    btn.disabled = true;
  });
  
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
      
      // Change the current button to "Added ✓" and keep it disabled
      const currentAddBtn = document.querySelector(`[data-line-id="${lineId}"].add-btn-inline`);
      currentAddBtn.textContent = 'Added ✓';
      currentAddBtn.disabled = true;
      
      // Re-enable all other Add buttons and restore their original states (except the current one)
      const allAddBtns = document.querySelectorAll('.add-btn-inline');
      allAddBtns.forEach(btn => {
        const btnLineId = btn.getAttribute('data-line-id');
        
        // Skip the current button that was just marked as "Added ✓"
        if (btnLineId === lineId.toString()) {
          return;
        }
        
        const originalState = buttonStates.get(btnLineId);
        if (originalState) {
          // Restore exactly what it was before
          btn.disabled = originalState.disabled;
          btn.textContent = originalState.text;
        } else {
          // Fallback to default state
          btn.disabled = false;
          btn.textContent = 'Add';
        }
      });
      
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
      
      // Mark the current button as "Fail" and keep it disabled
      const currentAddBtn = document.querySelector(`[data-line-id="${lineId}"].add-btn-inline`);
      currentAddBtn.textContent = 'Fail';
      currentAddBtn.disabled = true;
      currentAddBtn.classList.add('fail-state');
      
      // Re-enable all other Add buttons and restore their original states
      const allAddBtns = document.querySelectorAll('.add-btn-inline');
      allAddBtns.forEach(btn => {
        const btnLineId = btn.getAttribute('data-line-id');
        
        // Skip the current button that was just marked as "Fail"
        if (btnLineId === lineId.toString()) {
          return;
        }
        
        const originalState = buttonStates.get(btnLineId);
        if (originalState) {
          // Restore original state
          btn.disabled = originalState.disabled;
          btn.textContent = originalState.text;
        } else {
          // Fallback to default state
          btn.disabled = false;
          btn.textContent = 'Add';
        }
      });
    }
  } catch (error) {
    console.error('Error adding narrative:', error);
    errorDiv.innerHTML = '<div class="error">Connection error. Please try again.</div>';
    errorDiv.style.display = 'block';
    
    // Mark the current button as "Fail" and keep it disabled
    const currentAddBtn = document.querySelector(`[data-line-id="${lineId}"].add-btn-inline`);
    currentAddBtn.textContent = 'Fail';
    currentAddBtn.disabled = true;
    currentAddBtn.classList.add('fail-state');
    
    // Re-enable all other Add buttons and restore their original states
    const allAddBtns = document.querySelectorAll('.add-btn-inline');
    allAddBtns.forEach(btn => {
      const btnLineId = btn.getAttribute('data-line-id');
      
      // Skip the current button that was just marked as "Fail"
      if (btnLineId === lineId.toString()) {
        return;
      }
      
      const originalState = buttonStates.get(btnLineId);
      if (originalState) {
        // Restore original state
        btn.disabled = originalState.disabled;
        btn.textContent = originalState.text;
      } else {
        // Fallback to default state
        btn.disabled = false;
        btn.textContent = 'Add';
      }
    });
  }
  
  // Check validation state after adding/attempting to add a line
  setTimeout(checkAllLinesValid, 300);
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
      
      // Trigger validation check after auto-populating story
      setTimeout(checkAllLinesValid, 100);
      
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
    const response = await fetch('/topics');
    if (response.ok) {
      const data = await response.json();
      
      // Ensure sheets datalist exists
      let topicsList = document.getElementById('topicsList');
      if (!topicsList) {
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
      });
      
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
    const response = await fetch(`/narratives/${encodeURIComponent(topic)}`);
    if (response.ok) {
      const data = await response.json();
      
      // Ensure narratives datalist exists
      let narrativesList = document.getElementById('narrativesList');
      if (!narrativesList) {
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
      });
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
    const response = await fetch('/all-records');
    if (response.ok) {
      const data = await response.json();
      
      // Extract unique narratives from all records
      const narratives = [...new Set(data.map(record => record.Narrative).filter(narrative => narrative && narrative.trim() !== ''))];
      
      // Ensure narratives datalist exists
      let narrativesList = document.getElementById('narrativesList');
      if (!narrativesList) {
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
      });
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
 * Open YouTube search using API and populate multiple lines with results
 */
async function openYouTubeSearch(lineId) {
  const storyTextarea = document.getElementById(`story${lineId}`);
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
      videoInfoDiv.innerHTML = '<div style="text-align: center; color: #999; font-size: 11px;">🔄 Generating search query...</div>';
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
      videoInfoDiv.innerHTML = '<div style="text-align: center; color: #999; font-size: 11px;">🔍 Searching for video...</div>';
    }
    
    // Step 2: Search for videos using the generated query - request 1 result
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
      // Hide loading state for the original line
      if (videoInfoDiv) {
        videoInfoDiv.style.display = 'none';
      }
      
      // Get the first (and only) video found
      const video = searchData.videos[0];
      
      // Populate the current line with video data
      const linkInput = document.getElementById(`link${lineId}`);
      if (linkInput) {
        linkInput.value = video.url;
        // Trigger validation check after auto-populating link
        setTimeout(checkAllLinesValid, 100);
      }
      
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
      
      // Show success message in the error div
      const errorDiv = document.getElementById('addNarrativeError');
      if (errorDiv) {
        errorDiv.innerHTML = `<div class="success">Found video and populated the current line!</div>`;
        errorDiv.style.display = 'block';
        
        // Hide success message after 3 seconds
        setTimeout(() => {
          errorDiv.style.display = 'none';
        }, 3000);
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
    }
  } else {
    // Fallback if popup is blocked
    alert('Popup blocked. Please allow popups and try again, or manually open: ' + videoUrl);
  }
}

// Global object to track debounce timers and auto-generation state
let narrativeAutoGeneration = {
  debounceTimers: {},
  inProgress: {},
  videoSearchInProgress: {},
  debounceDelay: 1500 // 1.5 seconds delay after user stops typing
};

/**
 * Automatically generate story when narrative is filled
 * This is a streamlined version of suggestStory for automatic triggers
 */
async function autoGenerateStory(lineId, isBlurTrigger = false) {
  const narrative = document.getElementById(`narrative${lineId}`).value.trim();
  const storyTextarea = document.getElementById(`story${lineId}`);
  const suggestBtn = document.querySelector(`[data-line-id="${lineId}"].suggest-story-btn`);
  
  // Don't auto-generate if:
  // 1. No narrative provided
  // 2. Story already has content (don't overwrite user's work)
  // 3. Auto-generation already in progress for this line
  // 4. Manual suggest button is disabled (manual generation in progress)
  if (!narrative || 
      storyTextarea.value.trim() || 
      narrativeAutoGeneration.inProgress[lineId] ||
      (suggestBtn && suggestBtn.disabled)) {
    return;
  }
  
  // Mark as in progress
  narrativeAutoGeneration.inProgress[lineId] = true;
  
  // Add subtle loading indicator
  const storyLabel = document.querySelector(`label[for="story${lineId}"]`);
  const originalLabelText = storyLabel ? storyLabel.textContent : '';
  if (storyLabel && !originalLabelText.includes('🤖')) {
    storyLabel.textContent = originalLabelText + ' 🤖';
  }
  
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
      
      // Only set the story if the textarea is still empty (user might have typed something)
      if (!storyTextarea.value.trim()) {
        storyTextarea.value = result.story;
        
        // Trigger validation check after auto-populating story
        setTimeout(checkAllLinesValid, 100);
        
        // Add a subtle visual indication that the story was auto-generated
        storyTextarea.style.backgroundColor = '#f0fff0'; // Very light green
        setTimeout(() => {
          storyTextarea.style.backgroundColor = '';
        }, 2000);
        
        // Automatically trigger video search after story is generated
        setTimeout(() => {
          autoYouTubeSearch(lineId);
        }, 1000); // Wait 1 second after story generation to start video search
      }
    }
  } catch (error) {
    // We don't show errors for automatic generation to avoid interrupting user flow
  } finally {
    // Mark as no longer in progress
    narrativeAutoGeneration.inProgress[lineId] = false;
    
    // Remove loading indicator
    const storyLabel = document.querySelector(`label[for="story${lineId}"]`);
    if (storyLabel && storyLabel.textContent.includes('🤖')) {
      storyLabel.textContent = storyLabel.textContent.replace(' 🤖', '');
    }
  }
}

/**
 * Automatically search for YouTube video when story is generated
 * This is a streamlined version of openYouTubeSearch for automatic triggers
 */
async function autoYouTubeSearch(lineId) {
  const storyTextarea = document.getElementById(`story${lineId}`);
  const videoInfoDiv = document.getElementById(`video-info-${lineId}`);
  const linkInput = document.getElementById(`link${lineId}`);
  
  // Don't auto-search if:
  // 1. No story content
  // 2. Link field already has content (don't overwrite user's work)
  // 3. Story field is empty (user might have cleared it)
  // 4. Auto video search already in progress for this line
  if (!storyTextarea || 
      !storyTextarea.value.trim() || 
      linkInput.value.trim() ||
      narrativeAutoGeneration.videoSearchInProgress[lineId]) {
    return;
  }
  
  const storyContent = storyTextarea.value.trim();
  
  // Mark video search as in progress
  narrativeAutoGeneration.videoSearchInProgress[lineId] = true;
  
  try {
    // Show subtle loading state
    if (videoInfoDiv) {
      videoInfoDiv.style.display = 'block';
      videoInfoDiv.innerHTML = '<div style="text-align: center; color: #999; font-size: 11px;">🔄 Auto-searching video...</div>';
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
      videoInfoDiv.innerHTML = '<div style="text-align: center; color: #999; font-size: 11px;">🔍 Finding video...</div>';
    }
    
    // Step 2: Search for videos using the generated query - request 1 result
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
      // Get the first (and only) video found
      const video = searchData.videos[0];
      
      // Only populate if link field is still empty (user might have filled it)
      if (!linkInput.value.trim()) {
        linkInput.value = video.url;
        
        // Trigger validation check after auto-populating link
        setTimeout(checkAllLinesValid, 100);
        
        // Add subtle visual indication that the link was auto-populated
        linkInput.style.backgroundColor = '#f0f8ff'; // Very light blue
        setTimeout(() => {
          linkInput.style.backgroundColor = '';
        }, 3000);
      }
      
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
            
            <div style="margin-top: 8px; padding: 4px 8px; background: rgba(0,255,0,0.1); border-radius: 4px; font-size: 10px; color: #4ade80;">
              ✨ Auto-suggested based on story
            </div>
          </div>
        `;
        videoInfoDiv.style.display = 'block';
      }
      
    } else {
      // No videos found - show subtle message
      if (videoInfoDiv) {
        videoInfoDiv.innerHTML = '<div style="color: #999; text-align: center; font-size: 11px;">No videos found for this story</div>';
        videoInfoDiv.style.display = 'block';
        
        // Hide the message after 3 seconds
        setTimeout(() => {
          videoInfoDiv.style.display = 'none';
        }, 3000);
      }
    }
    
  } catch (error) {
    // Hide loading indicator on error
    if (videoInfoDiv) {
      videoInfoDiv.style.display = 'none';
    }
    // We don't show errors for automatic operations to avoid interrupting user flow
  } finally {
    // Mark video search as no longer in progress
    narrativeAutoGeneration.videoSearchInProgress[lineId] = false;
  }
}

/**
 * Setup automatic story generation for narrative fields
 */
function setupAutoStoryGeneration() {
  // Set up debounced input listeners for narrative fields
  const narrativeInputs = document.querySelectorAll('.narrative-input');
  
  narrativeInputs.forEach(input => {
    const lineId = input.id.replace('narrative', '');
    
    // Clear any existing timer for this line
    if (narrativeAutoGeneration.debounceTimers[lineId]) {
      clearTimeout(narrativeAutoGeneration.debounceTimers[lineId]);
    }
    
    // Add input event listener for debounced auto-generation
    input.addEventListener('input', function() {
      const narrativeText = this.value.trim();
      
      // Clear previous timer
      if (narrativeAutoGeneration.debounceTimers[lineId]) {
        clearTimeout(narrativeAutoGeneration.debounceTimers[lineId]);
      }
      
      // Only auto-generate if there's text and no story content yet
      if (narrativeText && !document.getElementById(`story${lineId}`).value.trim()) {
        narrativeAutoGeneration.debounceTimers[lineId] = setTimeout(() => {
          autoGenerateStory(lineId, false);
        }, narrativeAutoGeneration.debounceDelay);
      }
    });
    
    // Add blur event listener for immediate auto-generation
    input.addEventListener('blur', function() {
      const narrativeText = this.value.trim();
      
      // Only auto-generate if there's text and no story content yet
      if (narrativeText && !document.getElementById(`story${lineId}`).value.trim()) {
        // Clear any pending timer and generate immediately
        if (narrativeAutoGeneration.debounceTimers[lineId]) {
          clearTimeout(narrativeAutoGeneration.debounceTimers[lineId]);
        }
        
        autoGenerateStory(lineId, true);
      }
    });
  });
}

/**
 * Check if all form lines are valid (have all required fields filled)
 */
function checkAllLinesValid() {
  const formLines = document.querySelectorAll('.narrative-form-line');
  const addAllButton = document.getElementById('addAllButton');
  
  if (!addAllButton || formLines.length === 0) {
    return;
  }
  
  let allValid = true;
  let validLines = 0;
  let addedLines = 0;
  
  formLines.forEach(line => {
    const lineId = line.getAttribute('data-line-id');
    const topic = document.getElementById(`sheet${lineId}`)?.value.trim() || '';
    const narrative = document.getElementById(`narrative${lineId}`)?.value.trim() || '';
    const story = document.getElementById(`story${lineId}`)?.value.trim() || '';
    const link = document.getElementById(`link${lineId}`)?.value.trim() || '';
    
    // Check if the line is already added (button shows "Added ✓") or failed (button shows "Fail")
    const addBtn = document.querySelector(`[data-line-id="${lineId}"].add-btn-inline`);
    if (addBtn && (addBtn.textContent === 'Added ✓' || addBtn.textContent === 'Fail')) {
      if (addBtn.textContent === 'Added ✓') {
        addedLines++;
      }
      return; // Skip validation for already added or failed lines
    }
    
    // Check if any required field is missing for non-added lines
    if (!topic || !narrative || !story || !link) {
      allValid = false;
    } else {
      validLines++;
    }
  });
  
  // Enable button if all non-added lines are valid and there's at least one line to process
  const hasLinesToProcess = (validLines > 0) || (formLines.length > 0 && addedLines < formLines.length);
  
  // Only update button if it's in normal state (not processing or completed)
  if (addAllButton.className === 'add-all-btn' || addAllButton.className === '') {
    if (allValid && hasLinesToProcess) {
      addAllButton.disabled = false;
      addAllButton.style.opacity = '1';
      addAllButton.style.background = '#357abd';
    } else {
      addAllButton.disabled = true;
      addAllButton.style.opacity = '0.5';
      addAllButton.style.background = '#4a90e2';
    }
  }
}

/**
 * Add all narrative lines one by one
 */
async function addAllNarratives() {
  const formLines = document.querySelectorAll('.narrative-form-line');
  const addAllButton = document.getElementById('addAllButton');
  const errorDiv = document.getElementById('addNarrativeError');
  
  if (!addAllButton || formLines.length === 0) {
    return;
  }
  
  // Clear previous messages
  if (errorDiv) {
    errorDiv.style.display = 'none';
  }
  
  // Change button state to processing
  addAllButton.disabled = true;
  addAllButton.textContent = '⏳ Adding All...';
  addAllButton.className = 'add-all-btn processing';
  
  let addedCount = 0;
  let errorCount = 0;
  let skippedCount = 0;
  
  // Process each line sequentially
  for (const line of formLines) {
    const lineId = line.getAttribute('data-line-id');
    const addBtn = document.querySelector(`[data-line-id="${lineId}"].add-btn-inline`);
    
    // Skip if already added or failed
    if (addBtn && (addBtn.textContent === 'Added ✓' || addBtn.textContent === 'Fail')) {
      skippedCount++;
      continue;
    }
    
    // Check if line is valid
    const topic = document.getElementById(`sheet${lineId}`)?.value.trim() || '';
    const narrative = document.getElementById(`narrative${lineId}`)?.value.trim() || '';
    const story = document.getElementById(`story${lineId}`)?.value.trim() || '';
    const link = document.getElementById(`link${lineId}`)?.value.trim() || '';
    
    if (!topic || !narrative || !story || !link) {
      errorCount++;
      continue;
    }
    
    try {
      // Update Add All button to show current progress
      addAllButton.textContent = `⏳ Adding Line ${parseInt(lineId)}...`;
      
      // Call the existing addSingleNarrative function
      await addSingleNarrative(parseInt(lineId));
      
      // Wait for a moment to see the result
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Check if it was successfully added
      if (addBtn && addBtn.textContent === 'Added ✓') {
        addedCount++;
      } else {
        errorCount++;
      }
      
    } catch (error) {
      console.error(`Error adding line ${lineId}:`, error);
      errorCount++;
    }
    
    // Small delay between requests to avoid overwhelming the server
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  
  // Update button state based on results
  if (errorCount === 0) {
    addAllButton.textContent = `✅ All Added (${addedCount})`;
    addAllButton.className = 'add-all-btn completed';
    
    if (errorDiv) {
      errorDiv.innerHTML = `<div class="success">✅ Successfully added ${addedCount} narratives!</div>`;
      errorDiv.style.display = 'block';
    }
  } else {
    addAllButton.textContent = `⚠️ Completed (${addedCount} added, ${errorCount} failed)`;
    addAllButton.className = 'add-all-btn';
    addAllButton.style.background = '#dc3545';
    
    if (errorDiv) {
      errorDiv.innerHTML = `<div class="error">Added ${addedCount} narratives, but ${errorCount} failed. Check individual line errors.</div>`;
      errorDiv.style.display = 'block';
    }
  }
  
  // Hide status message after 5 seconds
  setTimeout(() => {
    if (errorDiv) {
      errorDiv.style.display = 'none';
    }
  }, 5000);
  
  // Button will stay in final state until modal is closed
  // No automatic reset - user can see the final results
}

/**
 * Reset the Add All button to its initial state
 */
function resetAddAllButton() {
  const addAllButton = document.getElementById('addAllButton');
  if (addAllButton) {
    addAllButton.disabled = true;
    addAllButton.textContent = '➕ Add All Lines';
    addAllButton.className = 'add-all-btn';
    addAllButton.style.opacity = '0.5';
    addAllButton.style.background = '#4a90e2';
  }
}
