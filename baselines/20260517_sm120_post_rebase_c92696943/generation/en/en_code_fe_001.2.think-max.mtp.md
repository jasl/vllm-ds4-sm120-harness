# Generation Transcript

- Case: `en_code_fe_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 66.97416
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 305, "total_tokens": 12649, "completion_tokens": 12344, "prompt_tokens_details": null}`
- Prompt tokens: 305
- Completion tokens: 12344
- Total tokens: 12649

## Prompt

```markdown
Create a single-file frontend app named `index.html`. Do not use external libraries, CDNs, images, or build tools. Keep the total code under 1,000 lines.

Task: build an accessible “meeting notes board” for a small team.

Functional requirements:
1. Users can add a note with title, owner, meeting date, tags, and body.
2. Notes appear as cards and can be filtered by owner, tag, and free-text search.
3. A note can be marked as “Action Required,” “Decision,” or “Reference.”
4. Users can edit and delete notes.
5. Persist all data in `localStorage`.
6. Provide a compact statistics strip: total notes, action-required count, unique owners, and most common tag.
7. Responsive layout: two-column card grid on wide screens, single column on narrow screens.
8. Basic accessibility: labels for inputs, keyboard-operable controls, visible focus states.

Output only the complete `index.html` content, including HTML, CSS, and JavaScript. Do not include explanatory text.
```

## Reasoning Content

````text
Let's build a single-file meeting notes board application with all the requirements. I'll create a complete `index.html` with embedded CSS and JavaScript that handles all the functionality.

Let me think through the architecture:

1. **Data Model**: Each note has id, title, owner, meetingDate, tags (array or comma-separated), body, type (action, decision, reference), createdAt, updatedAt.

2. **Storage**: localStorage with a key like 'meetingNotes'.

3. **UI Components**:
   - Add/Edit form (modal or inline)
   - Notes grid (cards)
   - Filter bar (owner, tag, search text)
   - Stats strip

4. **Responsive**: CSS grid with media query for single column on narrow screens.

5. **Accessibility**: labels, keyboard navigation, focus states.

Let me write the code:

I'll structure it as:
- HTML: form, filters, stats, notes container
- CSS: styling, responsive grid
- JavaScript: data management, rendering, event handling

Let me be thorough and create a polished app.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meeting Notes Board</title>
    <style>
        /* styles */
    </style>
</head>
<body>
    <!-- HTML structure -->
    <script>
        // JavaScript
    </script>
</body>
</html>
```

Let me design the layout:

Header: "Meeting Notes Board" with stats strip below.

Main area: Filter bar, then "Add Note" button, then notes grid.

Form modal: overlay with form fields.

Stats strip: total notes, action required count, unique owners, most common tag.

Let me code this step by step.

Stats:
- total notes: count
- action required count: notes with type 'action'
- unique owners: count of distinct owners
- most common tag: find the tag with highest frequency across all notes

Filtering:
- by owner: dropdown or select
- by tag: dropdown or select
- by free-text: input that searches title, body

I'll use select elements for owner and tag filters, populated from existing data.

For the form, fields:
- Title (text input, required)
- Owner (text input, required)
- Meeting Date (date input, required)
- Tags (text input, comma separated)
- Body (textarea, required)
- Type (radio buttons or select: Action Required, Decision, Reference)

Let me build this out. I'll aim for clean, accessible code.

Let me write the JavaScript with:
- CRUD operations
- Filter logic
- Stats calculation
- localStorage persistence
- Form handling for add/edit

I'll use event delegation for the note cards (edit/delete buttons).

Let me code now.

For the form modal, I'll use a dialog or a simple overlay. I'll use a div overlay with the form, toggling visibility.

For accessibility:
- Labels associated with inputs using for/id
- Buttons have aria-labels or visible text
- Focus management when opening/closing modal
- Keyboard support (Escape to close modal)
- Visible focus outlines

Let me write the complete code. I need to keep it under 1000 lines total, so I'll be concise but complete.

Let me sketch the stats computation:
- totalNotes: notes.length
- actionCount: notes.filter(n => n.type === 'action').length
- uniqueOwners: new Set(notes.map(n => n.owner)).size
- mostCommonTag: iterate all tags, count frequencies, find max

Let me now write the complete file.

I need to be careful with:
- Properly saving and loading from localStorage
- Updating stats when notes change
- Filtering correctly
- Form validation

Let me code it.

I'll use a unique id for notes using Date.now() + random string.

Here's my plan for the HTML structure:

```
<header>
  <h1>Meeting Notes Board</h1>
  <div class="stats">...</div>
</header>
<main>
  <div class="filters">
    <select id="filter-owner">...</select>
    <select id="filter-tag">...</select>
    <input id="filter-search" type="search" placeholder="Search...">
    <button id="add-note-btn">+ Add Note</button>
  </div>
  <div id="notes-grid">...</div>
</main>
<!-- Modal overlay -->
<div id="note-modal" class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <form id="note-form">
    <h2 id="modal-title">Add Note</h2>
    <!-- fields -->
    <button type="submit">Save</button>
    <button type="button" id="cancel-btn">Cancel</button>
  </form>
