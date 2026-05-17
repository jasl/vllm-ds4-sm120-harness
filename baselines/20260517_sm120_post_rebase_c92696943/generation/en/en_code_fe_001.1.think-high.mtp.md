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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 66.281954
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 226, "total_tokens": 12588, "completion_tokens": 12362, "prompt_tokens_details": null}`
- Prompt tokens: 226
- Completion tokens: 12362
- Total tokens: 12588

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
The user wants me to create a single-file frontend app called `index.html` that implements a "meeting notes board" for a small team. Let me plan this out carefully.

**Functional Requirements:**
1. Add notes with title, owner, meeting date, tags, and body
2. Notes as cards, filterable by owner, tag, and free-text search
3. Notes can be marked as "Action Required", "Decision", or "Reference"
4. Edit and delete notes
5. Persist in localStorage
6. Statistics strip: total notes, action-required count, unique owners, most common tag
7. Responsive layout: 2-column grid on wide, 1-column on narrow
8. Accessibility: labels, keyboard-operable, visible focus states

Let me build this step by step.

**Data Model:**
```json
{
  id: string,
  title: string,
  owner: string,
  meetingDate: string,
  tags: string[],
  body: string,
  type: 'action-required' | 'decision' | 'reference',
  createdAt: string,
  updatedAt: string
}
```

**UI Structure:**
- Header with title
- Statistics strip
- Filter controls (owner dropdown, tag dropdown, search input)
- Add note form (initially collapsed or inline)
- Notes grid (cards)

Let me write the complete HTML file now.

I'll structure the HTML with:
1. A header section
2. A statistics strip
3. A filter section
4. An add/edit note form (modal or inline)
5. A notes grid

Let me think about the design approach:
- Clean, minimal design
- Accessible color scheme with good contrast
- Proper ARIA attributes
- Keyboard navigation

Let me code this up now.

Actually, let me think about the form. I'll use a modal dialog for adding/editing notes, which is more accessible and cleaner.

For the statistics strip:
- Total notes
- Action required count
- Unique owners
- Most common tag

Let me start coding:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meeting Notes Board</title>
    ...
</head>
<body>
    ...
</body>
</html>
```

Let me think about the color scheme - I'll use a professional, clean palette with good contrast for accessibility.

I need to be careful about:
- Focus states (visible outlines)
- Labels for all inputs
- Keyboard operability (Enter/Space to activate buttons, Escape to close modals)
- ARIA attributes where needed

Let me write the full implementation now.

I'll use a dialog element for the modal since it has built-in accessibility features.

Let me think about the tags input - I'll use a comma-separated input that gets converted to tags.

For the filter by owner and tag, I'll populate dropdowns dynamically from the existing notes.

Let me write the complete code now. I'll keep it under 1000 lines.

Here's my plan for the layout:

```
+------------------------------------------+
| 🗒️ Meeting Notes Board                    |
+------------------------------------------+
| 📊 Stats: 12 notes | 3 action req |       |
| 5 owners | Most common: "sprint"          |
+------------------------------------------+
| [Filter by owner ▼] [Filter by tag ▼]    |
| [🔍 Search notes...]                      |
| [+ Add Note]                             |
+------------------------------------------+
| ┌──────────┐  ┌──────────┐               |
| │ Card 1   │  │ Card 2   │               |
| │ ...      │  │ ...      │               |
| └──────────┘  └──────────┘               |
| ┌──────────┐  ┌──────────┐               |
| │ Card 3   │  │ Card 4   │               |
| │ ...      │  │ ...      │               |
| └──────────┘  └──────────┘               |
+------------------------------------------+
```

On narrow screens, cards stack in a single column.

For the modal:
```
+------------------------------------------+
| ✏️ Add Note / Edit Note                  |
+------------------------------------------+
| Title: [________________________]         |
| Owner: [________________________]         |
| Date: [____________]                      |
| Tags: [________________________] (comma)  |
| Type: [○ Action Required ○ Decision ○ Ref]|
| Body: [________________________]          |
| [Cancel] [Save]                          |
+------------------------------------------+
```

Let me now write the complete implementation. I'll make sure to:
- Use semantic HTML
- Include proper labels
- Use ARIA where needed (role, aria-label, aria-modal, etc.)
- Have visible focus styles
- Support keyboard navigation

Let me write the code now.

I need to be careful about the total line count - under 1000 lines.

Let me write clean, well-organized code.

Actually, for the "type" field, I'll use radio buttons since only one can be selected.

For the modal, I'll use the `<dialog>` element which has good browser support and built-in accessibility.

Let me finalize the design and write the code.

One thing to consider: the "most common tag" in statistics. If there are no tags, I should handle that gracefully.

Also, "unique owners" - count of distinct owner values.

For filtering:
- Owner filter: dropdown with "All" option + all unique owners
- Tag filter: dropdown with "All" option + all unique tags
- Search: free text search across title, body, owner, tags

Let me write the complete code.

