# Generation Transcript

- Case: `en_code_fe_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 117.924671
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 226, "total_tokens": 11855, "completion_tokens": 11629, "prompt_tokens_details": null}`
- Prompt tokens: 226
- Completion tokens: 11629
- Total tokens: 11855

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
The user wants me to build a complete single-file "meeting notes board" application. Let me carefully plan this out:

**HTML Structure:**
- Header with title
- Stats strip (total notes, action-required count, unique owners, most common tag)
- Filter controls (owner, tag, free-text search)
- Add/Edit note form (title, owner, meeting date, tags, body, category)
- Notes grid (cards)

**CSS:**
- Responsive layout (2-column grid on wide screens, 1 column on narrow)
- Accessible styles (focus states, labels)
- Clean, professional design

**JavaScript:**
- CRUD operations for notes
- localStorage persistence
- Filtering logic
- Stats computation
- Form handling (add/edit)

Let me build this step by step.

I'll design the data model:
```js
{
  id: string,
  title: string,
  owner: string,
  meetingDate: string,
  tags: string[],
  body: string,
  category: 'action-required' | 'decision' | 'reference',
  createdAt: string
}
```

Let me write the complete implementation.

I need to be careful about:
- Accessibility: labels, aria attributes, keyboard navigation, focus states
- Responsive design
- localStorage persistence
- All the CRUD operations

Let me build this now.

I'll structure the HTML with clear sections, use semantic HTML elements, and ensure all interactive elements are keyboard accessible.

Let me think about the layout:
- Top: Header with title
- Stats bar: 4 stat items in a row
- Filter section: owner dropdown, tag dropdown, search input
- Form section: add/edit note
- Notes grid: cards in 2-column layout

For the form, I'll use a simple form with fields for title, owner, meeting date, tags (comma-separated or individual), body, and category select.

Let me think about the tags input - I'll use a text input where users can type comma-separated tags, or I could use a tag input with add/remove. For simplicity, I'll use a comma-separated text input.

Actually, let me use a more user-friendly approach - a text input where you type a tag and press Enter to add it, with chips displayed. But that might be complex. Let me go with a simple comma-separated input for now.

Actually, I'll do a tag input where you type and press Enter/comma to add tags as chips. This is more accessible and user-friendly.

Let me write this carefully.

Actually, for simplicity and to keep code under 1000 lines, let me use a comma-separated text input for tags. But I'll make it work well.

Hmm, let me reconsider. A tag input with chips is more user-friendly and not too complex. Let me implement that.

Let me plan the JavaScript structure:

1. Data management:
   - loadNotes() from localStorage
   - saveNotes() to localStorage
   - addNote(note)
   - updateNote(id, updates)
   - deleteNote(id)

2. UI rendering:
   - renderNotes() - renders filtered notes
   - renderStats() - updates stats strip
   - renderFilters() - populates filter dropdowns
   - renderForm(note?) - shows form for add/edit

3. Filtering:
   - getFilteredNotes() - applies all filters

4. Event handlers:
   - Form submit
   - Filter changes
   - Edit/delete buttons

Let me write the complete code now.

Actually, let me think about the tag input more carefully. I'll use a div-based tag input where:
- User types in an input
- Pressing Enter or comma adds the tag as a chip
- Each chip has a remove button
- Tags are stored as an array

This is more accessible and looks better.

Let me now write the complete implementation.

I need to be mindful of the 1000 line limit, so I'll keep the code concise but well-commented and clean.

Let me start coding:

Actually, I realize I should use a simpler tag input approach to keep things manageable. Let me use a text input with comma separation, and display tags as chips below/beside the input.

Actually, let me just go with the chip-based tag input. It's cleaner and more user-friendly.

Let me write the complete file now.

Here's my plan for the form fields:
- Title: text input (required)
- Owner: text input (required) - with autocomplete from existing owners
- Meeting Date: date input
- Tags: custom tag input with chips
- Category: select dropdown (Action Required, Decision, Reference)
- Body: textarea (required)

For the edit flow, I'll fill the form with existing data and change the submit button to "Update" instead of "Add".

Let me write the code.

I'll use a clean, modern design with a color scheme that's professional and accessible.

Let me think about colors:
- Background: #f5f7fa
- Cards: white
- Primary: #4a6cf7 (blue)
- Action Required: #e74c3c (red)
- Decision: #f39c12 (amber)
- Reference: #2ecc71 (green)

OK, let me write the complete implementation now.

Actually, I want to make sure the tag input is really usable and accessible. Let me implement it as a custom component with:
- A container div
- An input field
- Chips displayed in the container
- Each chip has a button to remove it
- Pressing Enter adds the current value as a tag
- Pressing Backspace in an empty input removes the last tag

This is a standard pattern and works well.

Let me code this up now.

Alright, I'll start writing the HTML file. Let me be thorough and make sure everything works.

