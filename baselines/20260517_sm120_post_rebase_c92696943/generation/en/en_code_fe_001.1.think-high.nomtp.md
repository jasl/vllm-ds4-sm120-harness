# Generation Transcript

- Case: `en_code_fe_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 113.346836
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 226, "total_tokens": 11398, "completion_tokens": 11172, "prompt_tokens_details": null}`
- Prompt tokens: 226
- Completion tokens: 11172
- Total tokens: 11398

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
The user wants me to create a single-file frontend app called `index.html` that implements a "meeting notes board" for a small team. Let me carefully plan and implement all the requirements:

1. **Add a note** with title, owner, meeting date, tags, and body
2. **Notes appear as cards** and can be filtered by owner, tag, and free-text search
3. **Note types**: "Action Required", "Decision", or "Reference"
4. **Edit and delete** notes
5. **localStorage** persistence
6. **Statistics strip**: total notes, action-required count, unique owners, most common tag
7. **Responsive layout**: two-column grid on wide screens, single on narrow
8. **Accessibility**: labels, keyboard controls, visible focus states

Let me build this step by step.

I'll structure the HTML with:
- A form for adding/editing notes
- A filter bar with owner dropdown, tag dropdown, and search input
- A statistics strip
- A card grid for displaying notes

Let me write the complete code:

I need to be careful about:
- Making sure all form inputs have labels
- Keyboard operability (buttons, links, etc.)
- Visible focus states
- Responsive CSS grid
- localStorage CRUD operations

Let me design the data model:
```js
{
  id: string (timestamp),
  title: string,
  owner: string,
  meetingDate: string (YYYY-MM-DD),
  tags: string (comma-separated),
  body: string,
  type: 'action' | 'decision' | 'reference',
  createdAt: timestamp
}
```

Let me build the UI:

I'll use a clean, professional design with good contrast and spacing.

Let me think about the statistics:
- Total notes: count of all notes
- Action required count: notes where type === 'action'
- Unique owners: count of unique owner values
- Most common tag: the tag that appears most frequently across all notes

For filtering:
- Owner filter: dropdown with unique owners
- Tag filter: dropdown with unique tags
- Free-text search: search in title, body, owner, etc.

Let me write the complete implementation now.

I need to be careful about the code length - keep it under 1000 lines.

Let me design a clean layout:

```
+------------------------------------------+
|  Meeting Notes Board                      |
+------------------------------------------+
|  [Stats strip: total | action | owners | tag] |
+------------------------------------------+
|  [Filter bar: owner dropdown | tag dropdown | search input] |
+------------------------------------------+
|  [Add Note button]                       |
+------------------------------------------+
|  +--------+  +--------+  +--------+     |
|  | Card 1 |  | Card 2 |  | Card 3 |     |
|  +--------+  +--------+  +--------+     |
|  +--------+  +--------+                  |
|  | Card 4 |  | Card 5 |                  |
|  +--------+  +--------+                  |
+------------------------------------------+
```

Let me now write the full code. I'll use a modal for add/edit to keep things clean.

Actually, I'll use an inline form that can be toggled, or a modal. A modal might be cleaner for accessibility. Let me use a modal dialog.

Let me think about the modal approach:
- Click "Add Note" opens a modal with the form
- Edit button opens the same modal pre-filled
- Modal has proper focus management and trap

Actually, for simplicity and accessibility, I'll use a section that appears at the top when adding/editing, or I'll use a modal. Let me use a modal dialog with `role="dialog"` and `aria-modal="true"`.

Let me code this up now.

I need to make sure:
- The modal can be closed with Escape key
- Focus is trapped in the modal
- The form is properly labeled

Let me write the complete code now.

Actually, let me simplify the approach - I'll use a form that slides in/out or appears as a modal overlay. A modal overlay is cleaner.

Let me go with a modal approach with a backdrop.

Here's my plan for the HTML structure:

```html
<!-- Header -->
<h1>Meeting Notes Board</h1>

<!-- Stats Strip -->
<div class="stats">...</div>

<!-- Filter Bar -->
<div class="filters">...</div>

<!-- Add Note Button -->
<button>Add Note</button>

<!-- Notes Grid -->
<div class="notes-grid">...</div>

<!-- Modal (hidden by default) -->
<div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <form>...</form>
</div>
```

Let me now write the complete implementation. I'll aim for a clean, professional look with good accessibility.

Let me write it all out now:

Actually, for the tags input, I'll use a simple text input where users can type comma-separated tags. This is simpler and more accessible than a complex tag picker.

For the owner field, I'll use a text input as well, but also provide a dropdown in the filter that shows unique owners.

Let me finalize the design and write the code.

One more thing - for the "most common tag" statistic, I need to handle the case where tags are comma-separated and there might be multiple tags per note. I'll split by comma and trim each tag.

Let me now write the full code.

I'll use a clean color scheme with a blue primary color and good contrast ratios.

