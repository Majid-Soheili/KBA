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

## Architecture

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
    OPEN_API_KEY=''
    EMBEDDINGS_MODEL=''
    PROMPTS_MODEL_NAME=''
    DB_PATH=''
    HASH_PATH=''
### 3. Run the Knowledge Base Automation Flow
You can run the full workflow (PDF → text → cleaned Markdown → KB draft) using:

    python src/flow.py
    
Example output:
```text
==========================================
 Welcome to Drooms – KB Automation (CLI) 
==========================================

Please enter your PDF: PROD-Duplicate_Detection-120925-214047.pdf
PDF found: PROD-Duplicate_Detection-120925-214047.pdf
 -[INFO]: Extracting the raw text.
 -[INFO]: Well-forming the raw text.
 -[INFO]: Calling LLM Agent ...
 -[INFO]: Well forming has been completed.
Do you want to edit the well-formed text? (Y/n): n
 -[INFO]: Detecting the feature
 -[INFO]: Calling LLM Agent ... 
 -[INFO]: Feature has been detected: Searching and Filtering
 -[INFO]: Subject has been detected: Main Functionality
Do you want to edit feature and subject? (Y/n): n
 -[INFO]: For feature: Searching and Filtering,a article type "FAQ" already exists.
 -[INFO]: Updating the product's document context.
 -[INFO]: Calling LLM Agent ... 
 -[INFO]: Updating FAQ article content...
 Do you want to edit the product's document content? (Y/n): n
 -[INFO]: Calling LLM Agent ... 
 -[INFO]: Article FAQ generated successfully.
 -[INFO]: Calling LLM Agent ... 
 Do you want to edit the KB article content? (Y/n): n
The FAQ Article has been generated: Main Functionality_Searching and Filtering_FAQ_V3.pdf
```

## Future
[KBA-Visual.pdf](KBA-Visual.pdf)
