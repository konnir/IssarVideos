// Video Tagger JavaScript Functions
let currentUsername = "";
let currentVideo = null;

// Utility function to get the base URL (works for both HTTP and HTTPS)
function getBaseUrl() {
  return window.location.origin;
}

// Utility function to make API calls with proper error handling
async function apiCall(endpoint, options = {}) {
  const url = `${getBaseUrl()}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
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

function showMessage(message, type = "info") {
  const messageSection = document.getElementById("messageSection");
  
  // For loading messages, create a full-screen overlay
  if (type === "loading") {
    showLoadingOverlay(message);
    return;
  }
  
  // For non-loading messages, use the regular message section
  const className = type === "error" ? "error" : type === "success" ? "success" : "loading";
  messageSection.innerHTML = `<div class="${className}">${message}</div>`;

  if (type !== "error") {
    setTimeout(() => {
      messageSection.innerHTML = "";
    }, 3000);
  }
}

function showLoadingOverlay(message) {
  // Remove existing overlay if any
  hideLoadingOverlay();
  
  // Create overlay
  const overlay = document.createElement('div');
  overlay.className = 'loading-overlay';
  overlay.id = 'loadingOverlay';
  
  // Create content
  overlay.innerHTML = `
    <div class="loading-content">
      <div class="spinner"></div>
      <div class="loading-text">${message}</div>
    </div>
  `;
  
  // Add to body
  document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) {
    overlay.remove();
  }
}

function getVideoEmbedUrl(link) {
  // Handle YouTube URLs
  if (link.includes("youtube.com/watch")) {
    const videoId = link.split("v=")[1].split("&")[0];
    return `https://www.youtube.com/embed/${videoId}`;
  }
  if (link.includes("youtu.be/")) {
    const videoId = link.split("youtu.be/")[1].split("?")[0];
    return `https://www.youtube.com/embed/${videoId}`;
  }

  // Handle TikTok URLs
  if (link.includes("tiktok.com")) {
    const videoId = link.split("/video/")[1];
    return `https://www.tiktok.com/embed/v2/${videoId}`;
  }

  // For other platforms, show a link
  return null;
}

async function startTagging() {
  const username = document.getElementById("username").value.trim();
  if (!username) {
    showMessage("Please enter your full name", "error");
    return;
  }

  currentUsername = username;
  
  try {
    // Refresh data to ensure we have the most current information
    showMessage("Loading fresh data...", "loading");
    
    // Add a small delay to ensure the message is visible
    await new Promise(resolve => setTimeout(resolve, 500));
    
    await apiCall("/refresh-data", { method: "POST" });
    
    showMessage("Loading your first video...", "loading");
    await updateTaggedCount();
    await loadNextVideo();
    
    // Hide loading overlay and show the video section
    hideLoadingOverlay();
    document.getElementById("videoSection").style.display = "block";
    // Add tagging mode class to hide title and reorganize layout
    document.body.classList.add("tagging-mode");
    hideLeaderboard(); // Hide leaderboard when user starts tagging
  } catch (error) {
    hideLoadingOverlay();
    showMessage("Error starting tagging: " + error.message, "error");
  }
}

async function loadNextVideo() {
  try {
    showMessage("Loading next video...", "loading");

    const response = await apiCall(
      `/random-narrative-for-user/${encodeURIComponent(currentUsername)}`
    );
    
    if (response.status === 404) {
      hideLoadingOverlay();
      showMessage(
        "No more videos to tag! You have completed all available videos.",
        "success"
      );
      return;
    }

    currentVideo = await response.json();
    displayVideo(currentVideo);

    // Clear previous selection
    document.querySelectorAll('input[name="result"]').forEach((radio) => {
      radio.checked = false;
    });

    hideLoadingOverlay();
  } catch (error) {
    hideLoadingOverlay();
    showMessage("Error loading video: " + error.message, "error");
  }
}

async function loadNextVideoWithoutLoading() {
  try {
    const response = await apiCall(
      `/random-narrative-for-user/${encodeURIComponent(currentUsername)}`
    );
    
    if (response.status === 404) {
      hideLoadingOverlay();
      showMessage(
        "No more videos to tag! You have completed all available videos.",
        "success"
      );
      return;
    }

    currentVideo = await response.json();
    displayVideo(currentVideo);

    // Clear previous selection
    document.querySelectorAll('input[name="result"]').forEach((radio) => {
      radio.checked = false;
    });

    hideLoadingOverlay();
  } catch (error) {
    hideLoadingOverlay();
    showMessage("Error loading video: " + error.message, "error");
  }
}

