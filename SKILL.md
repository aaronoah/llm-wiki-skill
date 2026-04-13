---
name: llm-wiki-skill
description: "A CLI agent skill based on Karpathy's LLM Wiki — Create and maintain a persistent, interconnected Markdown knowledge base—ingesting sources, enabling queries over compiled knowledge, and ensuring consistency through linting."
license: MIT
metadata:
  author: aaronoah
  version: 1.0.0
  homepage: https://github.com/aaronoah
  repository: https://github.com/aaronoah/llm-wiki-skill
  tags: [wiki, knowledge-base, notes, markdown]
---

# LLM Wiki Skill

Continuously update and grow a persistent knowledge base composed of interlinked markdown files. Raw contents are curated by humans and the agent uses this skill to collect, dedupe, cross-reference and summarize raw contents into structured markdown files. This skill is activated when the user wants:
- Create, or start a wiki or knowledge base
- Ingest, add, or process original content into a wiki
- Asks questions about a wiki or knowledge base
- Lint, audit, or health-check the wiki, make sure they are in good shape

## Quick Start

### Directory Structure

Below is a sample wiki directory structure:
```
llm-wiki/
├── SCHEMA.md           # Layer 3: A document for User and LLM to co-evolve the wiki conventions, structure of wiki and tag taxonomy
├── index.md            # Always exists, regardless of SCHEMA.md definition. Catalog of everything, organizaed by categoies (entities, concepts etc), each page listed with a link and a one-line summary
├── log.md              # Always exists, regardless of SCHEMA.md definition. Chronological action log (append-only, rotated yearly)
├── raw/                # Layer 1: Always exists, regardless of SCHEMA.md definition. Immutable content curated by humans
│   ├── documents/      # Web articles, clippings, PDFs
│   └── assets/         # Images, diagrams referenced by sources
├── generated/          # Layer 2: Always exists, regardless of SCHEMA.md definition. LLM-generated directories and markdown files
│   ├── entities/       # Always exists, regardless of SCHEMA.md definition. Entity pages (people, orgs, products, models)
│   ├── topics/         # Always exists, regardless of SCHEMA.md definition. Topic pages (concepts, terms)
│   ├── comparisons/    # Side-by-side analysis (between entities or between topics)
```

3 layers will be explained in next secion. The Wiki or the knowledge base is built using above structure, user can **ONLY** apply this skill when the CLI agent (Codex, Claude Code, Gemini etc) is invoked at the `llm-wiki/` folder root level given that agents have scoped file-system permissions, that means there should be `SCHEMA.md`, `index.md`, `log.md` and `raw/`, `generated/` folders underneath. If user invokes CLI agent anywhere else inside the wiki subfolders this skill will abort. 


### index.md Template

The index is sectioned by type. Each entry is one line: wikilink + summary.

```markdown
# Wiki Index

> Format: `## Last Updated: [YYYY-MM-DDThh:mm:ss] | subject | Total pages: N`
> Subject: the term (entity/topic/comparison etc)
> Total pages: how many pages the term is brought up

## Entities
<!-- Alphabetical within section -->

## Topics

## Comparisons
```

### log.md Template

```markdown
# Log File

> Format: `## [YYYY-MM-DDThh:mm:ss] action | subject | files`
> Actions: ingest, update, lint, archive, delete
> Subject: the summary of what happened within 300 characters
> Files: related files such as raw documents locations, generated wikis
> When log.md exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.
```

### SCHEMA.md Template

Adapt to the user's preference. The schema constrains agent behavior and ensures consistency:

```markdown
# Wiki Schema

## Conventions
- Raw files can be broken down to several markdown files that live in `entities/`, `topics/` etc.
- Only create the wiki pages when an entity/topic is mentioned in 2+ sources or is central to one source.
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to cross-link between pages (minimum 2 outbound links per page)
- Every new or updated page must link to at least 2 other pages via `[[wikilinks]]`.
- When updating a page, always bump the `updated` date
- When new information conflicts with existing content:
   1. Check the dates — newer sources generally supersede older ones
   2. If genuinely contradictory, note both positions with dates and sources
   3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
   4. Flag for user review

## Frontmatter
>  ---
>  title: Page Title
>  created: YYYY-MM-DDThh:mm:ss
>  updated: YYYY-MM-DDThh:mm:ss
>  type: entity | topic | comparison
>  sources: [raw/documents/source-name.md]
>  ---

## Layer 1 (User can specify, otherwise default to this file)

### Documents
Any single document in different formats user put in

