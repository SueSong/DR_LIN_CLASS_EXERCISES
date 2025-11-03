# ARIA Roles Explanation

## What Are ARIA Roles?

**ARIA (Accessible Rich Internet Applications) roles** are HTML attributes that help screen readers and other assistive technologies understand the structure and purpose of elements on a webpage.

**Important**: ARIA roles do NOT change the visual appearance of your page! They are invisible to sighted users.

## What Changed?

I added ARIA roles throughout the chat interface to make it more accessible for users with disabilities (especially screen reader users).

### Before:
- Chat messages had no semantic meaning for screen readers
- Screen readers couldn't distinguish between different message types
- Status messages weren't announced properly
- Icons and decorative elements weren't hidden from screen readers

### After:
- Each message type has a proper role:
  - **System messages**: `role="status"` - Screen reader announces: "System message"
  - **Coach messages**: `role="article"` with `aria-label="Coach advice"` - Screen reader announces: "Coach advice"
  - **Mentor messages**: `role="article"` with `aria-label="Mentor reply"` - Screen reader announces: "Mentor reply"
  - **Your messages**: `role="article"` with `aria-label="Your message"` - Screen reader announces: "Your message"
- Connection status is announced when it changes
- Typing indicator is announced when coach starts typing
- Decorative icons are hidden from screen readers (`aria-hidden="true"`)
- Citations section is properly labeled for navigation

## How to Verify ARIA Roles Are Working

### Method 1: Browser Developer Tools (Inspect Elements)

1. Open your browser's Developer Tools (F12)
2. Go to the **Elements** tab
3. Select any message bubble in the chat
4. Look for attributes like:
   - `role="article"` or `role="status"`
   - `aria-label="..."`

**Example**:
```html
<div role="article" aria-label="Coach advice">
  <div class="message-bubble">
    <!-- message content -->
  </div>
</div>
```

### Method 2: Accessibility Tree (Best Method)

1. Open Developer Tools (F12)
2. Go to the **Accessibility** tab (or **Elements** tab → Right-click → **Show accessibility tree**)
3. Select the chat message area
4. You should see:
   - `log` role for the messages container
   - `article` roles for individual messages
   - Proper labels for each message type

### Method 3: Screen Reader Simulation (Chrome)

1. Install a Chrome extension like **Screen Reader** or use Chrome's built-in screen reader
2. Turn on screen reader mode
3. Navigate through the chat
4. You should hear:
   - "Chat messages" when entering the message area
   - "Coach advice" when encountering coach messages
   - "System message" for system notifications
   - "Coach is typing" when the typing indicator appears

### Method 4: Automated Accessibility Testing

You can use browser extensions or tools like:
- **axe DevTools** (Chrome/Firefox extension)
- **WAVE** (Web Accessibility Evaluation Tool)
- **Lighthouse** (built into Chrome DevTools)

Run an accessibility audit - it will show if ARIA roles are properly applied.

## Visual Difference: NONE! ✅

**You won't see any visual changes** because ARIA roles are purely for assistive technologies. The page looks exactly the same.

## What This Means for Users

### For Sighted Users:
- **No change** - Everything looks and works the same

### For Screen Reader Users:
- **Much better experience**:
  - Can understand message types ("Coach advice" vs "Your message")
  - Get notified when status changes ("Connecting..." → "Active Session")
  - Can navigate citations more easily
  - Are not confused by decorative icons

## Real-World Impact

A visually impaired user navigating your chat with a screen reader will now hear:
- ✅ "Chat messages, log" (enters message area)
- ✅ "Coach advice" (reads coach message)
- ✅ "Citation sources, region" (enters citations section)
- ✅ "Source: Bedtime Routine Best Practices, link" (each citation)
- ✅ "Coach is typing" (when typing indicator appears)

Instead of just:
- ❌ "Div, div, div..." (generic HTML elements with no meaning)

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Visual appearance** | Same | Same (no change) |
| **Functionality** | Same | Same (no change) |
| **Screen reader experience** | Poor (generic divs) | Excellent (semantic roles) |
| **Accessibility score** | Lower | Higher |
| **WCAG compliance** | Partial | Better |

The changes are **invisible but important** for accessibility compliance and inclusion! 🎯