Actually, I realize I should think about the visual design more carefully. Let me go with:
- A clean, modern look with a blue/indigo primary color
- Cards with subtle shadows and rounded corners
- Color-coded type badges (action required = red/orange, decision = blue, reference = gray/green)
- Good spacing and typography

Let me write it all now.

Let me think about the tag display in cards - I'll show them as small pills/badges.

OK, let me just write the code. I'll make it comprehensive and clean.

One more thing - for the edit functionality, I need to pre-populate the form with the existing note data.

For delete, I'll add a confirmation dialog. I can use the native confirm() dialog for simplicity, or a custom one. Let me use confirm() to keep it simple and under 1000 lines.

Actually, let me use a custom confirmation dialog within the modal or a separate one for better UX and accessibility. Or I could just use confirm() - it's simpler and keeps the code shorter.

Let me use confirm() for delete confirmation.

Let me start writing the code now.

I'll structure the JavaScript as:
1. Data management (localStorage read/write)
2. Render functions (stats, filters, cards)
3. Event handlers (add, edit, delete, filter)
4. Modal management (open, close, populate)
5. Initialization

Let me write the full implementation now.

Actually, for the filter dropdowns, I need to rebuild them when notes change (add/edit/delete) to reflect the current set of owners and tags.

Let me think about the flow:
1. On page load, load notes from localStorage
2. Render stats, filter dropdowns, and cards
3. When a note is added/edited/deleted, save to localStorage and re-render

For the tags input, I'll use a text input where users type comma-separated tags. I'll split by comma and trim.

OK, let me write the code now. I'll aim for clean, well-organized code that's under 1000 lines.

Let me draft the HTML structure first, then CSS, then JavaScript.

Actually, I'll go ahead and write the entire file at once since I have a clear picture.

Let me think about one more thing: the "meeting date" field - I'll use an HTML date input.

For the body, I'll use a textarea.

OK, let me write the complete file now.

I'll aim for about 800-900 lines to leave room for thorough implementation.

Let me also think about accessibility details:
- The filter dropdowns need labels
- The search input needs a label (can be visually hidden but accessible)
- The modal needs proper focus management
- The cards should be focusable and have action buttons that are keyboard accessible
- Color contrast needs to meet WCAG AA standards

Let me write the code now.

Here's my color palette:
- Primary: #4F46E5 (indigo)
- Primary hover: #4338CA
- Background: #F8FAFC
- Card background: #FFFFFF
- Text: #1E293B
- Text secondary: #64748B
- Border: #E2E8F0
- Action required: #EF4444 (red)
- Decision: #3B82F6 (blue)
- Reference: #8B5CF6 (purple) - actually, let me use a more neutral color like #6B7280 or #10B981 (green)
- Focus ring: #4F46E5 with ring offset

Let me use:
- Action Required: #DC2626 (red)
- Decision: #2563EB (blue)
- Reference: #059669 (green)

These have good contrast and are distinguishable.

OK let me just write the code now.

I'll use a slightly different approach for the type selector - instead of radio buttons, I could use a select dropdown or a set of buttons. Radio buttons are most accessible for single-select options. Let me use radio buttons styled as a button group.

Actually, for simplicity and accessibility, I'll use a select dropdown for the type. No, radio buttons are actually better for 3 options. Let me use radio buttons.

Let me write the final code now.

Wait, for the "most common tag" stat, if there are no tags across all notes, I'll show "N/A" or "none".

OK, here's my complete implementation plan. Let me write it all now.

I'll write the code with careful attention to:
1. Clean, semantic HTML
2. Responsive CSS with good accessibility (focus states, contrast, etc.)
3. Well-organized JavaScript with clear functions

