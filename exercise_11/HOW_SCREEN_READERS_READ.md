# How Screen Readers Read HTML

## Short Answer

**Screen readers don't read the HTML file directly.** They read the **rendered webpage** that the browser displays!

---

## The Process

### 1. **Browser Renders HTML → Creates DOM (Document Object Model)**

```
HTML File (source code)
    ↓
Browser reads it
    ↓
Browser renders it (creates visual page)
    ↓
Browser creates DOM tree (structure in memory)
    ↓
Screen Reader reads from DOM
    ↓
Screen Reader speaks aloud
```

### 2. **Screen Reader Reads the Rendered Page**

When you visit a webpage:

1. **Browser loads HTML** → Reads the `.html` file
2. **Browser renders** → Creates visual page you see
3. **Browser builds DOM** → Creates tree structure in memory
4. **Screen Reader connects** → Accesses the DOM (not the HTML file!)
5. **Screen Reader reads** → Goes through DOM elements one by one
6. **Screen Reader speaks** → Converts text to speech

---

## Example

### HTML File (What You See in Code):
```html
<div role="article" aria-label="Coach advice">
  <p>Hello! How can I help?</p>
</div>
```

### Rendered Page (What Browser Shows):
```
┌─────────────────────────┐
│  Hello! How can I help? │
└─────────────────────────┘
```

### DOM (What Browser Creates in Memory):
```
Document
└── div (role="article", aria-label="Coach advice")
    └── p
        └── Text: "Hello! How can I help?"
```

### Screen Reader Reads:
**"Coach advice, article. Hello! How can I help?"**

---

## Key Points

### ❌ Screen Reader Does NOT:
- Read the raw `.html` file
- Read the source code
- Read comments (`<!-- comment -->`)
- Read CSS files
- Read JavaScript files directly

### ✅ Screen Reader DOES:
- Read the **rendered DOM** (what browser creates)
- Read **visible text** on the page
- Read **ARIA attributes** (`aria-label`, `role`, etc.)
- Read **HTML semantic elements** (`<button>`, `<nav>`, `<article>`, etc.)
- Read **alt text** from images (`<img alt="description">`)
- Navigate through **interactive elements** (links, buttons, forms)

---

## What Screen Reader Actually Reads

### 1. **HTML Elements**
```html
<h1>Welcome</h1>
```
Screen reader: **"Welcome, heading level 1"**

### 2. **ARIA Roles**
```html
<div role="button">Click me</div>
```
Screen reader: **"Click me, button"**

### 3. **ARIA Labels**
```html
<button aria-label="Close dialog">X</button>
```
Screen reader: **"Close dialog, button"** (NOT "X, button"!)

### 4. **Visible Text**
```html
<p>This is visible text</p>
```
Screen reader: **"This is visible text"**

### 5. **Hidden Elements**
```html
<span className="sr-only">Screen reader only text</span>
```
Screen reader: **"Screen reader only text"** ✅

```html
<div aria-hidden="true">Decorative icon</div>
```
Screen reader: **SKIPS IT** ❌ (Doesn't read)

---

## Real Example from Your Chatbot

### HTML Code:
```html
<div role="article" aria-label="Coach advice">
  <div role="img" aria-label="Coach avatar">
    <Bot className="w-7 h-7" aria-hidden="true" />
  </div>
  <p>Establishing a consistent bedtime routine helps...</p>
  <div role="region" aria-label="Citation sources">
    <a href="..." aria-label="Source: Bedtime Guide">Bedtime Guide</a>
  </div>
</div>
```

### What Screen Reader Reads:
1. **"Coach advice, article"** ← From `role` + `aria-label`
2. **"Coach avatar"** ← From avatar's `aria-label`
3. (Bot icon is skipped) ← Because `aria-hidden="true"`
4. **"Establishing a consistent bedtime routine helps..."** ← Visible text
5. **"Citation sources, region"** ← From citations section
6. **"Source: Bedtime Guide, link"** ← From citation link's `aria-label`

---

## Browser Accessibility Tree

Modern browsers create an **Accessibility Tree** from the DOM:

```
DOM Tree                    →    Accessibility Tree
─────────────────────────────────────────────────────
<div>                       →    [Container]
  <p>Hello</p>              →      [Text: "Hello"]
  <button>Click</button>     →      [Button: "Click"]
</div>                      →
```

Screen readers read from the **Accessibility Tree**, which includes:
- Element roles (from HTML + ARIA)
- Element names (from text + ARIA labels)
- Element states (enabled, disabled, checked, etc.)
- Element relationships (parent/child, labelled-by, described-by)

---

## How to See What Screen Reader Sees

### Method 1: Browser DevTools - Accessibility Panel

1. Open your chatbot in browser
2. Press **F12** (Developer Tools)
3. Click on **Accessibility** tab (or Elements → Right-click → Show accessibility tree)
4. Select any element
5. See what screen reader would see!

**Example:**
```
Name: "Coach advice"
Role: article
Description: (empty)
```

### Method 2: Chrome Accessibility Inspector

1. Open DevTools (F12)
2. Press **Ctrl+Shift+P** (Command Palette)
3. Type "Accessibility"
4. Select "Show Accessibility Tree"
5. See the full accessibility tree!

---

## Testing with Screen Reader

### Using Windows Narrator:

1. **Press `Win + Ctrl + Enter`** to turn on Narrator
2. Navigate to your chatbot
3. Press **`Tab`** to move through elements
4. Narrator reads from the **rendered page**, not the HTML file!

**What Narrator Reads:**
- ✅ Visible text on screen
- ✅ ARIA roles and labels
- ✅ Button/link names
- ❌ Hidden elements (unless they have `sr-only` class)
- ❌ Elements with `aria-hidden="true"`

---

## Why This Matters for Your Chatbot

### Before ARIA:
```html
<div>
  <div>Hello</div>
</div>
```

Screen reader reads: **"Div. Div. Hello."** (confusing!)

### After ARIA:
```html
<div role="article" aria-label="Coach advice">
  <p>Hello</p>
</div>
```

Screen reader reads: **"Coach advice, article. Hello."** (clear!)

---

## Summary

| Question | Answer |
|----------|--------|
| **Does screen reader read HTML files?** | ❌ No - reads rendered webpage |
| **Does screen reader read source code?** | ❌ No - reads browser's DOM |
| **Does screen reader read visible text?** | ✅ Yes |
| **Does screen reader read ARIA attributes?** | ✅ Yes - very important! |
| **Does screen reader read CSS?** | ❌ No - only uses it for layout hints |
| **Does screen reader read JavaScript?** | ❌ No - but reads JS-created DOM elements |
| **Can you test without screen reader?** | ✅ Yes - use DevTools Accessibility panel |

---

## Key Takeaway

**Screen readers don't read the HTML file itself** - they read the **rendered webpage** that your browser creates from the HTML, CSS, and JavaScript!

That's why ARIA attributes are so important - they tell the browser (and screen reader) what elements **mean**, not just what they **look like**.

🎯 **Think of it like this:**
- **HTML file** = Recipe
- **Rendered page** = The actual dish
- **Screen reader** = A blind person describing the dish (not the recipe!)