### Assets
Any media files, images, video links etc.

## Layer 2 (User can specify, otherwise default to this file)

### Entities
One markdown page per notable entity. Include:
- Overview / what it is
- Key facts and dates
- Relationships to other entities ([[wikilinks]])
- Source references

### Topics
One markdown page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge
- Open questions or debates
- Related concepts ([[wikilinks]])

### Comparison Pages
Side-by-side analysis in markdown. Include:
- What is being compared and why
- Dimensions of comparison (table format preferred)
- Verdict or synthesis
- Sources
```

### Architecture

**Three Layers**

**Layer 1 — Raw Contents:** Immutable directory and files. The agent can read but can never modify them.
**Layer 2 — The Wiki or knowledge base:** Agent-owned directories and markdown files. Created, updated, and
cross-referenced by the agent.
**Layer 3 — The Schema:** `SCHEMA.md` defines user preferences of `llm-wiki/` conventions, and tag taxonomy.

### Create a New Wiki

1. Create the directory structure as in [Directory Structure](#directory-structure).
2. Ask user preferences of Layer 1 and Layer 2 directory structures and print the directory structure to confirm user intent.
3. Print conventions based on [SCHEMA.md](#schemamd-template), ask user preferences of conventions if they want to change.
4. Write updated template of [SCHEMA.md](#schemamd-template) to `SCHEMA.md` with user preferences based on 2 and 3.
5. Write initial `index.md` based on [index.md template](#indexmd-template) with sectioned header.
6. Write initial `log.md` based on [log.md template](#logmd-template) with creation entry.
7. Confirm the wiki is ready and suggest first sources to ingest.

### Ingest original content into a Wiki

1. Read the files in `raw/` using the code block below, the output is a list of each file metadata with `mtime`.

```bash
python3 $HOME/.agents/skills/llm-wiki-skill/scripts/ingest.py --collect ./raw
```

2. Read last line of `log.md` to retrieve the "date time", use the below code block to retrieve its `mtime`

```bash
python3 $HOME/.agents/skills/llm-wiki-skill/scripts/ingest.py --iso-to-mtime "date time"
```

then find files generated in step 1 that are added after the "date time".
3. Based on `SCHEMA.md` convetions section, summarize each newly added file.
4. Find files that are added before and on the date time to prepare for step 4 and 5.
5. For file content conflicts, refer to conventions section defined in `SCHEMA.md`.
6. New files are created, existing files are updated, all with newly added cross-links under `generated/`.
7. Update `index.md` with sectioned header.
8. Update `log.md` with creation entry.
9. List out all files that are newly added or changed for user.

### Ask questions about a Wiki

1. Find relevant headings in `index.md`.
2. Locate similar pages under the Wiki and summarize them based on `SCHEMA.md` using the format like "Based on [[page-1]], [[page-2]], ...".
3. present to user in markdown fashion.
4. Ask user if they want to store the answers back in Wiki, if so take the following steps:
   - create a `queries/` folder if that does not exist
   - if the question is for comparisons, put the file in `comparisons/`, otherwise put in `queries/`
5. Update `index.md` with sectioned header.
6. Update `log.md` with creation entry.
7. List out all files just created to the user, filenames should be enough no need to show content.

### Lint, Audit or health-check a Wiki

__Note:__ Below are 4 rules we lint, after they are checked, add a entry in `log.md` with lint action, subject should be "Rules passed: N, rules failed: M, which rule failed and a brief summary within 200 characters".

1. **Always** read the `SCHEMA.md` first, find any violations and unresolved contradictions in the wiki.
2. Find any orphan pages that no cross-link to other pages, using below code. The output is a list of orphan page file names.

```bash
python3 $HOME/.agents/skills/llm-wiki-skill/scripts/links.py --orphan ./generated
```
3. and find any cross-links that are broken (unreachable), using below code. The output is a dictionary of file name to all its own broken links 

```bash
python3 $HOME/.agents/skills/llm-wiki-skill/scripts/links.py --broken ./generated
```
4. Every wiki page under `generated/` should be listed in `index.md`, flag any pages that are not listed.

## Rules (MUST FOLLOW)

- **Always print a message to user when a task is finished, follow the below template:

|-------Your request has been taken care of!---------|

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Always orient first** — read SCHEMA + index + recent log before any operation in a new session.
  Skipping this causes duplicates and missed cross-references.
- **Always update index.md and log.md** — skipping this makes the wiki degrade. These are the
  navigational backbone.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, and staleness detection.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages or create 10+ new pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY.md` and start fresh.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.