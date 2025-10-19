# Knowledge Base Automation

## Overview
**Knowledge Base Automation** is an intelligent system designed to automatically generate and update knowledge base (KB) articles from product documentation.

## Key Features

- **Confluence Integration**  
  Reads release documentation and feature pages directly from Confluence.

- **Automated Parsing**  
  Cleans unnecessary sections (e.g., project team, meeting notes) and extracts relevant content like feature descriptions and updates.

- **AI-Powered Article Generation**  
  Uses LLM agents to produce draft KB articles (FAQ, troubleshooting, process steps, etc.) in Markdown format.

- **Feature Detection**  
  Automatically detects product features, and subjects to categorize KB entries correctly.

- **Version-Aware Syncing**  
  Detects changes between document versions to update only the affected KB sections.

## Architecture (updated)

- **SQLite** – Lightweight database used as the primary datastore for metadata and article management (dev-friendly, file-based).
- **SQLModel** – ORM/typed layer (built on SQLAlchemy + Pydantic) to define models (classes) and map them to SQLite tables; handles schema, queries, and migrations scaffolding.
- **Transitions** – Finite State Machine controlling the end-to-end KB automation flow (ingest → parse → clean → generate → review → publish).
- **LLM Agents** – Specialized generators (FAQ, troubleshooting, tutorials) that transform cleaned source text into draft KB articles.
- **Markdown Pipeline** – Utilities for text normalization, section extraction, and export (Markdown to PDF/HTML for review).
- **Confluence Service** – Fetches source documents/releases; provides content for parsing and feature detection.
- **CLI Interface** – Developer-friendly entry point to run and debug the workflow locally.


## Usage

Follow these steps to set up and run the **Knowledge Base Automation** project locally.

---

### 1. Create and Activate a Virtual Environment
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
### 2. Configure Environment Variables
    Create a .env file in the project root:
    DB_URL=sqlite:///db.sqlite3
    CONFLUENCE_API_KEY=your_key_here
    OPENAI_API_KEY=your_key_here
### 3. Run the Knowledge Base Automation Flow
You can run the full workflow (PDF → text → cleaned Markdown → KB draft) using:

    python src/Flow.py
    
Example output:
```text
==========================================
 Welcome to KB Automation (CLI)
==========================================

Please enter your PDF path: ./docs/feature_update.pdf
PDF found: ./docs/feature_update.pdf
[INFO] Parsing document...
[INFO] Cleaning sections...
[INFO] Extracting feature metadata...
[INFO] Generating draft Knowledge Base article...