from __future__ import annotations

import os
import sys
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict
from transitions import Machine

# --- Project imports (adjust paths to your project) ---
from dotenv import load_dotenv
from src.Agents.agents import FeatureDetectorAgent, DocumentCleanerAgent, DocumentMergeAgent
from src.model.Article import Article
from src.model.Feature import Feature
from src.repository.ArticleRepository import ArticleRepository
from src.repository.DBConnection import DBConnection
from src.repository.DBInit import DBInit
from src.repository.SubjectRepository import SubjectRepository
from src.repository.FeatureRepository import FeatureRepository
from src.service.confluence import ConfluenceService
from sqlmodel import SQLModel, Field, Session, create_engine, select, delete
from src.Agents.ArticleAgentFactory import ArticleAgentFactory
from src.service.markdown import MarkdownHandler


@dataclass
class FlowState:
    pdf_path: Path = None
    raw_text: str = ""
    well_formed_text: str = ""
    feature: Feature = None
    last_version: Article = None
    current_version: Article = None
    current_version_document: str = None
    current_version_article: str = None
    article_type_index = -1

class Flow:
    nodes = ["start", "welcome","get_pdf", "pars_pdf", "well_forming", "print_source",
             "feature_detecting", "fetch_last_version", "update_article", "generate_article", "end"]
    flow_state = FlowState()
    machine:Machine = None
    session : Session = None
    markdown_handler = MarkdownHandler()
    logger: logging.Logger = None

    def __init__(self, connection: DBConnection, initial="start"):
        self.dbconnection = connection
        self.session = Session(self.dbconnection.engine)
        self.machine = Machine(model=self, states=self.nodes, initial=initial)

        self.machine.add_transition("next", "start", dest="welcome")
        self.machine.add_transition("next", "welcome", dest="get_pdf")
        self.machine.add_transition("next", "get_pdf", dest="pars_pdf", conditions = "source_exist")
        self.machine.add_transition("next", "get_pdf", dest="get_pdf")

        self.machine.add_transition("next", "pars_pdf", "well_forming")
        self.machine.add_transition("next", "well_forming", "print_source")
        self.machine.add_transition("next", "print_source", "feature_detecting")
        self.machine.add_transition("next", "feature_detecting", "fetch_last_version")
        self.machine.add_transition("next", "feature_detecting", "end")


        ## log configuration
        logging.getLogger("transitions").disabled = True
        logging.getLogger("transitions.core").disabled = True
        logging.getLogger("agents").setLevel(logging.ERROR)
        logging.getLogger("agents").propagate = False
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        self.logger = logging.getLogger("Flow")
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, format=" -[%(levelname)s]: %(message)s" )

    def run(self):
        self.next()
    # Callbacks =======================================================

    def on_enter_welcome(self):
        print("==========================================")
        print(" Welcome to Drooms – KB Automation (CLI) ")
        print("==========================================\n")
        self.next()

    def on_enter_get_pdf(self):
        path = self.ask("Please enter your PDF")
        candidate = Path(path).expanduser()
        if candidate.is_file():
            self.flow_state.pdf_path = candidate
            print(f"PDF found: {self.flow_state.pdf_path}")
        else:
            print("File not found. Try again.")
        self.next()

    def on_enter_pars_pdf(self):
        handler = ConfluenceService()
        handler.set_file_path(str(self.flow_state.pdf_path))
        self.flow_state.raw_text = handler.process_pdf()
        self.logger.info(f"Extracting the raw text.")
        self.next()

    def on_enter_well_forming(self):
        raw_text = self.flow_state.raw_text
        self.logger.info("Well-forming the raw text.")
        self.logger.info(f"Calling LLM Agent ...")
        self.flow_state.well_formed_text = DocumentCleanerAgent().invoke(text=raw_text, context=None, history=None)
        self.logger.info(f"Well forming has been completed.")
        self.next()

    def on_enter_print_source(self):
        answer = self.ask_yes_no("Do you want to see the well-formed text?")
        if answer:
            print("=======================================================")
            print("Well form text extracted from selected file:\n\n")
            print(self.flow_state.well_formed_text)
            print("\n\n=======================================================")
        self.next()

    def on_enter_feature_detecting(self):
        self.logger.info(f"Detecting the feature")
        self.logger.info(f"Calling LLM Agent ... ")
        well_formed_text = self.flow_state.well_formed_text
        context = FeatureRepository(self.session).get_names()
        feature_json = FeatureDetectorAgent().invoke(text=well_formed_text, context=context, history=None)
        feature = FeatureRepository(self.session).find_by_json(feature_json)
        self.flow_state.feature = feature
        self.logger.info(f"Feature has been detected: {feature.name}")
        self.logger.info(f"Subject has been detected: {feature.subject.name}")
        self.next()

    def on_enter_generate_articles(self):
        feature = self.flow_state.feature
        session = Session(self.dbconnection.engine)
        well_formed_text = self.flow_state.well_formed_text
        for article_type in feature.article_types:
            last_version_article = ArticleRepository(session).get_article(feature.name, article_type.type_id)
            if last_version_article: # The new document and article will be combined with the last version
                last_document_text = self.markdown_handler.load(last_version_article.hash_file_document)
                last_article_text = self.markdown_handler.load(last_version_article.hash_file_article)
                new_document_text = DocumentMergeAgent().invoke(text=well_formed_text, history=last_document_text, context=None)
                new_article_text = ArticleAgentFactory(article_type = article_type.type_id,  text = well_formed_text, history= last_article_text).generate_article()
            else:
                new_document_text = well_formed_text
                new_article_text = ArticleAgentFactory(article_type = article_type.type_id,  text = well_formed_text, history= None).generate_article()

            document_hash_file = self.markdown_handler.set_text(new_document_text).save()
            article_hash_file = self.markdown_handler.set_text(new_article_text).save()


            if last_version_article: # Update the last version
                article = last_version_article
            else: # Insert a new version
                article = Article()
                article.feature_id = feature.feature_id
                article.type_id = article_type.type_id

            article.hash_file_document = document_hash_file
            article.hash_file_article = article_hash_file
            article.version +=1
            session.add(article)
            session.commit()

            print(f"\nArticle {article.hash_file_document} has been generated.")

    # Guards functions ===============================================
    def source_exist(self) -> bool:
        return bool(self.flow_state.pdf_path and self.flow_state.pdf_path.is_file())

    # Utility functions ==============================================
    @staticmethod
    def ask(prompt: str) -> str:
        return input(f"{prompt}: ").strip()

    @staticmethod
    def ask_yes_no(prompt: str, default_yes: bool = True) -> bool:
        default = "Y/n" if default_yes else "y/N"
        while True:
            s = input(f"{prompt} ({default}): ").strip().lower()
            if not s:
                return default_yes
            if s in ("y", "yes"):
                return True
            if s in ("n", "no"):
                return False
            print("Please answer y or n.")

    def get_current_article_type(self) -> int:
        idx = self.flow_state.article_type_index
        return self.flow_state.feature.article_types[idx].type_id

if __name__ == "__main__":
    load_dotenv()
    dbconnection = DBConnection()
    flow = Flow(dbconnection)
    flow.run()