Let me produce the final output.
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
        /* ===== Reset & Base ===== */
        *,
        *::before,
        *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        :root {
            --color-primary: #4F46E5;
            --color-primary-hover: #4338CA;
            --color-primary-light: #EEF2FF;
            --color-bg: #F1F5F9;
            --color-surface: #FFFFFF;
            --color-text: #1E293B;
            --color-text-secondary: #64748B;
            --color-text-muted: #94A3B8;
            --color-border: #E2E8F0;
            --color-border-focus: #4F46E5;
            --color-action: #DC2626;
            --color-action-bg: #FEF2F2;
            --color-decision: #2563EB;
            --color-decision-bg: #EFF6FF;
            --color-reference: #059669;
            --color-reference-bg: #ECFDF5;
            --color-danger: #DC2626;
            --color-danger-hover: #B91C1C;
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
            --radius: 10px;
            --radius-sm: 6px;
            --radius-lg: 14px;
            --font-sans: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            --transition: 150ms ease;
        }

        html {
            font-size: 16px;
            scroll-behavior: smooth;
        }

        body {
            font-family: var(--font-sans);
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.6;
            min-height: 100vh;
            padding: 1.5rem;
            -webkit-font-smoothing: antialiased;
        }

        /* ===== Focus ===== */
        :focus-visible {
            outline: 2px solid var(--color-border-focus);
            outline-offset: 2px;
            border-radius: var(--radius-sm);
        }

        /* ===== Layout ===== */
        .app-container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* ===== Header ===== */
        .app-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.25rem;
        }

        .app-header h1 {
            font-size: 1.65rem;
            font-weight: 700;
            color: var(--color-text);
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .app-header h1 svg {
            width: 1.75rem;
            height: 1.75rem;
            color: var(--color-primary);
        }

        /* ===== Stats Strip ===== */
        .stats-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem 1.5rem;
            background: var(--color-surface);
            border-radius: var(--radius-lg);
            padding: 1rem 1.5rem;
            margin-bottom: 1.25rem;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--color-border);
            align-items: center;
        }

        .stat-item {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.875rem;
            color: var(--color-text-secondary);
        }

        .stat-item .stat-icon {
            font-size: 1.1rem;
            line-height: 1;
        }

        .stat-value {
            font-weight: 700;
            color: var(--color-text);
            font-size: 1rem;
            margin-right: 0.15rem;
        }

        .stat-divider {
            width: 1px;
            height: 1.5rem;
            background: var(--color-border);
            display: inline-block;
        }

        @media (max-width: 600px) {
            .stats-strip {
                gap: 0.5rem 1rem;
                padding: 0.75rem 1rem;
            }
            .stat-item {
                font-size: 0.8rem;
            }
            .stat-value {
                font-size: 0.9rem;
            }
        }

        /* ===== Controls Bar ===== */
        .controls-bar {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            align-items: center;
            margin-bottom: 1.5rem;
            background: var(--color-surface);
            border-radius: var(--radius-lg);
            padding: 1rem 1.25rem;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--color-border);
        }

        .filter-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .filter-group label {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--color-text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        .filter-group select,
        .filter-group input[type="search"] {
            padding: 0.45rem 0.75rem;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            font-size: 0.875rem;
            background: var(--color-surface);
            color: var(--color-text);
            min-width: 130px;
            transition: border-color var(--transition), box-shadow var(--transition);
            font-family: inherit;
        }

        .filter-group select:hover,
        .filter-group input[type="search"]:hover {
            border-color: var(--color-text-muted);
        }

        .filter-group select:focus-visible,
        .filter-group input[type="search"]:focus-visible {
            border-color: var(--color-border-focus);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
        }

        .search-wrap {
            position: relative;
            flex: 1 1 180px;
            min-width: 140px;
        }

        .search-wrap input[type="search"] {
            width: 100%;
            min-width: 0;
            padding-left: 2rem;
        }

        .search-wrap .search-icon {
            position: absolute;
            left: 0.6rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--color-text-muted);
            font-size: 0.9rem;
            pointer-events: none;
        }

        .btn-primary {
            background: var(--color-primary);
            color: #fff;
            border: none;
            padding: 0.5rem 1.25rem;
            border-radius: var(--radius-sm);
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: background var(--transition), transform var(--transition), box-shadow var(--transition);
            font-family: inherit;
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }

        .btn-primary:hover {
            background: var(--color-primary-hover);
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }

        .btn-primary:active {
            transform: translateY(0);
        }

        .btn-secondary {
            background: transparent;
            color: var(--color-text-secondary);
            border: 1px solid var(--color-border);
            padding: 0.45rem 1rem;
            border-radius: var(--radius-sm);
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: background var(--transition), border-color var(--transition);
            font-family: inherit;
        }

        .btn-secondary:hover {
            background: var(--color-bg);
            border-color: var(--color-text-muted);
        }

        .btn-danger {
            background: var(--color-danger);
            color: #fff;
            border: none;
            padding: 0.5rem 1.25rem;
            border-radius: var(--radius-sm);
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: background var(--transition);
            font-family: inherit;
        }

        .btn-danger:hover {
            background: var(--color-danger-hover);
        }

        .btn-sm {
            padding: 0.3rem 0.7rem;
            font-size: 0.8rem;
        }

        /* ===== Notes Grid ===== */
        .notes-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.25rem;
        }

        @media (max-width: 780px) {
            .notes-grid {
                grid-template-columns: 1fr;
            }
        }

        .empty-state {
            grid-column: 1 / -1;
            text-align: center;
            padding: 4rem 2rem;
            color: var(--color-text-muted);
            background: var(--color-surface);
            border-radius: var(--radius-lg);
            border: 2px dashed var(--color-border);
        }

        .empty-state .empty-icon {
            font-size: 3rem;
            margin-bottom: 0.75rem;
            display: block;
        }
        .empty-state h3 {
            font-size: 1.1rem;
            color: var(--color-text-secondary);
            margin-bottom: 0.3rem;
            font-weight: 600;
        }
        .empty-state p {
            font-size: 0.9rem;
        }

        /* ===== Note Card ===== */
        .note-card {
            background: var(--color-surface);
            border-radius: var(--radius-lg);
            padding: 1.25rem 1.25rem 1rem;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--color-border);
            transition: box-shadow var(--transition), transform var(--transition);
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .note-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }

        .note-card-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }

        .note-card-title {
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--color-text);
            line-height: 1.3;
            word-break: break-word;
            flex: 1;
        }

        .note-card-type {
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            white-space: nowrap;
            flex-shrink: 0;
            margin-top: 0.15rem;
        }

        .note-card-type.type-action {
            background: var(--color-action-bg);
            color: var(--color-action);
        }
        .note-card-type.type-decision {
            background: var(--color-decision-bg);
            color: var(--color-decision);
        }
        .note-card-type.type-reference {
            background: var(--color-reference-bg);
            color: var(--color-reference);
        }

        .note-card-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem 1rem;
            font-size: 0.8rem;
            color: var(--color-text-secondary);
            margin-bottom: 0.6rem;
        }

        .note-card-meta span {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }

        .note-card-meta .meta-icon {
            font-size: 0.85rem;
        }

        .note-card-body {
            font-size: 0.875rem;
            color: var(--color-text-secondary);
            line-height: 1.6;
            margin-bottom: 0.75rem;
            word-break: break-word;
            flex: 1;
            max-height: 5.5em;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
        }

        .note-card-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin-bottom: 0.75rem;
        }

        .note-tag {
            font-size: 0.7rem;
            font-weight: 500;
            background: var(--color-primary-light);
            color: var(--color-primary);
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
            border: 1px solid rgba(79, 70, 229, 0.12);
            transition: background var(--transition);
        }

        .note-tag:hover {
            background: #DBE4FF;
        }

        .note-card-actions {
            display: flex;
            gap: 0.5rem;
            justify-content: flex-end;
            border-top: 1px solid var(--color-border);
            padding-top: 0.75rem;
            margin-top: auto;
        }

        .note-card-actions button {
            font-family: inherit;
            cursor: pointer;
            border: none;
            background: transparent;
            padding: 0.25rem 0.5rem;
            border-radius: var(--radius-sm);
            font-size: 0.8rem;
            font-weight: 500;
            transition: background var(--transition), color var(--transition);
            color: var(--color-text-secondary);
        }

        .note-card-actions button:hover {
            background: var(--color-bg);
            color: var(--color-text);
        }

        .note-card-actions .edit-btn:hover {
            background: var(--color-primary-light);
            color: var(--color-primary);
        }

        .note-card-actions .delete-btn:hover {
            background: var(--color-action-bg);
            color: var(--color-action);
        }

        /* ===== Modal (Dialog) ===== */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.4);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 1rem;
            opacity: 0;
            visibility: hidden;
            transition: opacity 200ms ease, visibility 200ms ease;
        }

        .modal-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .modal {
            background: var(--color-surface);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-lg);
            width: 100%;
            max-width: 560px;
            max-height: 90vh;
            overflow-y: auto;
            padding: 1.75rem 1.75rem 1.5rem;
            transform: translateY(20px) scale(0.97);
            transition: transform 200ms ease;
        }

        .modal-overlay.active .modal {
            transform: translateY(0) scale(1);
        }

        .modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
        }

        .modal-header h2 {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--color-text);
        }

        .modal-close {
            background: transparent;
            border: none;
            font-size: 1.5rem;
            line-height: 1;
            cursor: pointer;
            color: var(--color-text-muted);
            padding: 0.25rem;
            border-radius: var(--radius-sm);
            transition: color var(--transition), background var(--transition);
            font-family: inherit;
        }

        .modal-close:hover {
            color: var(--color-text);
            background: var(--color-bg);
        }

        .form-group {
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--color-text-secondary);
            margin-bottom: 0.3rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 0.55rem 0.75rem;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            font-size: 0.9rem;
            font-family: inherit;
            background: var(--color-surface);
            color: var(--color-text);
            transition: border-color var(--transition), box-shadow var(--transition);
        }

        .form-group input:hover,
        .form-group textarea:hover,
        .form-group select:hover {
            border-color: var(--color-text-muted);
        }

        .form-group input:focus-visible,
        .form-group textarea:focus-visible,
        .form-group select:focus-visible {
            border-color: var(--color-border-focus);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
            outline: none;
        }

        .form-group textarea {
            min-height: 100px;
            resize: vertical;
        }

        .form-row {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .form-row .form-group {
            flex: 1;
            min-width: 120px;
        }

        .type-radios {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            padding-top: 0.2rem;
        }

        .type-radios label {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.85rem;
            font-weight: 500;
            text-transform: none;
            letter-spacing: normal;
            color: var(--color-text-secondary);
            cursor: pointer;
            padding: 0.3rem 0.7rem;
            border-radius: var(--radius-sm);
            border: 1px solid var(--color-border);
            transition: border-color var(--transition), background var(--transition);
        }

        .type-radios label:hover {
            border-color: var(--color-text-muted);
            background: var(--color-bg);
        }

        .type-radios input[type="radio"] {
            width: auto;
            accent-color: var(--color-primary);
        }

        .type-radios input[type="radio"]:focus-visible {
            outline: 2px solid var(--color-border-focus);
            outline-offset: 2px;
        }

        .type-radios label:has(input:checked) {
            border-color: var(--color-primary);
            background: var(--color-primary-light);
            color: var(--color-primary);
        }

        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 0.75rem;
            margin-top: 1.25rem;
            padding-top: 1rem;
            border-top: 1px solid var(--color-border);
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

        /* ===== Toast ===== */
        .toast {
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            background: var(--color-text);
            color: #fff;
            padding: 0.75rem 1.25rem;
            border-radius: var(--radius-sm);
            font-size: 0.85rem;
            font-weight: 500;
            box-shadow: var(--shadow-lg);
            opacity: 0;
            transform: translateY(10px);
            transition: opacity 250ms ease, transform 250ms ease;
            pointer-events: none;
            z-index: 2000;
            max-width: 320px;
        }

        .toast.show {
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }

        /* ===== Responsive tweaks ===== */
        @media (max-width: 600px) {
            body {
                padding: 0.75rem;
            }
            .app-header h1 {
                font-size: 1.3rem;
            }
            .controls-bar {
                flex-direction: column;
                align-items: stretch;
                gap: 0.6rem;
                padding: 0.75rem 1rem;
            }
            .filter-group {
                flex-wrap: wrap;
            }
            .filter-group select,
            .filter-group .search-wrap {
                flex: 1 1 100%;
                min-width: 0;
            }
            .search-wrap input[type="search"] {
                min-width: 0;
            }
            .btn-primary {
                justify-content: center;
                width: 100%;
            }
            .modal {
                padding: 1.25rem 1rem 1rem;
            }
            .form-row {
                flex-direction: column;
                gap: 0;
            }
            .form-row .form-group {
                min-width: 0;
            }
            .type-radios {
                gap: 0.5rem;
            }
            .type-radios label {
                flex: 1;
                justify-content: center;
            }
        }

        @media (max-width: 400px) {
            .note-card-header {
                flex-direction: column;
                gap: 0.3rem;
            }
            .note-card-type {
                align-self: flex-start;
            }
            .stats-strip .stat-divider {
                display: none;
            }
            .stats-strip {
                gap: 0.3rem 0.8rem;
            }
        }
    </style>
</head>
<body>

    <div class="app-container">

        <!-- ===== HEADER ===== -->
        <header class="app-header">
            <h1>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
                    <rect x="9" y="3" width="6" height="4" rx="1" />
                    <path d="M9 12l2 2 4-4" />
                </svg>
                Meeting Notes Board
            </h1>
            <span style="font-size:0.8rem;color:var(--color-text-muted);" aria-live="polite" id="note-count-label"></span>
        </header>

        <!-- ===== STATS STRIP ===== -->
        <section class="stats-strip" aria-label="Statistics">
            <div class="stat-item">
                <span class="stat-icon" aria-hidden="true">📋</span>
                <span><span class="stat-value" id="stat-total">0</span> notes</span>
            </div>
            <span class="stat-divider" aria-hidden="true"></span>
            <div class="stat-item">
                <span class="stat-icon" aria-hidden="true">⚡</span>
                <span><span class="stat-value" id="stat-action">0</span> action req.</span>
            </div>
            <span class="stat-divider" aria-hidden="true"></span>
            <div class="stat-item">
                <span class="stat-icon" aria-hidden="true">👥</span>
                <span><span class="stat-value" id="stat-owners">0</span> owners</span>
            </div>
            <span class="stat-divider" aria-hidden="true"></span>
            <div class="stat-item">
                <span class="stat-icon" aria-hidden="true">🏷️</span>
                <span>Top tag: <span class="stat-value" id="stat-tag">—</span></span>
            </div>
        </section>

        <!-- ===== CONTROLS ===== -->
        <section class="controls-bar" aria-label="Filters and actions">
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

            <div class="filter-group search-wrap">
                <label for="filter-search" class="sr-only">Search notes</label>
                <span class="search-icon" aria-hidden="true">🔍</span>
                <input type="search" id="filter-search" placeholder="Search notes…" autocomplete="off">
            </div>

            <button class="btn-primary" id="btn-add-note" type="button">
                <span aria-hidden="true">+</span> Add Note
            </button>
        </section>

        <!-- ===== NOTES GRID ===== -->
        <div class="notes-grid" id="notes-grid" role="list" aria-label="Meeting notes">
            <!-- Cards rendered by JS -->
        </div>

    </div>

    <!-- ===== MODAL OVERLAY ===== -->
    <div class="modal-overlay" id="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="modal">
            <div class="modal-header">
                <h2 id="modal-title">Add Note</h2>
                <button class="modal-close" id="modal-close" aria-label="Close dialog">&times;</button>
            </div>

            <form id="note-form" novalidate>
                <input type="hidden" id="note-id" value="">

                <div class="form-group">
                    <label for="note-title">Title <span aria-hidden="true">*</span></label>
                    <input type="text" id="note-title" required placeholder="e.g. Sprint Retrospective">
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="note-owner">Owner <span aria-hidden="true">*</span></label>
                        <input type="text" id="note-owner" required placeholder="e.g. Alice">
                    </div>
                    <div class="form-group">
                        <label for="note-date">Meeting date</label>
                        <input type="date" id="note-date">
                    </div>
                </div>

                <div class="form-group">
                    <label for="note-tags">Tags (comma-separated)</label>
                    <input type="text" id="note-tags" placeholder="e.g. sprint, frontend, design">
                </div>

                <div class="form-group">
                    <label>Type</label>
                    <div class="type-radios" role="radiogroup" aria-label="Note type">
                        <label>
                            <input type="radio" name="note-type" value="action" checked>
                            ⚡ Action Required
                        </label>
                        <label>
                            <input type="radio" name="note-type" value="decision">
                            🎯 Decision
                        </label>
                        <label>
                            <input type="radio" name="note-type" value="reference">
                            📌 Reference
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label for="note-body">Body</label>
                    <textarea id="note-body" placeholder="Details, action items, decisions…"></textarea>
                </div>

                <div class="modal-footer">
                    <button type="button" class="btn-secondary" id="modal-cancel">Cancel</button>
                    <button type="submit" class="btn-primary" id="modal-save">Save Note</button>
                </div>
            </form>
        </div>
    </div>

    <!-- ===== TOAST ===== -->
    <div class="toast" id="toast" role="status" aria-live="polite"></div>

    <script>
        (function() {
            'use strict';

            // ===== State =====
            let notes = [];
            let editingId = null;
            let currentFilter = { owner: '', tag: '', search: '' };

            // ===== DOM refs =====
            const grid = document.getElementById('notes-grid');
            const overlay = document.getElementById('modal-overlay');
            const form = document.getElementById('note-form');
            const titleInput = document.getElementById('note-title');
            const ownerInput = document.getElementById('note-owner');
            const dateInput = document.getElementById('note-date');
            const tagsInput = document.getElementById('note-tags');
            const bodyTextarea = document.getElementById('note-body');
            const noteIdHidden = document.getElementById('note-id');
            const modalTitle = document.getElementById('modal-title');
            const saveBtn = document.getElementById('modal-save');
            const cancelBtn = document.getElementById('modal-cancel');
            const closeBtn = document.getElementById('modal-close');
            const addBtn = document.getElementById('btn-add-note');
            const filterOwner = document.getElementById('filter-owner');
            const filterTag = document.getElementById('filter-tag');
            const filterSearch = document.getElementById('filter-search');
            const statTotal = document.getElementById('stat-total');
            const statAction = document.getElementById('stat-action');
            const statOwners = document.getElementById('stat-owners');
            const statTag = document.getElementById('stat-tag');
            const toastEl = document.getElementById('toast');
            const noteCountLabel = document.getElementById('note-count-label');

            // ===== Helpers =====
            function generateId() {
                return Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8);
            }

            function parseTags(str) {
                return str.split(',')
                    .map(s => s.trim())
                    .filter(s => s.length > 0);
            }

            function formatDate(dateStr) {
                if (!dateStr) return '';
                const parts = dateStr.split('-');
                if (parts.length !== 3) return dateStr;
                const d = new Date(+parts[0], +parts[1] - 1, +parts[2]);
                return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
            }

            function getTypeLabel(type) {
                const map = { action: 'Action Required', decision: 'Decision', reference: 'Reference' };
                return map[type] || 'Reference';
            }

            function getTypeClass(type) {
                const map = { action: 'type-action', decision: 'type-decision', reference: 'type-reference' };
                return map[type] || 'type-reference';
            }

            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            // ===== localStorage =====
            function loadNotes() {
                try {
                    const data = localStorage.getItem('meeting-notes');
                    if (data) {
                        notes = JSON.parse(data);
                        if (!Array.isArray(notes)) notes = [];
                    } else {
                        notes = [];
                    }
                } catch {
                    notes = [];
                }
            }

            function saveNotes() {
                try {
                    localStorage.setItem('meeting-notes', JSON.stringify(notes));
                } catch (e) {
                    showToast('Failed to save to localStorage');
                }
            }

            // ===== Toast =====
            let toastTimer = null;

            function showToast(msg) {
                toastEl.textContent = msg;
                toastEl.classList.add('show');
                clearTimeout(toastTimer);
                toastTimer = setTimeout(() => {
                    toastEl.classList.remove('show');
                }, 2800);
            }

            // ===== Statistics =====
            function computeStats() {
                const total = notes.length;
                const actionCount = notes.filter(n => n.type === 'action').length;
                const owners = new Set(notes.map(n => n.owner.trim().toLowerCase()).filter(Boolean));
                const uniqueOwners = owners.size;

                // Most common tag
                const tagCount = {};
                notes.forEach(n => {
                    (n.tags || []).forEach(t => {
                        const key = t.trim().toLowerCase();
                        if (key) {
                            tagCount[key] = (tagCount[key] || 0) + 1;
                        }
                    });
                });
                let topTag = '—';
                let topCount = 0;
                for (const [tag, count] of Object.entries(tagCount)) {
                    if (count > topCount) {
                        topCount = count;
                        topTag = tag;
                    }
                }
                // Capitalize first letter of top tag
                if (topTag !== '—') {
                    topTag = topTag.charAt(0).toUpperCase() + topTag.slice(1);
                }

                statTotal.textContent = total;
                statAction.textContent = actionCount;
                statOwners.textContent = uniqueOwners;
                statTag.textContent = topTag;

                // Update aria-label for header
                noteCountLabel.textContent = `${total} note${total !== 1 ? 's' : ''} total`;
            }

            // ===== Filter helpers =====
            function getFilteredNotes() {
                const owner = filterOwner.value.trim().toLowerCase();
                const tag = filterTag.value.trim().toLowerCase();
                const search = filterSearch.value.trim().toLowerCase();

                currentFilter = { owner, tag, search };

                return notes.filter(n => {
                    if (owner && n.owner.trim().toLowerCase() !== owner) return false;
                    if (tag) {
                        const noteTags = (n.tags || []).map(t => t.trim().toLowerCase());
                        if (!noteTags.includes(tag)) return false;
                    }
                    if (search) {
                        const haystack = [
                            n.title,
                            n.owner,
                            n.body || '',
                            ...(n.tags || [])
                        ].join(' ').toLowerCase();
                        if (!haystack.includes(search)) return false;
                    }
                    return true;
                });
            }

            function populateFilterDropdowns() {
                // Owners
                const ownerSet = new Set();
                notes.forEach(n => {
                    const o = n.owner.trim();
                    if (o) ownerSet.add(o);
                });
                const ownerList = Array.from(ownerSet).sort();
                const currentOwner = filterOwner.value;
                filterOwner.innerHTML = '<option value="">All Owners</option>';
                ownerList.forEach(o => {
                    const opt = document.createElement('option');
                    opt.value = o.toLowerCase();
                    opt.textContent = o;
                    filterOwner.appendChild(opt);
                });
                // try to restore selection
                if (currentOwner && ownerList.some(o => o.toLowerCase() === currentOwner)) {
                    filterOwner.value = currentOwner;
                } else {
                    filterOwner.value = '';
                }

                // Tags
                const tagSet = new Set();
                notes.forEach(n => {
                    (n.tags || []).forEach(t => {
                        const trimmed = t.trim();
                        if (trimmed) tagSet.add(trimmed);
                    });
                });
                const tagList = Array.from(tagSet).sort();
                const currentTag = filterTag.value;
                filterTag.innerHTML = '<option value="">All Tags</option>';
                tagList.forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = t.toLowerCase();
                    opt.textContent = t;
                    filterTag.appendChild(opt);
                });
                if (currentTag && tagList.some(t => t.toLowerCase() === currentTag)) {
                    filterTag.value = currentTag;
                } else {
                    filterTag.value = '';
                }
            }

            // ===== Render =====
            function render() {
                const filtered = getFilteredNotes();

                populateFilterDropdowns();

                if (filtered.length === 0) {
                    grid.innerHTML = `
                        <div class="empty-state" role="listitem">
                            <span class="empty-icon" aria-hidden="true">📝</span>
                            <h3>No notes found</h3>
                            <p>${notes.length === 0 ? 'Add your first meeting note to get started.' : 'Try adjusting your filters.'}</p>
                        </div>
                    `;
                    computeStats();
                    return;
                }

                let html = '';
                filtered.forEach(n => {
                    const typeLabel = getTypeLabel(n.type);
                    const typeClass = getTypeClass(n.type);
                    const dateStr = formatDate(n.meetingDate);
                    const tags = n.tags || [];
                    const bodyExcerpt = n.body ? n.body.substring(0, 200) : '';
                    const escapedTitle = escapeHtml(n.title);
                    const escapedOwner = escapeHtml(n.owner);
                    const escapedBody = escapeHtml(bodyExcerpt);

                    let tagsHtml = '';
                    tags.forEach(t => {
                        const et = escapeHtml(t);
                        tagsHtml += `<span class="note-tag">${et}</span>`;
                    });

                    html += `
                        <div class="note-card" role="listitem" data-id="${n.id}">
                            <div class="note-card-header">
                                <span class="note-card-title">${escapedTitle}</span>
                                <span class="note-card-type ${typeClass}">${typeLabel}</span>
                            </div>
                            <div class="note-card-meta">
                                <span><span class="meta-icon" aria-hidden="true">👤</span> ${escapedOwner}</span>
                                ${dateStr ? `<span><span class="meta-icon" aria-hidden="true">📅</span> ${dateStr}</span>` : ''}
                            </div>
                            ${tagsHtml ? `<div class="note-card-tags">${tagsHtml}</div>` : ''}
                            ${escapedBody ? `<div class="note-card-body">${escapedBody}</div>` : ''}
                            <div class="note-card-actions">
                                <button class="edit-btn" data-id="${n.id}" type="button" aria-label="Edit note: ${escapedTitle}">✏️ Edit</button>
                                <button class="delete-btn" data-id="${n.id}" type="button" aria-label="Delete note: ${escapedTitle}">🗑️ Delete</button>
                            </div>
                        </div>
                    `;
                });

                grid.innerHTML = html;
                computeStats();

                // Attach event listeners to card buttons
                grid.querySelectorAll('.edit-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        const id = btn.getAttribute('data-id');
                        openEditModal(id);
                    });
                });
                grid.querySelectorAll('.delete-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        const id = btn.getAttribute('data-id');
                        deleteNote(id);
                    });
                });
            }

            // ===== CRUD =====
            function addNote(data) {
                const note = {
                    id: generateId(),
                    title: data.title.trim(),
                    owner: data.owner.trim(),
                    meetingDate: data.meetingDate || '',
                    tags: data.tags,
                    type: data.type || 'reference',
                    body: data.body ? data.body.trim() : '',
                    createdAt: new Date().toISOString(),
                    updatedAt: new Date().toISOString(),
                };
                notes.push(note);
                saveNotes();
                render();
                showToast('Note added');
            }

            function updateNote(id, data) {
                const idx = notes.findIndex(n => n.id === id);
                if (idx === -1) return;
                notes[idx] = {
                    ...notes[idx],
                    title: data.title.trim(),
                    owner: data.owner.trim(),
                    meetingDate: data.meetingDate || '',
                    tags: data.tags,
                    type: data.type || 'reference',
                    body: data.body ? data.body.trim() : '',
                    updatedAt: new Date().toISOString(),
                };
                saveNotes();
                render();
                showToast('Note updated');
            }

            function deleteNote(id) {
                const note = notes.find(n => n.id === id);
                if (!note) return;
                const confirmed = confirm(`Delete "${note.title}"? This cannot be undone.`);
                if (!confirmed) return;
                notes = notes.filter(n => n.id !== id);
                saveNotes();
                render();
                showToast('Note deleted');
            }

            // ===== Modal =====
            function openAddModal() {
                editingId = null;
                modalTitle.textContent = 'Add Note';
                saveBtn.textContent = 'Save Note';
                form.reset();
                noteIdHidden.value = '';
                // Set default date to today
                const today = new Date();
                const yyyy = today.getFullYear();
                const mm = String(today.getMonth() + 1).padStart(2, '0');
                const dd = String(today.getDate()).padStart(2, '0');
                dateInput.value = `${yyyy}-${mm}-${dd}`;
                // Default type
                document.querySelector('input[name="note-type"][value="action"]').checked = true;
                overlay.classList.add('active');
                setTimeout(() => titleInput.focus(), 100);
            }

            function openEditModal(id) {
                const note = notes.find(n => n.id === id);
                if (!note) return;
                editingId = id;
                modalTitle.textContent = 'Edit Note';
                saveBtn.textContent = 'Update Note';
                noteIdHidden.value = id;
                titleInput.value = note.title;
                ownerInput.value = note.owner;
                dateInput.value = note.meetingDate || '';
                tagsInput.value = (note.tags || []).join(', ');
                bodyTextarea.value = note.body || '';
                const radio = document.querySelector(`input[name="note-type"][value="${note.type}"]`);
                if (radio) radio.checked = true;
                overlay.classList.add('active');
                setTimeout(() => titleInput.focus(), 100);
            }

            function closeModal() {
                overlay.classList.remove('active');
                editingId = null;
                form.reset();
                noteIdHidden.value = '';
            }

            function handleFormSubmit(e) {
                e.preventDefault();

                const title = titleInput.value.trim();
                const owner = ownerInput.value.trim();
                const meetingDate = dateInput.value;
                const tags = parseTags(tagsInput.value);
                const typeEl = document.querySelector('input[name="note-type"]:checked');
                const type = typeEl ? typeEl.value : 'reference';
                const body = bodyTextarea.value.trim();

                if (!title) {
                    titleInput.focus();
                    showToast('Title is required');
                    return;
                }
                if (!owner) {
                    ownerInput.focus();
                    showToast('Owner is required');
                    return;
                }

                const data = { title, owner, meetingDate, tags, type, body };

                if (editingId) {
                    updateNote(editingId, data);
                } else {
                    addNote(data);
                }
                closeModal();
            }

            // ===== Keyboard: Escape to close modal =====
            function handleKeydown(e) {
                if (e.key === 'Escape' && overlay.classList.contains('active')) {
                    closeModal();
                    e.preventDefault();
                }
            }

            // ===== Init =====
            function init() {
                loadNotes();

                // Event listeners
                addBtn.addEventListener('click', openAddModal);
                cancelBtn.addEventListener('click', closeModal);
                closeBtn.addEventListener('click', closeModal);
                overlay.addEventListener('click', function(e) {
                    if (e.target === overlay) closeModal();
                });
                form.addEventListener('submit', handleFormSubmit);
                document.addEventListener('keydown', handleKeydown);

                filterOwner.addEventListener('change', render);
                filterTag.addEventListener('change', render);
                filterSearch.addEventListener('input', render);

                render();
            }

            // ===== Start =====
            init();

        })();
    </script>

</body>
</html>
```
````
