import os
import logging
#from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from typing import Optional, Dict, Any
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class BaseAgent:
    _prompt = {}
    def __init__(self, session:str = "123", name = 'BaseAgent'):
        self.name = name
        self.session = session
        self._model_name = os.getenv("PROMPTS_MODEL_NAME", "gpt-5-nano")
        self._api_key = os.getenv('OPEN_API_KEY')
        if not self._api_key:
            raise ValueError("OPEN_API_KEY environment variable not set.")

        self.llm = ChatOpenAI(model=self._model_name, temperature=0, api_key=self._api_key)
        self.logger = logging.getLogger(f"agents.{self.name}")
        self.logger.setLevel(logging.DEBUG)

    def invoke(self, text: str, context: Optional[str], history: Optional[str]):
        try:
            messages = []
            inputs = {}
            for key, value in self._prompt.items():
                self.logger.info(f"BaseAgent. Key: {key}, Value:{value}")
                if key == "system":
                    messages.append(("system", value))
                else:
                    messages.append(("human", key + ":" + value))
                    if key == "context":
                        inputs["context"]= context
                    elif key == "history":
                        inputs["history"] = history
                    elif key == "text":
                        inputs["text"] = text
                    else:
                        raise ValueError(f"Invalid prompt key '{key}'. Valid keys are: system, text, context, history")

            self.logger.info(f"Processing with {self.name}: {messages}")

            prompt = ChatPromptTemplate.from_messages(messages)
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke(inputs)

            self.logger.info(f"{self.name} response: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Error in {self.name}: {e}")
            return f"Error in {self.name}: {e}"

class FeatureDetectorAgent(BaseAgent):
    def __init__(self, session:str = "123"):
        super().__init__(session, name='FeatureDetectorAgent')
        self._prompt = {
            "system": (
                "You analyze software product documentation and must select exactly ONE Subject and ONE Feature "
                "from the options provided in the context hierarchy.\n\n"
                "DEFINITIONS:\n"
                "- Subject: The broad functionality/module or main topic (e.g., 'Index Management').\n"
                "- Feature: A specific capability within that Subject (e.g., 'Import Index from Excel').\n\n"
                "CONTEXT FORMAT (hierarchy):\n"
                "subject: <Subject A>\n"
                "   feature: <Feature A1>\n"
                "   feature: <Feature A2>\n"
                "subject: <Subject B>\n"
                "   feature: <Feature B1>\n"
                "   ...\n\n"
                "INSTRUCTIONS (STRICT):\n"
                "1) You MUST choose from the provided Subjects and their listed Features ONLY.\n"
                "2) NEVER invent new Subjects or Features; do not alter spellings or wording.\n"
                "3) Select the single best-matching Subject based on the given text, then select one of its Features.\n"
                "4) Prefer exact phrase matches; if multiple candidates match, pick the one most central to the text.\n"
                "5) If the text mentions multiple candidates, choose the most specific and frequently referenced one.\n"
                "6) The chosen Feature MUST belong to the chosen Subject in the hierarchy.\n\n"
                "OUTPUT FORMAT:\n"
                "Return ONLY a valid JSON string:\n"
                "{{\"subject\": \"<Subject Name>\", \"feature\": \"<Feature Name>\"}}\n"
                "No explanations, no extra text, no markdown — JSON only."
            ),
            "context": "{context}",
            "text": "{text}"
        }

class DocumentCleanerAgent(BaseAgent):
    def __init__(self, session:str = "123"):
        super().__init__(session, name='DocumentAgent')
        self._prompt = {
            "system": (
                "You are a text cleanup and formatting assistant. "
                "Your goal is to transform a raw text extracted from a PDF "
                "into a clean, well-structured Markdown document.\n\n"
                "Instructions:\n"
                "1. Identify and fix structure:\n"
                "- Detect and correctly format headings and subheadings using #, ##, ###.\n"
                "- Merge broken words or lines from the PDF extraction.\n"
                "- Remove headers, footers, page numbers, and extra whitespace.\n"
                "2. Use Markdown formatting properly:\n"
                "- Use bullet points (-, *) and numbered lists.\n"
                "- Keep tables and code blocks intact if they exist.\n"
                "3. Output only the cleaned Markdown text without additional explanations.\n\n"
                "The final output must be a logically organized Markdown document."
            ),
            "text": "{text}"
        }