For the stats strip, I need:
1. Total notes count
2. Action-required count (notes with category "action-required")
3. Unique owners count
4. Most common tag

For the most common tag, I need to find the tag that appears most frequently across all notes. If there's a tie, I'll show the first one alphabetically or just "None" if no tags exist.

Let me think about the responsive breakpoint. I'll use 768px as the breakpoint for mobile vs desktop.

Alright, let me write the complete code now.

One more thing - for the filter by owner and tag, I need to populate dropdowns with existing values from notes. The filter options should update dynamically as notes change.

For the free-text search, I'll search through title, body, owner, and tags.

Let me write the complete implementation now. I'll aim for clean, well-organized code.

Let me think about the structure more carefully:

```
<div id="app">
  <header>
    <h1>Meeting Notes Board</h1>
  </header>

  <section id="stats-bar">
    <!-- 4 stat items -->
  </section>

  <section id="filters">
    <!-- filter controls -->
  </section>

  <section id="note-form">
    <!-- add/edit form -->
  </section>

  <section id="notes-grid">
    <!-- note cards -->
  </section>
</div>
```

OK, let me write this now. I'll make sure it's a complete, working application.

Let me write the JavaScript first to make sure the logic is solid, then wrap it in HTML and CSS.

Actually, I'll just write the whole thing from top to bottom.

Let me be very careful with accessibility:
- All form inputs need associated labels (using htmlFor or aria-label)
- Buttons need accessible names
- Focus styles should be visible (using outline)
- Keyboard navigation should work (Tab, Enter, Escape)
- Use semantic HTML elements

Here we go...

Let me think about the tag input one more time. I'll make it a reusable component within the app.

For the tag input, I'll create a container div with class "tag-input" that contains:
- A flex-wrap container for chips and the input
- Each chip is a span with the tag name and a button with an "x" to remove
- The input is a regular input field

When the user presses Enter or types a comma, the current input value is added as a tag chip.

For accessibility:
- The input has a label
- Each remove button has aria-label="Remove [tag]"
- The container has role="list" and chips have role="listitem"

Let me finalize and write the code.

Actually, I think I'll keep the tag input simpler - just an input where you type comma-separated tags, and I'll show the tags as chips below the input. This is simpler and still user-friendly.

Wait, actually the chip-based input where chips appear inline is more compact and professional. Let me do that.

OK let me just write the code now. I've planned enough.

Let me think about the form layout:
- Two columns on wide screens for the form fields
- Full width on narrow screens

Fields:
- Title (full width)
- Owner (half width) + Meeting Date (half width)
- Category (full width)
- Tags (full width)
- Body (full width)

Actually, let me keep the form simple - single column layout for the form fields.

Let me write the complete code now. Here goes:

I'll write a clean, comprehensive implementation. Let me make sure all the pieces fit together well.

One thing I want to be careful about - when editing a note, the form should be pre-filled with the note's data. When submitting, it should update the note instead of creating a new one.

I'll track the "editing" state with a variable that holds the ID of the note being edited, or null if adding a new note.

Let me also think about the delete confirmation - I'll use a simple confirm() dialog for now to keep things simple.

