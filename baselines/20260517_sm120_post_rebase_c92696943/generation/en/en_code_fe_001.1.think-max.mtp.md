# Generation Transcript

- Case: `en_code_fe_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 97.233019
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 305, "total_tokens": 18070, "completion_tokens": 17765, "prompt_tokens_details": null}`
- Prompt tokens: 305
- Completion tokens: 17765
- Total tokens: 18070

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
    *   **Output:** Only the content of `index.html` (HTML, CSS, JavaScript). No explanatory text.
    *   **Constraints:**
        *   Single file (`index.html`).
        *   No external libraries, CDNs, images, or build tools.
        *   Total code under 1000 lines.
        *   Basic accessible: labels, keyboard navigation, visible focus.
    *   **Functional Requirements:**
        1.  Add notes (title, owner, meeting date, tags, body).
        2.  Notes appear as cards. Filters (owner, tag, free-text search).
        3.  Note types: “Action Required”, “Decision”, “Reference”.
        4.  Edit and delete notes.
        5.  Persist in `localStorage`.
        6.  Statistics strip: total notes, action-required count, unique owners, most common tag.
        7.  Responsive layout: two-column grid (wide), single column (narrow).
    *   **Output Format:** Only the raw HTML content.

2.  **Deconstruct the UI/UX:**
    *   **Header:** Title "Meeting Notes Board". Stats strip.
    *   **Filters Section:**
        *   Owner dropdown (populated from unique owners in notes).
        *   Tag filter (dropdown or free-text).
        *   Free-text search input.
    *   **Add/Edit Note Form (Modal or inline):**
        *   Title input (`id`, `label`).
        *   Owner input (`id`, `label`).
        *   Meeting Date input (`id`, `label`).
        *   Tags input/textarea (`id`, `label`). (Let's use a text input where users type tags separated by commas).
        *   Body textarea (`id`, `label`).
        *   Note Type radio buttons or dropdown ("Action Required", "Decision", "Reference").
        *   Submit/Cancel buttons.
    *   **Notes Grid:**
        *   Cards displaying all info.
        *   Edit/Delete buttons per card.
    *   **Accessibility:**
        *   `aria-label`, `role`, `tabindex`, `focus()` triggers.
        *   Semantic HTML (`<header>`, `<main>`, `<section>`, `<form>`, `<button>`, `<h1>`, `<h2>`, `<h3>`).

3.  **Data Model (JSON in localStorage):**
    ```json
    {
      "notes": [
        {
          "id": "uuid",
          "title": "string",
          "owner": "string",
          "date": "YYYY-MM-DD",
          "tags": ["tag1", "tag2"],
          "body": "string",
          "type": "action" | "decision" | "reference",
          "createdAt": "timestamp"
        }
      ]
    }
    Key for localStorage: `meetingNotesBoardData`
    ```

4.  **Stats Strip Logic:**
    *   Total notes: `data.notes.length`
    *   Action required count: `data.notes.filter(n => n.type === 'action').length`
    *   Unique owners: `new Set(data.notes.map(n => n.owner)).size`
    *   Most common tag:
        *   Flatten all tags.
        *   Count occurrences.
        *   Find max.

5.  **Filtering Logic:**
    *   `currentOwnerFilter` (string)
    *   `currentTagFilter` (string)
    *   `currentSearchFilter` (string)
    *   Filter `data.notes` based on these.

6.  **CRUD Operations:**
    *   **Create:** Form submission generates ID, pushes to `data.notes`, saves, re-renders.
    *   **Read:** Renders filtered notes.
    *   **Update:** Edit button populates form with note data. Submit updates the existing note by ID.
    *   **Delete:** Delete button removes note by ID. Confirmation? The spec doesn't strictly say confirmation, but it's good UX. I will add a simple `confirm()` dialog for deletion.

7.  **HTML Structure (Draft):**
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Meeting Notes Board</title>
        <style>...</style>
    </head>
    <body>
        <header>
            <h1>Meeting Notes Board</h1>
            <div class="stats" aria-live="polite">
                <!-- Stats injected by JS -->
            </div>
        </header>
        <main>
            <section class="filters" aria-label="Filters">
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
                    <label for="filter-search">Search</label>
                    <input type="search" id="filter-search" placeholder="Search title or body...">
                </div>
            </section>
            <section class="controls">
                <button id="open-add-modal">+ Add Note</button>
            </section>
            <section class="notes-grid" aria-label="Notes" id="notes-grid">
                <!-- Cards injected by JS -->
            </section>
        </main>

        <!-- Modal for Add/Edit -->
        <div class="modal-overlay" id="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
            <div class="modal-content">
                <h2 id="modal-title">Add Note</h2>
                <form id="note-form">
                    <input type="hidden" id="note-id" value="">
                    <!-- ... fields ... -->
                    <div class="form-actions">
                        <button type="submit">Save</button>
                        <button type="button" id="cancel-modal">Cancel</button>
                    </div>
                </form>
            </div>
        </div>

        <script>...</script>
    </body>
    </html>
    ```

8.  **CSS Styling (Draft):**
    *   CSS Custom Properties for theming.
    *   Flexbox/Grid layout.
    *   `.notes-grid` with `grid-template-columns: repeat(2, 1fr)` for wide.
    *   `@media (max-width: 768px) { .notes-grid { grid-template-columns: 1fr; } }`
    *   Modal styling (fixed overlay, centered content).
    *   Visible focus states: `:focus-visible { outline: 2px solid blue; outline-offset: 2px; }`.
    *   Card styling (border, shadow, padding, type colors/badges).

9.  **JavaScript Logic (Draft):**
    *   `const STORAGE_KEY = 'meetingNotesBoardData';`
    *   `let data = { notes: [] };`
    *   `let editingId = null;`
    *   `let filterState = { owner: '', tag: '', search: '' };`
    *   Functions:
        *   `loadData()`
        *   `saveData()`
        *   `generateId()`
        *   `getStats()` -> `{ total, actionCount, uniqueOwners, mostCommonTag }`
        *   `renderStats()`
        *   `getFilteredNotes()`
        *   `renderNotes()`
        *   `renderFilters()`
        *   `openModal(note = null)`
        *   `closeModal()`
        *   `handleFormSubmit(e)`
        *   `handleDeleteNote(id)`
        *   `setupEventListeners()`
        *   `init()`

10. **Refining the Code Details:**

    *   **Tags:** Input as comma-separated string. Convert to array for storage. Sort tags in stats.
    *   **Date:** Input type `date`.
    *   **Owner:** Input type `text` (simpler than managing a predefined team list, but filter dropdown should aggregate unique owners from existing notes). Wait, the spec says "filtered by owner, tag, and free-text search". A dropdown for owner makes sense, populated dynamically. A text input for adding an owner also works.
    *   **Most Common Tag:** Find the tag with the highest count across all notes. If tie, the first one alphabetically or just the first one found.
    *   **Editing ID:** Use a hidden input or a global variable.
    *   **Accessibility:**
        *   `aria-live="polite"` on stats.
        *   Labels for inputs.
        *   Keyboard event handlers (Enter to submit, Escape to close modal).
        *   Focus management: when modal opens, focus the first input. When modal closes, return focus to the button that opened it.
        *   `tabindex` for proper order.
    *   **Under 1000 lines:** Very generous limit. The task is easily doable within 500 lines. I will focus on clean, well-structured code. I should avoid unnecessary verbosity.

11. **Check requirements against the plan:**
    1.  *Add a note with title, owner, meeting date, tags, and body.* -> Form handles this.
    2.  *Cards filtered by owner, tag, free-text search.* -> Filters section, dynamic filtering.
    3.  *Mark as Action Required, Decision, Reference.* -> Radio buttons or dropdown. Dropdown is cleaner for a select. Let's use a `<select>` for note type.
    4.  *Edit and delete notes.* -> Edit/Delete buttons on cards.
    5.  *Persist in localStorage.* -> `loadData`/`saveData`.
    6.  *Stats strip: total, action-required, unique owners, most common tag.* -> Dedicated function.
    7.  *Responsive layout.* -> CSS Grid with media query.
    8.  *Accessibility.* -> Labels, keyboard, focus states.
    *All covered.*

12. **Detailed Code Construction (Mental Sandbox):**

    **HTML:**
    ```html
    <!-- Stats -->
    <div class="stats">
        <span id="stat-total">Total: 0</span>
        <span id="stat-actions">Actions: 0</span>
        <span id="stat-owners">Owners: 0</span>
        <span id="stat-top-tag">Top Tag: N/A</span>
    </div>
    ```

    **CSS (Minimalist but clean):**
    *   Root: `--color-primary: #4361ee; --color-action: #ef476f; --color-decision: #06d6a0; --color-reference: #ffd166; --bg: #f8f9fa;`
    *   Body: `font-family: system-ui, sans-serif;`
    *   Card actions: `position: absolute; top: 0.5rem; right: 0.5rem;`
    *   Type badge: `padding: 0.25em 0.5em; border-radius: 4px;`
    *   Focus visible: `:focus-visible { outline: 3px solid var(--color-primary); outline-offset: 2px; }`

    **JavaScript:**
    *   `let data = { notes: [] };`
    *   `let editingNoteId = null;`
    *   `let previousOwningButton = null;` // for focus management on modal close

    *   `loadData()`:
        ```javascript
        function loadData() {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {
                try { data = JSON.parse(raw); } catch(e) { data = { notes: [] }; }
            }
            if (!data.notes) data.notes = [];
        }
        function saveData() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        }
        ```

    *   `generateId()`:
        ```javascript
        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substring(2, 7);
        }
        ```

    *   `getStats()`:
        ```javascript
        function getStats() {
            const notes = data.notes;
            const total = notes.length;
            const actionCount = notes.filter(n => n.type === 'action').length;
            const uniqueOwners = new Set(notes.map(n => n.owner.toLowerCase().trim())).size;
            const tagCounts = {};
            notes.forEach(n => {
                (n.tags || []).forEach(t => {
                    const tag = t.trim().toLowerCase();
                    if (tag) tagCounts[tag] = (tagCounts[tag] || 0) + 1;
                });
            });
            let mostCommonTag = null;
            let maxCount = 0;
            for (const [tag, count] of Object.entries(tagCounts)) {
                if (count > maxCount) {
                    mostCommonTag = tag;
                    maxCount = count;
                }
            }
            return { total, actionCount, uniqueOwners, mostCommonTag };
        }
        ```

    *   `renderStats()`:
        ```javascript
        function renderStats() {
            const stats = getStats();
            document.getElementById('stat-total').textContent = `Total: ${stats.total}`;
            document.getElementById('stat-actions').textContent = `Actions: ${stats.actionCount}`;
            document.getElementById('stat-owners').textContent = `Owners: ${stats.uniqueOwners}`;
            document.getElementById('stat-top-tag').textContent = `Top Tag: ${stats.mostCommonTag || 'N/A'}`;
        }
        ```

    *   `getFilteredNotes()`:
        ```javascript
        function getFilteredNotes() {
            const ownerFilter = document.getElementById('filter-owner').value.toLowerCase();
            const tagFilter = document.getElementById('filter-tag').value.toLowerCase();
            const searchFilter = document.getElementById('filter-search').value.toLowerCase();

            return data.notes.filter(note => {
                if (ownerFilter && !note.owner.toLowerCase().includes(ownerFilter) &&
                    note.owner.toLowerCase() !== ownerFilter) {
                    // If the dropdown value is an exact owner, check exact match
                    // If the dropdown value is just a text filter, use includes. Let's use exact match for dropdown.
                    if (note.owner.toLowerCase() !== ownerFilter) return false;
                }
                // Actually, let's make the dropdown populate unique owners and filter by exact match.
                if (tagFilter && !(note.tags || []).some(t => t.toLowerCase() === tagFilter)) {
                    return false;
                }
                if (searchFilter) {
                    const searchTerm = searchFilter.toLowerCase();
                    const titleMatch = note.title.toLowerCase().includes(searchTerm);
                    const bodyMatch = note.body.toLowerCase().includes(searchTerm);
                    const ownerMatch = note.owner.toLowerCase().includes(searchTerm);
                    const tagsMatch = (note.tags || []).some(t => t.toLowerCase().includes(searchTerm));
                    if (!titleMatch && !bodyMatch && !ownerMatch && !tagsMatch) return false;
                }
                return true;
            });
        }
        ```
        *Correction on owner filter:* The filter dropdown should list unique owners. Selecting one should filter by exact match. The search bar provides the text search.

    *   `populateFilterDropdowns()`:
        ```javascript
        function populateFilterDropdowns() {
            const owners = [...new Set(data.notes.map(n => n.owner.trim()).filter(Boolean))].sort();
            const tags = [...new Set(data.notes.flatMap(n => n.tags || []).map(t => t.trim()).filter(Boolean))].sort();

            const ownerSelect = document.getElementById('filter-owner');
            const tagSelect = document.getElementById('filter-tag');

            const currentOwner = ownerSelect.value;
            const currentTag = tagSelect.value;

            ownerSelect.innerHTML = '<option value="">All Owners</option>' + owners.map(o => `<option value="${o}" ${o === currentOwner ? 'selected' : ''}>${o}</option>`).join('');
            tagSelect.innerHTML = '<option value="">All Tags</option>' + tags.map(t => `<option value="${t}" ${t === currentTag ? 'selected' : ''}>${t}</option>`).join('');
        }
        ```

    *   `renderNotes()`:
        ```javascript
        function renderNotes() {
            const filteredNotes = getFilteredNotes();
            const grid = document.getElementById('notes-grid');
            grid.innerHTML = '';
            if (filteredNotes.length === 0) {
                grid.innerHTML = '<p class="empty-state">No notes match your filters.</p>';
                return;
            }
            filteredNotes.forEach(note => {
                const card = document.createElement('article');
                card.className = 'note-card';
                card.setAttribute('aria-label', `Note: ${note.title}`);
                card.dataset.id = note.id;

                const typeColors = { action: 'var(--color-action)', decision: 'var(--color-decision)', reference: 'var(--color-reference)' };
                const typeLabels = { action: 'Action Required', decision: 'Decision', reference: 'Reference' };

                card.innerHTML = `
                    <div class="card-header">
                        <h3 class="card-title">${escapeHtml(note.title)}</h3>
                        <span class="card-type" style="background: ${typeColors[note.type] || '#ccc'};">${typeLabels[note.type] || note.type}</span>
                    </div>
                    <div class="card-meta">
                        <span>👤 ${escapeHtml(note.owner)}</span>
                        <span>📅 ${note.date || 'N/A'}</span>
                    </div>
                    <div class="card-tags">
                        ${(note.tags || []).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}
                    </div>
                    <p class="card-body">${escapeHtml(note.body)}</p>
                    <div class="card-actions">
                        <button class="btn-edit" data-id="${note.id}" aria-label="Edit ${note.title}">Edit</button>
                        <button class="btn-delete" data-id="${note.id}" aria-label="Delete ${note.title}">Delete</button>
                    </div>
                `;
                grid.appendChild(card);
            });

            // Attach event listeners to cards
            document.querySelectorAll('.btn-edit').forEach(btn => {
                btn.addEventListener('click', () => openModalForEdit(btn.dataset.id));
            });
            document.querySelectorAll('.btn-delete').forEach(btn => {
                btn.addEventListener('click', () => handleDelete(btn.dataset.id));
            });
        }
        ```
        *Self-Correction on `escapeHtml`:* Need an HTML escaping function to prevent XSS.
        ```javascript
        function escapeHtml(unsafe) {
            if (!unsafe) return '';
            return unsafe.toString()
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
        ```

    *   `Modal Logic`:
        ```javascript
        const modalOverlay = document.getElementById('modal-overlay');
        const modalTitle = document.getElementById('modal-title');
        const noteForm = document.getElementById('note-form');
        const noteIdInput = document.getElementById('note-id');
        const titleInput = document.getElementById('note-title');
        const ownerInput = document.getElementById('note-owner');
        const dateInput = document.getElementById('note-date');
        const tagInput = document.getElementById('note-tags');
        const bodyTextarea = document.getElementById('note-body');
        const typeSelect = document.getElementById('note-type');
        const cancelBtn = document.getElementById('cancel-modal');
        const addNoteBtn = document.getElementById('open-add-modal');

        function openModalForAdd() {
            editingNoteId = null;
            modalTitle.textContent = 'Add Note';
            noteForm.reset();
            noteIdInput.value = '';
            // Set default date
            dateInput.value = new Date().toISOString().split('T')[0];
            modalOverlay.style.display = 'flex';
            titleInput.focus();
            previousOwningButton = addNoteBtn;
        }

        function openModalForEdit(id) {
            const note = data.notes.find(n => n.id === id);
            if (!note) return;
            editingNoteId = id;
            modalTitle.textContent = 'Edit Note';
            noteIdInput.value = id;
            titleInput.value = note.title || '';
            ownerInput.value = note.owner || '';
            dateInput.value = note.date || '';
            tagInput.value = (note.tags || []).join(', ');
            bodyTextarea.value = note.body || '';
            typeSelect.value = note.type || 'reference';
            modalOverlay.style.display = 'flex';
            titleInput.focus();
            previousOwningButton = document.querySelector(`.btn-edit[data-id="${id}"]`);
        }

        function closeModal() {
            modalOverlay.style.display = 'none';
            if (previousOwningButton) {
                previousOwningButton.focus();
                previousOwningButton = null;
            } else {
                addNoteBtn.focus();
            }
        }

        // Event listeners for modal
        addNoteBtn.addEventListener('click', openModalForAdd);
        cancelBtn.addEventListener('click', closeModal);
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeModal();
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modalOverlay.style.display === 'flex') {
                closeModal();
            }
        });
        ```

    *   `Form Submission`:
        ```javascript
        noteForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const title = titleInput.value.trim();
            const owner = ownerInput.value.trim();
            const date = dateInput.value;
            const tags = tagInput.value.split(',').map(t => t.trim()).filter(Boolean);
            const body = bodyTextarea.value.trim();
            const type = typeSelect.value;

            if (!title || !owner) {
                alert('Title and Owner are required.');
                return;
            }

            const noteData = { title, owner, date, tags, body, type };

            if (editingNoteId) {
                const index = data.notes.findIndex(n => n.id === editingNoteId);
                if (index > -1) {
                    data.notes[index] = { ...data.notes[index], ...noteData };
                }
            } else {
                noteData.id = generateId();
                noteData.createdAt = new Date().toISOString();
                data.notes.push(noteData);
            }

            saveData();
            closeModal();
            refreshUI();
        });
        ```

    *   `Handle Delete`:
        ```javascript
        function handleDelete(id) {
            if (!confirm('Are you sure you want to delete this note?')) return;
            data.notes = data.notes.filter(n => n.id !== id);
            saveData();
            refreshUI();
        }
        ```

    *   `Refresh UI`:
        ```javascript
        function refreshUI() {
            populateFilterDropdowns();
            renderNotes();
            renderStats();
        }
        ```

    *   `Init`:
        ```javascript
        function init() {
            loadData();
            // Ensure notes exist
            if (!data.notes) data.notes = [];
            // Add some sample data if empty? The spec doesn't ask for it, but it makes demoing easier. I will skip it to keep code focused, or add a couple of example notes for the user to see. "Build an accessible 'meeting notes board' for a small team." Usually, having sample data is beneficial for showcasing. Let's add a small sample data block if the array is empty, just so the UI isn't completely blank on first load. Actually, providing sample data can make the code feel complete. Let's do it.
            if (data.notes.length === 0) {
                data.notes = [
                    { id: 'sample1', title: 'Design Review', owner: 'Alice', date: '2024-05-20', tags: ['design', 'frontend'], body: 'Review the new component designs.', type: 'decision', createdAt: '2024-05-20T10:00:00Z' },
                    { id: 'sample2', title: 'API Integration', owner: 'Bob', date: '2024-05-21', tags: ['backend', 'api'], body: 'Finalize the API endpoints for the user module.', type: 'action', createdAt: '2024-05-21T14:00:00Z' },
                    { id: 'sample3', title: 'Weekly Sync Notes', owner: 'Charlie', date: '2024-05-22', tags: ['meeting'], body: 'General updates from the team.', type: 'reference', createdAt: '2024-05-22T09:00:00Z' },
                ];
                saveData();
            }

            refreshUI();
        }
        ```

    *   **Filter Event Listeners:**
        ```javascript
        document.getElementById('filter-owner').addEventListener('change', () => {
            renderNotes();
            renderStats(); // Stats might change based on filter? No, the spec says "compact statistics strip: total notes, action-required count, unique owners, and most common tag." This usually implies total stats for the whole board, not filtered. If it's filtered stats, it would say "filtered". I will make it *total* stats for the whole board, but it's easy to change. Let's read the spec again: "Provide a compact statistics strip: total notes, action-required count, unique owners, and most common tag." This sounds like *board-wide* stats. Yes. I will keep `renderStats()` showing total, unfiltered stats. `renderNotes()` is for the filtered view.

        // Let's refine: `renderStats()` shows global stats. `renderNotes()` shows filtered.

        document.getElementById('filter-owner').addEventListener('change', renderNotes);
        document.getElementById('filter-tag').addEventListener('change', renderNotes);
        document.getElementById('filter-search').addEventListener('input', renderNotes);
        // Wait, if filters change, the cards change, but stats stay. `refreshUI()` calls both. The filter listeners should just call `renderNotes()`.

        // Actually, the stats strip could reflect the *visible* notes, which is a nice dynamic touch. "total notes, action-required count, unique owners, and most common tag." It doesn't strictly say "filtered". To maintain simplicity and clear spec compliance, I will just render stats based on the *whole* dataset. Let's re-read: "Provide a compact statistics strip: total notes, action-required count, unique owners, and most common tag." "for a small team". It sounds like board-wide stats. I will stick to board-wide stats.
        ```

    *   **Refining Modal Focus Management:**
        When the modal opens, the first focusable element should be the title input. When it closes, focus returns to the button that triggered it (either the Add Note button or the specific Edit button). The code above handles this.

    *   **Refining CSS for Accessibility and Layout:**
        *   `* { box-sizing: border-box; }`
        *   Body: `background: #f0f2f5; min-height: 100vh;`
        *   Header: `background: white; padding: 1rem 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);`
        *   Stats: `display: flex; gap: 1.5rem; flex-wrap: wrap;`
        *   Stats items: `font-size: 0.9rem; color: #555;`
        *   Main: `max-width: 1200px; margin: 2rem auto; padding: 0 2rem;`
        *   Filters: `display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; align-items: flex-end;`
        *   Filter group label: `display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.25rem;`
        *   Filter group input/select: `padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; font-size: 0.9rem;`
        *   Controls (Add button): `margin-bottom: 1.5rem;`
        *   Notes Grid: `display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem;`
        *   @media (max-width: 768px): `.notes-grid { grid-template-columns: 1fr; }`
        *   Card: `background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); position: relative; border-left: 4px solid;`
        *   Card type classes or inline style for border color.
        *   Card header: `display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem;`
        *   Card title: `margin: 0 0 0.5rem 0; font-size: 1.1rem;`
        *   Card type badge: `font-size: 0.75rem; padding: 0.2rem 0.6rem; border-radius: 4px; font-weight: 600; white-space: nowrap;`
        *   Card meta: `font-size: 0.85rem; color: #666; margin-bottom: 0.5rem; display: flex; gap: 1rem;`
        *   Card tags: `display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.75rem;`
        *   Tag: `background: #e0e7ff; color: #3730a3; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.8rem;`
        *   Card body: `font-size: 0.9rem; color: #333; line-height: 1.5; margin-bottom: 1rem;`
        *   Card actions: `display: flex; gap: 0.5rem; justify-content: flex-end; border-top: 1px solid #eee; padding-top: 1rem;`
        *   Card actions buttons: `padding: 0.4rem 0.8rem; border: 1px solid #ccc; background: white; border-radius: 4px; cursor: pointer; font-size: 0.85rem;`
        *   `button:hover:not(:disabled) { background: #f0f0f0; }`
        *   Modal Overlay: `position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; display: none;`
        *   Modal Content: `background: white; border-radius: 12px; padding: 2rem; max-width: 600px; width: 90%; max-height: 90vh; overflow-y: auto;`
        *   Form: `display: flex; flex-direction: column; gap: 1rem;`
        *   Form groups: `display: flex; flex-direction: column;`
        *   Form label: `font-weight: 600; margin-bottom: 0.25rem;`
        *   Form input, textarea, select: `padding: 0.6rem; border: 1px solid #ccc; border-radius: 4px; font-size: 0.95rem;`
        *   Form textarea: `min-height: 100px; resize: vertical;`
        *   Form actions: `display: flex; gap: 1rem; justify-content: flex-end; margin-top: 0.5rem;`
        *   Form actions button: `padding: 0.6rem 1.5rem; border-radius: 6px; cursor: pointer; font-weight: 600;`
        *   Button primary: `background: var(--color-primary); color: white; border: none;`
        *   Button secondary: `background: white; border: 1px solid #ccc;`
        *   Add Note button: `padding: 0.75rem 1.5rem; background: var(--color-primary); color: white; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer;`

    *   **Focus Patterns:**
        `:focus-visible` is great. I will add:
        ```css
        :focus-visible {
            outline: 2px solid var(--color-primary);
            outline-offset: 2px;
        }
        button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {
            outline: 2px solid var(--color-primary);
            outline-offset: 2px;
            border-color: var(--color-primary);
        }
        ```

    *   **Checking stats rendering:**
        The stats section is `aria-live="polite"` so screen readers announce updates.
        ```html
        <div class="stats" aria-live="polite">
            <span id="stat-total">Total: 0</span>
            <span id="stat-actions">Actions: 0</span>
            <span id="stat-owners">Owners: 0</span>
            <span id="stat-top-tag">Top Tag: N/A</span>
        </div>
        ```

    *   **Filter dropdown population bug fix:**
        Previously I used `populateFilterDropdowns()` in `refreshUI()`. This updates the filter options.
        If a user is filtering by "Bob", and a note with owner "Bob" is deleted, "Bob" should disappear from the dropdown. If the current selection is "Bob", we must keep it, or reset it to "All Owners". It's safer to reset to the current value if it still exists, otherwise reset to `""`.
        ```javascript
        function populateFilterDropdowns() {
            const owners = [...new Set(data.notes.map(n => n.owner.trim()).filter(Boolean))].sort((a,b) => a.localeCompare(b));
            const tags = [...new Set(data.notes.flatMap(n => n.tags || []).map(t => t.trim()).filter(Boolean))].sort((a,b) => a.localeCompare(b));

            const ownerSelect = document.getElementById('filter-owner');
            const tagSelect = document.getElementById('filter-tag');

            const selectedOwner = ownerSelect.value;
            const selectedTag = tagSelect.value;

            ownerSelect.innerHTML = '<option value="">All Owners</option>' + owners.map(o => `<option value="${o}" ${o === selectedOwner ? 'selected' : ''}>${o}</option>`).join('');
            if (!owners.includes(selectedOwner)) {
                ownerSelect.value = '';
            }

            tagSelect.innerHTML = '<option value="">All Tags</option>' + tags.map(t => `<option value="${t}" ${t === selectedTag ? 'selected' : ''}>${t}</option>`).join('');
            if (!tags.includes(selectedTag)) {
                tagSelect.value = '';
            }
        }
        ```

    *   **Accessibility Tree:**
        Ensure Notes Grid section has `aria-label` or `role`. I gave it `aria-label="Notes"`.
        The filter section has `aria-label="Filters"`.
        Stats are in a `div` with `aria-live="polite"`.
        Modal has `role="dialog"`, `aria-modal="true"`, `aria-labelledby="modal-title"`.

    *   **Keyboard Navigation:**
        *   `Tab` between elements.
        *   `Enter` / `Space` to activate buttons/links.
        *   `Escape` to close modal.
        *   `Enter` on form to submit.
        All default browser behavior.

    *   **Edge Cases:**
        *   No notes: Show empty state.
        *   No tags for a note: Show no tags.
        *   No date: Show "N/A".
        *   Very long body: `word-break: break-word;`
        *   Special characters in names/tags: `escapeHtml` handles this.
        *   Double submit prevention on form. The form submit handler disables the button, or just ignore. I will just ignore for simplicity, but adding a `disabled` attribute on submit to prevent double submit is good UX. Let's do it:
            ```javascript
            const submitBtn = noteForm.querySelector('button[type="submit"]');
            // In handle submit:
            submitBtn.disabled = true;
            // ... async operation (none, it's synchronous) ...
            submitBtn.disabled = false;
            ```
            Actually, the save is synchronous. Double submit won't happen easily. I will leave it without disabled for simplicity, it keeps code shorter.

    *   **Code Length Limit:** 1000 lines is a lot. This entire app will likely be around 300-400 lines of HTML/CSS/JS combined. I can spread it out nicely with comments.

    *   **UI Polish:**
        *   Drop shadows for cards.
        *   Hover effects.
        *   Smooth transitions.
        *   Good color contrast.
        *   Visible focus states.
        *   Error message for form validation (required fields). I will just use `alert()` to keep it simple per the constraints, or `setCustomValidity`? `required` attribute on inputs is the easiest and most accessible. `input[required] { border-left: 3px solid red; }` but standard is fine.
        *   Let's use HTML5 validation (required attribute).

    *   **Refactoring the `init()` function:**
        ```javascript
        function init() {
            loadData();
            // Seed data for demonstration
            if (!data.notes || data.notes.length === 0) {
                data.notes = [
                    {
                        id: generateId(),
                        title: 'Sprint Planning',
                        owner: 'Alice',
                        date: '2024-06-10',
                        tags: ['sprint', 'planning'],
                        body: 'Plan the upcoming sprint goals and tasks.',
                        type: 'decision',
                        createdAt: new Date().toISOString()
                    },
                    {
                        id: generateId(),
                        title: 'Bug Bash Results',
                        owner: 'Bob',
                        date: '2024-06-11',
                        tags: ['bugs', 'testing'],
                        body: 'Review and assign the bugs found during the bug bash.',
                        type: 'action',
                        createdAt: new Date().toISOString()
                    }
                ];
                saveData();
            }
            refreshUI();
        }
        ```

    *   **Reviewing requirements:**
        *   Add note with title, owner, meeting date, tags, body. -> Done.
        *   Filter by owner, tag, free-text. -> Done.
        *   Note types (Action, Decision, Reference). -> Done.
        *   Edit and Delete. -> Done.
        *   Persist in localStorage. -> Done.
        *   Statistics strip. -> Done.
        *   Responsive layout. -> Done.
        *   Basic accessibility. -> Done.
        *   Under 1000 lines. -> Done.
        *   Single file, no external libraries. -> Done.

    *   **Code Structure:**
        *   `<head>` (meta, title, style)
        *   `<body>` (header with stats, main with filters, controls, note grid, modal)
        *   `<script>` (all JS)

    *   **Double-checking all IDs and selectors:**
        *   `filter-owner`, `filter-tag`, `filter-search`
        *   `stat-total`, `stat-actions`, `stat-owners`, `stat-top-tag`
        *   `open-add-modal`, `notes-grid`
        *   `modal-overlay`, `modal-title`, `note-form`
        *   `note-id`, `note-title`, `note-owner`, `note-date`, `note-tags`, `note-body`, `note-type`
        *   `cancel-modal`
        *   JS variables match these.

    *   **Ensuring `escapeHtml` is used in all injected HTML.**
        *   Card HTML: `escapeHtml(note.title)`, `escapeHtml(note.owner)`, `escapeHtml(note.body)`, `escapeHtml(t)` for tags.
        *   Dropdown options: `o` and `t` are from the data, already trimmed. I will escape them too just to be safe: `escapeHtml(o)`, `escapeHtml(t)`.

    *   **Improving the form:**
        *   Type select: `action`, `decision`, `reference`.
        *   Tags input: placeholder `e.g., design, frontend, meeting`.
        *   Date input: label `Meeting Date`.

    *   **Will the stats be filtered or global?**
        "Provide a compact statistics strip: total notes, action-required count, unique owners, and most common tag." The wording doesn't mention it should be filtered. It's safer and cleaner to make it *board-wide* stats instead of filtered results. The task says "notes appear as cards and can be filtered". The stats strip is separate. I will make it board-wide stats. `renderStats()` reads `data.notes` directly.

    *   **Refining `renderStats` to show `N/A` when there are no notes:**
        Total: 0
        Actions: 0
        Owners: 0
        Top Tag: N/A
        This is handled by the existing logic. If `mostCommonTag` is null, it shows "N/A".

    *   **Refining the "No notes" empty state:**
        If there are no notes at all vs no notes matching filter.
        `if (data.notes.length === 0) { grid.innerHTML = '<p class="empty-state">No notes yet. Click "Add Note" to get started!</p>'; }`
        `else if (filteredNotes.length === 0) { grid.innerHTML = '<p class="empty-state">No notes match your filters.</p>'; }`

    *   **Event Listeners for filters:**
        `input` event for search field to provide instant feedback. `change` event for dropdowns.

    *   **Modal transition:**
        Using `display: flex` / `display: none`. No fancy transitions needed, keeps it robust and accessible. If I want opacity transition, `visibility` and `opacity` are better but `display` is the simplest and safest for `aria-modal` etc. I will stick with `display`.

    *   **Focus trapping?**
        The spec says "basic accessibility". Focus trapping in a modal is an advanced accessibility feature. While excellent, I will just manage focus on open and close as required. For a simple modal, it's okay if focus can tab out. Adding focus trapping is beneficial. Let's add a simple focus trap.
        ```javascript
        function trapFocus(element) {
            const focusableEls = element.querySelectorAll('a[href]:not([disabled]), button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled])');
            const firstFocusableEl = focusableEls[0];
            const lastFocusableEl = focusableEls[focusableEls.length - 1];
            function handleTab(e) {
                if (e.key !== 'Tab') return;
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusableEl) {
                        e.preventDefault();
                        lastFocusableEl.focus();
                    }
                } else {
                    if (document.activeElement === lastFocusableEl) {
                        e.preventDefault();
                        firstFocusableEl.focus();
                    }
                }
            }
            element.addEventListener('keydown', handleTab);
            // store handleTab to remove it later, but since it only applies when modal is open, it's fine to just add it. Let's clean it up.
            // Actually, using the global keydown for Escape is already set. I will just add the trap in the openModal function.
        }
        ```
        Let's simplify: I will just use the global keydown listener for Escape. Focus trapping is nice but slightly complex and can be buggy without proper cleanup. Let's stick to the spec's "basic accessibility" and just ensure all controls are reachable and labeled.

    *   **Testing the flow:**
        1. Page loads -> `init()` -> `loadData()` -> renders stats, filters, notes (or sample data).
        2. Click "Add Note" -> `openModalForAdd()` -> form resets, modal opens.
        3. Fill form, click Save -> `noteForm submit` -> adds note, saves, closes modal, `refreshUI()`.
        4. Click Edit on a card -> `openModalForEdit(id)` -> form filled, modal opens.
        5. Change fields, click Save -> `noteForm submit` -> updates note, saves, closes modal, `refreshUI()`.
        6. Click Delete -> `handleDelete(id)` -> confirm, remove, save, `refreshUI()`.
        7. Change filter dropdowns / search -> `renderNotes()` updates the grid.

    *   **Are there any missing visual elements?**
        *   The type of note is shown as a badge on the card.
        *   Tags are displayed.
        *   Owner and date.
        *   Body text.
        *   Edit and Delete buttons.

    *   **Styling the stats:**
        Use semantic spans.
        ```css
        .stats {
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
            background: #f8f9fa;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin-top: 0.5rem;
        }
        .stats span {
            font-size: 0.9rem;
            color: #333;
        }
        .stats strong {
            font-weight: 600;
        }
        ```

    *   **Code organization:**
        Comments separating sections:
        `/* ---- Data Management ---- */`
        `/* ---- Statistics ---- */`
        `/* ---- Filtering ---- */`
        `/* ---- Rendering ---- */`
        `/* ---- Modal Logic ---- */`
        `/* ---- Event Handlers ---- */`
        `/* ---- Initialization ---- */`

    *   **Word Count / Line Count Check:**
        The code will most likely be well under 1000 lines. HTML (~80 lines), CSS (~150 lines), JS (~250 lines). Total ~480 lines.

    *   **Self-Correction on `type` attribute in CSS:**
        For the card's border-left, I can use inline `style` or a class.
        Using inline `border-left: 4px solid var(--color-action);` etc. is easiest.
        Or use CSS classes `.type-action { border-left-color: var(--color-action); }` etc.
        I will use classes for cleaner HTML.
        `<article class="note-card type-${note.type}">`
        ```css
        .note-card.type-action { border-left-color: var(--color-action); }
        .note-card.type-decision { border-left-color: var(--color-decision); }
        .note-card.type-reference { border-left-color: var(--color-reference); }
        ```

    *   **Accessibility of the filter search:**
        `<input type="search" id="filter-search">` is semantic.

    *   **Accessibility of the notes grid:**
        `aria-label="Notes list"` or just let screen readers treat the `<section>` as a landmark. I will add `aria-label="Notes"`.

    *   **Form labels:**
        `label for` matching `input id`.
        Fields ids: `note-title`, `note-owner`, `note-date`, `note-tags`, `note-body`, `note-type`.

    *   **Everything looks solid.** Let's write the final code.

    *   Wait, is `event.stopPropagation()` needed anywhere? Modal overlay clicking needs it if clicking inside modal shouldn't close it. I already have the logic:
        ```javascript
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeModal();
        });
        ```
        This correctly closes only if the overlay itself is clicked, not the modal content.

    *   Ensure the modal content doesn't close it. `e.stopPropagation()` on the modal content div's click event.
        ```javascript
        document.querySelector('.modal-content').addEventListener('click', (e) => e.stopPropagation());
        ```
        This is a good practice.

    *   **Checking the "most common tag" ties:**
        If there is a tie, the first one encountered in the `for...in` loop is kept. This is fine.

    *   **Data validation:**
        User can submit empty tags, empty body. Title and Owner are required. The form has `required` attribute on them. Let's also add the validation in JS as a safety net.

    *   Let's write the complete index.html.

    **Final checks against constraints:**
    *   No external libs: yes.
    *   Single file: yes.
    *   Under 1000 lines: yes.
    *   Add note: yes.
    *   Cards filtered: yes.
    *   Types: yes.
    *   Edit/Delete: yes.
    *   localStorage: yes.
    *   Stats: yes.
    *   Responsive: yes.
    *   Accessible: labels, keyboard, focus states.

    I am ready to generate the output.
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
        /* ---- CSS Reset & Variables ---- */
        *,
        *::before,
        *::after {
            box-sizing: border-box;
        }

        :root {
            --color-primary: #4361ee;
            --color-action: #ef476f;
            --color-decision: #06d6a0;
            --color-reference: #ffd166;
            --color-bg: #f4f6f8;
            --color-card-bg: #ffffff;
            --color-text: #1a1a2e;
            --color-muted: #6c757d;
            --color-border: #dee2e6;
            --radius-sm: 6px;
            --radius-md: 10px;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
            --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.10);
            --font-sans: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        }

        body {
            font-family: var(--font-sans);
            background: var(--color-bg);
            color: var(--color-text);
            margin: 0;
            padding: 0;
            line-height: 1.5;
            min-height: 100vh;
        }

        :focus-visible {
            outline: 2px solid var(--color-primary);
            outline-offset: 2px;
            border-radius: 2px;
        }

        button:focus-visible,
        input:focus-visible,
        select:focus-visible,
        textarea:focus-visible {
            outline: 2px solid var(--color-primary);
            outline-offset: 2px;
            border-color: var(--color-primary);
        }

        /* ---- Layout ---- */
        header {
            background: var(--color-card-bg);
            padding: 1.25rem 2rem;
            box-shadow: var(--shadow-sm);
            border-bottom: 1px solid var(--color-border);
        }

        header h1 {
            margin: 0 0 0.75rem 0;
            font-size: 1.6rem;
            color: var(--color-text);
        }

        .stats {
            display: flex;
            gap: 1.5rem 2rem;
            flex-wrap: wrap;
            padding: 0.65rem 1rem;
            background: #f8f9fa;
            border-radius: var(--radius-sm);
            font-size: 0.9rem;
        }

        .stats span {
            color: var(--color-muted);
        }

        .stats strong {
            color: var(--color-text);
            font-weight: 600;
        }

        main {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        /* ---- Filters ---- */
        .filters {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: flex-end;
            margin-bottom: 1.5rem;
            padding: 1.25rem 1.5rem;
            background: var(--color-card-bg);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
        }

        .filter-group {
            display: flex;
            flex-direction: column;
        }

        .filter-group label {
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            color: var(--color-muted);
            margin-bottom: 0.25rem;
        }

        .filter-group select,
        .filter-group input {
            padding: 0.5rem 0.75rem;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            font-size: 0.9rem;
            background: var(--color-card-bg);
            min-width: 160px;
            font-family: inherit;
        }

        .filter-group input[type="search"] {
            min-width: 220px;
        }

        /* ---- Controls ---- */
        .controls {
            margin-bottom: 1.5rem;
        }

        .btn-primary {
            background: var(--color-primary);
            color: #fff;
            border: none;
            padding: 0.7rem 1.5rem;
            border-radius: var(--radius-sm);
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s ease;
        }

        .btn-primary:hover,
        .btn-primary:focus-visible {
            background: #3651d4;
        }

        /* ---- Notes Grid ---- */
        .notes-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
        }

        @media (max-width: 768px) {
            .notes-grid {
                grid-template-columns: 1fr;
            }
            main {
                padding: 1.25rem;
            }
            header {
                padding: 1rem 1.25rem;
            }
            .stats {
                gap: 1rem;
            }
        }

        .empty-state {
            grid-column: 1 / -1;
            text-align: center;
            color: var(--color-muted);
            padding: 3rem 1rem;
            background: var(--color-card-bg);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
        }

        /* ---- Note Card ---- */
        .note-card {
            background: var(--color-card-bg);
            border-radius: var(--radius-md);
            padding: 1.5rem;
            box-shadow: var(--shadow-sm);
            border-left: 5px solid var(--color-border);
            display: flex;
            flex-direction: column;
            transition: box-shadow 0.15s ease;
        }

        .note-card:hover {
            box-shadow: var(--shadow-md);
        }

        .note-card.type-action {
            border-left-color: var(--color-action);
        }
        .note-card.type-decision {
            border-left-color: var(--color-decision);
        }
        .note-card.type-reference {
            border-left-color: var(--color-reference);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 0.5rem;
        }

        .card-title {
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
            word-break: break-word;
        }

        .card-type {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            padding: 0.2rem 0.6rem;
            border-radius: var(--radius-sm);
            white-space: nowrap;
            flex-shrink: 0;
            color: #fff;
        }

        .note-card.type-action .card-type {
            background: var(--color-action);
        }
        .note-card.type-decision .card-type {
            background: var(--color-decision);
            color: #1a1a2e;
        }
        .note-card.type-reference .card-type {
            background: var(--color-reference);
            color: #1a1a2e;
        }

        .card-meta {
            font-size: 0.85rem;
            color: var(--color-muted);
            display: flex;
            gap: 1.5rem;
            margin-bottom: 0.6rem;
        }

        .card-meta span {
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }

        .card-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin-bottom: 0.75rem;
        }

        .card-tags .tag {
            background: #eef2ff;
            color: #4338ca;
            padding: 0.15rem 0.55rem;
            border-radius: var(--radius-sm);
            font-size: 0.8rem;
            font-weight: 500;
        }

        .card-body {
            font-size: 0.92rem;
            color: #333;
            line-height: 1.6;
            margin: 0 0 1rem 0;
            flex-grow: 1;
            word-break: break-word;
        }

        .card-actions {
            display: flex;
            gap: 0.6rem;
            justify-content: flex-end;
            border-top: 1px solid var(--color-border);
            padding-top: 1rem;
            margin-top: auto;
        }

        .card-actions button {
            padding: 0.4rem 0.9rem;
            border: 1px solid var(--color-border);
            background: var(--color-card-bg);
            border-radius: var(--radius-sm);
            font-size: 0.85rem;
            cursor: pointer;
            font-weight: 500;
            transition: background 0.1s ease, border-color 0.1s ease;
            font-family: inherit;
        }

        .card-actions button:hover {
            background: #f0f2f5;
            border-color: #bbb;
        }

        .card-actions .btn-delete {
            color: #b91c1c;
            border-color: #fecaca;
        }

        .card-actions .btn-delete:hover {
            background: #fef2f2;
            border-color: #fca5a5;
        }

        /* ---- Modal ---- */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.45);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 1rem;
        }

        .modal-content {
            background: var(--color-card-bg);
            border-radius: var(--radius-md);
            padding: 2rem 2.25rem;
            max-width: 600px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
            position: relative;
        }

        .modal-content h2 {
            margin: 0 0 1.25rem 0;
            font-size: 1.4rem;
            color: var(--color-text);
        }

        /* ---- Form ---- */
        .note-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group label {
            font-weight: 600;
            margin-bottom: 0.25rem;
            font-size: 0.92rem;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            padding: 0.6rem 0.75rem;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            font-size: 0.95rem;
            font-family: inherit;
            transition: border-color 0.15s ease;
        }

        .form-group textarea {
            min-height: 90px;
            resize: vertical;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            border-color: var(--color-primary);
        }

        .form-row {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .form-row .form-group {
            flex: 1;
            min-width: 140px;
        }

        .form-actions {
            display: flex;
            gap: 0.75rem;
            justify-content: flex-end;
            margin-top: 0.5rem;
        }

        .form-actions button {
            padding: 0.6rem 1.5rem;
            border-radius: var(--radius-sm);
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            font-family: inherit;
            transition: background 0.1s ease;
        }

        .form-actions .btn-secondary {
            background: var(--color-card-bg);
            border: 1px solid var(--color-border);
            color: var(--color-text);
        }

        .form-actions .btn-secondary:hover {
            background: #f0f2f5;
        }

        .form-actions .btn-primary {
            border: none;
        }

        .form-actions .btn-primary:hover {
            background: #3651d4;
        }

        /* ---- Required field indicator ---- */
        .required::after {
            content: " *";
            color: var(--color-action);
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <h1>Meeting Notes Board</h1>
        <div class="stats" aria-live="polite">
            <span><strong id="stat-total">0</strong> total notes</span>
            <span><strong id="stat-actions">0</strong> action required</span>
            <span><strong id="stat-owners">0</strong> unique owners</span>
            <span>Top tag: <strong id="stat-top-tag">N/A</strong></span>
        </div>
    </header>

    <!-- Main Content -->
    <main>
        <!-- Filters -->
        <section class="filters" aria-label="Filters for notes">
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
                <label for="filter-search">Search</label>
                <input type="search" id="filter-search" placeholder="Search title, body, owner…">
            </div>
        </section>

        <!-- Controls -->
        <div class="controls">
            <button id="open-add-modal" class="btn-primary">+ Add Note</button>
        </div>

        <!-- Notes Grid -->
        <section class="notes-grid" id="notes-grid" aria-label="Notes">
            <!-- Cards rendered by JavaScript -->
        </section>
    </main>

    <!-- Modal Overlay -->
    <div class="modal-overlay" id="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="modal-content">
            <h2 id="modal-title">Add Note</h2>
            <form class="note-form" id="note-form" novalidate>
                <input type="hidden" id="note-id" value="">

                <div class="form-group">
                    <label for="note-title" class="required">Title</label>
                    <input type="text" id="note-title" required autocomplete="off">
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="note-owner" class="required">Owner</label>
                        <input type="text" id="note-owner" required autocomplete="off">
                    </div>
                    <div class="form-group">
                        <label for="note-date">Meeting Date</label>
                        <input type="date" id="note-date">
                    </div>
                </div>

                <div class="form-group">
                    <label for="note-tags">Tags</label>
                    <input type="text" id="note-tags" placeholder="e.g. design, frontend, sprint" autocomplete="off">
                </div>

                <div class="form-group">
                    <label for="note-body">Body</label>
                    <textarea id="note-body"></textarea>
                </div>

                <div class="form-group">
                    <label for="note-type">Note Type</label>
                    <select id="note-type">
                        <option value="reference">Reference</option>
                        <option value="action">Action Required</option>
                        <option value="decision">Decision</option>
                    </select>
                </div>

                <div class="form-actions">
                    <button type="button" id="cancel-modal" class="btn-secondary">Cancel</button>
                    <button type="submit" id="submit-modal" class="btn-primary">Save</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        /* ---- Data Management ---- */
        const STORAGE_KEY = 'meetingNotesBoardData';
        let data = { notes: [] };
        let editingNoteId = null;
        let previousOwningButton = null;

        function loadData() {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {
                try {
                    data = JSON.parse(raw);
                } catch (e) {
                    data = { notes: [] };
                }
            }
            if (!data.notes) data.notes = [];
        }

        function saveData() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        }

        function generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substring(2, 7);
        }

        function escapeHtml(unsafe) {
            if (!unsafe) return '';
            return unsafe.toString()
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }

        /* ---- Statistics ---- */
        function getStats() {
            const notes = data.notes;
            const total = notes.length;
            const actionCount = notes.filter(n => n.type === 'action').length;
            const uniqueOwners = new Set(notes.map(n => n.owner.trim().toLowerCase()).filter(Boolean)).size;

            const tagCounts = {};
            notes.forEach(n => {
                (n.tags || []).forEach(t => {
                    const tag = t.trim().toLowerCase();
                    if (tag) {
                        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
                    }
                });
            });

            let mostCommonTag = null;
            let maxCount = 0;
            for (const [tag, count] of Object.entries(tagCounts)) {
                if (count > maxCount) {
                    mostCommonTag = tag;
                    maxCount = count;
                }
            }
            return { total, actionCount, uniqueOwners, mostCommonTag };
        }

        function renderStats() {
            const stats = getStats();
            document.getElementById('stat-total').textContent = stats.total;
            document.getElementById('stat-actions').textContent = stats.actionCount;
            document.getElementById('stat-owners').textContent = stats.uniqueOwners;
            document.getElementById('stat-top-tag').textContent = stats.mostCommonTag || 'N/A';
        }

        /* ---- Filtering ---- */
        function getFilteredNotes() {
            const ownerFilter = document.getElementById('filter-owner').value.trim().toLowerCase();
            const tagFilter = document.getElementById('filter-tag').value.trim().toLowerCase();
            const searchFilter = document.getElementById('filter-search').value.trim().toLowerCase();

            return data.notes.filter(note => {
                // Owner filter (exact match)
                if (ownerFilter && note.owner.trim().toLowerCase() !== ownerFilter) {
                    return false;
                }
                // Tag filter (exact match)
                if (tagFilter && !(note.tags || []).some(t => t.trim().toLowerCase() === tagFilter)) {
                    return false;
                }
                // Free-text search (title, body, owner, tags)
                if (searchFilter) {
                    const titleMatch = note.title.toLowerCase().includes(searchFilter);
                    const bodyMatch = (note.body || '').toLowerCase().includes(searchFilter);
                    const ownerMatch = note.owner.toLowerCase().includes(searchFilter);
                    const tagsMatch = (note.tags || []).some(t => t.toLowerCase().includes(searchFilter));
                    if (!titleMatch && !bodyMatch && !ownerMatch && !tagsMatch) {
                        return false;
                    }
                }
                return true;
            });
        }

        function populateFilterDropdowns() {
            const owners = [...new Set(data.notes.map(n => n.owner.trim()).filter(Boolean))].sort((a, b) => a.localeCompare(b));
            const tags = [...new Set(data.notes.flatMap(n => n.tags || []).map(t => t.trim()).filter(Boolean))].sort((a, b) => a.localeCompare(b));

            const ownerSelect = document.getElementById('filter-owner');
            const tagSelect = document.getElementById('filter-tag');

            const selectedOwner = ownerSelect.value;
            const selectedTag = tagSelect.value;

            ownerSelect.innerHTML = '<option value="">All Owners</option>' +
                owners.map(o => `<option value="${escapeHtml(o)}" ${o === selectedOwner ? 'selected' : ''}>${escapeHtml(o)}</option>`).join('');
            if (selectedOwner && !owners.includes(selectedOwner)) {
                ownerSelect.value = '';
            }

            tagSelect.innerHTML = '<option value="">All Tags</option>' +
                tags.map(t => `<option value="${escapeHtml(t)}" ${t === selectedTag ? 'selected' : ''}>${escapeHtml(t)}</option>`).join('');
            if (selectedTag && !tags.includes(selectedTag)) {
                tagSelect.value = '';
            }
        }

        /* ---- Rendering ---- */
        function renderNotes() {
            const filteredNotes = getFilteredNotes();
            const grid = document.getElementById('notes-grid');
            grid.innerHTML = '';

            if (data.notes.length === 0) {
                grid.innerHTML = '<p class="empty-state">No notes yet. Click "Add Note" to get started!</p>';
                return;
            }

            if (filteredNotes.length === 0) {
                grid.innerHTML = '<p class="empty-state">No notes match your filters.</p>';
                return;
            }

            filteredNotes.forEach(note => {
                const typeLabels = { action: 'Action Required', decision: 'Decision', reference: 'Reference' };
                const typeLabel = typeLabels[note.type] || 'Reference';

                const card = document.createElement('article');
                card.className = `note-card type-${note.type || 'reference'}`;
                card.setAttribute('aria-label', `Note: ${escapeHtml(note.title)}`);

                const tagsHtml = (note.tags || [])
                    .filter(t => t.trim())
                    .map(t => `<span class="tag">${escapeHtml(t.trim())}</span>`)
                    .join('');

                card.innerHTML = `
                        <div class="card-header">
                            <h3 class="card-title">${escapeHtml(note.title)}</h3>
                            <span class="card-type">${escapeHtml(typeLabel)}</span>
                        </div>
                        <div class="card-meta">
                            <span>👤 ${escapeHtml(note.owner)}</span>
                            <span>📅 ${note.date || 'N/A'}</span>
                        </div>
                        ${tagsHtml ? `<div class="card-tags">${tagsHtml}</div>` : ''}
                        <p class="card-body">${escapeHtml(note.body) || '…'}</p>
                        <div class="card-actions">
                            <button class="btn-edit" data-id="${escapeHtml(note.id)}" aria-label="Edit ${escapeHtml(note.title)}">Edit</button>
                            <button class="btn-delete" data-id="${escapeHtml(note.id)}" aria-label="Delete ${escapeHtml(note.title)}">Delete</button>
                        </div>
                    `;

                grid.appendChild(card);
            });

            // Attach event listeners to cards
            document.querySelectorAll('.btn-edit').forEach(btn => {
                btn.addEventListener('click', () => openModalForEdit(btn.dataset.id));
            });
            document.querySelectorAll('.btn-delete').forEach(btn => {
                btn.addEventListener('click', () => handleDelete(btn.dataset.id));
            });
        }

        function refreshUI() {
            populateFilterDropdowns();
            renderNotes();
            renderStats();
        }

        /* ---- Modal Logic ---- */
        const modalOverlay = document.getElementById('modal-overlay');
        const modalTitle = document.getElementById('modal-title');
        const noteForm = document.getElementById('note-form');
        const noteIdInput = document.getElementById('note-id');
        const titleInput = document.getElementById('note-title');
        const ownerInput = document.getElementById('note-owner');
        const dateInput = document.getElementById('note-date');
        const tagInput = document.getElementById('note-tags');
        const bodyTextarea = document.getElementById('note-body');
        const typeSelect = document.getElementById('note-type');
        const cancelBtn = document.getElementById('cancel-modal');
        const addNoteBtn = document.getElementById('open-add-modal');

        function openModalForAdd() {
            editingNoteId = null;
            modalTitle.textContent = 'Add Note';
            noteForm.reset();
            noteIdInput.value = '';
            dateInput.value = new Date().toISOString().split('T')[0];
            modalOverlay.style.display = 'flex';
            previousOwningButton = addNoteBtn;
            titleInput.focus();
        }

        function openModalForEdit(id) {
            const note = data.notes.find(n => n.id === id);
            if (!note) return;
            editingNoteId = id;
            modalTitle.textContent = 'Edit Note';
            noteIdInput.value = id;
            titleInput.value = note.title || '';
            ownerInput.value = note.owner || '';
            dateInput.value = note.date || '';
            tagInput.value = (note.tags || []).join(', ');
            bodyTextarea.value = note.body || '';
            typeSelect.value = note.type || 'reference';
            modalOverlay.style.display = 'flex';
            previousOwningButton = document.querySelector(`.btn-edit[data-id="${id}"]`);
            titleInput.focus();
        }

        function closeModal() {
            modalOverlay.style.display = 'none';
            if (previousOwningButton && document.contains(previousOwningButton)) {
                previousOwningButton.focus();
            } else {
                addNoteBtn.focus();
            }
            previousOwningButton = null;
        }

        /* ---- Event Handlers ---- */
        addNoteBtn.addEventListener('click', openModalForAdd);
        cancelBtn.addEventListener('click', closeModal);

        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeModal();
        });

        document.querySelector('.modal-content').addEventListener('click', (e) => {
            e.stopPropagation();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modalOverlay.style.display === 'flex') {
                closeModal();
            }
        });

        // Form submission
        noteForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const title = titleInput.value.trim();
            const owner = ownerInput.value.trim();
            const date = dateInput.value;
            const tags = tagInput.value.split(',').map(t => t.trim()).filter(Boolean);
            const body = bodyTextarea.value.trim();
            const type = typeSelect.value;

            if (!title || !owner) {
                alert('Title and Owner are required.');
                return;
            }

            const noteData = { title, owner, date, tags, body, type };

            if (editingNoteId) {
                const index = data.notes.findIndex(n => n.id === editingNoteId);
                if (index > -1) {
                    data.notes[index] = { ...data.notes[index], ...noteData };
                }
            } else {
                noteData.id = generateId();
                noteData.createdAt = new Date().toISOString();
                data.notes.push(noteData);
            }

            saveData();
            closeModal();
            refreshUI();
        });

        // Delete handler
        function handleDelete(id) {
            if (!confirm('Are you sure you want to delete this note?')) return;
            data.notes = data.notes.filter(n => n.id !== id);
            saveData();
            refreshUI();
        }

        // Filter change handlers
        document.getElementById('filter-owner').addEventListener('change', renderNotes);
        document.getElementById('filter-tag').addEventListener('change', renderNotes);
        document.getElementById('filter-search').addEventListener('input', renderNotes);

        /* ---- Initialization ---- */
        function init() {
            loadData();

            // Seed sample data if board is empty
            if (!data.notes || data.notes.length === 0) {
                data.notes = [{
                    id: generateId(),
                    title: 'Sprint Planning',
                    owner: 'Alice',
                    date: new Date().toISOString().split('T')[0],
                    tags: ['sprint', 'planning'],
                    body: 'Plan the upcoming sprint goals and distribute tasks among the team.',
                    type: 'decision',
                    createdAt: new Date().toISOString()
                }, {
                    id: generateId(),
                    title: 'Bug Triage Results',
                    owner: 'Bob',
                    date: new Date().toISOString().split('T')[0],
                    tags: ['bugs', 'testing'],
                    body: 'Address the critical bugs found in the latest release candidate.',
                    type: 'action',
                    createdAt: new Date().toISOString()
                }, {
                    id: generateId(),
                    title: 'Architecture Sync',
                    owner: 'Charlie',
                    date: new Date().toISOString().split('T')[0],
                    tags: ['architecture'],
                    body: 'Reviewed the new service boundaries and data flow diagrams.',
                    type: 'reference',
                    createdAt: new Date().toISOString()
                }];
                saveData();
            }

            refreshUI();
        }

        init();
    </script>
</body>
</html>
```
````