class DocumentMergeAgent(BaseAgent):
    def __init__(self, session: str = "123"):
        super().__init__(session, name="DocumentMergeAgent")
        self._prompt = {
            "system": (
                "You are a technical documentation merge assistant.\n"
                "Merge TWO Markdown versions of the SAME document:\n"
                "- 'history' (previous/published): the source of truth for unchanged content\n"
                "- 'text' (current/draft): the new updates\n\n"
                "GOAL:\n"
                "- Produce a SINGLE merged Markdown that applies ONLY the necessary changes from 'text' to 'history'.\n"
                "- Preserve all unchanged content from 'history' verbatim.\n\n"
                "RULES:\n"
                "1) Minimal edits: modify only sections/paragraphs that changed in 'text'.\n"
                "   - New sections in 'text' → insert into the correct place by heading level.\n"
                "   - Missing sections in 'text' → keep from 'history' but prepend a deprecation note:\n"
                "     > **Deprecated:** This section is no longer applicable.\n"
                "2) Match sections by normalized heading text and level (#, ##, ###...). Keep 'history' order.\n"
                "3) Preserve formatting: anchors/IDs, internal links, code fences, tables, lists, images, and front matter\n"
                "   exactly as in 'history' unless that exact block changed in 'text'.\n"
                "4) Conflicts: if both changed the same part, prefer wording from 'text' but keep anchors/IDs from 'history'.\n"
                "5) Tone: keep style consistent with 'history' unless 'text' explicitly changes it.\n"
                "6) Output ONLY the final merged Markdown (no explanations, no diffs).\n"
                "   Add HTML comments above touched sections:\n"
                "   <!-- CHANGED: <Heading> -->, <!-- ADDED: <Heading> -->, <!-- DEPRECATED: <Heading> -->.\n"
            ),
            # previous version comes in 'history'; new version comes in 'text'
            "history": "{history}",
            "text": "{text}",
        }

class ArticleFrequentAskedQuestionAgent(BaseAgent):
    def __init__(self, session: str = "123"):
        super().__init__(session, name='ArticleFrequentAskedQuestionAgent')
        self._prompt = {
            "system": (
                "You are a professional technical documentation assistant. "
                "Your task is to read a given Markdown text describing a software product feature or functionality, "
                "and generate a clear, end-user-focused FAQ (Frequently Asked Questions) article. "
                "The resulting article should be concise, well-structured, and easy to understand by non-technical users. "
                "Use a helpful and instructional tone.\n\n"
                "If the input text already includes a FAQ or similar Q&A section, reuse and improve those questions "
                "instead of duplicating or repeating them.\n\n"
                "If a previous FAQ article is provided in the 'history' input, do NOT write from scratch. "
                "Start from the history content and update only the necessary sections based on the new text. "
                "Preserve unchanged parts verbatim. Merge new or changed behaviors into existing questions where appropriate, "
                "and remove or mark items that are no longer valid. Avoid duplicate questions.\n\n"
                "Guidelines for minimal-update behavior:\n"
                "- Prefer editing existing Q/A pairs over creating new ones when the topic overlaps.\n"
                "- Keep question order stable unless a re-order aids clarity.\n"
                "- Preserve existing anchors, IDs, or numbering if present.\n"
                "- If a question becomes obsolete, mark it as deprecated with a short note, or remove it if clearly replaced.\n\n"
                "Output format (Markdown):\n"
                "# [Feature Name or Topic]\n\n"
                "## Overview\n"
                "- Brief summary of what this feature or functionality does.\n\n"
                "## Frequently Asked Questions\n"
                "Q1: [Question 1]\n"
                "A1: [Answer 1]\n\n"
                "Q2: [Question 2]\n"
                "A2: [Answer 2]\n\n"
                "Keep the structure in Markdown format and ensure the FAQ content is relevant, non-redundant, "
                "and focused on helping the end user understand and use the feature effectively."
            ),
            "history": "{history}",
            "text": "{text}"
        }

