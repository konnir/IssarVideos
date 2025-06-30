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
  const className =
    type === "error"
      ? "error"
      : type === "success"
      ? "success"
      : "loading";
  messageSection.innerHTML = `<div class="${className}">${message}</div>`;

  if (type !== "error") {
    setTimeout(() => {
      messageSection.innerHTML = "";
    }, 3000);
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
  showMessage("Loading your first video...", "loading");

  try {
    await updateTaggedCount();
    await loadNextVideo();
    document.getElementById("videoSection").style.display = "block";
    hideLeaderboard(); // Hide leaderboard when user starts tagging
  } catch (error) {
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

    showMessage("");
  } catch (error) {
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

  // Update narrative content
  const narrativeEnglish = document.getElementById("narrativeEnglish");

  if (narrativeEnglish) {
    narrativeEnglish.textContent =
      video.Narrative || "No narrative available";
  }
}

async function submitTag() {
  const selectedResult = document.querySelector(
    'input[name="result"]:checked'
  );

  if (!selectedResult) {
    showMessage("Please select a result option", "error");
    return;
  }

  const result = parseInt(selectedResult.value);

  try {
    showMessage("Submitting tag...", "loading");

    const response = await apiCall("/tag-record", {
      method: "POST",
      body: JSON.stringify({
        link: currentVideo.Link,
        username: currentUsername,
        result: result,
      }),
    });

    const responseData = await response.json();
    showMessage("Tag submitted successfully!", "success");

    await updateTaggedCount();
    await loadNextVideo();
  } catch (error) {
    showMessage("Error submitting tag: " + error.message, "error");
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
