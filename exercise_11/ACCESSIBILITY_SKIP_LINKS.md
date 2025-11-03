    # Skip Links for Accessibility

## What are Skip Links?

**Skip links** are invisible links at the top of the page that become visible when you press **Tab**. They let keyboard users jump directly to the main content, skipping repetitive navigation.

## Visual Example

```
┌─────────────────────────────────────────┐
│ [Tab] → "Skip to main content"          │ ← Hidden until Tab is pressed
├─────────────────────────────────────────┤
│ Navigation Bar (Home | About | Contact) │ ← Skip this repetitive content
├─────────────────────────────────────────┤
│ Header/Banner                            │ ← Skip this too
├─────────────────────────────────────────┤
│ ← Skip link jumps HERE                  │
│                                          │
│ Main Content Area                        │ ← This is where users want to go
│ Chat messages, forms, etc.              │
│                                          │
└─────────────────────────────────────────┘
```

## Why They're Important

**Without skip links:**
- Keyboard user presses Tab 10+ times to get past navigation
- Screen reader announces every nav item
- Slow and frustrating

**With skip links:**
- Keyboard user presses Tab once → sees "Skip to main content"
- Presses Enter → jumps directly to main content
- Fast and efficient ✅

## How to Implement

### HTML Structure:
```html
<!-- Skip link (hidden by default, visible on focus) -->
<a href="#main-content" className="skip-link">
  Skip to main content
</a>

<!-- Navigation (repetitive, skip over this) -->
<nav>...</nav>

<!-- Main content (target of skip link) -->
<main id="main-content">
  <!-- Chat, form, or main content here -->
</main>
```

### CSS:
```css
.skip-link {
  position: absolute;
  top: -40px;  /* Hidden off-screen */
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;  /* Appears when focused (Tab pressed) */
}
```

## For Your Chat Page

Your chat page has:
- Header with "Child Growth Assistant" title
- Navigation/buttons
- Chat messages (main content)

**Skip link would jump directly to the chat messages area**, skipping the header.

## Do You Need Skip Links?

**You need skip links if:**
- ✅ Page has repetitive navigation/headers
- ✅ Multiple links before main content
- ✅ Want to improve keyboard accessibility

**You might not need skip links if:**
- ❌ Very simple page with no navigation
- ❌ Main content is immediately after page start
- ❌ No repetitive elements to skip

## Task 12 Requirement

For Task 12 (Accessibility & UX polish), skip links are a **recommended enhancement** but not strictly required if:
- Your page structure is simple
- Main content appears early
- Tab order is already logical

**Focus on:**
1. ✅ ARIA roles (required)
2. ✅ Keyboard navigation (Arrow keys, Enter, Escape) ✅ You have this
3. ✅ ARIA labels (required)
4. ⚠️ Skip links (nice to have, but optional if page is simple)

---

## Quick Check

**Ask yourself:**
- Does a keyboard user need to Tab through 5+ elements before reaching the chat?
- If YES → Add skip link
- If NO → Skip links optional

For your chat page, since the input field appears relatively early and there's minimal navigation, **skip links are optional** for Task 12.

