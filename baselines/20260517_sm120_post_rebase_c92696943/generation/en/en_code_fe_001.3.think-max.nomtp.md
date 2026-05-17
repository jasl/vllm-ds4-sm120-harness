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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 189.334394
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 305, "total_tokens": 18933, "completion_tokens": 18628, "prompt_tokens_details": null}`
- Prompt tokens: 305
- Completion tokens: 18628
- Total tokens: 18933

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
    *   **Format:** Single file `index.html`.
    *   **Constraints:** No external libraries, CDNs, images, or build tools. Under 1000 lines.
    *   **Task:** "Meeting Notes Board" for a small team.
    *   **Functional Requirements:**
        1.  Add note: title, owner, meeting date, tags, body.
        2.  Filter notes: owner, tag, free-text search.
        3.  Note category: "Action Required," "Decision," "Reference."
        4.  Edit and delete notes.
        5.  Persist: `localStorage`.
        6.  Statistics: total notes, action-required count, unique owners, most common tag.
        7.  Responsive: two-column grid (wide), single column (narrow).
        8.  Accessibility: labels, keyboard operable, visible focus states.
    *   **Output:** Only the complete `index.html` content.

    2.  **Design & Planning:**

    *   **HTML Structure:**
        *   `<header>`: Title + Stats strip.
        *   `<main>`: Filter/Search controls + Add Note form + Notes grid.
        *   `<section id="app">`:
            *   `stats-bar`: total notes, action items, unique owners, top tag.
            *   `controls`: search input, filter by owner (dropdown), filter by tag (dropdown).
            *   `note-form`: inputs for title, owner, date, tags, body, type (radio/dropdown). Submit button.
            *   `notes-container`: grid of cards.

    *   **CSS Structure:**
        *   Reset/Normalize basics.
        *   Variables for colors (CSS custom properties).
        *   Layout: Flexbox/Grid for responsiveness.
        *   Card design.
        *   Form styling.
        *   Focus states (`:focus`, `:focus-visible`).
        *   Responsive breakpoint (e.g., 768px).

    *   **JavaScript Structure:**
        *   `localStorage` helper: `saveNotes(notes)`, `loadNotes()`.
        *   Data model: `{ id, title, owner, date, tags, body, type, createdAt, updatedAt }`
        *   State: `notes`, `filteredNotes`, `currentEditId`(optional).
        *   DOM references: form elements, container, stats elements, search, owner filter, tag filter.
        *   Functions:
            *   `renderStats(notes)`
            *   `renderNotes(notes)`
            *   `filterNotes()` -> applies search, owner, tag.
            *   `handleAddNote(event)`
            *   `handleEditNote(id)`
            *   `handleDeleteNote(id)`
            *   `handleSaveEdit(id)`
            *   `init()`

    *   **Data Model Considerations:**
        *   `type`: enum of 'action', 'decision', 'reference'.
        *   `tags`: stored as a string (comma separated), rendered as badges. For filtering, we need unique tags.

    *   **Stats Computations:**
        *   Total: `notes.length`
        *   Action Required: `notes.filter(n => n.type === 'action').length`
        *   Unique Owners: `new Set(notes.map(n => n.owner)).size`
        *   Most Common Tag:
            *   Count occurrences of each tag.
            *   Find the max.
            *   Handle ties (return first).

    *   **Accessibility:**
        *   Labels for all inputs.
        *   `<button>` elements for actions.
        *   Roles like `alert`, `region`, `main`.
        *   `aria-live` regions for dynamic updates.
        *   Proper heading hierarchy (`h1`, `h2`).

    *   **Code Layout (Approx Lines):**
        *   HTML: ~150 lines
        *   CSS: ~250 lines
        *   JavaScript: ~400 lines
        *   Total: ~800 lines. Under 1000 is easy.

    *   **Drafting the HTML:**
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Meeting Notes Board</title>
            <!-- Styles -->
            <style>
                ...
            </style>
        </head>
        <body>
            <header id="app-header">
                <h1>Meeting Notes Board</h1>
                <section id="stats" aria-label="Statistics">
                    ...
                </section>
            </header>

            <main>
                <section id="controls">
                    <h2>Search & Filter</h2>
                    <label for="search">Search</label>
                    <input type="search" id="search" ...>

                    <label for="filter-owner">Owner</label>
                    <select id="filter-owner">...</select>

                    <label for="filter-tag">Tag</label>
                    <select id="filter-tag">...</select>
                </section>

                <section id="note-form-section">
                    <h2 id="form-title">Add New Note</h2>
                    <form id="note-form">
                        <label for="title">Title</label>
                        <input type="text" id="title" required>

                        <label for="owner">Owner</label>
                        <input type="text" id="owner" required>

                        <label for="date">Meeting Date</label>
                        <input type="date" id="date" required>

                        <label for="tags">Tags (comma separated)</label>
                        <input type="text" id="tags">

                        <label for="body">Body</label>
                        <textarea id="body" rows="4"></textarea>

                        <fieldset>
                            <legend>Note Type</legend>
                            <label><input type="radio" name="type" value="action" checked> Action Required</label>
                            <label><input type="radio" name="type" value="decision"> Decision</label>
                            <label><input type="radio" name="type" value="reference"> Reference</label>
                        </fieldset>

                        <button type="submit">Add Note</button>
                    </form>
                </section>

                <section id="notes-section">
                    <h2>Notes</h2>
                    <div id="notes-container" role="list">
                        <!-- Cards go here -->
                    </div>
                </section>
            </main>

            <script>
                // JavaScript
            </script>
        </body>
        </html>
        ```

    *   **Refining Stats:**
        Stats strip is compact. `<ul>` is good for accessibility.
        ```html
        <ul id="stats-list">
            <li>Total Notes: <span id="stat-total">0</span></li>
            <li>Action Required: <span id="stat-action">0</span></li>
            <li>Unique Owners: <span id="stat-owners">0</span></li>
            <li>Most Common Tag: <span id="stat-tag">N/A</span></li>
        </ul>
        ```
        We can just use `<div>`s or a `<dl>`. Let's use a `<ul>` for the stats as a list is inherently accessible. Or just `<div>`s with `aria-label` on the container. Let's keep it semantic.

    *   **Filter Logic (JS):**
        ```javascript
        let notes = loadNotes();
        let currentFilters = { query: '', owner: '', tag: '' };

        function getFilteredNotes() {
            return notes.filter(note => {
                const searchStr = `${note.title} ${note.body} ${note.owner} ${note.tags}`.toLowerCase();
                const queryMatch = !currentFilters.query || searchStr.includes(currentFilters.query.toLowerCase());
                const ownerMatch = !currentFilters.owner || note.owner === currentFilters.owner;
                const tagMatch = !currentFilters.tag || note.tags.split(',').map(t => t.trim()).includes(currentFilters.tag);
                return queryMatch && ownerMatch && tagMatch;
            });
        }
        ```

    *   **Rendering:**
        ```javascript
        function renderNotes(notesToRender) {
            container.innerHTML = '';
            if (notesToRender.length === 0) {
                container.innerHTML = '<p>No notes found.</p>';
                return;
            }
            notesToRender.forEach(note => {
                const card = document.createElement('div');
                card.className = 'note-card';
                card.setAttribute('role', 'listitem');
                card.innerHTML = `
                    <div class="card-header">
                        <h3>${escapeHtml(note.title)}</h3>
                        <span class="note-type type-${note.type}">${note.type}</span>
                    </div>
                    <div class="card-meta">
                        <span>Owner: ${escapeHtml(note.owner)}</span>
                        <span>Date: ${note.date}</span>
                    </div>
                    <p>${escapeHtml(note.body)}</p>
                    <div class="card-tags">
                        ${note.tags ? note.tags.split(',').map(t => `<span class="tag">${escapeHtml(t.trim())}</span>`).join('') : ''}
                    </div>
                    <div class="card-actions">
                        <button class="btn-edit" data-id="${note.id}" aria-label="Edit ${note.title}">Edit</button>
                        <button class="btn-delete" data-id="${note.id}" aria-label="Delete ${note.title}">Delete</button>
                    </div>
                `;
                container.appendChild(card);
            });

            // Add event listeners for edit and delete
            container.querySelectorAll('.btn-edit').forEach(btn => {
                btn.addEventListener('click', () => editNote(btn.dataset.id));
            });
            container.querySelectorAll('.btn-delete').forEach(btn => {
                btn.addEventListener('click', () => deleteNote(btn.dataset.id));
            });
        }
        ```

    *   **CRUD Operations:**
        `addNote(note)` -> push, save, re-render.
        `editNote(id)` -> populate form, change form title, toggle submit/save, store editing id.
        `deleteNote(id)` -> filter, save, re-render.

    *   **Statistics Rendering:**
        ```javascript
        function renderStats(notes) {
            const total = notes.length;
            const actionCount = notes.filter(n => n.type === 'action').length;
            const uniqueOwners = new Set(notes.map(n => n.owner)).size;
            const tagCounts = {};
            notes.forEach(n => {
                if (n.tags) {
                    n.tags.split(',').map(t => t.trim()).forEach(t => {
                        if (t) {
                            tagCounts[t] = (tagCounts[t] || 0) + 1;
                        }
                    });
                }
            });
            let mostCommonTag = 'N/A';
            let maxCount = 0;
            for (const [tag, count] of Object.entries(tagCounts)) {
                if (count > maxCount) {
                    maxCount = count;
                    mostCommonTag = tag;
                }
            }

            document.getElementById('stat-total').textContent = total;
            document.getElementById('stat-action').textContent = actionCount;
            document.getElementById('stat-owners').textContent = uniqueOwners;
            document.getElementById('stat-tag').textContent = mostCommonTag;
        }
        ```

    *   **Form Handling (Add / Edit):**
        Use a single form. When editing, load the data into the form fields, change the button text to "Save Changes", and handle the submit differently.
        ```javascript
        let editingId = null;

        function handleFormSubmit(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const note = {
                title: formData.get('title'),
                owner: formData.get('owner'),
                date: formData.get('date'),
                tags: formData.get('tags'),
                body: formData.get('body'),
                type: formData.get('type'),
            };

            if (editingId) {
                // Update existing note
                const index = notes.findIndex(n => n.id === editingId);
                if (index !== -1) {
                    notes[index] = { ...notes[index], ...note };
                    notes[index].updatedAt = new Date().toISOString();
                }
                editingId = null;
                document.getElementById('form-title').textContent = 'Add New Note';
                document.querySelector('#note-form button[type="submit"]').textContent = 'Add Note';
            } else {
                note.id = Date.now().toString(36) + Math.random().toString(36).substring(2, 5);
                note.createdAt = new Date().toISOString();
                note.updatedAt = note.createdAt;
                notes.push(note);
            }

            saveNotes(notes);
            e.target.reset();
            // Reset date to today? Or keep it empty. Let's keep it empty.
            updateUI();
        }

        function editNote(id) {
            const note = notes.find(n => n.id === id);
            if (!note) return;

            document.getElementById('title').value = note.title;
            document.getElementById('owner').value = note.owner;
            document.getElementById('date').value = note.date;
            document.getElementById('tags').value = note.tags;
            document.getElementById('body').value = note.body;
            document.querySelector(`input[name="type"][value="${note.type}"]`).checked = true;

            editingId = id;
            document.getElementById('form-title').textContent = 'Edit Note';
            document.querySelector('#note-form button[type="submit"]').textContent = 'Save Changes';
            document.getElementById('note-form-section').scrollIntoView({ behavior: 'smooth' });
        }

        function deleteNote(id) {
            if (!confirm('Are you sure you want to delete this note?')) return;
            notes = notes.filter(n => n.id !== id);
            saveNotes(notes);
            updateUI();
        }
        ```

    *   **Dropdowns for Filtering:**
        Owner dropdown and Tag dropdown should be populated dynamically from the stored notes.
        ```javascript
        function populateFilters() {
            const owners = [...new Set(notes.map(n => n.owner))];
            const tags = [...new Set(notes.flatMap(n => n.tags.split(',').map(t => t.trim()).filter(t => t)))];

            const ownerSelect = document.getElementById('filter-owner');
            const tagSelect = document.getElementById('filter-tag');

            const currentOwner = ownerSelect.value;
            const currentTag = tagSelect.value;

            ownerSelect.innerHTML = '<option value="">All Owners</option>' + owners.map(o => `<option value="${o}">${o}</option>`).join('');
            tagSelect.innerHTML = '<option value="">All Tags</option>' + tags.map(t => `<option value="${t}">${t}</option>`).join('');

            ownerSelect.value = currentOwner;
            tagSelect.value = currentTag;
        }
        ```

    *   **CSS Styling:**
        *   Variables: `--color-primary`, `--color-bg`, `--color-card`, `--color-border`, `--color-text`.
        *   Layout: `main` has max-width, centered.
        *   Stats: Flexbox row, wraps on small screens.
        *   Controls: Flexbox row for search, owner, tag. Wraps.
        *   Form: Grid or Flex column.
        *   Notes Container: CSS Grid `grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))`
        *   Cards: Border, shadow, padding. Badge colors for types.
        *   Accessibility: `:focus-visible` styles. `button:focus-visible`, `input:focus-visible`, `select:focus-visible`, `textarea:focus-visible`.

        Let's refine the CSS:
        ```css
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --action-color: #ef4444;
            --decision-color: #f59e0b;
            --reference-color: #6b7280;
            --radius: 8px;
            --shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; padding: 1rem; }

        header { text-align: center; margin-bottom: 1.5rem; }
        h1 { font-size: 1.75rem; color: var(--primary); }

        #stats { display: flex; flex-wrap: wrap; justify-content: center; gap: 1rem 2rem; padding: 1rem; background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); margin-top: 1rem; }
        .stat { display: flex; flex-direction: column; align-items: center; }
        .stat-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); }
        .stat-value { font-size: 1.25rem; font-weight: 600; }

        main { max-width: 1200px; margin: 0 auto; }

        #controls { display: flex; flex-wrap: wrap; gap: 1rem; align-items: end; margin-bottom: 1.5rem; padding: 1rem; background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); }
        .control-group { display: flex; flex-direction: column; flex: 1 1 200px; }
        .control-group label { font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem; color: var(--text-muted); }
        .control-group input, .control-group select { padding: 0.5rem; border: 1px solid var(--border); border-radius: 4px; font-size: 1rem; }

        #note-form-section { margin-bottom: 1.5rem; }
        #note-form-section h2 { margin-bottom: 0.5rem; }

        #note-form { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; padding: 1.5rem; background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); }
        .form-group { display: flex; flex-direction: column; }
        .form-group.full-width { grid-column: span 2; }
        .form-group label { font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem; }
        .form-group input, .form-group textarea, .form-group select { padding: 0.5rem; border: 1px solid var(--border); border-radius: 4px; font-size: 1rem; }
        .form-group textarea { resize: vertical; min-height: 80px; }
        fieldset { grid-column: span 2; border: none; padding: 0; }
        fieldset legend { font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; }
        .radio-group { display: flex; gap: 1.5rem; flex-wrap: wrap; }
        .radio-group label { display: flex; align-items: center; gap: 0.25rem; font-size: 0.875rem; cursor: pointer; }
        .radio-group input[type="radio"] { width: auto; }

        #note-form button[type="submit"] { grid-column: span 2; padding: 0.75rem; background: var(--primary); color: white; border: none; border-radius: var(--radius); font-size: 1rem; font-weight: 600; cursor: pointer; }
        #note-form button[type="submit"]:hover { background: var(--primary-hover); }
        #note-form button[type="submit"]:focus-visible { outline: 3px solid var(--primary); outline-offset: 2px; }

        #notes-section h2 { margin-bottom: 1rem; }

        #notes-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }

        .note-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; box-shadow: var(--shadow); display: flex; flex-direction: column; gap: 0.75rem; }
        .note-card:focus-within { outline: 2px solid var(--primary); outline-offset: 2px; }

        .card-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; }
        .card-header h3 { font-size: 1.125rem; font-weight: 600; word-break: break-word; }
        .note-type { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; padding: 0.15em 0.5em; border-radius: 4px; white-space: nowrap; flex-shrink: 0; }
        .type-action { background: #fee2e2; color: #991b1b; }
        .type-decision { background: #fef3c7; color: #92400e; }
        .type-reference { background: #f3f4f6; color: #374151; }

        .card-meta { display: flex; justify-content: space-between; font-size: 0.875rem; color: var(--text-muted); }
        .card-body { font-size: 0.875rem; color: var(--text); line-height: 1.5; word-break: break-word; max-height: 100px; overflow-y: auto; }
        .card-tags { display: flex; flex-wrap: wrap; gap: 0.25rem; }
        .tag { background: #e0e7ff; color: #3730a3; font-size: 0.75rem; padding: 0.1em 0.5em; border-radius: 4px; }

        .card-actions { display: flex; gap: 0.5rem; margin-top: auto; }
        .card-actions button { padding: 0.4rem 0.75rem; border: 1px solid var(--border); border-radius: 4px; background: white; font-size: 0.875rem; cursor: pointer; }
        .card-actions button:hover { background: var(--bg); }
        .card-actions button:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
        .btn-edit { color: var(--primary); }
        .btn-delete { color: var(--action-color); }

        @media (max-width: 768px) {
            #note-form { grid-template-columns: 1fr; }
            .form-group.full-width { grid-column: span 1; }
            fieldset { grid-column: span 1; }
            #note-form button[type="submit"] { grid-column: span 1; }
            #notes-container { grid-template-columns: 1fr; }
            #controls { flex-direction: column; }
            .control-group { flex: 1 1 auto; }
        }

        /* Accessibility */
        .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border-width: 0; }
        input:focus-visible, select:focus-visible, textarea:focus-visible { outline: 2px solid var(--primary); outline-offset: 1px; }
        button:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
        ```

    *   **Accessibility Enhancements:**
        *   `aria-live="polite"` on stats and notes container to announce changes.
        *   `role="status"` on stats.
        *   `role="region"` with `aria-label` for main sections.
        *   Form has `aria-label`.
        *   Better labeling for filter controls.
        *   Announce number of filtered results after filtering.
        *   Use `<time>` element for dates? Yes, in JSON it's a string, display it as text. `datetime` attribute.
        *   `aria-describedby` for form inputs? Might be overkill. Let's keep labels properly associated.

        Let's add an `aria-live` region for dynamic updates.
        ```html
        <div id="announcements" class="sr-only" aria-live="polite"></div>
        ```
        Use `window.announce(msg)` function.

    *   **JavaScript Function Details:**
        *   `escapeHtml(str)` to prevent XSS.
        *   `updateUI()` -> `populateFilters()`, `renderStats()`, `renderNotes()`.
        *   Initialization:
            ```javascript
            document.addEventListener('DOMContentLoaded', () => {
                notes = loadNotes();
                document.getElementById('note-form').addEventListener('submit', handleFormSubmit);
                document.getElementById('search').addEventListener('input', (e) => {
                    currentFilters.query = e.target.value;
                    updateUI();
                });
                document.getElementById('filter-owner').addEventListener('change', (e) => {
                    currentFilters.owner = e.target.value;
                    updateUI();
                });
                document.getElementById('filter-tag').addEventListener('change', (e) => {
                    currentFilters.tag = e.target.value;
                    updateUI();
                });
                updateUI();
            });
            ```
        *   Cancel Edit Button:
            It would be good to add a "Cancel" button when editing to reset the form.
            ```html
            <button type="button" id="cancel-edit" style="display:none;">Cancel</button>
            ```
            JS:
            ```javascript
            document.getElementById('cancel-edit').addEventListener('click', cancelEdit);
            function cancelEdit() {
                editingId = null;
                document.getElementById('note-form').reset();
                document.getElementById('form-title').textContent = 'Add New Note';
                document.querySelector('#note-form button[type="submit"]').textContent = 'Add Note';
                document.getElementById('cancel-edit').style.display = 'none';
            }
            function editNote(id) {
                // ...
                document.getElementById('cancel-edit').style.display = 'inline-block';
            }
            ```

    *   **Reviewing the Data Flow:**
        1.  App loads, `notes` from `localStorage`.
        2.  `updateUI()` runs: populates filter dropdowns, renders stats, renders notes.
        3.  User types in search / changes filter: `updateUI()` runs.
        4.  User submits form: `handleFormSubmit()` runs, adds/updates note, saves, `updateUI()`.
        5.  User clicks Edit: `editNote()` populates form.
        6.  User clicks Delete: `deleteNote()` removes, saves, `updateUI()`.

    *   **`escapeHtml` implementation:**
        ```javascript
        function escapeHtml(unsafe) {
            if (!unsafe) return '';
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
        ```

    *   **Improving Filter Tags Logic:**
        The `tag` filter dropdown needs to show all possible tags. Let's extract tags from all notes.
        ```javascript
        const allTags = [...new Set(notes.flatMap(n => n.tags.split(',').map(t => t.trim()).filter(t => t)))];
        ```

    *   **Handling `body` in filter search:**
        Already accounted for in the `getFilteredNotes()` function.

    *   **Reviewing Stats:**
        "most common tag" -> the algorithm iterates. If there's a tie, the first one encountered with the max count is kept. This is fine.

    *   **Reviewing "compact statistics strip":**
        "compact statistics strip: total notes, action-required count, unique owners, and most common tag."
        I will make it a simple horizontal bar.
        ```html
        <section id="stats" aria-label="Notes Statistics" role="status">
            <div class="stat">
                <span class="stat-value" id="stat-total">0</span>
                <span class="stat-label">Total Notes</span>
            </div>
            <div class="stat">
                <span class="stat-value" id="stat-action">0</span>
                <span class="stat-label">Action Required</span>
            </div>
            <div class="stat">
                <span class="stat-value" id="stat-owners">0</span>
                <span class="stat-label">Unique Owners</span>
            </div>
            <div class="stat">
                <span class="stat-value" id="stat-tag">N/A</span>
                <span class="stat-label">Most Common Tag</span>
            </div>
        </section>
        ```

    *   **Reviewing Responsive Layout:**
        "two-column card grid on wide screens, single column on narrow screens."
        CSS Grid handles this with `auto-fill, minmax(300px, 1fr)`. If the width is less than ~650px, it becomes single column. A media query can explicitly set `grid-template-columns: 1fr` at 768px. The request says "two-column card grid". The current CSS already does this.

    *   **Checking Total Lines:**
        Let's roughly count.
        HTML (~100 lines) + CSS (~150 lines) + JS (~300 lines) = ~550 lines. Well within the 1000 line limit. I can add more robust comments and features if needed, but keeping it clean and under 1000 is best.

    *   **Refining Accessibility Details:**
        *   `<label>` elements properly connected via `for` attributes.
        *   `fieldset` and `legend` for radio buttons.
        *   `aria-live="polite"` on container and stats.
        *   `role="list"` on notes container, `role="listitem"` on cards.
        *   Focus management: when editing, focus the first input. On cancel, focus the add button.

    *   **Edge Cases:**
        *   Empty notes array.
        *   Tags missing (empty string).
        *   Notes without an owner (shouldn't happen if required, but handle gracefully).
        *   `localStorage` is full or not available (e.g., private browsing on some old browsers). `try/catch` around `localStorage` access.
        ```javascript
        function saveNotes(notes) {
            try {
                localStorage.setItem('meetingNotes', JSON.stringify(notes));
            } catch (e) {
                console.error('Failed to save notes', e);
            }
        }
        function loadNotes() {
            try {
                const data = localStorage.getItem('meetingNotes');
                return data ? JSON.parse(data) : [];
            } catch (e) {
                console.error('Failed to load notes', e);
                return [];
            }
        }
        ```

    *   **Date Input:**
        `type="date"` requires a specific format. `valueAsDate` or `value` (string YYYY-MM-DD).

    *   **Type handling in form:**
        The default type is "action" (checked).

    *   **Role for Stats:**
        `role="status"` is appropriate as it's a live region for results.

    *   **Role for Notes Container:**
        `role="list"` is good. Cards have `role="listitem"`.

    *   **Code Construction:**

        Let's write out the full file mentally to check for completeness.
        `<!DOCTYPE html>` ... `<html lang="en">`
        `<head>` ... `<meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>Meeting Notes Board</title>`
        `<style>` (all CSS)
        `</head>`
        `<body>`
        `<header>` ... `<h1>Meeting Notes Board</h1>` ... `<section id="stats">` ... `</section>` ... `</header>`
        `<main>`
        `<section id="controls" aria-label="Search and filter controls">`
        `<div class="control-group"> <label for="search">Search</label> <input type="search" id="search" ...> </div>`
        `<div class="control-group"> <label for="filter-owner">Owner</label> <select id="filter-owner"> ... </select> </div>`
        `<div class="control-group"> <label for="filter-tag">Tag</label> <select id="filter-tag"> ... </select> </div>`
        `</section>`
        `<section id="note-form-section" aria-label="Add or Edit Note">`
        `<h2 id="form-title">Add New Note</h2>`
        `<form id="note-form" novalidate>` -> `novalidate` allows our own validation. Actually, built-in HTML5 validation is good for accessibility, let's keep `required` attributes but remove `novalidate`.
        `<div class="form-group"> <label for="title">Title</label> <input type="text" id="title" required> </div>`
        `<div class="form-group"> <label for="owner">Owner</label> <input type="text" id="owner" required> </div>`
        `<div class="form-group"> <label for="date">Meeting Date</label> <input type="date" id="date" required> </div>`
        `<div class="form-group"> <label for="tags">Tags (comma separated)</label> <input type="text" id="tags"> </div>`
        `<div class="form-group full-width"> <label for="body">Body</label> <textarea id="body" rows="4"></textarea> </div>`
        `<fieldset>`
        `<legend>Note Type</legend>`
        `<div class="radio-group">`
        `<label><input type="radio" name="type" value="action" checked> Action Required</label>`
        `<label><input type="radio" name="type" value="decision"> Decision</label>`
        `<label><input type="radio" name="type" value="reference"> Reference</label>`
        `</div>`
        `</fieldset>`
        `<div class="form-actions"> <button type="submit">Add Note</button> <button type="button" id="cancel-edit" class="btn-cancel" style="display:none;">Cancel</button> </div>`
        `</form>`
        `</section>`
        `<section id="notes-section" aria-label="Notes list">`
        `<h2>Notes</h2>`
        `<div id="notes-container" role="list">`
        `<!-- Cards dynamically inserted -->`
        `</div>`
        `</section>`
        `<div id="announcements" class="sr-only" aria-live="polite"></div>`
        `</main>`
        `<script>`
        `// All JS`
        `</script>`
        `</body>`
        `</html>`

    *   **Refining the JS:**
        ```javascript
        let notes = [];
        let editingId = null;
        const currentFilters = { query: '', owner: '', tag: '' };

        function announce(message) {
            const announcer = document.getElementById('announcements');
            if (announcer) {
                announcer.textContent = '';
                setTimeout(() => { announcer.textContent = message; }, 100);
            }
        }

        function saveNotes(data) {
            try { localStorage.setItem('meetingNotes', JSON.stringify(data)); } catch (e) { console.error('Save failed', e); }
        }
        function loadNotes() {
            try { const data = localStorage.getItem('meetingNotes'); return data ? JSON.parse(data) : []; } catch (e) { console.error('Load failed', e); return []; }
        }

        function escapeHtml(unsafe) {
            if (!unsafe) return '';
            return unsafe.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
        }

        function getFilteredNotes() {
            return notes.filter(note => {
                const searchStr = `${note.title} ${note.body} ${note.owner} ${note.tags}`.toLowerCase();
                const queryMatch = !currentFilters.query || searchStr.includes(currentFilters.query.toLowerCase());
                const ownerMatch = !currentFilters.owner || note.owner === currentFilters.owner;
                const tagMatch = !currentFilters.tag || (note.tags && note.tags.split(',').map(t => t.trim()).includes(currentFilters.tag));
                return queryMatch && ownerMatch && tagMatch;
            });
        }

        function renderStats(notesData) {
            const total = notesData.length;
            const actionCount = notesData.filter(n => n.type === 'action').length;
            const uniqueOwners = new Set(notesData.map(n => n.owner)).size;
            const tagCounts = {};
            notesData.forEach(n => {
                if (n.tags) {
                    n.tags.split(',').map(t => t.trim()).filter(t => t).forEach(t => {
                        tagCounts[t] = (tagCounts[t] || 0) + 1;
                    });
                }
            });
            let mostCommonTag = 'N/A';
            let maxCount = 0;
            for (const [tag, count] of Object.entries(tagCounts)) {
                if (count > maxCount) { maxCount = count; mostCommonTag = tag; }
            }
            document.getElementById('stat-total').textContent = total;
            document.getElementById('stat-action').textContent = actionCount;
            document.getElementById('stat-owners').textContent = uniqueOwners;
            document.getElementById('stat-tag').textContent = mostCommonTag;
        }

        function populateFilters() {
            const owners = [...new Set(notes.map(n => n.owner))];
            const tags = [...new Set(notes.flatMap(n => (n.tags || '').split(',').map(t => t.trim()).filter(t => t)))];

            const ownerSelect = document.getElementById('filter-owner');
            const tagSelect = document.getElementById('filter-tag');

            const prevOwner = ownerSelect.value;
            const prevTag = tagSelect.value;

            ownerSelect.innerHTML = '<option value="">All Owners</option>' + owners.map(o => `<option value="${escapeHtml(o)}">${escapeHtml(o)}</option>`).join('');
            tagSelect.innerHTML = '<option value="">All Tags</option>' + tags.map(t => `<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`).join('');

            ownerSelect.value = prevOwner;
            tagSelect.value = prevTag;
        }

        function renderNotes(notesData) {
            const container = document.getElementById('notes-container');
            container.innerHTML = '';
            if (notesData.length === 0) {
                container.innerHTML = '<p role="listitem">No notes found.</p>';
                return;
            }
            notesData.forEach(note => {
                const card = document.createElement('div');
                card.className = 'note-card';
                card.setAttribute('role', 'listitem');
                const tagsHtml = (note.tags || '').split(',').map(t => `<span class="tag">${escapeHtml(t.trim())}</span>`).join('');

                card.innerHTML = `
                    <div class="card-header">
                        <h3>${escapeHtml(note.title)}</h3>
                        <span class="note-type type-${escapeHtml(note.type)}">${escapeHtml(note.type)}</span>
                    </div>
                    <div class="card-meta">
                        <span>Owner: ${escapeHtml(note.owner)}</span>
                        <time datetime="${escapeHtml(note.date)}">${escapeHtml(note.date)}</time>
                    </div>
                    <div class="card-body">${escapeHtml(note.body)}</div>
                    <div class="card-tags">${tagsHtml}</div>
                    <div class="card-actions">
                        <button class="btn-edit" data-id="${note.id}" aria-label="Edit note: ${escapeHtml(note.title)}">Edit</button>
                        <button class="btn-delete" data-id="${note.id}" aria-label="Delete note: ${escapeHtml(note.title)}">Delete</button>
                    </div>
                `;
                container.appendChild(card);
            });

            container.querySelectorAll('.btn-edit').forEach(btn => {
                btn.addEventListener('click', () => editNote(btn.dataset.id));
            });
            container.querySelectorAll('.btn-delete').forEach(btn => {
                btn.addEventListener('click', () => deleteNote(btn.dataset.id));
            });
            announce(`Showing ${notesData.length} notes.`);
        }

        function updateUI() {
            const filtered = getFilteredNotes();
            renderStats(filtered);
            populateFilters();
            renderNotes(filtered);
        }

        function handleFormSubmit(e) {
            e.preventDefault();
            const form = e.target;
            const title = form.title.value.trim();
            const owner = form.owner.value.trim();
            const date = form.date.value;
            const tags = form.tags.value.trim();
            const body = form.body.value.trim();
            const type = form.type.value;

            if (!title || !owner || !date) {
                announce('Please fill in Title, Owner, and Date.');
                return;
            }

            if (editingId) {
                const index = notes.findIndex(n => n.id === editingId);
                if (index !== -1) {
                    notes[index] = { ...notes[index], title, owner, date, tags, body, type, updatedAt: new Date().toISOString() };
                    announce(`Note "${title}" updated.`);
                }
                cancelEdit();
            } else {
                const newNote = {
                    id: Date.now().toString(36) + Math.random().toString(36).substring(2, 8),
                    title, owner, date, tags, body, type,
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString()
                };
                notes.push(newNote);
                announce(`Note "${title}" added.`);
                form.reset();
            }
            saveNotes(notes);
            updateUI();
        }

        function editNote(id) {
            const note = notes.find(n => n.id === id);
            if (!note) return;

            document.getElementById('title').value = note.title;
            document.getElementById('owner').value = note.owner;
            document.getElementById('date').value = note.date;
            document.getElementById('tags').value = note.tags || '';
            document.getElementById('body').value = note.body || '';
            document.querySelector(`input[name="type"][value="${note.type}"]`).checked = true;

            editingId = id;
            document.getElementById('form-title').textContent = 'Edit Note';
            document.querySelector('#note-form button[type="submit"]').textContent = 'Save Changes';
            document.getElementById('cancel-edit').style.display = 'inline-block';
            document.getElementById('note-form-section').scrollIntoView({ behavior: 'smooth' });
            document.getElementById('title').focus();
        }

        function cancelEdit() {
            editingId = null;
            document.getElementById('note-form').reset();
            document.getElementById('form-title').textContent = 'Add New Note';
            document.querySelector('#note-form button[type="submit"]').textContent = 'Add Note';
            document.getElementById('cancel-edit').style.display = 'none';
            announce('Edit cancelled.');
        }

        function deleteNote(id) {
            const note = notes.find(n => n.id === id);
            if (!note) return;
            if (!confirm(`Delete note "${note.title}"?`)) return;
            notes = notes.filter(n => n.id !== id);
            saveNotes(notes);
            updateUI();
            announce(`Note "${note.title}" deleted.`);
        }

        document.addEventListener('DOMContentLoaded', () => {
            notes = loadNotes();

            document.getElementById('note-form').addEventListener('submit', handleFormSubmit);
            document.getElementById('cancel-edit').addEventListener('click', cancelEdit);

            document.getElementById('search').addEventListener('input', (e) => {
                currentFilters.query = e.target.value;
                updateUI();
            });
            document.getElementById('filter-owner').addEventListener('change', (e) => {
                currentFilters.owner = e.target.value;
                updateUI();
            });
            document.getElementById('filter-tag').addEventListener('change', (e) => {
                currentFilters.tag = e.target.value;
                updateUI();
            });

            updateUI();
        });
        ```

    *   **CSS Refinements:**
        Check responsive behavior. The form grid uses `grid-template-columns: 1fr 1fr`. On small screens, it's `1fr`. The button is `grid-column: span 2` / `span 1`.
        The stats section layout. Let's ensure it wraps nicely on small screens.
        ```css
        #stats { display: flex; flex-wrap: wrap; justify-content: center; gap: 1rem 2rem; padding: 1rem; background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); margin-top: 1rem; }
        ```
        How about the body max-height? `max-height: 100px; overflow-y: auto;` This keeps cards relatively consistent in height.

        Accessible focus styles:
        ```css
        :focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
        .card-actions button:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
        .note-card:focus-within { outline: 2px solid var(--primary); outline-offset: 2px; }
        ```

        Let's add a `skip-link` for accessibility. A simple "Skip to main" link.
        ```html
        <a href="#main-content" class="skip-link">Skip to main content</a>
        ```
        ```css
        .skip-link { position: absolute; top: -40px; left: 0; background: var(--primary); color: white; padding: 0.5rem 1rem; z-index: 100; }
        .skip-link:focus { top: 0; }
        ```
        And `id="main-content"` on `<main>`.

    *   **Checking the Data Persistance:**
        `localStorage` key: `meetingNotes`. No collisions.

    *   **Checking Requirements:**
        1. Add note with title, owner, meeting date, tags, body. (Done)
        2. Appear as cards, filter by owner, tag, free-text. (Done)
        3. Marked as “Action Required,” “Decision,” or “Reference.” (Done)
        4. Edit and delete. (Done)
        5. Persist in `localStorage`. (Done)
        6. Stats: total, action-required count, unique owners, most common tag. (Done)
        7. Responsive: 2-column grid (wide), single column (narrow). (Done)
        8. Accessibility: labels, keyboard-operable, visible focus states. (Done)
        *   Total under 1000 lines. (Yes, ~250 HTML + CSS + JS).

    *   **Reviewing Visual Design:**
        Adding some subtle borders, shadows, using system fonts.
        ```css
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", Arial, sans-serif; }
        ```

    *   **Fine-Tuning the HTML structure:**
        Let's put the `<style>` and `<script>` in the `<head>` and end of `<body>` respectively as requested by typical single file apps, though any placement works. `<style>` in `<head>` is best practice.

    *   **Line Count Check:**
        Let's mentally estimate.
        HTML: ~120 lines
        CSS: ~180 lines
        JS: ~200 lines
        Total: 500 lines. Very safe.

    *   **Potential Improvements / Edge Cases:**
        *   What if the owner field is very long? `word-break: break-word` added.
        *   What if the body is very long? `max-height: 100px; overflow-y: auto;` added.
        *   What if no tags? Then "Most Common Tag" is "N/A". Empty tags string is handled gracefully.
        *   What if `localStorage` is corrupted? `try/catch` falls back gracefully to empty array `[]`.

    *   **Let's build the output strictly as requested.**

        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Meeting Notes Board</title>
            <style>
                /* ... CSS ... */
            </style>
        </head>
        <body>
            <a href="#main-content" class="skip-link">Skip to main content</a>
            <!-- Header -->
            <!-- Main -->
            <!-- Script -->
        </body>
        </html>
        ```

        Should I use `<article>` for the notes? `<div role="listitem">` is sufficient since we said `role="list"` on the container. `<article>` would be semantically better inside the list.
        Yes, `<article class="note-card" role="listitem">`.

        Let's refine the card template:
        ```javascript
        const card = document.createElement('article');
        card.className = 'note-card';
        card.setAttribute('role', 'listitem');
        ...
        ```
        This makes the HTML more semantic. The `article` tag represents a complete composition.

        Let's add a "No notes yet" placeholder.
        ```javascript
        if (notesData.length === 0) {
            container.innerHTML = '<p class="placeholder">No notes found. Create one above!</p>';
            return;
        }
        ```

        Alright, let me write out the full complete `index.html` content now.

        **Double-checking the filter for owner:**
        The filter compares the `note.owner` string directly. This is fine.
        The filter for tag compares the trimmed tag values.

        **Form validation:**
        `required` attribute prevents submission on clients with valid HTML5 form validation. Our manual check `if (!title || !owner || !date)` also catches it if JS validation runs first or `novalidate` is present. Better to keep `novalidate` on the form and rely on our semantic validation + `announce()` for robustness across all cases.

        Let's add `novalidate` to the form element.
        `<form id="note-form" novalidate>`

        **Ensuring keyboard operability:**
        Buttons are `<button>` elements, which are inherently keyboard operable.
        Inputs and selects are natively keyboard operable.
        Custom focus: `<div>` elements don't need tabindex. Everything is in standard controls.

        **Stats layout on narrow screens:**
        `flex-wrap: wrap` will handle it. We might want to center the text.
        ```css
        .stat { display: flex; flex-direction: column; align-items: center; min-width: 100px; }
        ```

        **Drafting the final output:**
        (Writing the entire code in my head, ensuring syntax is perfect, then outputting).

        *   CSS Variables: Blue primary, neutral backgrounds.
        *   Skip link, aria labels, roles.
        *   Stats bar with `role="status"`.
        *   Form with `fieldset` / `legend`.
        *   Card grid `display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;`
        *   Responsive: `@media (max-width: 768px) { ... grid-template-columns: 1fr; ... }`
        *   JS functions structured cleanly, no external deps.

        Let's execute the writing.
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
        /* ---- Reset & Base ---- */
        *,
        *::before,
        *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg: #f1f5f9;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --action-bg: #fee2e2;
            --action-text: #991b1b;
            --decision-bg: #fef3c7;
            --decision-text: #92400e;
            --reference-bg: #f3f4f6;
            --reference-text: #374151;
            --tag-bg: #e0e7ff;
            --tag-text: #3730a3;
            --radius: 0.5rem;
            --shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
            --focus-ring: 3px solid var(--primary);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 1rem;
            min-height: 100vh;
        }

        /* ---- Accessibility Helpers ---- */
        .skip-link {
            position: absolute;
            top: -40px;
            left: 0;
            background: var(--primary);
            color: #fff;
            padding: 0.5rem 1rem;
            z-index: 100;
            text-decoration: none;
        }
        .skip-link:focus {
            top: 0;
            outline: var(--focus-ring);
            outline-offset: 2px;
        }

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

        /* ---- Focus Styles ---- */
        :focus-visible {
            outline: var(--focus-ring);
            outline-offset: 2px;
        }
        input:focus-visible,
        select:focus-visible,
        textarea:focus-visible,
        button:focus-visible {
            outline: var(--focus-ring);
            outline-offset: 2px;
        }

        /* ---- Header & Stats ---- */
        #app-header {
            text-align: center;
            margin-bottom: 1.5rem;
        }

        #app-header h1 {
            font-size: 1.75rem;
            color: var(--primary);
            margin-bottom: 0.75rem;
        }

        #stats {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1rem 2.5rem;
            padding: 1rem 1.5rem;
            background: var(--card-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
        }

        .stat {
            display: flex;
            flex-direction: column;
            align-items: center;
            min-width: 90px;
        }

        .stat-value {
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.2;
        }

        .stat-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-weight: 600;
        }

        /* ---- Main Layout ---- */
        #main-content {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* ---- Search & Filter Controls ---- */
        #controls {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: end;
            margin-bottom: 1.5rem;
            padding: 1rem 1.5rem;
            background: var(--card-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
        }

        .control-group {
            display: flex;
            flex-direction: column;
            flex: 1 1 180px;
            min-width: 140px;
        }

        .control-group label {
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 0.2rem;
            color: var(--text-muted);
        }

        .control-group input,
        .control-group select {
            padding: 0.5rem 0.6rem;
            border: 1px solid var(--border);
            border-radius: 4px;
            font-size: 0.95rem;
            background: var(--card-bg);
            color: var(--text);
        }

        .control-group input::placeholder {
            color: #94a3b8;
        }

        /* ---- Form Section ---- */
        #note-form-section {
            margin-bottom: 1.5rem;
        }

        #note-form-section h2 {
            font-size: 1.25rem;
            margin-bottom: 0.75rem;
        }

        #note-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem 1rem;
            padding: 1.5rem;
            background: var(--card-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group.full-width {
            grid-column: span 2;
        }

        .form-group label {
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 0.2rem;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            padding: 0.5rem 0.6rem;
            border: 1px solid var(--border);
            border-radius: 4px;
            font-size: 0.95rem;
            font-family: inherit;
            background: var(--card-bg);
            color: var(--text);
        }

        .form-group textarea {
            resize: vertical;
            min-height: 80px;
        }

        fieldset {
            grid-column: span 2;
            border: none;
            padding: 0;
        }

        fieldset legend {
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 0.4rem;
        }

        .radio-group {
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
        }

        .radio-group label {
            display: flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.9rem;
            cursor: pointer;
        }

        .radio-group input[type="radio"] {
            width: auto;
            accent-color: var(--primary);
        }

        .form-actions {
            grid-column: span 2;
            display: flex;
            gap: 0.75rem;
            align-items: center;
            margin-top: 0.5rem;
        }

        .btn-primary {
            padding: 0.65rem 1.5rem;
            background: var(--primary);
            color: #fff;
            border: none;
            border-radius: var(--radius);
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s;
        }

        .btn-primary:hover {
            background: var(--primary-hover);
        }

        .btn-cancel {
            padding: 0.65rem 1.25rem;
            background: transparent;
            color: var(--text-muted);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
        }

        .btn-cancel:hover {
            background: var(--bg);
            color: var(--text);
        }

        /* ---- Notes Section ---- */
        #notes-section h2 {
            font-size: 1.25rem;
            margin-bottom: 1rem;
        }

        #notes-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
        }

        /* ---- Note Cards ---- */
        .note-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.25rem;
            box-shadow: var(--shadow);
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
            transition: box-shadow 0.15s;
        }

        .note-card:focus-within {
            outline: 2px solid var(--primary);
            outline-offset: 2px;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.5rem;
        }

        .card-header h3 {
            font-size: 1.1rem;
            font-weight: 600;
            word-break: break-word;
        }

        .note-type {
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            padding: 0.2em 0.6em;
            border-radius: 4px;
            white-space: nowrap;
            flex-shrink: 0;
            letter-spacing: 0.02em;
        }

        .type-action {
            background: var(--action-bg);
            color: var(--action-text);
        }
        .type-decision {
            background: var(--decision-bg);
            color: var(--decision-text);
        }
        .type-reference {
            background: var(--reference-bg);
            color: var(--reference-text);
        }

        .card-meta {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--text-muted);
            gap: 0.5rem;
        }

        .card-meta time {
            flex-shrink: 0;
        }

        .card-body {
            font-size: 0.85rem;
            color: var(--text);
            line-height: 1.5;
            word-break: break-word;
            max-height: 110px;
            overflow-y: auto;
            background: var(--bg);
            padding: 0.5rem 0.6rem;
            border-radius: 4px;
        }

        .card-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.3rem;
        }

        .tag {
            background: var(--tag-bg);
            color: var(--tag-text);
            font-size: 0.7rem;
            padding: 0.1em 0.6em;
            border-radius: 4px;
            font-weight: 500;
        }

        .card-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: auto;
            padding-top: 0.25rem;
        }

        .card-actions button {
            padding: 0.35rem 0.8rem;
            border: 1px solid var(--border);
            border-radius: 4px;
            background: var(--card-bg);
            font-size: 0.85rem;
            cursor: pointer;
            font-weight: 500;
            transition: background 0.1s;
        }

        .card-actions button:hover {
            background: var(--bg);
        }

        .btn-edit {
            color: var(--primary);
        }

        .btn-delete {
            color: var(--action-text);
        }

        .placeholder {
            grid-column: 1 / -1;
            text-align: center;
            color: var(--text-muted);
            padding: 2rem;
            font-size: 1rem;
        }

        /* ---- Responsive ---- */
        @media (max-width: 768px) {
            #note-form {
                grid-template-columns: 1fr;
            }

            .form-group.full-width {
                grid-column: span 1;
            }

            fieldset {
                grid-column: span 1;
            }

            .form-actions {
                grid-column: span 1;
                flex-direction: column;
            }

            .form-actions button {
                width: 100%;
            }

            #notes-container {
                grid-template-columns: 1fr;
            }

            #controls {
                flex-direction: column;
            }

            .control-group {
                flex: 1 1 auto;
                min-width: 0;
            }

            #stats {
                gap: 0.75rem 1.5rem;
            }

            .stat {
                min-width: 70px;
            }

            .stat-value {
                font-size: 1.1rem;
            }

            .stat-label {
                font-size: 0.6rem;
            }
        }

        @media (max-width: 480px) {
            body {
                padding: 0.5rem;
            }

            #stats {
                padding: 0.75rem 1rem;
                gap: 0.5rem 1rem;
            }

            .stat {
                min-width: 60px;
            }

            #controls {
                padding: 0.75rem 1rem;
            }

            #note-form {
                padding: 1rem;
            }

            .note-card {
                padding: 1rem;
            }

            .card-meta {
                flex-direction: column;
                gap: 0.2rem;
            }
        }
    </style>
</head>
<body>

    <a href="#main-content" class="skip-link">Skip to main content</a>

    <header id="app-header">
        <h1>📋 Meeting Notes Board</h1>
        <section id="stats" aria-label="Notes Statistics" role="status">
            <div class="stat">
                <span class="stat-value" id="stat-total">0</span>
                <span class="stat-label">Total Notes</span>
            </div>
            <div class="stat">
                <span class="stat-value" id="stat-action">0</span>
                <span class="stat-label">Action Required</span>
            </div>
            <div class="stat">
                <span class="stat-value" id="stat-owners">0</span>
                <span class="stat-label">Unique Owners</span>
            </div>
            <div class="stat">
                <span class="stat-value" id="stat-tag">N/A</span>
                <span class="stat-label">Most Common Tag</span>
            </div>
        </section>
    </header>

    <main id="main-content">

        <section id="controls" aria-label="Search and filter controls">
            <div class="control-group">
                <label for="search">Search</label>
                <input type="search" id="search" placeholder="Search notes…" autocomplete="off">
            </div>
            <div class="control-group">
                <label for="filter-owner">Owner</label>
                <select id="filter-owner">
                    <option value="">All Owners</option>
                </select>
            </div>
            <div class="control-group">
                <label for="filter-tag">Tag</label>
                <select id="filter-tag">
                    <option value="">All Tags</option>
                </select>
            </div>
        </section>

        <section id="note-form-section" aria-label="Add or edit a note">
            <h2 id="form-title">Add New Note</h2>
            <form id="note-form" novalidate>
                <div class="form-group">
                    <label for="title">Title *</label>
                    <input type="text" id="title" required>
                </div>
                <div class="form-group">
                    <label for="owner">Owner *</label>
                    <input type="text" id="owner" required>
                </div>
                <div class="form-group">
                    <label for="date">Meeting Date *</label>
                    <input type="date" id="date" required>
                </div>
                <div class="form-group">
                    <label for="tags">Tags (comma separated)</label>
                    <input type="text" id="tags" placeholder="e.g. sprint, frontend">
                </div>
                <div class="form-group full-width">
                    <label for="body">Body</label>
                    <textarea id="body" rows="4"></textarea>
                </div>

                <fieldset>
                    <legend>Note Type</legend>
                    <div class="radio-group">
                        <label>
                            <input type="radio" name="type" value="action" checked>
                            Action Required
                        </label>
                        <label>
                            <input type="radio" name="type" value="decision">
                            Decision
                        </label>
                        <label>
                            <input type="radio" name="type" value="reference">
                            Reference
                        </label>
                    </div>
                </fieldset>

                <div class="form-actions">
                    <button type="submit" class="btn-primary">Add Note</button>
                    <button type="button" id="cancel-edit" class="btn-cancel" style="display:none;">Cancel</button>
                </div>
            </form>
        </section>

        <section id="notes-section" aria-label="Notes list">
            <h2>Notes</h2>
            <div id="notes-container" role="list">
                <!-- Cards are dynamically inserted here -->
            </div>
        </section>

        <div id="announcements" class="sr-only" aria-live="polite"></div>

    </main>

    <script>
        (function() {
            'use strict';

            // ---- State ----
            let notes = [];
            let editingId = null;
            const currentFilters = {
                query: '',
                owner: '',
                tag: ''
            };

            // ---- DOM refs ----
            const statsTotal = document.getElementById('stat-total');
            const statsAction = document.getElementById('stat-action');
            const statsOwners = document.getElementById('stat-owners');
            const statsTag = document.getElementById('stat-tag');
            const filterOwner = document.getElementById('filter-owner');
            const filterTag = document.getElementById('filter-tag');
            const searchInput = document.getElementById('search');
            const notesContainer = document.getElementById('notes-container');
            const noteForm = document.getElementById('note-form');
            const formTitle = document.getElementById('form-title');
            const submitBtn = noteForm.querySelector('button[type="submit"]');
            const cancelEditBtn = document.getElementById('cancel-edit');
            const titleInput = document.getElementById('title');
            const ownerInput = document.getElementById('owner');
            const dateInput = document.getElementById('date');
            const tagsInput = document.getElementById('tags');
            const bodyInput = document.getElementById('body');
            const typeRadios = noteForm.querySelectorAll('input[name="type"]');
            const announcer = document.getElementById('announcements');

            // ---- Storage helpers ----
            function saveNotes(data) {
                try {
                    localStorage.setItem('meetingNotes', JSON.stringify(data));
                } catch (e) {
                    console.error('localStorage save failed:', e);
                }
            }

            function loadNotes() {
                try {
                    const data = localStorage.getItem('meetingNotes');
                    return data ? JSON.parse(data) : [];
                } catch (e) {
                    console.error('localStorage load failed:', e);
                    return [];
                }
            }

            // ---- Announce for screen readers ----
            function announce(message) {
                if (announcer) {
                    announcer.textContent = '';
                    setTimeout(function() {
                        announcer.textContent = message;
                    }, 100);
                }
            }

            // ---- Escape HTML ----
            function escapeHtml(unsafe) {
                if (!unsafe && unsafe !== 0) return '';
                return String(unsafe)
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
            }

            // ---- Filter logic ----
            function getFilteredNotes() {
                return notes.filter(function(note) {
                    var searchStr = (
                        (note.title || '') + ' ' +
                        (note.body || '') + ' ' +
                        (note.owner || '') + ' ' +
                        (note.tags || '')
                    ).toLowerCase();
                    var queryMatch = !currentFilters.query ||
                        searchStr.includes(currentFilters.query.toLowerCase());
                    var ownerMatch = !currentFilters.owner ||
                        note.owner === currentFilters.owner;
                    var tagMatch = !currentFilters.tag ||
                        (note.tags && note.tags.split(',').map(function(t) { return t.trim(); })
                            .includes(currentFilters.tag));
                    return queryMatch && ownerMatch && tagMatch;
                });
            }

            // ---- Render Stats ----
            function renderStats(notesData) {
                var total = notesData.length;
                var actionCount = notesData.filter(function(n) { return n.type === 'action'; }).length;
                var uniqueOwners = new Set(notesData.map(function(n) { return n.owner; })).size;

                var tagCounts = {};
                notesData.forEach(function(n) {
                    if (n.tags) {
                        n.tags.split(',').map(function(t) { return t.trim(); }).filter(Boolean).forEach(
                        function(t) {
                            tagCounts[t] = (tagCounts[t] || 0) + 1;
                        });
                    }
                });
                var mostCommonTag = 'N/A';
                var maxCount = 0;
                for (var tag in tagCounts) {
                    if (tagCounts.hasOwnProperty(tag) && tagCounts[tag] > maxCount) {
                        maxCount = tagCounts[tag];
                        mostCommonTag = tag;
                    }
                }

                statsTotal.textContent = total;
                statsAction.textContent = actionCount;
                statsOwners.textContent = uniqueOwners;
                statsTag.textContent = mostCommonTag;
            }

            // ---- Populate filter dropdowns ----
            function populateFilters() {
                var owners = [];
                var tags = [];
                notes.forEach(function(n) {
                    if (n.owner && owners.indexOf(n.owner) === -1) owners.push(n.owner);
                    if (n.tags) {
                        n.tags.split(',').map(function(t) { return t.trim(); }).filter(Boolean).forEach(
                        function(t) {
                            if (tags.indexOf(t) === -1) tags.push(t);
                        });
                    }
                });
                owners.sort();
                tags.sort();

                var prevOwner = filterOwner.value;
                var prevTag = filterTag.value;

                var ownerHtml = '<option value="">All Owners</option>';
                owners.forEach(function(o) {
                    ownerHtml += '<option value="' + escapeHtml(o) + '">' + escapeHtml(o) + '</option>';
                });
                filterOwner.innerHTML = ownerHtml;
                filterOwner.value = prevOwner;

                var tagHtml = '<option value="">All Tags</option>';
                tags.forEach(function(t) {
                    tagHtml += '<option value="' + escapeHtml(t) + '">' + escapeHtml(t) + '</option>';
                });
                filterTag.innerHTML = tagHtml;
                filterTag.value = prevTag;
            }

            // ---- Render Notes ----
            function renderNotes(notesData) {
                if (notesData.length === 0) {
                    notesContainer.innerHTML = '<p class="placeholder" role="listitem">No notes found. Create one above!</p>';
                    return;
                }

                var html = '';
                notesData.forEach(function(note) {
                    var tagsHtml = '';
                    if (note.tags) {
                        tagsHtml = note.tags.split(',').map(function(t) {
                            return '<span class="tag">' + escapeHtml(t.trim()) + '</span>';
                        }).join('');
                    }

                    html +=
                        '<article class="note-card" role="listitem">' +
                        '<div class="card-header">' +
                        '<h3>' + escapeHtml(note.title) + '</h3>' +
                        '<span class="note-type type-' + escapeHtml(note.type) + '">' + escapeHtml(note.type) +
                        '</span>' +
                        '</div>' +
                        '<div class="card-meta">' +
                        '<span>Owner: ' + escapeHtml(note.owner) + '</span>' +
                        '<time datetime="' + escapeHtml(note.date) + '">' + escapeHtml(note.date) + '</time>' +
                        '</div>' +
                        '<div class="card-body">' + escapeHtml(note.body) + '</div>' +
                        '<div class="card-tags">' + tagsHtml + '</div>' +
                        '<div class="card-actions">' +
                        '<button class="btn-edit" data-id="' + note.id + '" aria-label="Edit note: ' + escapeHtml(note
                            .title) + '">Edit</button>' +
                        '<button class="btn-delete" data-id="' + note.id + '" aria-label="Delete note: ' + escapeHtml(
                            note.title) + '">Delete</button>' +
                        '</div>' +
                        '</article>';
                });
                notesContainer.innerHTML = html;

                // Attach listeners
                notesContainer.querySelectorAll('.btn-edit').forEach(function(btn) {
                    btn.addEventListener('click', function() { editNote(btn.dataset.id); });
                });
                notesContainer.querySelectorAll('.btn-delete').forEach(function(btn) {
                    btn.addEventListener('click', function() { deleteNote(btn.dataset.id); });
                });

                announce('Showing ' + notesData.length + ' note' + (notesData.length !== 1 ? 's' : '') + '.');
            }

            // ---- Update whole UI ----
            function updateUI() {
                var filtered = getFilteredNotes();
                renderStats(filtered);
                populateFilters();
                renderNotes(filtered);
            }

            // ---- CRUD: Add / Update ----
            function handleFormSubmit(e) {
                e.preventDefault();

                var title = titleInput.value.trim();
                var owner = ownerInput.value.trim();
                var date = dateInput.value;
                var tags = tagsInput.value.trim();
                var body = bodyInput.value.trim();
                var typeEl = noteForm.querySelector('input[name="type"]:checked');
                var type = typeEl ? typeEl.value : 'action';

                if (!title || !owner || !date) {
                    announce('Please fill in Title, Owner, and Date.');
                    return;
                }

                if (editingId) {
                    var index = -1;
                    for (var i = 0; i < notes.length; i++) {
                        if (notes[i].id === editingId) { index = i; break; }
                    }
                    if (index !== -1) {
                        notes[index] = {
                            ...notes[index],
                            title: title,
                            owner: owner,
                            date: date,
                            tags: tags,
                            body: body,
                            type: type,
                            updatedAt: new Date().toISOString()
                        };
                        announce('Note "' + title + '" updated.');
                    }
                    cancelEdit();
                } else {
                    var newNote = {
                        id: Date.now().toString(36) + Math.random().toString(36).substring(2, 8),
                        title: title,
                        owner: owner,
                        date: date,
                        tags: tags,
                        body: body,
                        type: type,
                        createdAt: new Date().toISOString(),
                        updatedAt: new Date().toISOString()
                    };
                    notes.push(newNote);
                    announce('Note "' + title + '" added.');
                    noteForm.reset();
                }

                saveNotes(notes);
                updateUI();
            }

            // ---- CRUD: Edit ----
            function editNote(id) {
                var note = null;
                for (var i = 0; i < notes.length; i++) {
                    if (notes[i].id === id) { note = notes[i]; break; }
                }
                if (!note) return;

                titleInput.value = note.title;
                ownerInput.value = note.owner;
                dateInput.value = note.date;
                tagsInput.value = note.tags || '';
                bodyInput.value = note.body || '';
                for (var j = 0; j < typeRadios.length; j++) {
                    if (typeRadios[j].value === note.type) {
                        typeRadios[j].checked = true;
                        break;
                    }
                }

                editingId = id;
                formTitle.textContent = 'Edit Note';
                submitBtn.textContent = 'Save Changes';
                cancelEditBtn.style.display = 'inline-block';
                document.getElementById('note-form-section').scrollIntoView({ behavior: 'smooth' });
                titleInput.focus();
            }

            // ---- CRUD: Cancel Edit ----
            function cancelEdit() {
                editingId = null;
                noteForm.reset();
                formTitle.textContent = 'Add New Note';
                submitBtn.textContent = 'Add Note';
                cancelEditBtn.style.display = 'none';
                announce('Edit cancelled.');
            }

            // ---- CRUD: Delete ----
            function deleteNote(id) {
                var note = null;
                for (var i = 0; i < notes.length; i++) {
                    if (notes[i].id === id) { note = notes[i]; break; }
                }
                if (!note) return;
                if (!confirm('Delete note "' + note.title + '"?')) return;

                notes = notes.filter(function(n) { return n.id !== id; });
                saveNotes(notes);
                updateUI();
                announce('Note "' + note.title + '" deleted.');
            }

            // ---- Init ----
            function init() {
                notes = loadNotes();

                noteForm.addEventListener('submit', handleFormSubmit);
                cancelEditBtn.addEventListener('click', cancelEdit);

                searchInput.addEventListener('input', function(e) {
                    currentFilters.query = e.target.value;
                    updateUI();
                });
                filterOwner.addEventListener('change', function(e) {
                    currentFilters.owner = e.target.value;
                    updateUI();
                });
                filterTag.addEventListener('change', function(e) {
                    currentFilters.tag = e.target.value;
                    updateUI();
                });

                updateUI();
            }

            document.addEventListener('DOMContentLoaded', init);
        })();
    </script>

</body>
</html>
```
````
