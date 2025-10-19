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


def main():

    # load environment variables ======================
    load_dotenv()

    # Init database ======================
    dbconnection = DBConnection()
    db = DBInit(dbconnection)
    db.initialize()

    # pdf analyzing
    path = '/Volumes/Researches/Curiosity/Drooms/AI Engineer Case study Data/PROD-Duplicate_Detection-120925-214047.pdf'
    handler = ConfluenceService()
    handler.set_file_path(path)
    raw_text = handler.process_pdf()


    with Session(dbconnection.engine) as session:

        # 01 - clean the raw text ==============================================
        cleaned_text = DocumentCleanerAgent().invoke(text = raw_text, context=None, history=None)

        # 02 - identity detection (feature and subject) ========================
        context = FeatureRepository(session).get_names() + "\n"
        feature_json = FeatureDetectorAgent().invoke(text=cleaned_text, context=context, history=None)
        feature = FeatureRepository(session).find_by_json(feature_json)

        # 03 - In a loop generate the corresponding articles
        mark_handler = MarkdownHandler()

        for article_type in feature.article_types:

            last_version_article = ArticleRepository(session).get_article(feature.name, article_type.type_id)
            if last_version_article: # The new document and article will be combined with the last version
                last_document_text = mark_handler.load(last_version_article.hash_file_document)
                last_article_text = mark_handler.load(last_version_article.hash_file_article)
                new_document_text = DocumentMergeAgent().invoke(text=cleaned_text, history=last_document_text, context=None)
                new_article_text = ArticleAgentFactory(article_type = article_type.type_id,  text = cleaned_text, history= last_article_text).generate_article()
            else:
                new_document_text = cleaned_text
                new_article_text = ArticleAgentFactory(article_type = article_type.type_id,  text = cleaned_text, history= None).generate_article()

            document_hash_file = mark_handler.set_text(new_document_text).save()
            article_hash_file = mark_handler.set_text(new_article_text).save()


            if last_version_article: # Update the last version
                last_version_article.hash_file_document = document_hash_file
                last_version_article.hash_file_article = article_hash_file
                article = last_version_article
            else: # Insert a new version
                article = Article()
                article.feature_id = feature.feature_id
                article.hash_file_document = document_hash_file
                article.hash_file_article = article_hash_file

            article.version +=1
            session.add(article)
        session.commit()

if __name__ == "__main__":
    main()