Alright, I'm going to write the complete code now.
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
        /* ===== Reset & Base ===== */
        *,
        *::before,
        *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        :root {
            --primary: #4361ee;
            --primary-hover: #3a56d4;
            --primary-light: #eef0ff;
            --danger: #e63946;
            --danger-hover: #c1121f;
            --warning: #f4a261;
            --success: #2a9d8f;
            --gray-50: #f8f9fa;
            --gray-100: #f1f3f5;
            --gray-200: #e9ecef;
            --gray-300: #dee2e6;
            --gray-400: #ced4da;
            --gray-500: #adb5bd;
            --gray-600: #6c757d;
            --gray-700: #495057;
            --gray-800: #343a40;
            --gray-900: #212529;
            --radius: 8px;
            --shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            --shadow-hover: 0 4px 16px rgba(0, 0, 0, 0.1);
            --transition: 0.2s ease;
            --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
        }

        html {
            font-size: 16px;
            scroll-behavior: smooth;
        }

        body {
            font-family: var(--font);
            background: var(--gray-50);
            color: var(--gray-900);
            line-height: 1.5;
            padding: 0 16px 40px;
            min-height: 100vh;
        }

        /* ===== Focus ===== */
        :focus-visible {
            outline: 3px solid var(--primary);
            outline-offset: 2px;
            border-radius: 2px;
        }

        /* ===== App Container ===== */
        #app {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* ===== Header ===== */
        header {
            padding: 24px 0 16px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            border-bottom: 2px solid var(--gray-200);
        }

        header h1 {
            font-size: 1.65rem;
            font-weight: 700;
            color: var(--gray-900);
            letter-spacing: -0.02em;
        }

        header .sub {
            font-size: 0.85rem;
            color: var(--gray-600);
        }

        /* ===== Stats Strip ===== */
        #stats-bar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            padding: 20px 0 16px;
        }

        .stat-card {
            background: white;
            border-radius: var(--radius);
            padding: 14px 16px;
            box-shadow: var(--shadow);
            border-left: 4px solid var(--primary);
            transition: var(--transition);
        }

        .stat-card:nth-child(2) {
            border-left-color: var(--danger);
        }
        .stat-card:nth-child(3) {
            border-left-color: var(--success);
        }
        .stat-card:nth-child(4) {
            border-left-color: var(--warning);
        }

        .stat-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--gray-600);
            font-weight: 600;
        }

        .stat-value {
            font-size: 1.6rem;
            font-weight: 700;
            line-height: 1.2;
            color: var(--gray-900);
        }

        .stat-meta {
            font-size: 0.8rem;
            color: var(--gray-600);
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* ===== Filters ===== */
        #filters {
            display: flex;
            flex-wrap: wrap;
            gap: 12px 16px;
            padding: 16px 0 20px;
            align-items: end;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 4px;
            flex: 1 1 160px;
            min-width: 120px;
        }

        .filter-group label {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--gray-700);
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        .filter-group input,
        .filter-group select {
            padding: 8px 12px;
            border: 1.5px solid var(--gray-300);
            border-radius: var(--radius);
            font-size: 0.9rem;
            background: white;
            color: var(--gray-900);
            transition: var(--transition);
            font-family: inherit;
        }

        .filter-group input:focus,
        .filter-group select:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.12);
        }

        .filter-group input::placeholder {
            color: var(--gray-500);
        }

        #clear-filters-btn {
            padding: 8px 18px;
            background: var(--gray-200);
            border: none;
            border-radius: var(--radius);
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--gray-700);
            cursor: pointer;
            transition: var(--transition);
            font-family: inherit;
            white-space: nowrap;
            height: 38px;
            align-self: end;
        }

        #clear-filters-btn:hover {
            background: var(--gray-300);
        }
        #clear-filters-btn:focus-visible {
            outline: 3px solid var(--primary);
            outline-offset: 2px;
        }

        /* ===== Form ===== */
        #note-form-section {
            background: white;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 20px 24px 24px;
            margin-bottom: 24px;
            border: 1px solid var(--gray-200);
        }

        #note-form-section h2 {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--gray-800);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        #note-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px 20px;
        }

        #note-form .form-group {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        #note-form .form-group.full-width {
            grid-column: 1 / -1;
        }

        #note-form label {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--gray-700);
        }

        #note-form label .required {
            color: var(--danger);
            margin-left: 2px;
        }

        #note-form input,
        #note-form select,
        #note-form textarea {
            padding: 8px 12px;
            border: 1.5px solid var(--gray-300);
            border-radius: var(--radius);
            font-size: 0.9rem;
            background: white;
            color: var(--gray-900);
            transition: var(--transition);
            font-family: inherit;
        }

        #note-form input:focus,
        #note-form select:focus,
        #note-form textarea:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.12);
            outline: none;
        }

        #note-form textarea {
            resize: vertical;
            min-height: 80px;
        }

        /* Tags input */
        .tag-input-wrapper {
            border: 1.5px solid var(--gray-300);
            border-radius: var(--radius);
            padding: 6px 8px;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-items: center;
            background: white;
            cursor: text;
            transition: var(--transition);
            min-height: 38px;
        }

        .tag-input-wrapper:focus-within {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.12);
        }

        .tag-chip {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: var(--primary-light);
            color: var(--primary);
            padding: 2px 10px 2px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            line-height: 1.6;
            border: 1px solid rgba(67, 97, 238, 0.15);
        }

        .tag-chip .remove-tag {
            background: none;
            border: none;
            color: var(--primary);
            font-size: 1rem;
            line-height: 1;
            cursor: pointer;
            padding: 0 2px;
            border-radius: 50%;
            transition: var(--transition);
            font-weight: 700;
            opacity: 0.7;
        }

        .tag-chip .remove-tag:hover {
            opacity: 1;
            background: rgba(67, 97, 238, 0.12);
        }
        .tag-chip .remove-tag:focus-visible {
            outline: 2px solid var(--primary);
            outline-offset: 1px;
        }

        .tag-input-inner {
            border: none;
            outline: none;
            font-size: 0.9rem;
            padding: 2px 4px;
            flex: 1 1 80px;
            min-width: 60px;
            background: transparent;
            font-family: inherit;
            color: var(--gray-900);
        }

        .tag-input-inner::placeholder {
            color: var(--gray-500);
        }

        /* Form buttons */
        .form-actions {
            grid-column: 1 / -1;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            padding-top: 4px;
        }

        .form-actions button {
            padding: 10px 24px;
            border: none;
            border-radius: var(--radius);
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            font-family: inherit;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
        }
        .btn-primary:hover {
            background: var(--primary-hover);
        }

        .btn-secondary {
            background: var(--gray-200);
            color: var(--gray-700);
        }
        .btn-secondary:hover {
            background: var(--gray-300);
        }

        .btn-danger {
            background: var(--danger);
            color: white;
        }
        .btn-danger:hover {
            background: var(--danger-hover);
        }

        #cancel-edit-btn {
            display: none;
        }

        /* ===== Notes Grid ===== */
        #notes-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding-top: 4px;
        }

        .note-card {
            background: white;
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 20px 22px 18px;
            border: 1px solid var(--gray-200);
            transition: var(--transition);
            display: flex;
            flex-direction: column;
        }

        .note-card:hover {
            box-shadow: var(--shadow-hover);
        }

        .note-card .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 10px;
        }

        .note-card .card-title {
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--gray-900);
            word-break: break-word;
            flex: 1;
        }

        .note-card .card-badge {
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: 3px 12px;
            border-radius: 20px;
            white-space: nowrap;
            flex-shrink: 0;
        }

        .badge-action {
            background: #fde8e8;
            color: #b91c1c;
        }
        .badge-decision {
            background: #fef3cd;
            color: #92400e;
        }
        .badge-reference {
            background: #d1fae5;
            color: #065f46;
        }

        .note-card .card-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px 16px;
            font-size: 0.8rem;
            color: var(--gray-600);
            margin-bottom: 10px;
        }

        .note-card .card-meta span {
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .note-card .card-meta .label {
            font-weight: 500;
            color: var(--gray-700);
        }

        .note-card .card-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 12px;
        }

        .note-card .card-tag {
            background: var(--gray-100);
            color: var(--gray-700);
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .note-card .card-body {
            font-size: 0.9rem;
            color: var(--gray-700);
            line-height: 1.6;
            margin-bottom: 14px;
            word-break: break-word;
            flex: 1;
            white-space: pre-wrap;
        }

        .note-card .card-actions {
            display: flex;
            gap: 8px;
            padding-top: 12px;
            border-top: 1px solid var(--gray-200);
        }

        .note-card .card-actions button {
            padding: 6px 16px;
            border: none;
            border-radius: var(--radius);
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
            font-family: inherit;
            background: var(--gray-100);
            color: var(--gray-700);
        }

        .note-card .card-actions button:hover {
            background: var(--gray-200);
        }

        .note-card .card-actions .btn-edit {
            background: var(--primary-light);
            color: var(--primary);
        }
        .note-card .card-actions .btn-edit:hover {
            background: #d6dcff;
        }

        .note-card .card-actions .btn-delete {
            background: #fde8e8;
            color: var(--danger);
        }
        .note-card .card-actions .btn-delete:hover {
            background: #f8d0d0;
        }

        /* ===== Empty state ===== */
        .empty-state {
            grid-column: 1 / -1;
            text-align: center;
            padding: 48px 24px;
            color: var(--gray-500);
            background: white;
            border-radius: var(--radius);
            border: 2px dashed var(--gray-300);
        }

        .empty-state p {
            font-size: 1rem;
        }
        .empty-state .hint {
            font-size: 0.85rem;
            margin-top: 6px;
            color: var(--gray-400);
        }

        /* ===== Responsive ===== */
        @media (max-width: 820px) {
            #notes-container {
                grid-template-columns: 1fr;
            }

            #stats-bar {
                grid-template-columns: repeat(2, 1fr);
            }

            #note-form {
                grid-template-columns: 1fr;
            }

            #note-form .form-group.full-width {
                grid-column: 1;
            }

            .form-actions {
                grid-column: 1;
            }

            #filters {
                flex-direction: column;
                align-items: stretch;
            }

            .filter-group {
                flex: 1 1 auto;
                min-width: 0;
            }

            #clear-filters-btn {
                align-self: stretch;
                height: auto;
                padding: 10px 18px;
            }

            header h1 {
                font-size: 1.35rem;
            }

            .stat-value {
                font-size: 1.3rem;
            }
        }

        @media (max-width: 480px) {
            #stats-bar {
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }

            .stat-card {
                padding: 10px 12px;
            }

            .stat-value {
                font-size: 1.15rem;
            }

            #note-form-section {
                padding: 16px;
            }

            .note-card {
                padding: 16px;
            }

            header {
                padding: 16px 0 12px;
            }
            body {
                padding: 0 10px 32px;
            }
        }

        /* ===== Utility ===== */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            border: 0;
        }
    </style>