function displayVideo(video) {
  const videoContainer = document.getElementById("videoContainer");
  const videoLinkSection = document.getElementById("videoLinkSection");

  const embedUrl = getVideoEmbedUrl(video.Link);

  if (embedUrl) {
    if (video.Link.includes("tiktok.com")) {
      videoContainer.innerHTML = `
                <iframe src="${embedUrl}" allowfullscreen></iframe>
            `;
    } else {
      videoContainer.innerHTML = `<iframe src="${embedUrl}" allowfullscreen></iframe>`;
    }
  } else {
    videoContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; background-color: #3d3d3d; border-radius: 8px;">
                <p style="margin-bottom: 15px;">Video Preview Not Available</p>
            </div>
        `;
  }

  // Update the video link button
  const videoLinkBtn = document.getElementById("videoLinkBtn");
  const restartVideoBtn = document.getElementById("restartVideoBtn");
  const skipVideoBtn = document.getElementById("skipVideoBtn");
  
  if (videoLinkBtn && video.Link) {
    // Ensure we have the full URL
    videoLinkBtn.href = video.Link;
    // Force a re-render by setting the attribute as well
    videoLinkBtn.setAttribute('href', video.Link);
    // Enable the button now that we have a valid link
    videoLinkBtn.style.opacity = '1';
    videoLinkBtn.style.pointerEvents = 'auto';
  }
  
  // Enable/disable restart video button based on whether video is embeddable
  if (restartVideoBtn) {
    if (embedUrl) {
      restartVideoBtn.style.opacity = '1';
      restartVideoBtn.style.pointerEvents = 'auto';
    } else {
      restartVideoBtn.style.opacity = '0.5';
      restartVideoBtn.style.pointerEvents = 'none';
    }
  }

  // Enable skip video button (always available when video is loaded)
  if (skipVideoBtn) {
    skipVideoBtn.style.opacity = '1';
    skipVideoBtn.style.pointerEvents = 'auto';
  }

  // Update narrative content
  const narrativeEnglish = document.getElementById("narrativeEnglish");
  const narrativeHighlight = document.getElementById("narrativeHighlight");

  if (narrativeEnglish) {
    narrativeEnglish.textContent =
      video.Narrative || "No narrative available";
  }
  
  // Update the highlighted narrative in the question section
  if (narrativeHighlight) {
    narrativeHighlight.textContent =
      video.Narrative || "No narrative available";
  }
}

async function submitTag(numericResult) {
  // Handle problem button (0)
  if (numericResult === 0) {
    // Problem button - submit as backend result 4
    try {
      showMessage("Reporting problem...", "loading");

      const response = await apiCall("/tag-record", {
        method: "POST",
        body: JSON.stringify({
          link: currentVideo.Link,
          username: currentUsername,
          result: 4, // Problem
          numeric_result: 0, // Problem indicator
        }),
      });

      const responseData = await response.json();
      
      showMessage("Loading next video...", "loading");
      await updateTaggedCount();
      await loadNextVideoWithoutLoading();
    } catch (error) {
      hideLoadingOverlay();
      showMessage("Error reporting problem: " + error.message, "error");
    }
    return;
  }

  // Validate the numeric result parameter (1-6)
  if (!numericResult || ![1, 2, 3, 4, 5, 6].includes(numericResult)) {
    showMessage("Invalid rating option", "error");
    return;
  }

  // Convert numeric result to backend result
  let backendResult;
  if (numericResult === 1 || numericResult === 2) {
    backendResult = 2; // No (Completely Unrelated, Doesn't Imply)
  } else if (numericResult === 3) {
    // Neutral/Unclear - save with backend result 4 (problem) and numeric result 3
    backendResult = 4; // Problem
  } else if (numericResult === 4 || numericResult === 5) {
    backendResult = 1; // Yes (Somewhat Implies, Strongly Implies)
  } else if (numericResult === 6) {
    backendResult = 3; // Too Obvious (previous value for 6)
  }

  try {
    showMessage("Submitting rating...", "loading");

    const response = await apiCall("/tag-record", {
      method: "POST",
      body: JSON.stringify({
        link: currentVideo.Link,
        username: currentUsername,
        result: backendResult,
        numeric_result: numericResult,
      }),
    });

    const responseData = await response.json();
    
    // Don't hide loading overlay yet - transition directly to loading next video
    showMessage("Loading next video...", "loading");

    await updateTaggedCount();
    await loadNextVideoWithoutLoading(); // Use a version that doesn't show its own loading
  } catch (error) {
    hideLoadingOverlay();
    showMessage("Error submitting rating: " + error.message, "error");
  }
}

async function updateTaggedCount() {
  try {
    const response = await apiCall(
      `/user-tagged-count/${encodeURIComponent(currentUsername)}`
    );
    
    const data = await response.json();
    const taggedCountElement = document.getElementById("taggedCount");
    if (taggedCountElement) {
      taggedCountElement.textContent = `You tagged: ${data.tagged_count}`;
    }
  } catch (error) {
    console.error("Error updating tagged count:", error);
    // Don't show error message to user for this non-critical operation
  }
}

async function loadLeaderboard() {
  try {
    const response = await apiCall("/leaderboard");
    const leaderboard = await response.json();
    
    const leaderboardContainer = document.getElementById("leaderboardContainer");
    
    if (leaderboard.length === 0) {
      leaderboardContainer.innerHTML = "<p>No tagging activity yet. Be the first to start!</p>";
      return;
    }
    
    let leaderboardHTML = '<div class="leaderboard-list">';
    leaderboard.forEach((user, index) => {
      const position = index + 1;
      const medalEmoji = position === 1 ? "🥇" : position === 2 ? "🥈" : position === 3 ? "🥉" : "📊";
      
      leaderboardHTML += `
        <div class="leaderboard-item ${position <= 3 ? 'top-three' : ''}">
          <div class="leaderboard-position">${medalEmoji} ${position}</div>
          <div class="leaderboard-username">${user.username}</div>
          <div class="leaderboard-count">${user.tagged_count} tagged</div>
        </div>
      `;
    });
    leaderboardHTML += '</div>';
    
    leaderboardContainer.innerHTML = leaderboardHTML;
  } catch (error) {
    console.error("Error loading leaderboard:", error);
    document.getElementById("leaderboardContainer").innerHTML = 
      "<p>Unable to load leaderboard.</p>";
  }
}

function hideLeaderboard() {
  const leaderboardSection = document.getElementById("leaderboardSection");
  const toggleBtn = document.getElementById("leaderboardToggleBtn");
  if (leaderboardSection) {
    leaderboardSection.style.display = "none";
  }
  if (toggleBtn) {
    toggleBtn.textContent = "🏆 Show Leaderboard";
  }
}

function showLeaderboard() {
  const leaderboardSection = document.getElementById("leaderboardSection");
  const toggleBtn = document.getElementById("leaderboardToggleBtn");
  if (leaderboardSection) {
    leaderboardSection.style.display = "block";
  }
  if (toggleBtn) {
    toggleBtn.textContent = "🏆 Hide Leaderboard";
  }
}

function toggleLeaderboard() {
  const leaderboardSection = document.getElementById("leaderboardSection");
  const toggleBtn = document.getElementById("leaderboardToggleBtn");
  
  if (leaderboardSection.style.display === "none") {
    showLeaderboard();
    // Reload leaderboard data when showing
    loadLeaderboard();
  } else {
    hideLeaderboard();
  }
}

/**
 * Restart the current video by reloading the iframe
 */
function restartVideo() {
  if (!currentVideo) {
    showMessage("No video to restart", "error");
    return;
  }
  
  const videoContainer = document.getElementById("videoContainer");
  const embedUrl = getVideoEmbedUrl(currentVideo.Link);
  
  if (embedUrl) {
    // Add a timestamp parameter to force iframe reload
    const separator = embedUrl.includes('?') ? '&' : '?';
    const reloadUrl = `${embedUrl}${separator}autoplay=1&t=${Date.now()}`;
    
    if (currentVideo.Link.includes("tiktok.com")) {
      videoContainer.innerHTML = `
        <iframe src="${reloadUrl}" allowfullscreen></iframe>
      `;
    } else {
      videoContainer.innerHTML = `<iframe src="${reloadUrl}" allowfullscreen></iframe>`;
    }
    
    showMessage("Video restarted", "success");
  } else {
    showMessage("Cannot restart video - no embedded player available", "error");
  }
}

/**
 * Skip the current video and load the next one without tagging
 */
async function skipVideo() {
  if (!currentVideo) {
    showMessage("No video to skip", "error");
    return;
  }

  try {
    showMessage("Loading next video...", "loading");
    await loadNextVideoWithoutLoading();
  } catch (error) {
    hideLoadingOverlay();
    showMessage("Error skipping video: " + error.message, "error");
  }
}

/**
 * Explain the current narrative in Hebrew
 */
async function explainNarrative() {
  if (!currentVideo || !currentVideo.Narrative) {
    showMessage("No narrative to explain", "error");
    return;
  }

  // Get the appropriate explain button (desktop or mobile)
  const desktopBtn = document.getElementById("explainBtn");
  const mobileBtn = document.getElementById("mobileExplainBtn");
  
  // Determine which button is visible/clicked
  let explainBtn;
  let isMobile = false;
  if (window.innerWidth <= 768) {
    explainBtn = mobileBtn;
    isMobile = true;
  } else {
    explainBtn = desktopBtn;
    isMobile = false;
  }
  
  if (!explainBtn) {
    showMessage("Explain button not found", "error");
    return;
  }
  
  const originalText = explainBtn.textContent;
  
  try {
    // Disable button and show appropriate loading state
    explainBtn.disabled = true;
    if (isMobile) {
      explainBtn.textContent = "...";
    } else {
      explainBtn.innerHTML = '<span class="spinner"></span>';
    }
    
    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, 10000); // 10 seconds timeout
    
    const response = await apiCall("/explain-narrative", {
      method: "POST",
      body: JSON.stringify({
        narrative: currentVideo.Narrative
      }),
      signal: controller.signal
    });
    
    // Clear timeout if request succeeds
    clearTimeout(timeoutId);
    
    const data = await response.json();
    
    // Create or update explanation modal
    showNarrativeExplanation(data.narrative_hebrew, data.explanation_hebrew);
    
  } catch (error) {
    console.error("Error explaining narrative:", error);
    
    // Handle timeout specifically
    if (error.name === 'AbortError') {
      showMessage("Explanation request timed out after 10 seconds. Please try again.", "error");
    } else {
      showMessage("Error explaining narrative: " + error.message, "error");
    }
  } finally {
    // Restore button
    explainBtn.disabled = false;
    explainBtn.textContent = originalText;
  }
}

/**
 * Show narrative explanation in a modal
 */
function showNarrativeExplanation(narrativeHebrew, explanationHebrew) {
  // Create modal HTML
  const modalHTML = `
    <div class="explanation-modal-overlay" id="explanationModal" onclick="closeExplanationModal()">
      <div class="explanation-modal-content" onclick="event.stopPropagation()">
        <div class="explanation-modal-header">
          <h3>הסבר הנרטיב</h3>
          <button class="explanation-close-btn" onclick="closeExplanationModal()">×</button>
        </div>
        <div class="explanation-modal-body">
          <div class="explanation-section">
            <h4>תרגום:</h4>
            <p class="narrative-hebrew">${narrativeHebrew}</p>
          </div>
          <div class="explanation-section">
            <h4>הסבר:</h4>
            <p class="explanation-hebrew">${explanationHebrew}</p>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Remove existing modal if any
  const existingModal = document.getElementById("explanationModal");
  if (existingModal) {
    existingModal.remove();
  }
  
  // Add modal to body
  document.body.insertAdjacentHTML("beforeend", modalHTML);
  
  // Add modal styles if not already present
  addExplanationModalStyles();
}

/**
 * Close explanation modal
 */
function closeExplanationModal() {
  const modal = document.getElementById("explanationModal");
  if (modal) {
    modal.remove();
  }
}

/**
 * Add CSS styles for the explanation modal
 */
function addExplanationModalStyles() {
  const styleId = "explanationModalStyles";
  
  // Don't add styles if already present
  if (document.getElementById(styleId)) {
    return;
  }
  
  const style = document.createElement("style");
  style.id = styleId;
  style.textContent = `
    .explanation-modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.8);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
    }
    
    .explanation-modal-content {
      background-color: #2a2a2a;
      border-radius: 12px;
      padding: 0;
      max-width: 600px;
      width: 90%;
      max-height: 80vh;
      overflow-y: auto;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
      direction: rtl;
    }
    
    .explanation-modal-header {
      background-color: #4caf50;
      color: white;
      padding: 15px 20px;
      border-radius: 12px 12px 0 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .explanation-modal-header h3 {
      margin: 0;
      font-size: 20px;
    }
    
    .explanation-close-btn {
      background: none;
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      padding: 0;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      transition: background-color 0.3s ease;
    }
    
    .explanation-close-btn:hover {
      background-color: rgba(255, 255, 255, 0.2);
    }
    
    .explanation-modal-body {
      padding: 20px;
    }
    
    .explanation-section {
      margin-bottom: 20px;
    }
    
    .explanation-section h4 {
      color: #4caf50;
      margin-bottom: 10px;
      font-size: 16px;
    }
    
    .narrative-hebrew {
      background-color: rgba(33, 150, 243, 0.1);
      padding: 15px;
      border-radius: 8px;
      border-right: 4px solid #2196F3;
      font-size: 16px;
      line-height: 1.5;
      color: #e0e0e0;
    }
    
    .explanation-hebrew {
      background-color: rgba(76, 175, 80, 0.1);
      padding: 15px;
      border-radius: 8px;
      border-right: 4px solid #4caf50;
      font-size: 16px;
      line-height: 1.6;
      color: #e0e0e0;
    }
    
    .spinner {
      display: inline-block;
      width: 12px;
      height: 12px;
      border: 2px solid #ffffff;
      border-radius: 50%;
      border-top-color: transparent;
      animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `;
  
  document.head.appendChild(style);
}

// Initialize event listeners when DOM is loaded
document.addEventListener("DOMContentLoaded", function() {
  // Load leaderboard on page load and ensure it's visible
  loadLeaderboard();
  showLeaderboard();
  
  // Allow Enter key to start tagging
  document
    .getElementById("username")
    .addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        startTagging();
      }
    });
});