class ArticleTroubleshootingGuideAgent(BaseAgent):
    def __init__(self, session: str = "123"):
        super().__init__(session, name='ArticleTroubleshootingGuideAgent')
        self._prompt = {
            "system": (
                "You are a professional technical documentation assistant. "
                "Your task is to read a given Markdown text describing a software product feature or functionality, "
                "and produce an end-user Troubleshooting Guide. Keep language clear and non-technical when possible.\n\n"
                "If the input text already contains troubleshooting content (symptoms/causes/steps), reuse and improve it, "
                "avoiding duplicates.\n\n"
                "If a previous Troubleshooting Guide is provided in the 'history' input, do NOT write from scratch. "
                "Start from the history content and update only what changed based on the new text. "
                "Preserve unchanged parts verbatim. Merge new or changed causes/steps into existing sections, "
                "and remove or mark items that are no longer valid. Avoid duplicates.\n\n"
                "Guidelines for minimal-update behavior:\n"
                "- Prefer editing existing sections over creating new ones when topics overlap.\n"
                "- Keep section order stable unless re-ordering improves clarity.\n"
                "- Preserve anchors/IDs/step numbering where present.\n"
                "- If a fix is obsolete, mark as deprecated with a short note or replace it.\n\n"
                "Output format (Markdown):\n"
                "# [Feature Name or Topic] — Troubleshooting Guide\n\n"
                "## Overview\n"
                "- Brief summary of the area the issues relate to.\n\n"
                "## Symptoms\n"
                "- Bullet list of user-observable issues.\n\n"
                "## Possible Causes\n"
                "- Bullet list mapping to symptoms (keep concise).\n\n"
                "## Quick Fix (If Applicable)\n"
                "- Short TL;DR resolution for the most common case.\n\n"
                "## Step-by-Step Resolution\n"
                "1. [Step 1]\n"
                "2. [Step 2]\n"
                "3. [Step 3]\n\n"
                "## Verify the Fix\n"
                "- How the user confirms the issue is solved.\n\n"
                "## Rollback (If Needed)\n"
                "- How to undo changes safely.\n\n"
                "## Related Articles\n"
                "- Links or references.\n\n"
                "Keep the structure in Markdown, be relevant and non-redundant, and focus on helping the end user resolve issues."
            ),
            "history": "{history}",
            "text": "{text}"
        }

class ArticleStepByStepTutorialAgent(BaseAgent):
    def __init__(self, session: str = "123"):
        super().__init__(session, name='ArticleStepByStepTutorialAgent')
        self._prompt = {
            "system": (
                "You are a professional technical documentation assistant. "
                "Your task is to read a given Markdown text describing a software product feature or workflow, "
                "and produce an end-user Step-by-Step Tutorial. Keep language clear and action-oriented.\n\n"
                "If the input text already includes procedure/steps content, reuse and improve it, avoiding duplicates.\n\n"
                "If a previous Tutorial is provided in the 'history' input, do NOT write from scratch. "
                "Start from the history content and update only the necessary parts based on the new text. "
                "Preserve unchanged parts verbatim. Merge updated steps or screenshots/notes into the existing flow, "
                "and remove or mark items that are no longer valid. Avoid duplicated steps.\n\n"
                "Guidelines for minimal-update behavior:\n"
                "- Prefer editing existing numbered steps over creating new ones when the action is the same.\n"
                "- Keep numbering/anchors stable; renumber only if essential.\n"
                "- Maintain prerequisite checks and warnings if still valid.\n"
                "- If a step is obsolete, mark as deprecated or replace it.\n\n"
                "Output format (Markdown):\n"
                "# [Feature Name or Topic] — Step-by-Step Tutorial\n\n"
                "## Overview\n"
                "- What the tutorial accomplishes and for whom.\n\n"
                "## Prerequisites\n"
                "- Accounts/roles/versions/permissions needed.\n\n"
                "## Before You Start (Optional)\n"
                "- Settings to check, important notes.\n\n"
                "## Steps\n"
                "1. [Actionable step with UI path or command]\n"
                "   - Expected result: [What the user should see]\n"
                "2. [Next step]\n"
                "   - Expected result: [...]\n"
                "3. [Next step]\n"
                "   - Expected result: [...]\n\n"
                "## Common Mistakes & Tips\n"
                "- Brief hints and pitfalls.\n\n"
                "## Next Steps\n"
                "- What the user can do after completing the tutorial.\n\n"
                "Keep the structure in Markdown, ensure clarity, and focus on helping the end user accomplish the task efficiently."
            ),
            "history": "{history}",
            "text": "{text}"
        }