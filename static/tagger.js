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
  const narrativeQuestion = document.getElementById("narrativeQuestion");

  const embedUrl = getVideoEmbedUrl(video.Link);

  if (embedUrl) {
    if (video.Link.includes("tiktok.com")) {
      videoContainer.innerHTML = `
                <iframe src="${embedUrl}" allowfullscreen></iframe>
                <p style="margin-top: 10px; text-align: center;">
                    <a href="${video.Link}" target="_blank" style="color: #4CAF50;">Open in TikTok</a>
                </p>
            `;
    } else {
      videoContainer.innerHTML = `<iframe src="${embedUrl}" allowfullscreen></iframe>`;
    }
  } else {
    videoContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; background-color: #3d3d3d; border-radius: 8px;">
                <p style="margin-bottom: 15px;">Video Preview Not Available</p>
                <a href="${video.Link}" target="_blank" style="color: #4CAF50; font-size: 18px;">
                    Open Video in New Tab
                </a>
            </div>
        `;
  }

  // Update narrative content
  const narrativeEnglish = document.getElementById("narrativeEnglish");
  const narrativeHebrew = document.getElementById("narrativeHebrew");

  narrativeEnglish.textContent =
    video.Narrative || "No English narrative available";
  narrativeHebrew.textContent =
    video.Hebrew_Title || "אין כותרת עברית זמינה";
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
    document.getElementById(
      "taggedCount"
    ).textContent = `You tagged: ${data.tagged_count}`;
  } catch (error) {
    console.error("Error updating tagged count:", error);
    // Don't show error message to user for this non-critical operation
  }
}

// Initialize event listeners when DOM is loaded
document.addEventListener("DOMContentLoaded", function() {
  // Allow Enter key to start tagging
  document
    .getElementById("username")
    .addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        startTagging();
      }
    });
});