Let me make sure the focus states are visible - I'll use a clear outline or ring.

Here's my implementation plan for the JavaScript:

```js
// Data management
let notes = [];
let editingId = null;

// Load from localStorage
function loadNotes() { ... }
function saveNotes() { ... }

// CRUD operations
function addNote(note) { ... }
function updateNote(id, note) { ... }
function deleteNote(id) { ... }

// Rendering
function renderNotes() { ... }
function renderStats() { ... }
function renderFilters() { ... }

// Modal management
function openModal(note) { ... }
function closeModal() { ... }

// Event listeners
// Form submission
// Filter changes
// etc.
```

Let me write the complete code now. I'll be thorough.

Let me think about the tag extraction for the most common tag:
- For each note, split tags by comma, trim each
- Count occurrences of each tag
- Find the most common one

For unique owners, I'll collect all owners and count unique ones.

OK, let me write the full code now. I'll keep it clean and well-organized.

Let me think about the responsive design:
- On wide screens (>= 768px), two-column grid
- On narrow screens (< 768px), single column

I'll use CSS grid with `grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))` or similar.

Actually, `repeat(2, 1fr)` for wide and `1fr` for narrow would be simpler and more controlled.

Let me use:
```css
.notes-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .notes-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

OK, let me now write the complete implementation. I'll be comprehensive.

Let me also think about the note type styling:
- Action Required: red/orange accent
- Decision: blue accent
- Reference: green/gray accent

This will help users visually distinguish note types.

Let me write the complete code now. Here goes:

I'll keep the design clean and minimal with:
- White cards with subtle shadows
- Clear typography
- Color-coded type badges
- Proper spacing

Let me finalize and write the complete code.

I need to make sure all the pieces work together. Let me think through the flow:

1. User opens the page → notes load from localStorage → render notes, stats, filters
2. User clicks "Add Note" → modal opens with empty form
3. User fills in form and submits → note is added to localStorage → re-render everything
4. User clicks "Edit" on a note → modal opens with pre-filled form → user updates → save to localStorage → re-render
5. User clicks "Delete" on a note → confirm dialog → delete from localStorage → re-render
6. User filters by owner/tag/search → filter notes and re-render

OK, let me write the complete code now.

For the filter dropdowns, I need to populate them dynamically based on the notes data. The owner dropdown should have unique owners, and the tag dropdown should have unique tags.

Let me also add a "All" option in the dropdowns for resetting the filter.

Alright, let me write the complete implementation now.

One more consideration: the meeting date should default to today's date when adding a new note.

OK, let me write the full code.

Actually, I realize I should also think about the note card layout. Each card should show:
- Title (large)
- Owner
- Meeting date
- Type badge
- Tags (as small badges)
- Body (truncated maybe)
- Edit and Delete buttons

Let me design the card layout carefully.

OK, I'm going to write the complete code now. Let me be thorough and make sure everything works.

Let me also think about empty state - when there are no notes, show a message.

And for the search, I'll search across title, body, owner, and tags.

Let me write the code now.

Actually, let me think about the modal more carefully for accessibility:
- The modal should have `role="dialog"` and `aria-modal="true"`
- The modal should have `aria-labelledby` pointing to the title
- Focus should be trapped inside the modal
- Pressing Escape should close the modal
- When the modal opens, focus should move to the first input
- When the modal closes, focus should return to the trigger element

I'll implement basic focus trapping and keyboard handling.

OK, let me write the complete code now. I'll aim for quality and completeness.

Let me write the code:

For the form, I need fields for:
- Title (text input, required)
- Owner (text input, required)
- Meeting Date (date input, required)
- Type (select, required) - Action Required, Decision, Reference
- Tags (text input, optional - comma separated)
- Body (textarea, required)

Let me make sure all inputs have proper labels.

OK, writing the code now.

I'm going to write clean, well-structured code that works well.
````

## Assistant

````markdown
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Meeting Notes Board</title>
    <style>
        *,
        *::before,
        *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        :root {
            --color-primary: #1a5fb4;
            --color-primary-hover: #13478a;
            --color-primary-light: #e8f0fe;
            --color-action: #e25c3a;
            --color-decision: #2a7de1;
            --color-reference: #3a8a6f;
            --color-bg: #f4f6f9;
            --color-card: #ffffff;
            --color-text: #1e1e2e;
            --color-text-secondary: #585b70;
            --color-border: #d9dce3;
            --color-shadow: rgba(0, 0, 0, 0.06);
            --radius: 10px;
            --radius-sm: 6px;
            --transition: 0.2s ease;
            --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        html {
            font-size: 16px;
            scroll-behavior: smooth;
        }

        body {
            font-family: var(--font);
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.5;
            padding: 1.25rem;
            min-height: 100vh;
        }

        /* Focus visible */
        :focus-visible {
            outline: 3px solid var(--color-primary);
            outline-offset: 2px;
            border-radius: var(--radius-sm);
        }

        button:focus-visible,
        a:focus-visible,
        input:focus-visible,
        select:focus-visible,
        textarea:focus-visible {
            outline: 3px solid var(--color-primary);
            outline-offset: 2px;
        }

        /* Layout container */
        .app-container {
            max-width: 1100px;
            margin: 0 auto;
        }

        /* Header */
        .app-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
            gap: 0.75rem;
        }

        .app-header h1 {
            font-size: 1.65rem;
            font-weight: 700;
            color: var(--color-text);
            letter-spacing: -0.02em;
        }

        .app-header .header-actions {
            display: flex;
            gap: 0.75rem;
            align-items: center;
            flex-wrap: wrap;
        }

        /* Buttons */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
            font-weight: 600;
            padding: 0.55rem 1.2rem;
            border: none;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: background var(--transition), transform var(--transition);
            text-decoration: none;
            line-height: 1.4;
            background: var(--color-primary);
            color: #fff;
        }

        .btn:hover {
            background: var(--color-primary-hover);
            transform: translateY(-1px);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn--secondary {
            background: transparent;
            color: var(--color-primary);
            border: 2px solid var(--color-primary);
        }

        .btn--secondary:hover {
            background: var(--color-primary-light);
        }

        .btn--danger {
            background: var(--color-action);
            color: #fff;
        }

        .btn--danger:hover {
            background: #c94d2e;
        }

        .btn--small {
            padding: 0.35rem 0.85rem;
            font-size: 0.8rem;
        }

        .btn--ghost {
            background: transparent;
            color: var(--color-text-secondary);
            padding: 0.35rem 0.65rem;
            font-size: 0.8rem;
        }

        .btn--ghost:hover {
            background: var(--color-border);
            color: var(--color-text);
        }

        /* Stats Strip */
        .stats-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem 2rem;
            background: var(--color-card);
            padding: 0.9rem 1.25rem;
            border-radius: var(--radius);
            box-shadow: 0 1px 4px var(--color-shadow);
            margin-bottom: 1.25rem;
            border: 1px solid var(--color-border);
        }

        .stat-item {
            display: flex;
            align-items: baseline;
            gap: 0.4rem;
            font-size: 0.9rem;
        }

        .stat-item .stat-value {
            font-weight: 700;
            font-size: 1.2rem;
            color: var(--color-primary);
        }

        .stat-item .stat-label {
            color: var(--color-text-secondary);
            font-size: 0.85rem;
        }

        .stat-item .stat-value.action {
            color: var(--color-action);
        }

        .stat-item .stat-value.tag {
            color: var(--color-decision);
        }

        /* Filter Bar */
        .filter-bar {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            align-items: center;
            background: var(--color-card);
            padding: 0.85rem 1.25rem;
            border-radius: var(--radius);
            box-shadow: 0 1px 4px var(--color-shadow);
            margin-bottom: 1.25rem;
            border: 1px solid var(--color-border);
        }

        .filter-bar label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--color-text-secondary);
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }

        .filter-bar select,
        .filter-bar input {
            font-size: 0.9rem;
            padding: 0.4rem 0.75rem;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            background: #fff;
            color: var(--color-text);
            min-width: 130px;
            font-family: inherit;
        }

        .filter-bar select:focus,
        .filter-bar input:focus {
            border-color: var(--color-primary);
            box-shadow: 0 0 0 2px var(--color-primary-light);
        }

        .filter-bar .search-wrap {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            flex: 1 1 180px;
            min-width: 140px;
        }

        .filter-bar .search-wrap input {
            flex: 1;
            min-width: 100px;
        }

        .filter-bar .filter-group {
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .filter-bar .clear-btn {
            font-size: 0.8rem;
            padding: 0.35rem 0.75rem;
            background: transparent;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            cursor: pointer;
            color: var(--color-text-secondary);
            transition: background var(--transition);
        }

        .filter-bar .clear-btn:hover {
            background: var(--color-border);
        }

        /* Notes Grid */
        .notes-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1rem;
        }

        @media (min-width: 768px) {
            .notes-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        /* Note Card */
        .note-card {
            background: var(--color-card);
            border-radius: var(--radius);
            box-shadow: 0 2px 8px var(--color-shadow);
            padding: 1.1rem 1.25rem 1rem;
            border: 1px solid var(--color-border);
            transition: box-shadow var(--transition), transform var(--transition);
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            position: relative;
        }

        .note-card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            transform: translateY(-2px);
        }

        .note-card .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.75rem;
        }

        .note-card .card-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--color-text);
            word-break: break-word;
            flex: 1;
        }

        .note-card .card-type {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: 0.2rem 0.65rem;
            border-radius: 20px;
            white-space: nowrap;
            flex-shrink: 0;
            margin-top: 0.1rem;
        }

        .note-card .card-type.action {
            background: #fde8e3;
            color: var(--color-action);
        }

        .note-card .card-type.decision {
            background: #e2edfc;
            color: var(--color-decision);
        }

        .note-card .card-type.reference {
            background: #e2f0ea;
            color: var(--color-reference);
        }

        .note-card .card-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem 1rem;
            font-size: 0.82rem;
            color: var(--color-text-secondary);
        }

        .note-card .card-meta span {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }

        .note-card .card-meta .meta-label {
            font-weight: 600;
            color: var(--color-text);
        }

        .note-card .card-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
        }

        .note-card .card-tags .tag {
            font-size: 0.72rem;
            padding: 0.15rem 0.55rem;
            background: var(--color-primary-light);
            color: var(--color-primary);
            border-radius: 20px;
            font-weight: 500;
        }

        .note-card .card-body {
            font-size: 0.9rem;
            color: var(--color-text);
            line-height: 1.55;
            word-break: break-word;
            padding-top: 0.15rem;
            flex: 1;
        }

        .note-card .card-body p {
            margin: 0;
        }

        .note-card .card-actions {
            display: flex;
            gap: 0.5rem;
            justify-content: flex-end;
            padding-top: 0.4rem;
            border-top: 1px solid var(--color-border);
            margin-top: auto;
        }

        /* Empty state */
        .empty-state {
            grid-column: 1 / -1;
            text-align: center;
            padding: 3rem 1rem;
            color: var(--color-text-secondary);
            background: var(--color-card);
            border-radius: var(--radius);
            border: 1px dashed var(--color-border);
        }

        .empty-state p {
            font-size: 1.1rem;
        }

        /* Modal Overlay */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.45);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 1rem;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.25s ease, visibility 0.25s ease;
        }

        .modal-overlay.open {
            opacity: 1;
            visibility: visible;
        }

        .modal-overlay .modal-content {
            background: var(--color-card);
            border-radius: var(--radius);
            max-width: 560px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            padding: 1.75rem 1.75rem 1.5rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
            transform: translateY(20px);
            transition: transform 0.25s ease;
        }

        .modal-overlay.open .modal-content {
            transform: translateY(0);
        }

        .modal-content .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
        }

        .modal-content .modal-header h2 {
            font-size: 1.35rem;
            font-weight: 700;
        }

        .modal-content .modal-close {
            background: transparent;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.25rem 0.5rem;
            border-radius: var(--radius-sm);
            color: var(--color-text-secondary);
            transition: background var(--transition);
            line-height: 1;
        }

        .modal-content .modal-close:hover {
            background: var(--color-border);
            color: var(--color-text);
        }

        /* Form */
        .note-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .note-form .form-row {
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
        }

        .note-form .form-row label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--color-text);
        }

        .note-form .form-row label .required {
            color: var(--color-action);
            margin-left: 0.15rem;
        }

        .note-form .form-row input,
        .note-form .form-row select,
        .note-form .form-row textarea {
            font-size: 0.95rem;
            padding: 0.55rem 0.75rem;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            font-family: inherit;
            background: #fff;
            color: var(--color-text);
            transition: border-color var(--transition), box-shadow var(--transition);
        }

        .note-form .form-row input:focus,
        .note-form .form-row select:focus,
        .note-form .form-row textarea:focus {
            border-color: var(--color-primary);
            box-shadow: 0 0 0 3px var(--color-primary-light);
            outline: none;
        }

        .note-form .form-row textarea {
            min-height: 100px;
            resize: vertical;
        }

        .note-form .form-row .hint {
            font-size: 0.78rem;
            color: var(--color-text-secondary);
            margin-top: 0.15rem;
        }

        .note-form .form-actions {
            display: flex;
            gap: 0.75rem;
            justify-content: flex-end;
            padding-top: 0.5rem;
            border-top: 1px solid var(--color-border);
            margin-top: 0.25rem;
        }

        /* Responsive tweaks */
        @media (max-width: 480px) {
            body {
                padding: 0.75rem;
            }

            .app-header h1 {
                font-size: 1.3rem;
            }

            .stats-strip {
                gap: 0.5rem 1.25rem;
                padding: 0.7rem 1rem;
            }

            .stat-item {
                font-size: 0.8rem;
            }

            .stat-item .stat-value {
                font-size: 1rem;
            }

            .filter-bar {
                flex-direction: column;
                align-items: stretch;
                padding: 0.75rem 1rem;
            }

            .filter-bar .filter-group {
                flex-wrap: wrap;
            }

            .filter-bar .search-wrap {
                flex: 1 1 auto;
                width: 100%;
            }

            .note-card {
                padding: 0.9rem 1rem 0.85rem;
            }

            .modal-content {
                padding: 1.25rem 1rem 1rem;
            }
        }

        @media (min-width: 481px) and (max-width: 767px) {
            .filter-bar .filter-group {
                flex: 1 1 auto;
            }

            .filter-bar select,
            .filter-bar input {
                min-width: 100px;
            }
        }

        /* Scrollbar styling */
        .modal-content::-webkit-scrollbar {
            width: 6px;
        }

        .modal-content::-webkit-scrollbar-track {
            background: transparent;
        }

        .modal-content::-webkit-scrollbar-thumb {
            background: var(--color-border);
            border-radius: 4px;
        }

        .modal-content::-webkit-scrollbar-thumb:hover {
            background: var(--color-text-secondary);
        }

        /* Note card type border accent */
        .note-card.type-action {
            border-left: 4px solid var(--color-action);
        }

        .note-card.type-decision {
            border-left: 4px solid var(--color-decision);
        }

        .note-card.type-reference {
            border-left: 4px solid var(--color-reference);
        }

        /* Smaller screen stats wrap */
        @media (max-width: 400px) {
            .stats-strip {
                flex-direction: column;
                gap: 0.3rem 0;
            }

            .stat-item {
                justify-content: space-between;
            }
        }
    </style>
</head>
<body>

    <div class="app-container" role="main">

        <!-- Header -->
        <header class="app-header">
            <h1>📋 Meeting Notes Board</h1>
            <div class="header-actions">
                <button class="btn" id="addNoteBtn" type="button">+ Add Note</button>
            </div>
        </header>

        <!-- Stats Strip -->
        <section class="stats-strip" aria-label="Statistics">
            <div class="stat-item">
                <span class="stat-value" id="statTotal">0</span>
                <span class="stat-label">Total notes</span>
            </div>
            <div class="stat-item">
                <span class="stat-value action" id="statAction">0</span>
                <span class="stat-label">Action required</span>
            </div>
            <div class="stat-item">
                <span class="stat-value" id="statOwners">0</span>
                <span class="stat-label">Unique owners</span>
            </div>
            <div class="stat-item">
                <span class="stat-value tag" id="statTopTag">—</span>
                <span class="stat-label">Most common tag</span>
            </div>
        </section>

        <!-- Filter Bar -->
        <section class="filter-bar" aria-label="Filters">
            <div class="filter-group">
                <label for="filterOwner">Owner</label>
                <select id="filterOwner" aria-label="Filter by owner">
                    <option value="">All</option>
                </select>
            </div>

            <div class="filter-group">
                <label for="filterTag">Tag</label>
                <select id="filterTag" aria-label="Filter by tag">
                    <option value="">All</option>
                </select>
            </div>

            <div class="search-wrap">
                <label for="filterSearch">Search</label>
                <input type="text" id="filterSearch" placeholder="Search notes…" aria-label="Search notes by text" />
                <button class="clear-btn" id="clearFiltersBtn" type="button" aria-label="Clear all filters">Clear</button>
            </div>
        </section>

        <!-- Notes Grid -->
        <div class="notes-grid" id="notesGrid" role="list" aria-label="Notes list">
            <!-- Rendered dynamically -->
        </div>

    </div>

    <!-- Modal Overlay -->
    <div class="modal-overlay" id="modalOverlay" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Add Note</h2>
                <button class="modal-close" id="modalCloseBtn" type="button" aria-label="Close dialog">&times;</button>
            </div>

            <form class="note-form" id="noteForm" novalidate>
                <input type="hidden" id="noteId" value="" />

                <div class="form-row">
                    <label for="noteTitle">Title <span class="required">*</span></label>
                    <input type="text" id="noteTitle" required aria-required="true" placeholder="e.g. Sprint review decisions" />
                </div>

                <div class="form-row">
                    <label for="noteOwner">Owner <span class="required">*</span></label>
                    <input type="text" id="noteOwner" required aria-required="true" placeholder="e.g. Alex" />
                </div>

                <div class="form-row">
                    <label for="noteDate">Meeting date <span class="required">*</span></label>
                    <input type="date" id="noteDate" required aria-required="true" />
                </div>

                <div class="form-row">
                    <label for="noteType">Type <span class="required">*</span></label>
                    <select id="noteType" required aria-required="true">
                        <option value="action">Action Required</option>
                        <option value="decision">Decision</option>
                        <option value="reference">Reference</option>
                    </select>
                </div>

                <div class="form-row">
                    <label for="noteTags">Tags</label>
                    <input type="text" id="noteTags" placeholder="e.g. frontend, design, sprint" />
                    <span class="hint">Separate tags with commas.</span>
                </div>

                <div class="form-row">
                    <label for="noteBody">Body <span class="required">*</span></label>
                    <textarea id="noteBody" required aria-required="true" placeholder="What was discussed, decided, or needs action…"></textarea>
                </div>

                <div class="form-actions">
                    <button class="btn btn--secondary" type="button" id="formCancelBtn">Cancel</button>
                    <button class="btn" type="submit" id="formSubmitBtn">Save Note</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        (function() {
            'use strict';

            // ─── State ───────────────────────────────────────────────
            let notes = [];
            let editingId = null;
            let currentFilters = {
                owner: '',
                tag: '',
                search: ''
            };

            // ─── DOM references ──────────────────────────────────────
            const $ = (sel) => document.querySelector(sel);
            const $$ = (sel) => document.querySelectorAll(sel);

            const grid = document.getElementById('notesGrid');
            const modalOverlay = document.getElementById('modalOverlay');
            const modalTitle = document.getElementById('modalTitle');
            const noteForm = document.getElementById('noteForm');
            const noteId = document.getElementById('noteId');
            const noteTitle = document.getElementById('noteTitle');
            const noteOwner = document.getElementById('noteOwner');
            const noteDate = document.getElementById('noteDate');
            const noteType = document.getElementById('noteType');
            const noteTags = document.getElementById('noteTags');
            const noteBody = document.getElementById('noteBody');
            const formSubmitBtn = document.getElementById('formSubmitBtn');
            const formCancelBtn = document.getElementById('formCancelBtn');
            const modalCloseBtn = document.getElementById('modalCloseBtn');
            const addNoteBtn = document.getElementById('addNoteBtn');

            const filterOwner = document.getElementById('filterOwner');
            const filterTag = document.getElementById('filterTag');
            const filterSearch = document.getElementById('filterSearch');
            const clearFiltersBtn = document.getElementById('clearFiltersBtn');

            const statTotal = document.getElementById('statTotal');
            const statAction = document.getElementById('statAction');
            const statOwners = document.getElementById('statOwners');
            const statTopTag = document.getElementById('statTopTag');

            // ─── Storage ─────────────────────────────────────────────
            const STORAGE_KEY = 'meetingNotesBoard';

            function loadNotes() {
                try {
                    const raw = localStorage.getItem(STORAGE_KEY);
                    if (raw) {
                        notes = JSON.parse(raw);
                        if (!Array.isArray(notes)) notes = [];
                    } else {
                        notes = [];
                    }
                } catch (e) {
                    notes = [];
                }
                // ensure each note has an id
                notes = notes.filter(n => n && typeof n === 'object');
                notes.forEach(n => {
                    if (!n.id) n.id = 'n_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6);
                    if (!n.tags) n.tags = '';
                    if (!n.type) n.type = 'reference';
                });
            }

            function saveNotes() {
                try {
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
                } catch (e) {
                    // storage full or unavailable
                }
            }

            // ─── Helpers ─────────────────────────────────────────────
            function getUniqueOwners() {
                const set = new Set();
                notes.forEach(n => { if (n.owner && n.owner.trim()) set.add(n.owner.trim()); });
                return Array.from(set).sort();
            }

            function getAllTags() {
                const map = new Map();
                notes.forEach(n => {
                    if (n.tags) {
                        n.tags.split(',').forEach(t => {
                            const tag = t.trim();
                            if (tag) map.set(tag, (map.get(tag) || 0) + 1);
                        });
                    }
                });
                return Array.from(map.entries()).sort((a, b) => b[1] - a[1]);
            }

            function getMostCommonTag() {
                const tags = getAllTags();
                return tags.length > 0 ? tags[0][0] : null;
            }

            function getActionCount() {
                return notes.filter(n => n.type === 'action').length;
            }

            function getUniqueOwnerCount() {
                return getUniqueOwners().length;
            }

            function getFilteredNotes() {
                const owner = currentFilters.owner.toLowerCase().trim();
                const tag = currentFilters.tag.toLowerCase().trim();
                const search = currentFilters.search.toLowerCase().trim();

                return notes.filter(n => {
                    // owner filter
                    if (owner && (!n.owner || n.owner.toLowerCase().trim() !== owner)) return false;
                    // tag filter
                    if (tag) {
                        const noteTags = (n.tags || '').split(',').map(t => t.trim().toLowerCase());
                        if (!noteTags.includes(tag)) return false;
                    }
                    // search filter
                    if (search) {
                        const haystack = [
                            n.title || '',
                            n.owner || '',
                            n.body || '',
                            n.tags || ''
                        ].join(' ').toLowerCase();
                        if (!haystack.includes(search)) return false;
                    }
                    return true;
                });
            }

            function formatDate(dateStr) {
                if (!dateStr) return '';
                try {
                    const d = new Date(dateStr + 'T00:00:00');
                    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
                } catch (_) { return dateStr; }
            }

            function getTodayStr() {
                const d = new Date();
                const y = d.getFullYear();
                const m = String(d.getMonth() + 1).padStart(2, '0');
                const day = String(d.getDate()).padStart(2, '0');
                return y + '-' + m + '-' + day;
            }

            // ─── Render ──────────────────────────────────────────────
            function renderStats() {
                const total = notes.length;
                const action = getActionCount();
                const owners = getUniqueOwnerCount();
                const topTag = getMostCommonTag();

                statTotal.textContent = total;
                statAction.textContent = action;
                statOwners.textContent = owners;
                statTopTag.textContent = topTag || '—';
            }

            function renderFilterDropdowns() {
                // Preserve current selections
                const selOwner = filterOwner.value;
                const selTag = filterTag.value;

                // Owner dropdown
                const owners = getUniqueOwners();
                filterOwner.innerHTML = '<option value="">All</option>';
                owners.forEach(o => {
                    const opt = document.createElement('option');
                    opt.value = o;
                    opt.textContent = o;
                    if (o === selOwner) opt.selected = true;
                    filterOwner.appendChild(opt);
                });

                // Tag dropdown
                const tags = getAllTags();
                filterTag.innerHTML = '<option value="">All</option>';
                tags.forEach(([tag]) => {
                    const opt = document.createElement('option');
                    opt.value = tag;
                    opt.textContent = tag;
                    if (tag === selTag) opt.selected = true;
                    filterTag.appendChild(opt);
                });
            }

            function renderNotes() {
                const filtered = getFilteredNotes();
                grid.innerHTML = '';

                if (filtered.length === 0) {
                    const empty = document.createElement('div');
                    empty.className = 'empty-state';
                    empty.setAttribute('role', 'listitem');
                    const msg = notes.length === 0 ?
                        'No notes yet. Click “+ Add Note” to get started.' :
                        'No notes match the current filters.';
                    empty.innerHTML = '<p>' + msg + '</p>';
                    grid.appendChild(empty);
                    return;
                }

                filtered.forEach(n => {
                    const card = document.createElement('div');
                    card.className = 'note-card type-' + (n.type || 'reference');
                    card.setAttribute('role', 'listitem');

                    // Type label
                    const typeLabel = {
                        action: 'Action Required',
                        decision: 'Decision',
                        reference: 'Reference'
                    } [n.type] || 'Reference';

                    // Tags
                    const tagsArr = (n.tags || '').split(',').map(t => t.trim()).filter(Boolean);

                    // Build card
                    card.innerHTML =
                        '<div class="card-header">' +
                        '<span class="card-title">' + escapeHtml(n.title || 'Untitled') + '</span>' +
                        '<span class="card-type ' + (n.type || 'reference') + '">' + typeLabel + '</span>' +
                        '</div>' +
                        '<div class="card-meta">' +
                        '<span><span class="meta-label">Owner:</span> ' + escapeHtml(n.owner || '—') + '</span>' +
                        '<span><span class="meta-label">Date:</span> ' + escapeHtml(formatDate(n.meetingDate)) + '</span>' +
                        '</div>' +
                        (tagsArr.length > 0 ?
                            '<div class="card-tags">' + tagsArr.map(t =>
                                '<span class="tag">' + escapeHtml(t) + '</span>'
                            ).join('') + '</div>' :
                            ''
                        ) +
                        '<div class="card-body"><p>' + escapeHtml(n.body || '') + '</p></div>' +
                        '<div class="card-actions">' +
                        '<button class="btn btn--small btn--ghost edit-btn" data-id="' + n.id + '" type="button">Edit</button>' +
                        '<button class="btn btn--small btn--danger delete-btn" data-id="' + n.id + '" type="button">Delete</button>' +
                        '</div>';

                    grid.appendChild(card);
                });

                // Attach event listeners to edit/delete buttons
                grid.querySelectorAll('.edit-btn').forEach(btn => {
                    btn.addEventListener('click', function(e) {
                        const id = this.getAttribute('data-id');
                        openEditModal(id);
                    });
                });

                grid.querySelectorAll('.delete-btn').forEach(btn => {
                    btn.addEventListener('click', function(e) {
                        const id = this.getAttribute('data-id');
                        deleteNote(id);
                    });
                });
            }

            function escapeHtml(str) {
                if (typeof str !== 'string') return '';
                const div = document.createElement('div');
                div.textContent = str;
                return div.innerHTML;
            }

            function renderAll() {
                renderStats();
                renderFilterDropdowns();
                renderNotes();
            }

            // ─── CRUD ────────────────────────────────────────────────
            function addNote(data) {
                const note = {
                    id: 'n_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
                    title: data.title.trim(),
                    owner: data.owner.trim(),
                    meetingDate: data.meetingDate,
                    type: data.type,
                    tags: data.tags.trim(),
                    body: data.body.trim(),
                    createdAt: Date.now()
                };
                notes.push(note);
                saveNotes();
                renderAll();
                return note;
            }

            function updateNote(id, data) {
                const idx = notes.findIndex(n => n.id === id);
                if (idx === -1) return null;
                notes[idx].title = data.title.trim();
                notes[idx].owner = data.owner.trim();
                notes[idx].meetingDate = data.meetingDate;
                notes[idx].type = data.type;
                notes[idx].tags = data.tags.trim();
                notes[idx].body = data.body.trim();
                saveNotes();
                renderAll();
                return notes[idx];
            }

            function deleteNote(id) {
                const note = notes.find(n => n.id === id);
                if (!note) return;
                const confirmMsg = 'Delete "' + (note.title || 'Untitled') + '"? This cannot be undone.';
                if (!window.confirm(confirmMsg)) return;
                notes = notes.filter(n => n.id !== id);
                saveNotes();
                renderAll();
                // If editing this note, close modal
                if (editingId === id) {
                    closeModal();
                }
            }

            // ─── Modal ───────────────────────────────────────────────
            function openAddModal() {
                editingId = null;
                modalTitle.textContent = 'Add Note';
                formSubmitBtn.textContent = 'Save Note';
                noteForm.reset();
                noteId.value = '';
                noteDate.value = getTodayStr();
                noteType.value = 'action';
                modalOverlay.classList.add('open');
                // focus first input
                setTimeout(() => noteTitle.focus(), 80);
                // trap focus
            }

            function openEditModal(id) {
                const note = notes.find(n => n.id === id);
                if (!note) return;
                editingId = id;
                modalTitle.textContent = 'Edit Note';
                formSubmitBtn.textContent = 'Update Note';
                noteId.value = note.id;
                noteTitle.value = note.title || '';
                noteOwner.value = note.owner || '';
                noteDate.value = note.meetingDate || '';
                noteType.value = note.type || 'reference';
                noteTags.value = note.tags || '';
                noteBody.value = note.body || '';
                modalOverlay.classList.add('open');
                setTimeout(() => noteTitle.focus(), 80);
            }

            function closeModal() {
                modalOverlay.classList.remove('open');
                editingId = null;
                noteForm.reset();
                noteId.value = '';
                // return focus to add button
                addNoteBtn.focus();
            }

            function handleFormSubmit(e) {
                e.preventDefault();

                const title = noteTitle.value.trim();
                const owner = noteOwner.value.trim();
                const meetingDate = noteDate.value;
                const type = noteType.value;
                const tags = noteTags.value.trim();
                const body = noteBody.value.trim();

                if (!title || !owner || !meetingDate || !body) {
                    // highlight missing fields
                    if (!title) noteTitle.focus();
                    else if (!owner) noteOwner.focus();
                    else if (!meetingDate) noteDate.focus();
                    else if (!body) noteBody.focus();
                    return;
                }

                const data = { title, owner, meetingDate, type, tags, body };

                const id = noteId.value;
                if (id && notes.some(n => n.id === id)) {
                    updateNote(id, data);
                } else {
                    addNote(data);
                }

                closeModal();
                renderAll();
            }

            // ─── Focus trap ──────────────────────────────────────────
            function trapFocus(e) {
                if (!modalOverlay.classList.contains('open')) return;
                const focusable = modalOverlay.querySelectorAll(
                    'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
                );
                if (focusable.length === 0) return;
                const first = focusable[0];
                const last = focusable[focusable.length - 1];

                if (e.key === 'Tab') {
                    if (e.shiftKey) {
                        if (document.activeElement === first) {
                            e.preventDefault();
                            last.focus();
                        }
                    } else {
                        if (document.activeElement === last) {
                            e.preventDefault();
                            first.focus();
                        }
                    }
                }
                if (e.key === 'Escape') {
                    closeModal();
                }
            }

            // ─── Filters ─────────────────────────────────────────────
            function updateFilters() {
                currentFilters.owner = filterOwner.value;
                currentFilters.tag = filterTag.value;
                currentFilters.search = filterSearch.value;
                renderNotes();
            }

            function clearFilters() {
                filterOwner.value = '';
                filterTag.value = '';
                filterSearch.value = '';
                currentFilters = { owner: '', tag: '', search: '' };
                renderNotes();
            }

            // ─── Init ────────────────────────────────────────────────
            function init() {
                loadNotes();
                renderAll();

                // Set default date for new notes
                noteDate.value = getTodayStr();

                // ── Event listeners ──
                addNoteBtn.addEventListener('click', openAddModal);

                modalCloseBtn.addEventListener('click', closeModal);
                formCancelBtn.addEventListener('click', closeModal);

                // Close on backdrop click
                modalOverlay.addEventListener('click', function(e) {
                    if (e.target === modalOverlay) closeModal();
                });

                noteForm.addEventListener('submit', handleFormSubmit);

                // Keyboard trap
                document.addEventListener('keydown', trapFocus);

                // Filter changes
                filterOwner.addEventListener('change', updateFilters);
                filterTag.addEventListener('change', updateFilters);
                filterSearch.addEventListener('input', updateFilters);
                clearFiltersBtn.addEventListener('click', clearFilters);

                // Expose for debugging
                window.__notes = notes;
            }

            // ─── Start ───────────────────────────────────────────────
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', init);
            } else {
                init();
            }

        })();
    </script>

</body>
</html>
```
````
