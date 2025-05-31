# Leaderboard Feature Documentation

## Overview

The leaderboard feature displays tagging statistics for all users on the main application page, encouraging friendly competition and showing overall progress.

## Features

### 🏆 Leaderboard Display

- Shows all users who have tagged at least one video
- Ranked by number of tagged videos (highest to lowest)
- Medal emojis for top 3 positions (🥇🥈🥉)
- Real-time updates when users tag videos

### 🎯 User Experience

- **Visible on Page Load**: Leaderboard appears when users first visit the app
- **Auto-Hide on Start**: Disappears immediately when user starts tagging
- **Clean Design**: Matches the application's dark theme with green accents

### 📊 Statistics Shown

- User position/rank
- Username
- Number of videos tagged
- Visual distinction for top 3 performers

## API Endpoints

### GET /leaderboard

Returns leaderboard data for all users.

**Response Format:**

```json
[
  {
    "username": "Nir Kon",
    "tagged_count": 15
  },
  {
    "username": "Issar Tzachor",
    "tagged_count": 12
  }
]
```

## Frontend Implementation

### HTML Structure

```html
<div class="leaderboard-section" id="leaderboardSection">
  <h2>🏆 Leaderboard</h2>
  <div class="leaderboard-container" id="leaderboardContainer">
    <!-- Leaderboard items loaded here -->
  </div>
</div>
```

### JavaScript Functions

- `loadLeaderboard()`: Fetches and displays leaderboard data
- `hideLeaderboard()`: Hides the leaderboard when user starts tagging
- Auto-loads on page load via DOMContentLoaded event

### CSS Classes

- `.leaderboard-section`: Main container styling
- `.leaderboard-item`: Individual user row styling
- `.top-three`: Special styling for top 3 positions
- Responsive design for mobile devices

## Behavior

1. **Page Load**: Leaderboard automatically loads and displays
2. **Empty State**: Shows "No tagging activity yet" message if no users have tagged
3. **User Interaction**: Disappears when user enters name and starts tagging
4. **Error Handling**: Gracefully handles API failures with fallback message

## Benefits

- **Motivation**: Encourages users to tag more videos
- **Progress Visibility**: Shows overall community engagement
- **Competition**: Creates friendly rivalry between taggers
- **Recognition**: Highlights top contributors

## Technical Notes

- Uses protocol-agnostic API calls for HTTPS compatibility
- Responsive design works on all device sizes
- No authentication required (public leaderboard)
- Real-time updates when new tags are submitted
- Performance optimized with efficient DOM manipulation
