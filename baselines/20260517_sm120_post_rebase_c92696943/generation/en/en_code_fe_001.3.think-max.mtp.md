# Generation Transcript

- Case: `en_code_fe_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 85.484493
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 305, "total_tokens": 16065, "completion_tokens": 15760, "prompt_tokens_details": null}`
- Prompt tokens: 305
- Completion tokens: 15760
- Total tokens: 16065

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
Thinking. 1.  **Analyze the Request:**
    *   **Format:** Single file (`index.html`).
    *   **Constraints:** No external libraries, CDNs, images, or build tools. Under 1000 lines of code. Output only the HTML, CSS, and JS.
    *   **Application:** Accessible “meeting notes board” for a small team.
    *   **Functional Requirements:**
        1.  Add note (title, owner, meeting date, tags, body).
        2.  Notes displayed as cards.
        3.  Filter by owner, tag, free-text search.
        4.  Status marking: “Action Required,” “Decision,” “Reference.”
        5.  Edit and delete notes.
        6.  Persist data in `localStorage`.
        7.  Statistics strip: total notes, action-required count, unique owners, most common tag.
        8.  Responsive layout: two-column grid (wide), single column (narrow).
        9.  Basic accessibility: labels for inputs, keyboard-operable controls, visible focus states.
    *   **Output:** Complete `index.html` content. No explanatory text.

    *   **Analysis & Strategy:**

        *   **Structure (HTML):**
            *   `<header>` with title.
            *   `<section>` for statistics.
            *   `<form>` for adding/editing notes.
            *   `<section>` for filters (search, owner, tag).
            *   `<main>` with `<div id="notes-container">` for the card grid.

        *   **Styling (CSS):**
            *   Modern, clean look. Base styles.
            *   Focus states (`:focus-visible` or `:focus`).
            *   Grid with `grid-template-columns: 1fr 1fr` (wide), `1fr` (narrow).
            *   Statistics strip (flexbox or grid).
            *   Cards styling.

        *   **Logic (JavaScript):**
            *   `localStorage` for persistence.
            *   IDs for notes (timestamp + random).
            *   Functions:
                *   `getNotes()`, `saveNotes(notes)`
                *   `renderNotes(notes)`, `renderStats(notes)`
                *   `addNote(event)`, `editNote(id)`, `deleteNote(id)`
                *   `filterNotes()`
                *   `populateFilterDropdowns()`
            *   Event delegation on the container for edit/delete buttons.
            *   Form validation (basic).

        *   **Accessibility:**
            *   `<label>` for every input (search, select, form fields).
            *   `aria-live` region for dynamic updates.
            *   Buttons for edit/delete.
            *   Form submission with Enter key.
            *   Role attributes if necessary (e.g. `role="status"` for stats).

        *   **Constraints Check:**
            *   Total code under 1000 lines. (HTML ~100, CSS ~200, JS ~300 = 600. Very safe.)
            *   No external libraries.

        *   **Implementation Details:**
            *   *Form fields:* Title (text), Owner (text or select, let's do select from existing owners + new owner field). Wait, requirement: "owner" is a tag. Let's provide a text input for owner, and a select filter.
                Let's make Owner a text input.
                "tags" (comma separated? Or a text input). Let's use a text input for tags, comma or space separated. For filtering, show a select dropdown of existing tags.
            *   *Status:* Radio buttons or select. Let's use a `<select>` for the status. Options: "General", "Action Required", "Decision", "Reference".
            *   *Date:* `<input type="date">`.
            *   *Body:* `<textarea>`.

        *   **Data Model:**
            ```javascript
            {
                id: string,
                title: string,
                owner: string,
                date: string, // YYYY-MM-DD
                tags: string, // comma separated
                body: string,
                status: 'general' | 'action-required' | 'decision' | 'reference'
            }
            ```

        *   **Statistics Strip:**
            *   Total notes: `notes.length`
            *   Action Required: `notes.filter(n => n.status === 'action-required').length`
            *   Unique Owners: `new Set(notes.map(n => n.owner).filter(Boolean)).size`
            *   Most common tag: Count tag occurrences from comma-separated strings.

        *   **Filtering:**
            *   Free text search: check title, body, owner, tags.
            *   Owner filter: select dropdown (`<option value="">All Owners</option>`, generated from data).
            *   Tag filter: select dropdown (`<option value="">All Tags</option>`, generated from data).
            *   Status filter: select dropdown (`<option value="">All Statuses</option>`, 'Action Required', 'Decision', 'Reference').

        *   **Editing:**
            *   Clicking "Edit" populates the form with the note data.
            *   Change the submit button text to "Update Note".
            *   Add a hidden `noteId` field.
            *   On submit, if editing, find the note and update it, then reset the form.
            *   Cancel button appears when editing.

        *   **Responsive Layout:**
            *   `@media (min-width: 600px)` or `768px`.
            *   `.notes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }` is even better than strictly two columns, but requirement says "two-column card grid on wide screens, single column on narrow". Let's stick to `grid-template-columns: 1fr 1fr` or `repeat(2, 1fr)`. Wait, `auto-fill` might be better UX. I'll do `grid-template-columns: 1fr 1fr` on wide, `1fr` on narrow.

        *   **Accessibility Details:**
            *   Use semantic HTML (`<header>`, `<nav>`, `<main>`, `<form>`, `<section>`, `<article>` for notes? Maybe, or just `<div>` with `role="article"`? `<article>` is fine).
            *   `<label>` elements properly connected to `<input>` via `for`/`id`.
            *   `aria-label` on buttons without text (e.g., delete button). Let's use text buttons or icons. "Edit", "Delete" text buttons.
            *   `aria-live="polite"` on the notes container or stats.
            *   Focus management after delete/edit (move focus to first card or heading).
            *   `ariaCurrent="page"` or similar? Not needed.

        *   **Code Structure:**
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Meeting Notes Board</title>
                <style>
                    /* ... css ... */
                </style>
            </head>
            <body>
                <header>
                    <h1> Meeting Notes Board</h1>
                </header>

                <section id="stats" role="status" aria-live="polite">
                    <!-- Stats injected by JS -->
                </section>

                <section id="add-edit-note">
                    <h2>Add / Edit Note</h2>
                    <form id="note-form">
                        <input type="hidden" id="note-id">
                        <label for="title">Title</label>
                        <input type="text" id="title" required>

                        <label for="owner">Owner</label>
                        <input type="text" id="owner">

                        <label for="meeting-date">Meeting Date</label>
                        <input type="date" id="meeting-date">

                        <label for="tags">Tags (comma separated)</label>
                        <input type="text" id="tags" placeholder="e.g. design, frontend">

                        <label for="status">Status</label>
                        <select id="status">
                            <option value="general">General</option>
                            <option value="action-required">Action Required</option>
                            <option value="decision">Decision</option>
                            <option value="reference">Reference</option>
                        </select>

                        <label for="body">Body</label>
                        <textarea id="body" rows="4"></textarea>

                        <button type="submit">Add Note</button>
                        <button type="reset" id="cancel-edit" style="display:none;">Cancel</button>
                    </form>
                </section>

                <section id="filters">
                    <h2>Filter Notes</h2>
                    <label for="search">Search</label>
                    <input type="search" id="search" placeholder="Free text search...">

                    <label for="filter-owner">Owner</label>
                    <select id="filter-owner">
                        <option value="">All Owners</option>
                    </select>

                    <label for="filter-tag">Tag</label>
                    <select id="filter-tag">
                        <option value="">All Tags</option>
                    </select>

                    <label for="filter-status">Status</label>
                    <select id="filter-status">
                        <option value="">All Statuses</option>
                        <option value="action-required">Action Required</option>
                        <option value="decision">Decision</option>
                        <option value="reference">Reference</option>
                    </select>
                </section>

                <main id="notes-container" aria-live="polite">
                    <!-- Notes cards injected by JS -->
                </main>

                <script>
                    // ... javascript ...
                </script>
            </body>
            </html>
            ```

        *   **Refining the JS:**
            *   `getNotes()`: `JSON.parse(localStorage.getItem('meetingNotes')) || []`
            *   `saveNotes(notes)`: `localStorage.setItem('meetingNotes', JSON.stringify(notes))`
            *   `render()`: Calls `renderStats()`, `renderNotes()`, `populateFilterDropdowns()`.
            *   `renderNotes(notesToRender)`:
                If no argument, use `getActiveFilteredNotes()`.
                `notesContainer.innerHTML = ''`.
                Loop over notes, create card `div` (`.note-card`), inner HTML with title, owner, date, tags, body, status badge, edit/delete buttons.
            *   `renderStats(notes)`:
                Use `notes` parameter or `getNotes()`.
                `total = notes.length`
                `actionRequired = notes.filter(n => n.status === 'action-required').length`
                `uniqueOwners = new Set(notes.map(n => n.owner).filter(Boolean)).size`
                `mostCommonTag`: Flatten all tags, count occurrences, find max.
                Update `#stats` inner HTML.
            *   `handleFormSubmit(event)`:
                Prevent default.
                Get values from form.
                `noteId` hidden field value. If empty, create new note. If exists, update existing note.
                Push ID (if new): `Date.now().toString(36) + Math.random().toString(36).substr(2, 5)`.
                Reset form.
                Call `render()`.
            *   `handleEdit(event)`:
                Find parent `.note-card`, get `data-id`.
                Find note in array.
                Populate form fields.
                Show cancel button.
            *   `handleDelete(event)`:
                Find parent `.note-card`, get `data-id`.
                Filter out note from array.
                Call `render()`.
            *   `getActiveFilteredNotes()`:
                Get `search`, `owner`, `tag`, `status` from filters.
                Filter notes based on these.
            *   Event listeners:
                Form submit.
                Filter inputs change / keyup (debounced or immediate for state).
                Container click (delegation for edit/delete buttons).

        *   **CSS Details:**
            *   Body: `font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;`
            *   Stats Strip: `display: flex; flex-wrap: wrap; gap: 16px; background: #f0f4f8; padding: 16px; border-radius: 8px;`
            *   Cards: `border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);`
            *   Status badges: `display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; text-transform: uppercase;`
            *   Grid: `.notes-grid { display: grid; grid-template-columns: 1fr; gap: 16px; }`
                `@media (min-width: 768px) { .notes-grid { grid-template-columns: 1fr 1fr; } }`
            *   Focus: `*:focus-visible { outline: 2px solid #3182ce; outline-offset: 2px; }`

        *   **Let's write the code.**

        *   **HTML structure check:**
            `<form>` with all inputs, hidden id, submit/cancel.
            `<section id="stats">`
            `<section id="filters">`
            `<main id="notes-container">`

        *   **CSS check:**
            Responsive grid.
            Focus styles.
            Stats strip.
            Card layout.
            Basic styling.

        *   **JS check:**
            Data management.
            Rendering.
            Form handling (Add/Edit).
            Deletion.
            Filtering.
            Statistics.
            Dropdown population (owners, tags).
            `aria-live` regions.

        *   **Edge Cases:**
            *   Empty state: "No notes yet. Add your first meeting note!"
            *   Most common tag when no tags: None.
            *   XSS: Use `textContent` instead of `innerHTML` where possible, or properly escape. `innerHTML` is generally fine for `template literals` if the data doesn't contain `<script>`. Let's use `textContent` for user-controlled values or escape them. Let's use `textContent` for body, title, owner, tags. Wait, rendering HTML elements nicely for the tag badges is easier with `innerHTML` controlled by the program. Title, Body, Owner are user strings. Let's create elements and set `textContent` for those, or sanitize. Since it's a local app, `innerHTML` is widely accepted, but let's use a simple escape function `escapeHtml(str)` to be safe.
            *   Edit mode: Changing the submit text, showing cancel.
            *   Reset form completely on cancel/submit.

        *   **Let's draft the code meticulously.**

        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Meeting Notes Board</title>
            <style>
                *, *::before, *::after { box-sizing: border-box; }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    margin: 0;
                    padding: 16px;
                    background-color: #f7fafc;
                    color: #2d3748;
                    line-height: 1.5;
                }
                header { margin-bottom: 24px; }
                h1 { margin: 0; font-size: 1.8rem; color: #1a202c; }
                h2 { font-size: 1.2rem; margin: 0 0 12px 0; color: #2d3748; }

                /* Stats Strip */
                #stats {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 16px;
                    background: #edf2f7;
                    padding: 16px 24px;
                    border-radius: 8px;
                    margin-bottom: 24px;
                }
                .stat-item {
                    flex: 1 1 150px;
                    padding: 8px;
                    text-align: center;
                    background: white;
                    border-radius: 6px;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                }
                .stat-value { font-size: 1.5rem; font-weight: 700; display: block; }
                .stat-label { font-size: 0.8rem; color: #718096; text-transform: uppercase; letter-spacing: 0.05em; }

                /* Form Section */
                #add-edit-note {
                    background: white;
                    padding: 24px;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    margin-bottom: 24px;
                }
                #note-form {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 12px;
                }
                #note-form .full-width {
                    grid-column: 1 / -1;
                }
                #note-form label {
                    display: block;
                    font-weight: 500;
                    margin-bottom: 4px;
                    font-size: 0.9rem;
                }
                #note-form input,
                #note-form select,
                #note-form textarea {
                    width: 100%;
                    padding: 8px 12px;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    font-size: 0.95rem;
                    background: #fdfdfd;
                }
                #note-form input:focus,
                #note-form select:focus,
                #note-form textarea:focus {
                    border-color: #63b3ed;
                    outline: none;
                    box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.5);
                }
                .form-actions {
                    grid-column: 1 / -1;
                    display: flex;
                    gap: 8px;
                }
                button, .btn {
                    padding: 10px 20px;
                    border: 1px solid transparent;
                    border-radius: 6px;
                    font-size: 0.95rem;
                    font-weight: 500;
                    cursor: pointer;
                    background: #3182ce;
                    color: white;
                    transition: background 0.2s;
                }
                button:hover, .btn:hover { background: #2b6cb0; }
                button:focus-visible, .btn:focus-visible {
                    outline: 2px solid #3182ce;
                    outline-offset: 2px;
                }
                button.secondary {
                    background: #a0aec0;
                }
                button.secondary:hover {
                    background: #718096;
                }
                button.danger {
                    background: #e53e3e;
                }
                button.danger:hover {
                    background: #c53030;
                }
                #cancel-edit {
                    display: none;
                }

                /* Filters Section */
                #filters {
                    background: white;
                    padding: 16px 24px;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    margin-bottom: 24px;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 16px;
                    align-items: flex-end;
                }
                #filters h2 {
                    flex: 0 0 100%;
                    margin-bottom: 4px;
                }
                .filter-group {
                    flex: 1 1 180px;
                }
                .filter-group label {
                    display: block;
                    font-weight: 500;
                    font-size: 0.85rem;
                    margin-bottom: 4px;
                }
                .filter-group input,
                .filter-group select {
                    width: 100%;
                    padding: 8px 12px;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    font-size: 0.9rem;
                }

                /* Notes Grid */
                #notes-container {
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: 16px;
                }
                @media (min-width: 768px) {
                    #notes-container {
                        grid-template-columns: 1fr 1fr;
                    }
                }
                @media (min-width: 1200px) {
                    #notes-container {
                        grid-template-columns: 1fr 1fr 1fr;
                    }
                }

                /* Note Card */
                .note-card {
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
                    display: flex;
                    flex-direction: column;
                }
                .note-card h3 {
                    margin: 0 0 8px 0;
                    font-size: 1.15rem;
                }
                .note-meta {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    font-size: 0.85rem;
                    color: #718096;
                    margin-bottom: 12px;
                }
                .note-body {
                    flex-grow: 1;
                    margin-bottom: 16px;
                    white-space: pre-wrap;
                }
                .note-tags {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 6px;
                    margin-bottom: 12px;
                }
                .tag-badge {
                    background: #e9d8fd;
                    color: #553c9a;
                    padding: 2px 10px;
                    border-radius: 999px;
                    font-size: 0.8rem;
                }
                .status-badge {
                    display: inline-block;
                    padding: 3px 12px;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                .status-action-required { background: #fed7d7; color: #9b2c2c; }
                .status-decision { background: #c6f6d5; color: #276749; }
                .status-reference { background: #bee3f8; color: #2a4365; }
                .status-general { background: #e2e8f0; color: #4a5568; }

                .note-actions {
                    display: flex;
                    gap: 8px;
                    margin-top: auto;
                    padding-top: 12px;
                    border-top: 1px solid #edf2f7;
                }
                .note-actions button {
                    flex: 1;
                    padding: 8px;
                    font-size: 0.85rem;
                }

                .empty-state {
                    grid-column: 1 / -1;
                    text-align: center;
                    padding: 60px 20px;
                    color: #a0aec0;
                }

                /* Visually hidden (for screen readers) */
                .sr-only {
                    position: absolute;
                    width: 1px;
                    height: 1px;
                    padding: 0;
                    margin: -1px;
                    overflow: hidden;
                    clip: rect(0, 0, 0, 0);
                    white-space: nowrap;
                    border-width: 0;
                }
            </style>
        </head>
        <body>

        <header>
            <h1> Meeting Notes Board</h1>
        </header>

        <!-- Stats -->
        <section id="stats" aria-label="Statistics">
            <!-- JS injects stats here -->
        </section>

        <!-- Add / Edit Form -->
        <section id="add-edit-note" aria-label="Add or Edit Note">
            <h2>Add / Edit Note</h2>
            <form id="note-form" novalidate>
                <input type="hidden" id="note-id" value="">
                <div>
                    <label for="title">Title <span aria-hidden="true">*</span></label>
                    <input type="text" id="title" required placeholder="Meeting title">
                </div>
                <div>
                    <label for="owner">Owner</label>
                    <input type="text" id="owner" placeholder="Who owns this?">
                </div>
                <div>
                    <label for="meeting-date">Meeting Date</label>
                    <input type="date" id="meeting-date">
                </div>
                <div>
                    <label for="tags">Tags (comma separated)</label>
                    <input type="text" id="tags" placeholder="e.g. design, sprint">
                </div>
                <div>
                    <label for="status">Status</label>
                    <select id="status">
                        <option value="general">General</option>
                        <option value="action-required">Action Required</option>
                        <option value="decision">Decision</option>
                        <option value="reference">Reference</option>
                    </select>
                </div>
                <div class="full-width">
                    <label for="body">Body</label>
                    <textarea id="body" rows="4" placeholder="Notes from the meeting..."></textarea>
                </div>
                <div class="form-actions">
                    <button type="submit">Add Note</button>
                    <button type="button" id="cancel-edit" class="secondary">Cancel</button>
                </div>
            </form>
        </section>

        <!-- Filters -->
        <section id="filters" aria-label="Filter Notes">
            <h2>Filter Notes</h2>
            <div class="filter-group">
                <label for="search">Search</label>
                <input type="search" id="search" placeholder="Search notes...">
            </div>
            <div class="filter-group">
                <label for="filter-owner">Owner</label>
                <select id="filter-owner">
                    <option value="">All Owners</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="filter-tag">Tag</label>
                <select id="filter-tag">
                    <option value="">All Tags</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="filter-status">Status</label>
                <select id="filter-status">
                    <option value="">All Statuses</option>
                    <option value="action-required">Action Required</option>
                    <option value="decision">Decision</option>
                    <option value="reference">Reference</option>
                </select>
            </div>
        </section>

        <!-- Notes Display -->
        <main id="notes-container" aria-label="Meeting Notes">
            <!-- JS injects note cards here -->
        </main>

        <script>
            (function() {
                'use strict';

                // --- Data Management ---
                const STORAGE_KEY = 'meetingNotesBoard';

                function getNotes() {
                    try {
                        const data = localStorage.getItem(STORAGE_KEY);
                        return data ? JSON.parse(data) : [];
                    } catch (e) {
                        return [];
                    }
                }

                function saveNotes(notes) {
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
                }

                function generateId() {
                    return Date.now().toString(36) + Math.random().toString(36).substring(2, 7);
                }

                // --- HTML Escaping ---
                function escapeHtml(str) {
                    if (typeof str !== 'string') return '';
                    const div = document.createElement('div');
                    div.textContent = str;
                    return div.innerHTML;
                }

                // --- Rendering ---
                function renderStats(notes) {
                    const statsSection = document.getElementById('stats');
                    const total = notes.length;
                    const actionRequiredCount = notes.filter(n => n.status === 'action-required').length;
                    const uniqueOwners = new Set(notes.map(n => n.owner ? n.owner.trim().toLowerCase() : '').filter(Boolean)).size;

                    // Most common tag
                    const tagCounts = {};
                    notes.forEach(n => {
                        if (n.tags) {
                            n.tags.split(',').forEach(tag => {
                                const trimmedTag = tag.trim().toLowerCase();
                                if (trimmedTag) {
                                    tagCounts[trimmedTag] = (tagCounts[trimmedTag] || 0) + 1;
                                }
                            });
                        }
                    });
                    let mostCommonTag = 'N/A';
                    let maxCount = 0;
                    for (const tag in tagCounts) {
                        if (tagCounts[tag] > maxCount) {
                            maxCount = tagCounts[tag];
                            mostCommonTag = tag;
                        }
                    }

                    statsSection.innerHTML = `
                        <div class="stat-item">
                            <span class="stat-value">${total}</span>
                            <span class="stat-label">Total Notes</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${actionRequiredCount}</span>
                            <span class="stat-label">Action Required</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${uniqueOwners}</span>
                            <span class="stat-label">Unique Owners</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${escapeHtml(mostCommonTag)}</span>
                            <span class="stat-label">Most Common Tag</span>
                        </div>
                    `;
                }

                function renderNotes(notes) {
                    const container = document.getElementById('notes-container');

                    if (notes.length === 0) {
                        container.innerHTML = '<div class="empty-state"><p>No notes found. Create your first note!</p></div>';
                        return;
                    }

                    let html = '';
                    notes.forEach(note => {
                        const statusClass = `status-badge status-${note.status || 'general'}`;
                        const statusLabel = (note.status || 'general').replace('-', ' ').replace(/\b\w/g, char => char.toUpperCase());

                        // Tags
                        let tagsHtml = '';
                        if (note.tags) {
                            const tagsList = note.tags.split(',').map(t => t.trim()).filter(Boolean);
                            tagsList.forEach(tag => {
                                tagsHtml += `<span class="tag-badge">${escapeHtml(tag)}</span>`;
                            });
                        }

                        html += `
                            <div class="note-card" data-id="${escapeHtml(note.id)}">
                                <h3>${escapeHtml(note.title) || 'Untitled'}</h3>
                                <div class="note-meta">
                                    <span>${escapeHtml(note.owner) || 'No owner'}</span>
                                    <span>${note.date || ''}</span>
                                    <span class="${statusClass}">${statusLabel}</span>
                                </div>
                                <div class="note-body">${escapeHtml(note.body) || ''}</div>
                                ${tagsHtml ? `<div class="note-tags">${tagsHtml}</div>` : ''}
                                <div class="note-actions">
                                    <button class="edit-note" type="button">Edit</button>
                                    <button class="delete-note danger" type="button">Delete</button>
                                </div>
                            </div>
                        `;
                    });

                    container.innerHTML = html;
                }

                function populateFilterDropdowns(notes) {
                    const ownerFilter = document.getElementById('filter-owner');
                    const tagFilter = document.getElementById('filter-tag');

                    const currentOwner = ownerFilter.value;
                    const currentTag = tagFilter.value;

                    // Owners
                    const owners = new Set();
                    notes.forEach(n => { if (n.owner) owners.add(n.owner.trim()); });
                    const sortedOwners = Array.from(owners).sort();

                    ownerFilter.innerHTML = '<option value="">All Owners</option>';
                    sortedOwners.forEach(owner => {
                        const opt = document.createElement('option');
                        opt.value = owner;
                        opt.textContent = owner;
                        if (owner === currentOwner) opt.selected = true;
                        ownerFilter.appendChild(opt);
                    });

                    // Tags
                    const tags = new Set();
                    notes.forEach(n => {
                        if (n.tags) {
                            n.tags.split(',').forEach(tag => {
                                const trimmedTag = tag.trim();
                                if (trimmedTag) tags.add(trimmedTag);
                            });
                        }
                    });
                    const sortedTags = Array.from(tags).sort();

                    tagFilter.innerHTML = '<option value="">All Tags</option>';
                    sortedTags.forEach(tag => {
                        const opt = document.createElement('option');
                        opt.value = tag;
                        opt.textContent = tag;
                        if (tag === currentTag) opt.selected = true;
                        tagFilter.appendChild(opt);
                    });
                }

                function render() {
                    const notes = getNotes();
                    const filteredNotes = getFilteredNotes(notes);
                    renderStats(notes);
                    renderNotes(filteredNotes);
                    populateFilterDropdowns(notes);
                }

                // --- Filtering ---
                function getFilteredNotes(notes) {
                    const search = document.getElementById('search').value.toLowerCase().trim();
                    const owner = document.getElementById('filter-owner').value;
                    const tag = document.getElementById('filter-tag').value;
                    const status = document.getElementById('filter-status').value;

                    return notes.filter(note => {
                        // Free text search
                        if (search) {
                            const textToSearch = `${note.title} ${note.owner} ${note.tags} ${note.body}`.toLowerCase();
                            if (!textToSearch.includes(search)) return false;
                        }

                        // Owner filter
                        if (owner && note.owner?.trim() !== owner) return false;

                        // Tag filter
                        if (tag) {
                            const noteTags = (note.tags || '').split(',').map(t => t.trim()).filter(Boolean);
                            if (!noteTags.includes(tag)) return false;
                        }

                        // Status filter
                        if (status && note.status !== status) return false;

                        return true;
                    });
                }

                // --- Form Handling ---
                function populateForm(note) {
                    document.getElementById('note-id').value = note.id || '';
                    document.getElementById('title').value = note.title || '';
                    document.getElementById('owner').value = note.owner || '';
                    document.getElementById('meeting-date').value = note.date || '';
                    document.getElementById('tags').value = note.tags || '';
                    document.getElementById('status').value = note.status || 'general';
                    document.getElementById('body').value = note.body || '';

                    const submitBtn = document.querySelector('#note-form button[type="submit"]');
                    submitBtn.textContent = note.id ? 'Update Note' : 'Add Note';

                    const cancelBtn = document.getElementById('cancel-edit');
                    cancelBtn.style.display = note.id ? 'inline-block' : 'none';
                }

                function resetForm() {
                    document.getElementById('note-form').reset();
                    document.getElementById('note-id').value = '';
                    const submitBtn = document.querySelector('#note-form button[type="submit"]');
                    submitBtn.textContent = 'Add Note';
                    document.getElementById('cancel-edit').style.display = 'none';
                }

                function handleFormSubmit(event) {
                    event.preventDefault();

                    const noteId = document.getElementById('note-id').value;
                    const title = document.getElementById('title').value.trim();
                    const owner = document.getElementById('owner').value.trim();
                    const date = document.getElementById('meeting-date').value;
                    const tags = document.getElementById('tags').value.trim();
                    const status = document.getElementById('status').value;
                    const body = document.getElementById('body').value.trim();

                    if (!title) {
                        alert('Title is required.');
                        document.getElementById('title').focus();
                        return;
                    }

                    const notes = getNotes();

                    if (noteId) {
                        // Edit mode
                        const index = notes.findIndex(n => n.id === noteId);
                        if (index !== -1) {
                            notes[index] = { ...notes[index], title, owner, date, tags, status, body };
                        }
                    } else {
                        // Add mode
                        const newNote = {
                            id: generateId(),
                            title,
                            owner,
                            date,
                            tags,
                            status,
                            body
                        };
                        notes.unshift(newNote); // Add to beginning
                    }

                    saveNotes(notes);
                    resetForm();
                    render();
                    // Announce to screen readers
                    const container = document.getElementById('notes-container');
                    container.querySelector('.note-card')?.focus();
                }

                function handleEdit(event) {
                    const card = event.target.closest('.note-card');
                    if (!card) return;
                    const noteId = card.dataset.id;
                    const notes = getNotes();
                    const note = notes.find(n => n.id === noteId);
                    if (note) {
                        populateForm(note);
                        document.getElementById('title').focus();
                    }
                }

                function handleDelete(event) {
                    if (!confirm('Are you sure you want to delete this note?')) return;
                    const card = event.target.closest('.note-card');
                    if (!card) return;
                    const noteId = card.dataset.id;
                    let notes = getNotes();
                    notes = notes.filter(n => n.id !== noteId);
                    saveNotes(notes);
                    render();
                }

                // --- Event Listeners ---
                function init() {
                    // Form submit
                    document.getElementById('note-form').addEventListener('submit', handleFormSubmit);

                    // Cancel edit
                    document.getElementById('cancel-edit').addEventListener('click', resetForm);

                    // Event delegation for edit/delete buttons
                    document.getElementById('notes-container').addEventListener('click', function(event) {
                        if (event.target.classList.contains('edit-note')) {
                            handleEdit(event);
                        } else if (event.target.classList.contains('delete-note')) {
                            handleDelete(event);
                        }
                    });

                    // Filter listeners
                    const filterInputs = ['search', 'filter-owner', 'filter-tag', 'filter-status'];
                    filterInputs.forEach(id => {
                        const el = document.getElementById(id);
                        el.addEventListener('input', function() {
                            render();
                        });
                        el.addEventListener('change', function() {
                            render();
                        });
                    });

                    // Initial render
                    render();

                    // Handle empty state focus management for screen readers - already handled by aria-live on container
                }

                // Start app
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

        Wait, `getFilteredNotes` is called inside `render()` which doesn't have a direct reference. Let's trace.

        ```javascript
        function render() {
            const notes = getNotes();
            const filteredNotes = getFilteredNotes(notes);
            renderStats(notes);
            renderNotes(filteredNotes);
            populateFilterDropdowns(notes);
        }
        ```
        Looks correct! `getFilteredNotes` is defined above.

        Wait, the `if (noteId)` block for edit:
        ```javascript
        if (index !== -1) {
            notes[index] = { ...notes[index], title, owner, date, tags, status, body };
        }
        ```
        Good, it spreads the existing note to preserve anything else (like id, date created if we had one). It's a clean update.

        Now check the keyword focus. After deleting a note, `render()` is called. If the focus is lost, it's okay, it will just go top. The `aria-live` region on the container will announce the new set of notes.

        Let's review the CSS grid.
        Wide screens: 2 columns (at 768px).
        Narrow screens: 1 column.
        Let's add an extra breakpoint.

        ```css
        #notes-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
        }
        @media (min-width: 768px) {
            #notes-container {
                grid-template-columns: 1fr 1fr;
            }
        }
        ```

        Are the labels properly connected?
        Yes, `<label for="title">Title</label>` matches `<input id="title">`.

        Are buttons keyboard operable?
        Yes, `<button>`, `<input>`, `<select>` are all natively keyboard accessible.

        Focus states:
        `:focus-visible` is used on buttons, and `input:focus` has `box-shadow` and `border-color`.

        Does the code handle the "meeting date" formatting?
        Yes, `<input type="date">` handles it natively.

        "most common tag" logic:
        It splits tags by comma, trims them, lowercases them, and counts. It shows the lowercase version. Maybe it should show the original casing? Ex: "Design", "design". The task says "most common tag". Using lowercase to deduplicate. "Design" and "design" will be grouped. "mostCommonTag" must be displayed. I will preserve the first occurrence's casing or the most common casing. Since it's just a local app, lowercasing the output is fine, but let's preserve the original casing of the most frequently occurring tag string. Let's adjust the logic slightly to keep track of the original casing.

        ```javascript
        const tagCounts = {};
        tagsOriginal = {}; // for casing
        notes.forEach(n => {
            if (n.tags) {
                n.tags.split(',').forEach(tag => {
                    const trimmedTag = tag.trim();
                    const trimmedLower = trimmedTag.toLowerCase();
                    if (trimmedLower) {
                        tagCounts[trimmedLower] = (tagCounts[trimmedLower] || 0) + 1;
                        // Store the original casing if not already stored
                        if (!tagsOriginal[trimmedLower]) {
                            tagsOriginal[trimmedLower] = trimmedTag;
                        }
                    }
                });
            }
        });
        let mostCommonTag = 'N/A';
        let maxCount = 0;
        for (const tagLower in tagCounts) {
            if (tagCounts[tagLower] > maxCount) {
                maxCount = tagCounts[tagLower];
                mostCommonTag = tagsOriginal[tagLower] || tagLower;
            }
        }
        ```
        This is better UX.

        Let's also make the "Action Required" count check the status correctly.
        Yes, `n.status === 'action-required'`.

        Unique owners:
        `n.owner ? n.owner.trim().toLowerCase() : ''`.
        This correctly deduplicates.

        Everything looks solid.

        Let's double check the requirement: "Users can add a note with title, owner, meeting date, tags, and body."
        Yes.

        "Notes appear as cards and can be filtered by owner, tag, and free-text search."
        Yes.

        "A note can be marked as Action Required, Decision, or Reference."
        Yes, status field.

        "Users can edit and delete notes."
        Yes.

        "Persist all data in localStorage."
        Yes.

        "Provide a compact statistics strip..."
        Yes.

        "Responsive layout: two-column card grid on wide screens..."
        Yes, 768px breakpoint.

        "Basic accessibility..."
        Yes, labels, keyboard, focus states.

        "Total code under 1,000 lines."
        Currently the CSS, HTML, and JS combined. Let's count.

        HTML: ~80 lines
        CSS: ~120 lines
        JS: ~140 lines
        Total: ~340 lines. Well within limit.

        "Output only the complete index.html content, including HTML, CSS, and JavaScript. Do not include explanatory text."

        Wait, I can remove the `div` for escaping, just use `replace` regex.
        `str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')`

        Let's refine the `escapeHtml` function to be lighter.

        ```javascript
        function escapeHtml(str) {
            if (typeof str !== 'string') return '';
            return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }
        ```

        Looks good.

        What about the `aria-live` region? The main container has `aria-live="polite"`. The stats section has `aria-live="polite"`.

        Let's check the filter inputs. "Change" and "input" events are both added. On a `<select>`, `input` is also supported in modern browsers for parent change, but `change` is the standard. Binding both ensures compatibility without hurting performance.

        The `search` field: `input` event is excellent for real-time search.

        Let's do a final scan.

        - No external libraries, CDNs, images, or build tools.
        - Accessible.
        - Meeting notes board.

        Let's refine the `populateForm` / `resetForm`.
        When cancel is clicked, `resetForm()` is called.
        `resetForm()` hides the cancel button, changes text to "Add Note".

        "Edit Note" focus management:
        When edit is clicked, the title field gets focus.
        `document.getElementById('title').focus();`
        This is great for accessibility.

        "Delete Note" confirmation:
        `if (!confirm('...')) return;`

        What if the user hasn't filled in the form and clicks edit? The form is populated.
        What if the user edits, then cancels? The form is reset.

        The `render` function is called from many places. It's efficient enough for this small app.

        Are we missing anything from the tags?
        "most common tag." With an empty board, `mostCommonTag` will be `'N/A'`.

        Let's add a `role` to the stats items, but it's fine.

        Should the notes be in `<article>` elements? Yes, `<article class="note-card">` would be more semantic. Let's change `div class="note-card"` to `article class="note-card"` in the `renderNotes` function.

        Everything looks ready. I will now produce the final output exactly as requested.

        Final check on line count: well under 1,000.

        Let's write the final block of code.
        I need to make sure the `script` tag is properly closed and there are no trailing strings.

        One last thing: the `novalidate` attribute on the form. This prevents the browser's built-in HTML5 validation tooltip from interfering with the custom validation (`alert`). It's a good practice for accessible custom forms. Actually, `novalidate` removes the browser validation completely. Let's keep it because I have an `alert` for the title.

        Alert is generally not great for a11y, but for a small team tool, it's acceptable. We could rely on the `required` attribute, but `novalidate` overrides it. Let's remove `novalidate` and just rely on HTML5 validation + our own check. If I keep `novalidate`, I have to do all validation in JS. Let's keep `novalidate` and use the JS alert so the developer experience is tighter.

        "Add a hidden noteId field." Done.

        Let's craft the final HTML.
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
        *, *::before, *::after { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 16px;
            background-color: #f7fafc;
            color: #2d3748;
            line-height: 1.5;
        }
        header { margin-bottom: 24px; }
        h1 { margin: 0; font-size: 1.8rem; color: #1a202c; }
        h2 { font-size: 1.2rem; margin: 0 0 12px 0; color: #2d3748; }

        /* Stats Strip */
        #stats {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            background: #edf2f7;
            padding: 16px 24px;
            border-radius: 8px;
            margin-bottom: 24px;
        }
        .stat-item {
            flex: 1 1 150px;
            padding: 8px;
            text-align: center;
            background: white;
            border-radius: 6px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .stat-value { font-size: 1.5rem; font-weight: 700; display: block; }
        .stat-label { font-size: 0.8rem; color: #718096; text-transform: uppercase; letter-spacing: 0.05em; }

        /* Form Section */
        #add-edit-note {
            background: white;
            padding: 24px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 24px;
        }
        #note-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        #note-form .full-width {
            grid-column: 1 / -1;
        }
        #note-form label {
            display: block;
            font-weight: 500;
            margin-bottom: 4px;
            font-size: 0.9rem;
        }
        #note-form input,
        #note-form select,
        #note-form textarea {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 0.95rem;
            background: #fdfdfd;
        }
        #note-form input:focus,
        #note-form select:focus,
        #note-form textarea:focus {
            border-color: #63b3ed;
            outline: none;
            box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.5);
        }
        .form-actions {
            grid-column: 1 / -1;
            display: flex;
            gap: 8px;
        }
        button, .btn {
            padding: 10px 20px;
            border: 1px solid transparent;
            border-radius: 6px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            background: #3182ce;
            color: white;
            transition: background 0.2s;
        }
        button:hover, .btn:hover { background: #2b6cb0; }
        button:focus-visible, .btn:focus-visible {
            outline: 2px solid #3182ce;
            outline-offset: 2px;
        }
        button.secondary {
            background: #a0aec0;
        }
        button.secondary:hover {
            background: #718096;
        }
        button.danger {
            background: #e53e3e;
        }
        button.danger:hover {
            background: #c53030;
        }
        #cancel-edit {
            display: none;
        }

        /* Filters Section */
        #filters {
            background: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 24px;
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            align-items: flex-end;
        }
        #filters h2 {
            flex: 0 0 100%;
            margin-bottom: 4px;
        }
        .filter-group {
            flex: 1 1 180px;
        }
        .filter-group label {
            display: block;
            font-weight: 500;
            font-size: 0.85rem;
            margin-bottom: 4px;
        }
        .filter-group input,
        .filter-group select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 0.9rem;
        }

        /* Notes Grid */
        #notes-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
        }
        @media (min-width: 768px) {
            #notes-container {
                grid-template-columns: 1fr 1fr;
            }
        }

        /* Note Card */
        .note-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            display: flex;
            flex-direction: column;
        }
        .note-card h3 {
            margin: 0 0 8px 0;
            font-size: 1.15rem;
        }
        .note-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 0.85rem;
            color: #718096;
            margin-bottom: 12px;
        }
        .note-body {
            flex-grow: 1;
            margin-bottom: 16px;
            white-space: pre-wrap;
        }
        .note-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 12px;
        }
        .tag-badge {
            background: #e9d8fd;
            color: #553c9a;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 0.8rem;
        }
        .status-badge {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .status-action-required { background: #fed7d7; color: #9b2c2c; }
        .status-decision { background: #c6f6d5; color: #276749; }
        .status-reference { background: #bee3f8; color: #2a4365; }
        .status-general { background: #e2e8f0; color: #4a5568; }

        .note-actions {
            display: flex;
            gap: 8px;
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid #edf2f7;
        }
        .note-actions button {
            flex: 1;
            padding: 8px;
            font-size: 0.85rem;
        }

        .empty-state {
            grid-column: 1 / -1;
            text-align: center;
            padding: 60px 20px;
            color: #a0aec0;
        }

        /* Screen reader only */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border-width: 0;
        }
    </style>
</head>
<body>

<header>
    <h1> Meeting Notes Board</h1>
</header>

<!-- STATS -->
<section id="stats" aria-label="Statistics" role="status">
    <!-- Stats injected by JS -->
</section>

<!-- ADD / EDIT FORM -->
<section id="add-edit-note" aria-label="Add or edit note">
    <h2>Add / Edit Note</h2>
    <form id="note-form" novalidate>
        <input type="hidden" id="note-id" value="">
        <div>
            <label for="title">Title <span aria-hidden="true">*</span></label>
            <input type="text" id="title" required placeholder="Meeting title">
        </div>
        <div>
            <label for="owner">Owner</label>
            <input type="text" id="owner" placeholder="Who owns this?">
        </div>
        <div>
            <label for="meeting-date">Meeting Date</label>
            <input type="date" id="meeting-date">
        </div>
        <div>
            <label for="tags">Tags (comma separated)</label>
            <input type="text" id="tags" placeholder="e.g. design, sprint">
        </div>
        <div>
            <label for="status">Status</label>
            <select id="status">
                <option value="general">General</option>
                <option value="action-required">Action Required</option>
                <option value="decision">Decision</option>
                <option value="reference">Reference</option>
            </select>
        </div>
        <div class="full-width">
            <label for="body">Body</label>
            <textarea id="body" rows="4" placeholder="Notes from the meeting..."></textarea>
        </div>
        <div class="form-actions">
            <button type="submit">Add Note</button>
            <button type="button" id="cancel-edit" class="secondary">Cancel</button>
        </div>
    </form>
</section>

<!-- FILTERS -->
<section id="filters" aria-label="Filter notes">
    <h2>Filter Notes</h2>
    <div class="filter-group">
        <label for="search">Search</label>
        <input type="search" id="search" placeholder="Search notes...">
    </div>
    <div class="filter-group">
        <label for="filter-owner">Owner</label>
        <select id="filter-owner">
            <option value="">All Owners</option>
        </select>
    </div>
    <div class="filter-group">
        <label for="filter-tag">Tag</label>
        <select id="filter-tag">
            <option value="">All Tags</option>
        </select>
    </div>
    <div class="filter-group">
        <label for="filter-status">Status</label>
        <select id="filter-status">
            <option value="">All Statuses</option>
            <option value="action-required">Action Required</option>
            <option value="decision">Decision</option>
            <option value="reference">Reference</option>
        </select>
    </div>
</section>

<!-- NOTES GRID -->
<main id="notes-container" aria-label="Meeting notes" aria-live="polite">
    <!-- Notes injected by JS -->
</main>

<script>
    (function () {
        'use strict';

        // --- Data Management ---
        const STORAGE_KEY = 'meetingNotesBoard';

        function getNotes() {
            try {
                const data = localStorage.getItem(STORAGE_KEY);
                return data ? JSON.parse(data) : [];
            } catch (e) {
                return [];
            }
        }

        function saveNotes(notes) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(notes));
        }

        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substring(2, 7);
        }

        // --- HTML Escaping ---
        function escapeHtml(str) {
            if (typeof str !== 'string') return '';
            return str
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        }

        // --- Rendering ---
        function renderStats(notes) {
            const statsSection = document.getElementById('stats');
            const total = notes.length;
            const actionRequiredCount = notes.filter(n => n.status === 'action-required').length;
            const uniqueOwners = new Set(
                notes.map(n => (n.owner ? n.owner.trim().toLowerCase() : '')).filter(Boolean)
            ).size;

            // Most common tag (preserve original casing)
            const tagCounts = {};
            const tagOriginal = {};
            notes.forEach(n => {
                if (n.tags) {
                    n.tags.split(',').forEach(tag => {
                        const trimmed = tag.trim();
                        const lower = trimmed.toLowerCase();
                        if (lower) {
                            tagCounts[lower] = (tagCounts[lower] || 0) + 1;
                            if (!tagOriginal[lower]) {
                                tagOriginal[lower] = trimmed;
                            }
                        }
                    });
                }
            });
            let mostCommonTag = 'N/A';
            let maxCount = 0;
            for (const lower in tagCounts) {
                if (tagCounts[lower] > maxCount) {
                    maxCount = tagCounts[lower];
                    mostCommonTag = tagOriginal[lower] || lower;
                }
            }

            statsSection.innerHTML = `
                <div class="stat-item">
                    <span class="stat-value">${total}</span>
                    <span class="stat-label">Total Notes</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${actionRequiredCount}</span>
                    <span class="stat-label">Action Required</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${uniqueOwners}</span>
                    <span class="stat-label">Unique Owners</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${escapeHtml(mostCommonTag)}</span>
                    <span class="stat-label">Most Common Tag</span>
                </div>
            `;
        }

        function renderNotes(notes) {
            const container = document.getElementById('notes-container');

            if (notes.length === 0) {
                container.innerHTML = '<div class="empty-state"><p>No notes found. Create your first note!</p></div>';
                return;
            }

            let html = '';
            notes.forEach(note => {
                const status = note.status || 'general';
                const statusClass = `status-badge status-${status}`;
                const statusLabel = status
                    .replace('-', ' ')
                    .replace(/\b\w/g, char => char.toUpperCase());

                // Tags
                let tagsHtml = '';
                if (note.tags) {
                    const tagsList = note.tags
                        .split(',')
                        .map(t => t.trim())
                        .filter(Boolean);
                    tagsList.forEach(tag => {
                        tagsHtml += `<span class="tag-badge">${escapeHtml(tag)}</span>`;
                    });
                }

                html += `
                    <article class="note-card" data-id="${escapeHtml(note.id)}">
                        <h3>${escapeHtml(note.title) || 'Untitled'}</h3>
                        <div class="note-meta">
                            <span>${escapeHtml(note.owner) || 'No owner'}</span>
                            <span>${note.date || ''}</span>
                            <span class="${statusClass}">${statusLabel}</span>
                        </div>
                        <div class="note-body">${escapeHtml(note.body) || ''}</div>
                        ${tagsHtml ? `<div class="note-tags">${tagsHtml}</div>` : ''}
                        <div class="note-actions">
                            <button class="edit-note" type="button">Edit</button>
                            <button class="delete-note danger" type="button">Delete</button>
                        </div>
                    </article>
                `;
            });

            container.innerHTML = html;
        }

        function populateFilterDropdowns(notes) {
            const ownerFilter = document.getElementById('filter-owner');
            const tagFilter = document.getElementById('filter-tag');

            const currentOwner = ownerFilter.value;
            const currentTag = tagFilter.value;

            // Owners
            const owners = new Set();
            notes.forEach(n => {
                if (n.owner) owners.add(n.owner.trim());
            });
            const sortedOwners = Array.from(owners).sort();

            ownerFilter.innerHTML = '<option value="">All Owners</option>';
            sortedOwners.forEach(owner => {
                const opt = document.createElement('option');
                opt.value = owner;
                opt.textContent = owner;
                if (owner === currentOwner) opt.selected = true;
                ownerFilter.appendChild(opt);
            });

            // Tags
            const tags = new Set();
            notes.forEach(n => {
                if (n.tags) {
                    n.tags.split(',').forEach(tag => {
                        const trimmed = tag.trim();
                        if (trimmed) tags.add(trimmed);
                    });
                }
            });
            const sortedTags = Array.from(tags).sort();

            tagFilter.innerHTML = '<option value="">All Tags</option>';
            sortedTags.forEach(tag => {
                const opt = document.createElement('option');
                opt.value = tag;
                opt.textContent = tag;
                if (tag === currentTag) opt.selected = true;
                tagFilter.appendChild(opt);
            });
        }

        function render() {
            const notes = getNotes();
            const filteredNotes = getFilteredNotes(notes);
            renderStats(notes);
            renderNotes(filteredNotes);
            populateFilterDropdowns(notes);
        }

        // --- Filtering ---
        function getFilteredNotes(notes) {
            const search = document.getElementById('search').value.toLowerCase().trim();
            const owner = document.getElementById('filter-owner').value;
            const tag = document.getElementById('filter-tag').value;
            const status = document.getElementById('filter-status').value;

            return notes.filter(note => {
                if (search) {
                    const textToSearch =
                        `${note.title} ${note.owner} ${note.tags} ${note.body}`.toLowerCase();
                    if (!textToSearch.includes(search)) return false;
                }
                if (owner && note.owner && note.owner.trim() !== owner) return false;
                if (tag) {
                    const noteTags = (note.tags || '')
                        .split(',')
                        .map(t => t.trim())
                        .filter(Boolean);
                    if (!noteTags.includes(tag)) return false;
                }
                if (status && note.status !== status) return false;
                return true;
            });
        }

        // --- Form Handling ---
        function populateForm(note) {
            document.getElementById('note-id').value = note.id || '';
            document.getElementById('title').value = note.title || '';
            document.getElementById('owner').value = note.owner || '';
            document.getElementById('meeting-date').value = note.date || '';
            document.getElementById('tags').value = note.tags || '';
            document.getElementById('status').value = note.status || 'general';
            document.getElementById('body').value = note.body || '';

            const submitBtn = document.querySelector('#note-form button[type="submit"]');
            submitBtn.textContent = note.id ? 'Update Note' : 'Add Note';

            const cancelBtn = document.getElementById('cancel-edit');
            cancelBtn.style.display = note.id ? 'inline-block' : 'none';
        }

        function resetForm() {
            document.getElementById('note-form').reset();
            document.getElementById('note-id').value = '';
            const submitBtn = document.querySelector('#note-form button[type="submit"]');
            submitBtn.textContent = 'Add Note';
            document.getElementById('cancel-edit').style.display = 'none';
        }

        function handleFormSubmit(event) {
            event.preventDefault();

            const noteId = document.getElementById('note-id').value;
            const title = document.getElementById('title').value.trim();
            const owner = document.getElementById('owner').value.trim();
            const date = document.getElementById('meeting-date').value;
            const tags = document.getElementById('tags').value.trim();
            const status = document.getElementById('status').value;
            const body = document.getElementById('body').value.trim();

            if (!title) {
                alert('Title is required.');
                document.getElementById('title').focus();
                return;
            }

            const notes = getNotes();

            if (noteId) {
                const index = notes.findIndex(n => n.id === noteId);
                if (index !== -1) {
                    notes[index] = {
                        ...notes[index],
                        title,
                        owner,
                        date,
                        tags,
                        status,
                        body,
                    };
                }
            } else {
                const newNote = {
                    id: generateId(),
                    title,
                    owner,
                    date,
                    tags,
                    status,
                    body,
                };
                notes.unshift(newNote);
            }

            saveNotes(notes);
            resetForm();
            render();
            const container = document.getElementById('notes-container');
            const firstCard = container.querySelector('.note-card');
            if (firstCard) firstCard.focus();
        }

        function handleEdit(event) {
            const card = event.target.closest('.note-card');
            if (!card) return;
            const noteId = card.dataset.id;
            const notes = getNotes();
            const note = notes.find(n => n.id === noteId);
            if (note) {
                populateForm(note);
                document.getElementById('title').focus();
            }
        }

        function handleDelete(event) {
            if (!confirm('Are you sure you want to delete this note?')) return;
            const card = event.target.closest('.note-card');
            if (!card) return;
            const noteId = card.dataset.id;
            let notes = getNotes();
            notes = notes.filter(n => n.id !== noteId);
            saveNotes(notes);
            render();
        }

        // --- Event Listeners ---
        function init() {
            document.getElementById('note-form').addEventListener('submit', handleFormSubmit);
            document.getElementById('cancel-edit').addEventListener('click', resetForm);

            // Event delegation for card buttons
            document.getElementById('notes-container').addEventListener('click', function (event) {
                if (event.target.classList.contains('edit-note')) {
                    handleEdit(event);
                } else if (event.target.classList.contains('delete-note')) {
                    handleDelete(event);
                }
            });

            // Filter listeners
            const filterIds = ['search', 'filter-owner', 'filter-tag', 'filter-status'];
            filterIds.forEach(id => {
                const el = document.getElementById(id);
                el.addEventListener('input', render);
                el.addEventListener('change', render);
            });

            render();
        }

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