</head>
<body>

    <div id="app">
        <!-- Header -->
        <header>
            <h1>📋 Meeting Notes Board</h1>
            <span class="sub">for your small team</span>
        </header>

        <!-- Stats Strip -->
        <section id="stats-bar" aria-label="Notes statistics">
            <div class="stat-card">
                <div class="stat-label">Total Notes</div>
                <div class="stat-value" id="stat-total">0</div>
                <div class="stat-meta">all categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Action Required</div>
                <div class="stat-value" id="stat-action">0</div>
                <div class="stat-meta">needs attention</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Unique Owners</div>
                <div class="stat-value" id="stat-owners">0</div>
                <div class="stat-meta">team members</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Top Tag</div>
                <div class="stat-value" id="stat-tag">—</div>
                <div class="stat-meta">most used</div>
            </div>
        </section>

        <!-- Filters -->
        <section id="filters" aria-label="Filter notes">
            <div class="filter-group">
                <label for="filter-owner">Owner</label>
                <select id="filter-owner">
                    <option value="">All owners</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="filter-tag">Tag</label>
                <select id="filter-tag">
                    <option value="">All tags</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="filter-search">Search</label>
                <input type="text" id="filter-search" placeholder="Free‑text search…" />
            </div>
            <button id="clear-filters-btn" type="button">Clear Filters</button>
        </section>

        <!-- Add / Edit Form -->
        <section id="note-form-section" aria-label="Add or edit a note">
            <h2 id="form-heading">✏️ Add a New Note</h2>
            <form id="note-form" novalidate>
                <div class="form-group full-width">
                    <label for="note-title">Title <span class="required" aria-hidden="true">*</span></label>
                    <input type="text" id="note-title" required aria-required="true" placeholder="e.g. Sprint retrospective outcomes" />
                </div>

                <div class="form-group">
                    <label for="note-owner">Owner <span class="required" aria-hidden="true">*</span></label>
                    <input type="text" id="note-owner" required aria-required="true" placeholder="e.g. Alex" list="owner-suggestions" />
                    <datalist id="owner-suggestions"></datalist>
                </div>

                <div class="form-group">
                    <label for="note-date">Meeting Date</label>
                    <input type="date" id="note-date" />
                </div>

                <div class="form-group">
                    <label for="note-category">Category <span class="required" aria-hidden="true">*</span></label>
                    <select id="note-category" required aria-required="true">
                        <option value="action-required">Action Required</option>
                        <option value="decision">Decision</option>
                        <option value="reference">Reference</option>
                    </select>
                </div>

                <div class="form-group full-width">
                    <label for="note-tags">Tags</label>
                    <div class="tag-input-wrapper" role="list" aria-label="Tag list">
                        <div id="tag-chips" role="none"></div>
                        <input type="text" id="note-tags" class="tag-input-inner" placeholder="Type and press Enter to add…" aria-label="Add a tag" />
                    </div>
                    <span style="font-size:0.7rem;color:var(--gray-500);margin-top:2px;">Press Enter or type a comma to add a tag. Click × to remove.</span>
                </div>

                <div class="form-group full-width">
                    <label for="note-body">Body <span class="required" aria-hidden="true">*</span></label>
                    <textarea id="note-body" required aria-required="true" rows="4" placeholder="Key discussion points, decisions, action items…"></textarea>
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn-primary" id="submit-btn">Add Note</button>
                    <button type="button" class="btn-secondary" id="cancel-edit-btn">Cancel Edit</button>
                </div>
            </form>
        </section>

        <!-- Notes Grid -->
        <section id="notes-section" aria-label="Meeting notes">
            <div id="notes-container" role="list">
                <!-- Cards injected here -->
                <div class="empty-state" id="empty-state">
                    <p>📝 No notes yet</p>
                    <p class="hint">Use the form above to add your first meeting note.</p>
                </div>
            </div>
        </section>
    </div>

    <script>
        (function() {
            'use strict';

            // ===== State =====
            let notes = [];
            let editingId = null;
            let currentTags = [];

            // ===== DOM refs =====
            const $ = (sel) => document.querySelector(sel);
            const $$ = (sel) => document.querySelectorAll(sel);

            const container = $('#notes-container');
            const emptyState = $('#empty-state');

            const form = $('#note-form');
            const titleInput = $('#note-title');
            const ownerInput = $('#note-owner');
            const dateInput = $('#note-date');
            const categorySelect = $('#note-category');
            const tagsInput = $('#note-tags');
            const tagChips = $('#tag-chips');
            const bodyTextarea = $('#note-body');
            const submitBtn = $('#submit-btn');
            const cancelBtn = $('#cancel-edit-btn');
            const formHeading = $('#form-heading');

            const filterOwner = $('#filter-owner');
            const filterTag = $('#filter-tag');
            const filterSearch = $('#filter-search');
            const clearFiltersBtn = $('#clear-filters-btn');

            const statTotal = $('#stat-total');
            const statAction = $('#stat-action');
            const statOwners = $('#stat-owners');
            const statTag = $('#stat-tag');

            const ownerSuggestions = $('#owner-suggestions');

            // ===== LocalStorage =====
            function loadNotes() {
                try {
                    const data = localStorage.getItem('meeting-notes-board');
                    if (data) {
                        notes = JSON.parse(data);
                        // ensure dates are strings
                        notes.forEach(n => {
                            if (!n.tags) n.tags = [];
                            if (!n.id) n.id = 'n_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6);
                        });
                    } else {
                        notes = [];
                    }
                } catch (_) {
                    notes = [];
                }
                // Ensure valid
                if (!Array.isArray(notes)) notes = [];
            }

            function saveNotes() {
                localStorage.setItem('meeting-notes-board', JSON.stringify(notes));
            }

            // ===== Helpers =====
            function generateId() {
                return 'n_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
            }

            function todayDate() {
                return new Date().toISOString().split('T')[0];
            }

            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            function getUniqueOwners() {
                const set = new Set();
                notes.forEach(n => { if (n.owner) set.add(n.owner.trim()); });
                return [...set].filter(Boolean).sort();
            }

            function getAllTags() {
                const set = new Set();
                notes.forEach(n => { (n.tags || []).forEach(t => { if (t.trim()) set.add(t.trim()); }); });
                return [...set].sort();
            }

            function getMostCommonTag() {
                const map = {};
                notes.forEach(n => {
                    (n.tags || []).forEach(t => {
                        const key = t.trim();
                        if (key) map[key] = (map[key] || 0) + 1;
                    });
                });
                const entries = Object.entries(map);
                if (!entries.length) return null;
                entries.sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
                return entries[0][0];
            }

            function getActionCount() {
                return notes.filter(n => n.category === 'action-required').length;
            }

            // ===== Tag input logic =====
            function renderTagChips() {
                tagChips.innerHTML = '';
                currentTags.forEach((tag, idx) => {
                    const chip = document.createElement('span');
                    chip.className = 'tag-chip';
                    chip.setAttribute('role', 'listitem');
                    chip.textContent = tag;
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'remove-tag';
                    btn.textContent = '×';
                    btn.setAttribute('aria-label', 'Remove tag ' + tag);
                    btn.tabIndex = 0;
                    btn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        removeTag(idx);
                    });
                    btn.addEventListener('keydown', function(e) {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            removeTag(idx);
                        }
                    });
                    chip.appendChild(btn);
                    tagChips.appendChild(chip);
                });
                tagsInput.focus();
            }

            function addTag(raw) {
                const tag = raw.trim().replace(/,/g, '').trim();
                if (!tag) return;
                if (currentTags.includes(tag)) return;
                currentTags.push(tag);
                renderTagChips();
            }

            function removeTag(idx) {
                currentTags.splice(idx, 1);
                renderTagChips();
            }

            function resetTags() {
                currentTags = [];
                renderTagChips();
            }

            function setTags(arr) {
                currentTags = arr.filter(t => t.trim());
                renderTagChips();
            }

            // ===== Form logic =====
            function resetForm() {
                form.reset();
                resetTags();
                editingId = null;
                submitBtn.textContent = 'Add Note';
                formHeading.textContent = '✏️ Add a New Note';
                cancelBtn.style.display = 'none';
                titleInput.focus();
                // Set default date
                dateInput.value = todayDate();
                // Clear validation
                document.querySelectorAll('.form-group .error-msg').forEach(el => el.remove());
            }

            function populateForm(note) {
                titleInput.value = note.title || '';
                ownerInput.value = note.owner || '';
                dateInput.value = note.meetingDate || '';
                categorySelect.value = note.category || 'reference';
                setTags(note.tags || []);
                bodyTextarea.value = note.body || '';
                editingId = note.id;
                submitBtn.textContent = 'Update Note';
                formHeading.textContent = '✏️ Edit Note';
                cancelBtn.style.display = 'inline-block';
                // Scroll to form
                document.getElementById('note-form-section').scrollIntoView({ behavior: 'smooth', block: 'center' });
            }

            function getFormData() {
                return {
                    title: titleInput.value.trim(),
                    owner: ownerInput.value.trim(),
                    meetingDate: dateInput.value || '',
                    category: categorySelect.value,
                    tags: currentTags.filter(t => t.trim()),
                    body: bodyTextarea.value.trim(),
                };
            }

            function validateForm(data) {
                const errors = [];
                if (!data.title) errors.push('Title is required.');
                if (!data.owner) errors.push('Owner is required.');
                if (!data.body) errors.push('Body is required.');
                if (!data.category) errors.push('Category is required.');
                return errors;
            }

            function showErrors(errors) {
                // Remove old errors
                document.querySelectorAll('.form-group .error-msg').forEach(el => el.remove());
                // Show first error in an alert
                if (errors.length) {
                    alert(errors.join('\n'));
                }
            }

            // ===== CRUD =====
            function addNote(data) {
                const note = {
                    id: generateId(),
                    title: data.title,
                    owner: data.owner,
                    meetingDate: data.meetingDate || '',
                    category: data.category,
                    tags: data.tags || [],
                    body: data.body,
                    createdAt: new Date().toISOString(),
                };
                notes.unshift(note);
                saveNotes();
                renderAll();
                resetForm();
            }

            function updateNote(id, data) {
                const idx = notes.findIndex(n => n.id === id);
                if (idx === -1) return;
                notes[idx] = {
                    ...notes[idx],
                    title: data.title,
                    owner: data.owner,
                    meetingDate: data.meetingDate || '',
                    category: data.category,
                    tags: data.tags || [],
                    body: data.body,
                };
                saveNotes();
                renderAll();
                resetForm();
            }

            function deleteNote(id) {
                if (!confirm('Delete this note permanently?')) return;
                notes = notes.filter(n => n.id !== id);
                saveNotes();
                renderAll();
                if (editingId === id) resetForm();
            }

            // ===== Filtering =====
            function getFilteredNotes() {
                const owner = filterOwner.value;
                const tag = filterTag.value;
                const search = filterSearch.value.toLowerCase().trim();

                return notes.filter(n => {
                    if (owner && n.owner !== owner) return false;
                    if (tag && !(n.tags || []).includes(tag)) return false;
                    if (search) {
                        const haystack = [
                            n.title,
                            n.owner,
                            n.body,
                            ...(n.tags || [])
                        ].join(' ').toLowerCase();
                        if (!haystack.includes(search)) return false;
                    }
                    return true;
                });
            }

            // ===== Rendering =====
            function renderStats() {
                const total = notes.length;
                const action = getActionCount();
                const owners = getUniqueOwners().length;
                const topTag = getMostCommonTag();

                statTotal.textContent = total;
                statAction.textContent = action;
                statOwners.textContent = owners;
                statTag.textContent = topTag || '—';
            }

            function renderFilterDropdowns() {
                // Save current selections
                const selOwner = filterOwner.value;
                const selTag = filterTag.value;

                // Owners
                filterOwner.innerHTML = '<option value="">All owners</option>';
                getUniqueOwners().forEach(o => {
                    const opt = document.createElement('option');
                    opt.value = o;
                    opt.textContent = o;
                    filterOwner.appendChild(opt);
                });
                if (getUniqueOwners().includes(selOwner)) filterOwner.value = selOwner;
                else filterOwner.value = '';

                // Tags
                filterTag.innerHTML = '<option value="">All tags</option>';
                getAllTags().forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = t;
                    opt.textContent = t;
                    filterTag.appendChild(opt);
                });
                if (getAllTags().includes(selTag)) filterTag.value = selTag;
                else filterTag.value = '';

                // Owner datalist
                ownerSuggestions.innerHTML = '';
                getUniqueOwners().forEach(o => {
                    const opt = document.createElement('option');
                    opt.value = o;
                    ownerSuggestions.appendChild(opt);
                });
            }

            function renderNotes() {
                const filtered = getFilteredNotes();

                // Remove all note cards but keep empty-state
                container.querySelectorAll('.note-card').forEach(el => el.remove());

                if (filtered.length === 0) {
                    emptyState.style.display = 'block';
                    emptyState.querySelector('p').textContent = notes.length === 0 ?
                        '📝 No notes yet' :
                        '🔍 No notes match your filters';
                    emptyState.querySelector('.hint').textContent = notes.length === 0 ?
                        'Use the form above to add your first meeting note.' :
                        'Try adjusting your filters above.';
                    return;
                }

                emptyState.style.display = 'none';

                filtered.forEach(note => {
                    const card = document.createElement('div');
                    card.className = 'note-card';
                    card.setAttribute('role', 'listitem');

                    // Badge class
                    const badgeClass = 'badge-' + (note.category === 'action-required' ? 'action' : note.category ===
                        'decision' ? 'decision' : 'reference');
                    const badgeLabel = note.category === 'action-required' ? 'Action Required' :
                        note.category === 'decision' ? 'Decision' : 'Reference';

                    const dateStr = note.meetingDate ? new Date(note.meetingDate + 'T00:00:00').toLocaleDateString(
                    'en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '—';

                    const tagsHtml = (note.tags || []).filter(t => t.trim()).map(t =>
                        `<span class="card-tag">${escapeHtml(t)}</span>`
                    ).join('');

                    card.innerHTML = `
                        <div class="card-header">
                            <span class="card-title">${escapeHtml(note.title || 'Untitled')}</span>
                            <span class="card-badge ${badgeClass}">${badgeLabel}</span>
                        </div>
                        <div class="card-meta">
                            <span><span class="label">Owner:</span> ${escapeHtml(note.owner || '—')}</span>
                            <span><span class="label">Date:</span> ${dateStr}</span>
                        </div>
                        ${tagsHtml ? `<div class="card-tags">${tagsHtml}</div>` : ''}
                        <div class="card-body">${escapeHtml(note.body || '')}</div>
                        <div class="card-actions">
                            <button type="button" class="btn-edit" data-id="${note.id}" aria-label="Edit note: ${escapeHtml(note.title)}">Edit</button>
                            <button type="button" class="btn-delete" data-id="${note.id}" aria-label="Delete note: ${escapeHtml(note.title)}">Delete</button>
                        </div>
                    `;

                    // Attach event listeners
                    card.querySelector('.btn-edit').addEventListener('click', function() {
                        const id = this.dataset.id;
                        const note = notes.find(n => n.id === id);
                        if (note) populateForm(note);
                    });

                    card.querySelector('.btn-delete').addEventListener('click', function() {
                        const id = this.dataset.id;
                        deleteNote(id);
                    });

                    container.appendChild(card);
                });
            }

            function renderAll() {
                renderStats();
                renderFilterDropdowns();
                renderNotes();
                // If currently editing, check if the note still exists
                if (editingId && !notes.find(n => n.id === editingId)) {
                    resetForm();
                }
            }

            // ===== Event handlers =====
            // Form submit
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const data = getFormData();
                const errors = validateForm(data);
                if (errors.length) {
                    showErrors(errors);
                    return;
                }
                if (editingId) {
                    updateNote(editingId, data);
                } else {
                    addNote(data);
                }
            });

            // Cancel edit
            cancelBtn.addEventListener('click', resetForm);

            // Tag input: Enter or comma
            tagsInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ',') {
                    e.preventDefault();
                    const val = this.value;
                    if (val.trim()) {
                        addTag(val);
                        this.value = '';
                    }
                }
                // Backspace to remove last tag if input empty
                if (e.key === 'Backspace' && !this.value && currentTags.length) {
                    e.preventDefault();
                    removeTag(currentTags.length - 1);
                }
            });

            // Tag input: also handle paste with commas
            tagsInput.addEventListener('paste', function(e) {
                const pasted = (e.clipboardData || window.clipboardData).getData('text');
                if (pasted.includes(',')) {
                    e.preventDefault();
                    const parts = pasted.split(',');
                    parts.forEach(p => {
                        const t = p.trim();
                        if (t) addTag(t);
                    });
                }
            });

            // Tag input: blur - add any leftover text
            tagsInput.addEventListener('blur', function() {
                const val = this.value.trim();
                if (val) {
                    addTag(val);
                    this.value = '';
                }
            });

            // Filter events
            filterOwner.addEventListener('change', renderNotes);
            filterTag.addEventListener('change', renderNotes);
            filterSearch.addEventListener('input', renderNotes);

            // Clear filters
            clearFiltersBtn.addEventListener('click', function() {
                filterOwner.value = '';
                filterTag.value = '';
                filterSearch.value = '';
                renderNotes();
                // Also update dropdowns to show all options
                renderFilterDropdowns();
            });

            // ===== Keyboard: close edit with Escape =====
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && editingId) {
                    resetForm();
                    e.preventDefault();
                }
            });

            // ===== Initialization =====
            function init() {
                loadNotes();
                // If no notes, add a sample
                if (notes.length === 0) {
                    const sample = {
                        id: generateId(),
                        title: 'Sprint Planning — Week 14',
                        owner: 'Alex',
                        meetingDate: new Date().toISOString().split('T')[0],
                        category: 'decision',
                        tags: ['sprint', 'planning'],
                        body: 'Decided to focus on payment gateway integration and user onboarding improvements. Story points estimated: 42.',
                        createdAt: new Date().toISOString(),
                    };
                    notes.push(sample);
                    const sample2 = {
                        id: generateId(),
                        title: 'QA Review Feedback',
                        owner: 'Jordan',
                        meetingDate: new Date(Date.now() - 86400000 * 2).toISOString().split('T')[0],
                        category: 'action-required',
                        tags: ['qa', 'bugs'],
                        body: 'Critical bug in login flow needs fixing before release. Assign to dev team. ETA: Friday.',
                        createdAt: new Date(Date.now() - 86400000).toISOString(),
                    };
                    notes.push(sample2);
                    const sample3 = {
                        id: generateId(),
                        title: 'Architecture Sync',
                        owner: 'Morgan',
                        meetingDate: new Date(Date.now() - 86400000 * 5).toISOString().split('T')[0],
                        category: 'reference',
                        tags: ['architecture', 'docs'],
                        body: 'Reviewed the new microservices diagram. Agreed on event-driven approach for notifications.',
                        createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
                    };
                    notes.push(sample3);
                    saveNotes();
                }
                // Default date in form
                dateInput.value = todayDate();
                renderAll();
                // Focus first field
                titleInput.focus();
            }

            init();

        })();
    </script>

</body>
</html>
```
````