</div>
```

Let me think about the form fields more carefully:

- Title: text input, required
- Owner: text input, required (could also be a select with existing owners + option to add new)
- Meeting Date: date input
- Tags: text input (comma-separated)
- Body: textarea, required
- Type: radio group with three options

For owner and tags, I'll use text inputs for simplicity but provide suggestions/tag display.

Actually, for a better UX, I could use a datalist for owners, but text input is fine.

For tags, I could show them as chips in the card, and in the form, comma-separated input.

Let me keep it simple with text inputs.

Now, let me write the CSS with a nice design. I'll use a color scheme that's professional but friendly.

Colors:
- Primary: #4A90D9 (blue)
- Action: #E74C3C (red)
- Decision: #F39C12 (orange)
- Reference: #2ECC71 (green)
- Background: #F5F7FA
- Card: white

I'll keep the design clean and minimal.

For the responsive grid:
- Desktop: 2 columns
- Mobile (< 768px): 1 column

Let me use CSS Grid with grid-template-columns: repeat(2, 1fr) and media query for single column.

Let me write the complete file now.

Actually, I realize for owner, it would be nice to have a dropdown of existing owners to make filtering easier. For the filter, I'll populate a select with all unique owners. For the form, I'll use a text input with a datalist for suggestions.

Similarly for tags in the filter.

Let me implement it.

OK, let me start writing the code. I'll aim for ~300-400 lines of well-structured code.

Let me write the full implementation:

<details>
<summary>Complete plan</summary>

HTML structure:
- header with title and stats
- filter bar
- notes grid
- modal for add/edit

CSS:
- variables for colors
- responsive grid
- accessible focus states
- card styling

JavaScript:
- Data management (load, save, CRUD)
- Render function
- Filter function
- Stats update
- Form handling
- Event listeners
- Keyboard support

I'll now write everything.

For the "most common tag", I need to handle tags being comma-separated strings. I'll split by comma, trim, and count.

Let me also think about empty states: when no notes, show a message.

Alright, let me write the code now.

I need to be careful about:
- The edit button should populate the form with existing data
- The delete button should confirm before deleting
- The form should validate required fields
- Escape key should close the modal

Let me write it.

For the modal, I'll use a simple overlay that covers the screen. I'll use display: flex to center the form.

For focus management:
- When modal opens, focus the first input
- When modal closes, focus the button that opened it (or the add button)
- Trap focus within the modal (nice to have but maybe keep it simple)

I'll implement basic focus management.

Let me now write the complete code.

Actually, I think I should use a dialog element but for simplicity, I'll use a div overlay.

Let me write the code:

```javascript
// Data
let notes = [];
let editingId = null;

// Load from localStorage
function loadNotes() {
    const data = localStorage.getItem('meetingNotes');
    if (data) {
        try {
            notes = JSON.parse(data);
        } catch (e) {
            notes = [];
        }
    }
}

// Save to localStorage
function saveNotes() {
    localStorage.setItem('meetingNotes', JSON.stringify(notes));
}

// CRUD
function addNote(note) {
    note.id = Date.now().toString(36) + Math.random().toString(36).substr(2);
    note.createdAt = new Date().toISOString();
    note.updatedAt = note.createdAt;
    notes.push(note);
    saveNotes();
    render();
}

function updateNote(id, updated) {
    const index = notes.findIndex(n => n.id === id);
    if (index !== -1) {
        updated.updatedAt = new Date().toISOString();
        notes[index] = { ...notes[index], ...updated, id: notes[index].id };
        saveNotes();
        render();
    }
}

