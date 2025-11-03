# What is a Screen Reader?

## Simple Explanation

A **screen reader** is a software program that reads the text on your computer screen **out loud** (using text-to-speech) or displays it on a **Braille display** for people who are blind or visually impaired.

Think of it like this:
- **Sighted person**: Looks at the screen → Sees text and images → Understands the page
- **Screen reader user**: Can't see the screen → Uses screen reader → Hears text read aloud → Understands the page

## Common Screen Readers

### Free / Built-in:
1. **NVDA (NonVisual Desktop Access)** - Free, Windows only
   - Download: https://www.nvaccess.org/
   - Very popular and free

2. **JAWS (Job Access With Speech)** - Paid, Windows
   - Most popular paid screen reader
   - Very powerful but expensive

3. **VoiceOver** - Free, built into Mac/iOS
   - Press `Cmd + F5` to turn on
   - Built into all Apple devices

4. **Narrator** - Free, built into Windows
   - Press `Win + Ctrl + Enter` to turn on
   - Built into Windows 10/11

5. **TalkBack** - Free, built into Android
   - Built into Android phones

### Chrome Browser Extension (For Testing):
- **Screen Reader** extension (simulates screen reader behavior)

## How Screen Readers Work

### 1. **Text-to-Speech**
- Reads all text on the page aloud
- Uses a computer voice (like Siri or Alexa, but more robotic)

### 2. **Keyboard Navigation**
- Screen reader users **don't use a mouse**
- They navigate using **keyboard shortcuts**:
  - `Tab` - Move to next element
  - `Shift + Tab` - Move to previous element
  - `Enter` - Click/activate
  - `Arrow keys` - Navigate within content
  - Special keys for different screen readers

### 3. **Announces What's Happening**
- "Link, Start Session"
- "Button, Send message"
- "Heading level 1, Ready to Start?"
- "Chat messages, log"
- "Coach advice, article"

## Real-World Example

### What a Sighted User Sees:
```
┌─────────────────────────────────┐
│  💬 Chat Messages               │
│                                 │
│  👤 Parent: Hello               │
│  🤖 Coach: Hi! How can I help?  │
│  └─ 📚 Sources:                 │
│     • Bedtime Guide             │
│                                 │
│  [Type your message...]  [Send] │
└─────────────────────────────────┘
```

### What a Screen Reader User Hears:
```
"Chat messages, log"
"Your message, article"
"Hello"
"Coach advice, article"
"Hi! How can I help?"
"Citation sources, region"
"Source: Bedtime Guide, link"
"Type your message, textbox"
"Send, button"
```

## Why ARIA Roles Matter

### Without ARIA Roles (Bad):
Screen reader says:
- "Div, div, div..." (confusing - what are these?)
- "Link, Start Session" (okay, but no context)
- "Div, div, div..." (more confusion)

### With ARIA Roles (Good):
Screen reader says:
- "Chat messages, log" (clear - this is a chat!)
- "Your message, article" (clear - this is your message)
- "Coach advice, article" (clear - this is coach's response)
- "Citation sources, region" (clear - these are references)
- "Source: Bedtime Guide, link" (clear - clickable citation)

## Try It Yourself! 🎯

### Method 1: Windows Narrator (Built-in)

1. Press `Win + Ctrl + Enter` to turn on Narrator
2. Navigate to your chatbot page
3. Press `Tab` to move through elements
4. Narrator will read everything aloud!
5. Press `Win + Ctrl + Enter` again to turn off

**Navigation Tips:**
- `Tab` / `Shift + Tab` - Move between interactive elements
- `Ctrl` - Stop reading
- `Caps Lock + Arrow keys` - Navigate by line/word/character

### Method 2: Chrome Screen Reader Extension

1. Install "Screen Reader" extension from Chrome Web Store
2. Turn it on
3. Navigate your page with `Tab` key
4. Listen to how it reads your page

### Method 3: VoiceOver on Mac

1. Press `Cmd + F5` to turn on VoiceOver
2. Navigate with keyboard
3. VoiceOver will announce everything

## Real Impact

### Statistics:
- **2.2 billion** people worldwide have vision impairments
- **285 million** people are blind or visually impaired
- **1 in 5** Americans has a disability

### Your Chatbot Impact:
Before ARIA roles:
- ❌ Screen reader users couldn't distinguish message types
- ❌ Status changes weren't announced
- ❌ Citations were confusing to navigate
- ❌ Poor accessibility score

After ARIA roles:
- ✅ Clear semantic structure
- ✅ Status changes are announced
- ✅ Easy citation navigation
- ✅ Much better accessibility score
- ✅ More inclusive! 🎉

## Summary

**Screen Reader** = Software that reads web pages aloud to blind/visually impaired users

**ARIA Roles** = Help screen readers understand what elements mean

**Result** = Your chatbot is now accessible to more people! 🌟

---

**Want to test?** Try Windows Narrator (`Win + Ctrl + Enter`) and navigate your chatbot with `Tab` key - you'll hear how screen readers experience your page!