function deleteNote(id) {
    if (confirm('Are you sure you want to delete this note?')) {
        notes = notes.filter(n => n.id !== id);
        saveNotes();
        render();
    }
}
```

Alright, I think I have a good plan. Let me write the full code now.

One more thing: for the tags, I'll store them as arrays in the data, but in the form, I'll use comma-separated input. When displaying, I'll show them as chips/badges.

For filtering tags, I'll create a dropdown with all unique tags from all notes.

Let me also consider: when adding a new note, the owner could be selected from existing ones or typed in. I'll use a text input with a datalist for suggestions.

OK let me just write the code. I'll make it clean and complete.

Let me think about the total line count. I need to keep it under 1000 lines. With HTML, CSS, and JS, I should be fine if I'm concise.

Let me write it now.

Actually, I want to make the UI pretty nice. Let me think about the card design:

Each card shows:
- Title (large)
- Owner, Date, Type (badge with color)
- Tags (small badges)
- Body (truncated? or full)
- Edit and Delete buttons (icon or text)

For the cards, I'll show the full body since notes are meant to be read. But if the body is very long, maybe truncate with a "show more" option? To keep it simple, I'll show full body with max-height and overflow, but actually better to just show it all since notes are likely short.

Let me keep it simple: show all content, and if it's very long, the card will expand.

For the stats strip, I'll show:
- 📝 Total: X
- ⚠️ Action Required: X
- 👥 Unique Owners: X
- 🏷️ Common Tag: X

I'll use simple text labels, not emoji icons (since no images/external resources). I can use Unicode characters though.

Actually, requirement says "no images" but emoji are text, so they're fine. But to be safe, I'll just use text with styling.

Let me use CSS to make stats visually appealing with colored backgrounds or borders.

Let me now write the complete file.
````

## Assistant

````markdown
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meeting Notes Board</title>
    <style>
        /* ── Reset & Base ── */
        *,
        *::before,
        *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: #f4f6f9;
            color: #1e293b;
            line-height: 1.5;
            padding: 1.25rem;
            min-height: 100vh;
        }

        /* ── Variables ── */
        :root {
            --color-primary: #3b82f6;
            --color-primary-hover: #2563eb;
            --color-action: #ef4444;
            --color-decision: #f59e0b;
            --color-reference: #10b981;
            --color-bg: #ffffff;
            --color-border: #e2e8f0;
            --color-text: #1e293b;
            --color-text-secondary: #64748b;
            --color-focus: #3b82f6;
            --radius: 0.75rem;
            --shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
            --shadow-lg: 0 4px 24px rgba(0, 0, 0, 0.12);
            --transition: 0.2s ease;
            --font-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        }

        /* ── Focus ── */
        :focus-visible {
            outline: 2px solid var(--color-focus);
            outline-offset: 2px;
        }

        button:focus-visible,
        input:focus-visible,
        select:focus-visible,
        textarea:focus-visible {
            outline: 2px solid var(--color-focus);
            outline-offset: 2px;
        }

        /* ── Header ── */
        .app-header {
            max-width: 1200px;
            margin: 0 auto 1.5rem;
        }

        .app-header h1 {
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            color: #0f172a;
            margin-bottom: 1rem;
        }

        /* ── Stats Strip ── */
        .stats {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            background: var(--color-bg);
            border-radius: var(--radius);
            padding: 1rem 1.25rem;
            box-shadow: var(--shadow);
            border: 1px solid var(--color-border);
        }

        .stat {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            padding: 0.25rem 0.75rem 0.25rem 0;
            border-right: 1px solid var(--color-border);
            padding-right: 1rem;
        }
        .stat:last-child {
            border-right: none;
            padding-right: 0;
        }
        .stat-value {
            font-weight: 700;
            font-size: 1.125rem;
            color: #0f172a;
            min-width: 1.5rem;
            text-align: center;
        }
        .stat-label {
            color: var(--color-text-secondary);
        }
        .stat-badge {
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            max-width: 160px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            background: #eef2ff;
            color: #4338ca;
        }
        .stat-action .stat-value {
            color: var(--color-action);
        }
        .stat-owners .stat-value {
            color: var(--color-primary);
        }
        .stat-tag .stat-value {
            color: var(--color-reference);
        }

        @media (max-width: 640px) {
            .stats {
                gap: 0.5rem;
                padding: 0.75rem 1rem;
            }
            .stat {
                font-size: 0.75rem;
                padding-right: 0.5rem;
            }
            .stat-value {
                font-size: 1rem;
            }
            .stat-badge {
                font-size: 0.625rem;
                max-width: 100px;
            }
        }

        /* ── Filter Bar ── */
        .filter-bar {
            max-width: 1200px;
            margin: 0 auto 1.25rem;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.75rem;
            background: var(--color-bg);
            border-radius: var(--radius);
            padding: 0.875rem 1.25rem;
            box-shadow: var(--shadow);
            border: 1px solid var(--color-border);
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 0.125rem;
            flex: 1 1 140px;
            min-width: 120px;
        }
        .filter-group label {
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--color-text-secondary);
        }

        .filter-group select,
        .filter-group input {
            padding: 0.375rem 0.625rem;
            border: 1px solid var(--color-border);
            border-radius: 0.5rem;
            font-size: 0.875rem;
            background: #f8fafc;
            color: var(--color-text);
            transition: border-color var(--transition), background var(--transition);
            width: 100%;
        }

        .filter-group select:focus,
        .filter-group input:focus {
            background: #fff;
            border-color: var(--color-focus);
        }

        .filter-bar .add-btn {
            flex: 0 0 auto;
            align-self: flex-end;
            padding: 0.5rem 1.25rem;
            background: var(--color-primary);
            color: #fff;
            border: none;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: background var(--transition), transform var(--transition);
            white-space: nowrap;
        }

        .filter-bar .add-btn:hover,
        .filter-bar .add-btn:focus-visible {
            background: var(--color-primary-hover);
        }
        .filter-bar .add-btn:active {
            transform: scale(0.97);
        }

        @media (max-width: 640px) {
            .filter-bar {
                padding: 0.75rem 1rem;
                gap: 0.5rem;
            }
            .filter-group {
                flex: 1 1 100%;
                min-width: 0;
            }
            .filter-bar .add-btn {
                width: 100%;
                padding: 0.5rem;
            }
        }

        /* ── Notes Grid ── */
        .notes-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.25rem;
        }

        @media (max-width: 768px) {
            .notes-grid {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
        }

        .empty-state {
            grid-column: 1 / -1;
            text-align: center;
            padding: 3rem 1rem;
            color: var(--color-text-secondary);
            background: var(--color-bg);
            border-radius: var(--radius);
            border: 2px dashed var(--color-border);
            font-size: 1rem;
        }
        .empty-state strong {
            color: var(--color-text);
        }

        /* ── Note Card ── */
        .note-card {
            background: var(--color-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            border: 1px solid var(--color-border);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            transition: box-shadow var(--transition), border-color var(--transition);
            position: relative;
        }
        .note-card:hover {
            box-shadow: var(--shadow-lg);
            border-color: #cbd5e1;
        }

        .note-card .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }

        .note-card .card-title {
            font-size: 1.125rem;
            font-weight: 700;
            color: #0f172a;
            word-break: break-word;
            flex: 1;
        }

        .note-card .type-badge {
            flex-shrink: 0;
            font-size: 0.625rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 0.25rem 0.625rem;
            border-radius: 999px;
            background: #e2e8f0;
            color: #475569;
            border: 1px solid transparent;
        }
        .type-action {
            background: #fef2f2;
            color: var(--color-action);
            border-color: #fecaca;
        }
        .type-decision {
            background: #fffbeb;
            color: #b45309;
            border-color: #fde68a;
        }
        .type-reference {
            background: #ecfdf5;
            color: #047857;
            border-color: #a7f3d0;
        }

        .note-card .card-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem 1rem;
            font-size: 0.8rem;
            color: var(--color-text-secondary);
            margin-bottom: 0.75rem;
        }
        .note-card .card-meta span {
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        .note-card .card-meta .label {
            font-weight: 600;
            color: var(--color-text);
        }

        .note-card .card-body {
            font-size: 0.9rem;
            color: #334155;
            white-space: pre-wrap;
            word-break: break-word;
            flex: 1;
            margin-bottom: 1rem;
            line-height: 1.55;
            max-height: 240px;
            overflow-y: auto;
            padding-right: 0.25rem;
        }
        .note-card .card-body::-webkit-scrollbar {
            width: 4px;
        }
        .note-card .card-body::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }

        .note-card .tags-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.375rem;
            margin-bottom: 1rem;
        }
        .note-card .tag-chip {
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 500;
            background: #f1f5f9;
            color: #475569;
            border: 1px solid #e2e8f0;
        }

        .note-card .card-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: auto;
            padding-top: 0.75rem;
            border-top: 1px solid var(--color-border);
        }

        .note-card .card-actions button {
            padding: 0.375rem 0.875rem;
            font-size: 0.8rem;
            font-weight: 600;
            border: 1px solid var(--color-border);
            border-radius: 0.5rem;
            background: #f8fafc;
            color: var(--color-text);
            cursor: pointer;
            transition: background var(--transition), border-color var(--transition), color var(--transition);
            flex: 1;
        }
        .note-card .card-actions button:hover,
        .note-card .card-actions button:focus-visible {
            background: #eef2ff;
            border-color: var(--color-primary);
            color: var(--color-primary);
        }
        .note-card .card-actions .delete-btn:hover,
        .note-card .card-actions .delete-btn:focus-visible {
            background: #fef2f2;
            border-color: var(--color-action);
            color: var(--color-action);
        }

        @media (max-width: 480px) {
            .note-card {
                padding: 1rem;
            }
            .note-card .card-title {
                font-size: 1rem;
            }
            .note-card .card-actions {
                flex-direction: column;
            }
        }

        /* ── Modal ── */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.45);
            backdrop-filter: blur(4px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 1rem;
            animation: fadeIn 0.15s ease;
        }
        .modal-overlay.open {
            display: flex;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        @keyframes slideUp {
            from {
                transform: translateY(16px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .modal-content {
            background: var(--color-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow-lg);
            width: 100%;
            max-width: 620px;
            max-height: 90vh;
            overflow-y: auto;
            padding: 1.75rem 2rem;
            animation: slideUp 0.2s ease;
            position: relative;
        }
        .modal-content h2 {
            font-size: 1.35rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 1.25rem;
            padding-right: 2rem;
        }

        .modal-close {
            position: absolute;
            top: 1rem;
            right: 1rem;
            width: 2rem;
            height: 2rem;
            border: none;
            background: transparent;
            font-size: 1.5rem;
            cursor: pointer;
            border-radius: 0.375rem;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--color-text-secondary);
            transition: background var(--transition), color var(--transition);
        }
        .modal-close:hover,
        .modal-close:focus-visible {
            background: #f1f5f9;
            color: var(--color-text);
        }

        .form-field {
            margin-bottom: 1.125rem;
        }
        .form-field label {
            display: block;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--color-text);
            margin-bottom: 0.25rem;
        }
        .form-field label .required {
            color: var(--color-action);
            margin-left: 0.125rem;
        }
        .form-field input,
        .form-field textarea,
        .form-field select {
            width: 100%;
            padding: 0.5rem 0.75rem;
            border: 1px solid var(--color-border);
            border-radius: 0.5rem;
            font-size: 0.9rem;
            font-family: inherit;
            background: #f8fafc;
            color: var(--color-text);
            transition: border-color var(--transition), background var(--transition);
        }
        .form-field input:focus,
        .form-field textarea:focus,
        .form-field select:focus {
            background: #fff;
            border-color: var(--color-focus);
        }
        .form-field textarea {
            resize: vertical;
            min-height: 100px;
        }
        .form-field .hint {
            font-size: 0.7rem;
            color: var(--color-text-secondary);
            margin-top: 0.25rem;
        }

        .radio-group {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-top: 0.375rem;
        }
        .radio-group label {
            display: flex;
            align-items: center;
            gap: 0.375rem;
            font-size: 0.875rem;
            font-weight: 400;
            cursor: pointer;
            padding: 0.25rem 0;
        }
        .radio-group input[type="radio"] {
            width: auto;
            accent-color: var(--color-primary);
        }

        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 0.75rem;
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid var(--color-border);
        }
        .form-actions button {
            padding: 0.5rem 1.5rem;
            font-size: 0.875rem;
            font-weight: 600;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: background var(--transition), transform var(--transition);
            border: 1px solid var(--color-border);
            background: #f8fafc;
            color: var(--color-text);
        }
        .form-actions button:hover,
        .form-actions button:focus-visible {
            background: #eef2ff;
            border-color: var(--color-primary);
        }
        .form-actions .btn-primary {
            background: var(--color-primary);
            color: #fff;
            border-color: var(--color-primary);
        }
        .form-actions .btn-primary:hover,
        .form-actions .btn-primary:focus-visible {
            background: var(--color-primary-hover);
            border-color: var(--color-primary-hover);
        }
        .form-actions .btn-primary:active {
            transform: scale(0.97);
        }

        @media (max-width: 640px) {
            .modal-content {
                padding: 1.25rem 1.25rem;
                max-height: 85vh;
            }
            .form-actions {
                flex-direction: column-reverse;
            }
            .form-actions button {
                width: 100%;
                text-align: center;
            }
            .radio-group {
                flex-direction: column;
                gap: 0.25rem;
            }
        }

        /* ── Scrollbar for modal ── */
        .modal-content::-webkit-scrollbar {
            width: 6px;
        }
        .modal-content::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 6px;
        }
        .modal-content::-webkit-scrollbar-track {
            background: transparent;
        }

        /* ── Utility for screen-reader-only ── */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }

        /* ── Responsive tweaks ── */
        @media (max-width: 400px) {
            body {
                padding: 0.75rem;
            }
            .app-header h1 {
                font-size: 1.35rem;
            }
        }
    </style>
</head>
<body>

    <!-- ════ HEADER ════ -->
    <header class="app-header">
        <h1>📋 Meeting Notes Board</h1>
        <div class="stats" role="status" aria-label="Notes statistics">
            <div class="stat stat-total">
                <span class="stat-value" id="stat-total">0</span>
                <span class="stat-label">Total</span>
            </div>
            <div class="stat stat-action">
                <span class="stat-value" id="stat-action">0</span>
                <span class="stat-label">Action Required</span>
            </div>
            <div class="stat stat-owners">
                <span class="stat-value" id="stat-owners">0</span>
                <span class="stat-label">Owners</span>
            </div>
            <div class="stat stat-tag">
                <span class="stat-label">Top Tag</span>
                <span class="stat-badge" id="stat-tag">—</span>
            </div>
        </div>
    </header>

    <!-- ════ FILTER BAR ════ -->
    <div class="filter-bar" role="search" aria-label="Filter notes">
        <div class="filter-group">
            <label for="filter-owner">Owner</label>
            <select id="filter-owner" aria-label="Filter by owner">
                <option value="">All Owners</option>
            </select>
        </div>

        <div class="filter-group">
            <label for="filter-tag">Tag</label>
            <select id="filter-tag" aria-label="Filter by tag">
                <option value="">All Tags</option>
            </select>
        </div>

        <div class="filter-group">
            <label for="filter-search">Search</label>
            <input type="search" id="filter-search" placeholder="Title, body…" autocomplete="off">
        </div>

        <button class="add-btn" id="add-note-btn" aria-label="Add new meeting note">+ Add Note</button>
    </div>

    <!-- ════ NOTES GRID ════ -->
    <main class="notes-grid" id="notes-grid" aria-label="Meeting notes list">
        <div class="empty-state" id="empty-state">
            <p><strong>No notes yet.</strong> Click <strong>+ Add Note</strong> to create the first meeting note.</p>
        </div>
    </main>

    <!-- ════ MODAL ════ -->
    <div class="modal-overlay" id="note-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="modal-content">
            <button class="modal-close" id="modal-close-btn" aria-label="Close dialog">&times;</button>
            <h2 id="modal-title">Add Note</h2>

            <form id="note-form" novalidate>
                <div class="form-field">
                    <label for="note-title">Title <span class="required" aria-hidden="true">*</span></label>
                    <input type="text" id="note-title" required autocomplete="off" placeholder="Brief meeting topic">
                </div>

                <div class="form-field">
                    <label for="note-owner">Owner <span class="required" aria-hidden="true">*</span></label>
                    <input type="text" id="note-owner" required autocomplete="off" placeholder="Name of the note owner" list="owner-suggestions">
                    <datalist id="owner-suggestions"></datalist>
                </div>

                <div class="form-field">
                    <label for="note-date">Meeting Date <span class="required" aria-hidden="true">*</span></label>
                    <input type="date" id="note-date" required>
                </div>

                <div class="form-field">
                    <label for="note-tags">Tags</label>
                    <input type="text" id="note-tags" autocomplete="off" placeholder="e.g. design, sprint, frontend" list="tag-suggestions">
                    <datalist id="tag-suggestions"></datalist>
                    <div class="hint">Separate tags with commas.</div>
                </div>

                <div class="form-field">
                    <label for="note-body">Notes <span class="required" aria-hidden="true">*</span></label>
                    <textarea id="note-body" required placeholder="Key points, decisions, action items…"></textarea>
                </div>

                <fieldset class="form-field">
                    <legend style="font-size:0.8rem;font-weight:600;margin-bottom:0.375rem;">Type <span class="required" aria-hidden="true">*</span></legend>
                    <div class="radio-group" role="radiogroup" aria-label="Note type">
                        <label>
                            <input type="radio" name="note-type" value="action" required>
                            ⚡ Action Required
                        </label>
                        <label>
                            <input type="radio" name="note-type" value="decision">
                            ✅ Decision
                        </label>
                        <label>
                            <input type="radio" name="note-type" value="reference">
                            📎 Reference
                        </label>
                    </div>
                </fieldset>

                <div class="form-actions">
                    <button type="button" id="cancel-btn">Cancel</button>
                    <button type="submit" class="btn-primary" id="save-btn">Save Note</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        /* ─────────────── STATE ─────────────── */
        let notes = [];
        let editingId = null;
        let currentFilter = { owner: '', tag: '', search: '' };

        const STORAGE_KEY = 'meetingNotesBoard';

        /* ─────────────── DOM refs ─────────────── */
        const grid = document.getElementById('notes-grid');
        const emptyState = document.getElementById('empty-state');
        const modal = document.getElementById('note-modal');
        const form = document.getElementById('note-form');
        const modalTitle = document.getElementById('modal-title');
        const saveBtn = document.getElementById('save-btn');
        const cancelBtn = document.getElementById('cancel-btn');
        const closeBtn = document.getElementById('modal-close-btn');
        const addBtn = document.getElementById('add-note-btn');

        const filterOwner = document.getElementById('filter-owner');
        const filterTag = document.getElementById('filter-tag');
        const filterSearch = document.getElementById('filter-search');

        const statTotal = document.getElementById('stat-total');
        const statAction = document.getElementById('stat-action');
        const statOwners = document.getElementById('stat-owners');
        const statTag = document.getElementById('stat-tag');

        const ownerSuggestions = document.getElementById('owner-suggestions');
        const tagSuggestions = document.getElementById('tag-suggestions');

        /* ─────────────── CRUD + Storage ─────────────── */
        function loadNotes() {
            try {
                const raw = localStorage.getItem(STORAGE_KEY);
                if (raw) {
                    notes = JSON.parse(raw);
                    if (!Array.isArray(notes)) notes = [];
                } else {
                    notes = [];
                }
            } catch (_) {
                notes = [];
            }
            // ensure each note has proper structure
            notes = notes.filter(n => n && typeof n === 'object');
            notes.forEach(n => {
                if (!n.id) n.id = generateId();
                if (!n.tags) n.tags = [];
                if (!n.type) n.type = 'reference';
                if (!n.createdAt) n.createdAt = new Date().toISOString();
                if (!n.updatedAt) n.updatedAt = n.createdAt;
            });
        }

        function saveNotes() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
        }

        function generateId() {
            return Date.now().toString(36) + '-' + Math.random().toString(36).substring(2, 8);
        }

        function addNote(note) {
            note.id = generateId();
            note.createdAt = new Date().toISOString();
            note.updatedAt = note.createdAt;
            note.tags = parseTags(note.tags);
            notes.push(note);
            saveNotes();
            render();
        }

        function updateNote(id, updated) {
            const idx = notes.findIndex(n => n.id === id);
            if (idx === -1) return;
            updated.tags = parseTags(updated.tags);
            updated.updatedAt = new Date().toISOString();
            // Preserve id and createdAt
            notes[idx] = { ...notes[idx], ...updated, id: notes[idx].id, createdAt: notes[idx].createdAt };
            saveNotes();
            render();
        }

        function deleteNote(id) {
            if (!confirm('Delete this note permanently?')) return;
            notes = notes.filter(n => n.id !== id);
            saveNotes();
            render();
        }

        function getNoteById(id) {
            return notes.find(n => n.id === id);
        }

        /* ─────────────── Helpers ─────────────── */
        function parseTags(input) {
            if (Array.isArray(input)) return input.map(t => t.trim()).filter(Boolean);
            if (typeof input === 'string') return input.split(',').map(t => t.trim()).filter(Boolean);
            return [];
        }

        function formatDate(dateStr) {
            if (!dateStr) return '';
            const d = new Date(dateStr + 'T00:00:00');
            if (isNaN(d)) return dateStr;
            return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
        }

        function escapeHtml(str) {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }

        /* ─────────────── Stats ─────────────── */
        function computeStats() {
            const total = notes.length;
            const actionCount = notes.filter(n => n.type === 'action').length;
            const uniqueOwners = new Set(notes.map(n => n.owner.trim().toLowerCase()).filter(Boolean)).size;

            // most common tag
            const tagFreq = {};
            notes.forEach(n => {
                (n.tags || []).forEach(t => {
                    const key = t.trim().toLowerCase();
                    if (key) tagFreq[key] = (tagFreq[key] || 0) + 1;
                });
            });
            let topTag = '—';
            let topCount = 0;
            for (const [tag, count] of Object.entries(tagFreq)) {
                if (count > topCount) {
                    topCount = count;
                    topTag = tag;
                }
            }
            // display with original casing from the first note that has it
            if (topTag !== '—') {
                for (const n of notes) {
                    const found = (n.tags || []).find(t => t.trim().toLowerCase() === topTag);
                    if (found) {
                        topTag = found.trim();
                        break;
                    }
                }
            }

            return { total, actionCount, uniqueOwners, topTag };
        }

        function updateStats() {
            const s = computeStats();
            statTotal.textContent = s.total;
            statAction.textContent = s.actionCount;
            statOwners.textContent = s.uniqueOwners;
            statTag.textContent = s.topTag || '—';
        }

        /* ─────────────── Filtering ─────────────── */
        function getFilteredNotes() {
            const f = currentFilter;
            return notes.filter(n => {
                // owner filter
                if (f.owner) {
                    const ownerNorm = n.owner.trim().toLowerCase();
                    if (ownerNorm !== f.owner.toLowerCase()) return false;
                }
                // tag filter
                if (f.tag) {
                    const tagNorm = f.tag.toLowerCase();
                    const hasTag = (n.tags || []).some(t => t.trim().toLowerCase() === tagNorm);
                    if (!hasTag) return false;
                }
                // search filter
                if (f.search) {
                    const q = f.search.toLowerCase();
                    const inTitle = n.title.toLowerCase().includes(q);
                    const inBody = n.body.toLowerCase().includes(q);
                    const inOwner = n.owner.toLowerCase().includes(q);
                    const inTags = (n.tags || []).some(t => t.toLowerCase().includes(q));
                    if (!(inTitle || inBody || inOwner || inTags)) return false;
                }
                return true;
            });
        }

        function updateFilterSelects() {
            // Collect unique owners and tags
            const owners = new Set();
            const tags = new Set();
            notes.forEach(n => {
                if (n.owner.trim()) owners.add(n.owner.trim());
                (n.tags || []).forEach(t => {
                    const tt = t.trim();
                    if (tt) tags.add(tt);
                });
            });

            // Owner dropdown
            const ownerVal = filterOwner.value;
            filterOwner.innerHTML = '<option value="">All Owners</option>';
            [...owners].sort().forEach(o => {
                const opt = document.createElement('option');
                opt.value = o;
                opt.textContent = o;
                filterOwner.appendChild(opt);
            });
            if ([...owners].some(o => o === ownerVal)) {
                filterOwner.value = ownerVal;
            } else {
                filterOwner.value = '';
            }

            // Tag dropdown
            const tagVal = filterTag.value;
            filterTag.innerHTML = '<option value="">All Tags</option>';
            [...tags].sort().forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                opt.textContent = t;
                filterTag.appendChild(opt);
            });
            if ([...tags].some(t => t === tagVal)) {
                filterTag.value = tagVal;
            } else {
                filterTag.value = '';
            }

            // Update current filter with actual values
            currentFilter.owner = filterOwner.value;
            currentFilter.tag = filterTag.value;
            currentFilter.search = filterSearch.value;

            // Update datalists for form
            ownerSuggestions.innerHTML = [...owners].sort().map(o => `<option value="${escapeHtml(o)}">`).join('');
            const allTags = [...tags].sort();
            tagSuggestions.innerHTML = allTags.map(t => `<option value="${escapeHtml(t)}">`).join('');
        }

        /* ─────────────── Render ─────────────── */
        function render() {
            updateFilterSelects();
            const filtered = getFilteredNotes();
            updateStats();

            // Clear grid (keep empty state element)
            const items = grid.querySelectorAll('.note-card');
            items.forEach(el => el.remove());

            if (filtered.length === 0) {
                emptyState.style.display = 'block';
                return;
            }
            emptyState.style.display = 'none';

            filtered.forEach(note => {
                const card = document.createElement('article');
                card.className = 'note-card';
                card.setAttribute('aria-label', `Note: ${note.title}`);

                const typeClass = 'type-' + note.type;
                const typeLabel = { action: 'Action Required', decision: 'Decision', reference: 'Reference' } [note
                .type] || note.type;

                const dateFormatted = formatDate(note.meetingDate);

                const tagChips = (note.tags || []).map(t =>
                    `<span class="tag-chip">${escapeHtml(t)}</span>`
                ).join('');

                card.innerHTML = `
              <div class="card-header">
                <div class="card-title">${escapeHtml(note.title)}</div>
                <span class="type-badge ${typeClass}">${typeLabel}</span>
              </div>
              <div class="card-meta">
                <span><span class="label">Owner:</span> ${escapeHtml(note.owner)}</span>
                ${dateFormatted ? `<span><span class="label">Date:</span> ${dateFormatted}</span>` : ''}
                ${note.updatedAt ? `<span><span class="label">Updated:</span> ${new Date(note.updatedAt).toLocaleDateString()}</span>` : ''}
              </div>
              ${tagChips ? `<div class="tags-row">${tagChips}</div>` : ''}
              <div class="card-body">${escapeHtml(note.body)}</div>
              <div class="card-actions">
                <button class="edit-btn" data-id="${note.id}" aria-label="Edit note: ${escapeHtml(note.title)}">✏️ Edit</button>
                <button class="delete-btn" data-id="${note.id}" aria-label="Delete note: ${escapeHtml(note.title)}">🗑️ Delete</button>
              </div>
            `;

                grid.appendChild(card);
            });
        }

        /* ─────────────── Form handling ─────────────── */
        function openModal(noteId) {
            editingId = noteId || null;
            form.reset();
            document.querySelectorAll('input[name="note-type"]').forEach(r => r.checked = false);

            if (noteId) {
                const note = getNoteById(noteId);
                if (!note) return;
                modalTitle.textContent = 'Edit Note';
                saveBtn.textContent = 'Update Note';
                document.getElementById('note-title').value = note.title || '';
                document.getElementById('note-owner').value = note.owner || '';
                document.getElementById('note-date').value = note.meetingDate || '';
                document.getElementById('note-tags').value = (note.tags || []).join(', ');
                document.getElementById('note-body').value = note.body || '';
                const typeRadio = document.querySelector(`input[name="note-type"][value="${note.type}"]`);
                if (typeRadio) typeRadio.checked = true;
            } else {
                modalTitle.textContent = 'Add Note';
                saveBtn.textContent = 'Save Note';
                // Pre-fill date with today
                const today = new Date().toISOString().split('T')[0];
                document.getElementById('note-date').value = today;
                // Suggest owner from filter if set
                if (currentFilter.owner) {
                    document.getElementById('note-owner').value = currentFilter.owner;
                }
            }

            modal.classList.add('open');
            // Focus first input
            setTimeout(() => {
                const firstInput = document.getElementById('note-title');
                if (firstInput) firstInput.focus();
            }, 50);
        }

        function closeModal() {
            modal.classList.remove('open');
            editingId = null;
            // Return focus to add button
            addBtn.focus();
        }

        function handleFormSubmit(e) {
            e.preventDefault();

            const title = document.getElementById('note-title').value.trim();
            const owner = document.getElementById('note-owner').value.trim();
            const meetingDate = document.getElementById('note-date').value;
            const tagsRaw = document.getElementById('note-tags').value.trim();
            const body = document.getElementById('note-body').value.trim();
            const typeEl = document.querySelector('input[name="note-type"]:checked');

            if (!title || !owner || !body || !meetingDate || !typeEl) {
                // highlight missing fields (native validation with reportValidity)
                form.reportValidity();
                return;
            }

            const type = typeEl.value;
            const tags = parseTags(tagsRaw);

            const data = { title, owner, meetingDate, tags, body, type };

            if (editingId) {
                updateNote(editingId, data);
            } else {
                addNote(data);
            }

            closeModal();
        }

        /* ─────────────── Event listeners ─────────────── */

        // Modal controls
        addBtn.addEventListener('click', () => openModal(null));
        cancelBtn.addEventListener('click', closeModal);
        closeBtn.addEventListener('click', closeModal);

        // Close on overlay click (only if clicking backdrop)
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });

        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('open')) {
                closeModal();
            }
        });

        // Form submit
        form.addEventListener('submit', handleFormSubmit);

        // Filter events
        filterOwner.addEventListener('change', () => {
            currentFilter.owner = filterOwner.value;
            render();
        });
        filterTag.addEventListener('change', () => {
            currentFilter.tag = filterTag.value;
            render();
        });
        filterSearch.addEventListener('input', () => {
            currentFilter.search = filterSearch.value;
            render();
        });

        // Deleting via delegation on grid
        grid.addEventListener('click', (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;

            if (btn.classList.contains('delete-btn')) {
                const id = btn.dataset.id;
                if (id) deleteNote(id);
            } else if (btn.classList.contains('edit-btn')) {
                const id = btn.dataset.id;
                if (id) openModal(id);
            }
        });

        // Keyboard support for cards (Enter/Space on buttons is native)
        // Also allow Enter on card itself to edit? Not needed, buttons handle it.

        // ─────────────── Initialisation ───────────────
        loadNotes();
        render();

        // If there are no notes, add a sample note for demonstration
        if (notes.length === 0) {
            const sample = {
                id: generateId(),
                title: 'Sprint Planning — Week 42',
                owner: 'Alex',
                meetingDate: new Date().toISOString().split('T')[0],
                tags: ['sprint', 'planning'],
                body: 'Discussed Q4 milestones.\n- Frontend: finish dashboard by Friday.\n- Backend: API review on Thursday.',
                type: 'decision',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            notes.push(sample);
            const sample2 = {
                id: generateId(),
                title: 'Design Review — Checkout Flow',
                owner: 'Jamie',
                meetingDate: new Date(Date.now() - 86400000 * 2).toISOString().split('T')[0],
                tags: ['design', 'ux'],
                body: 'New checkout mockups approved. Need to implement error states and loading skeletons.\nAction: Alex to finalise mobile breakpoints by EOD.',
                type: 'action',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            notes.push(sample2);
            const sample3 = {
                id: generateId(),
                title: 'Architecture Notes — Auth Service',
                owner: 'Sam',
                meetingDate: new Date(Date.now() - 86400000 * 5).toISOString().split('T')[0],
                tags: ['backend', 'auth', 'reference'],
                body: 'Decision to use OAuth 2.0 + JWT. Token refresh every 15 minutes.\nSee RFC 6749 for details.',
                type: 'reference',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            notes.push(sample3);
            saveNotes();
            render();
        }

        console.log('📋 Meeting Notes Board ready —', notes.length, 'notes loaded.');
    </script>

</body>
</html>
```
````
