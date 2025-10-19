from src.Agents.agents import BaseAgent
from src.Agents.agents import ArticleFrequentAskedQuestionAgent, ArticleTroubleshootingGuideAgent, ArticleTroubleshootingGuideAgent
from typing import Optional, Dict, Any
# type 1 = 'FAQ'
# type 2 = 'Troubleshooting'
# type 3 = 'Tutorials'

class ArticleAgentFactory:
    def __init__(self, article_type: int = None, text:str = None, context: Optional[str] = None, history: Optional[str] = None):
        self.article_type = article_type
        self.text = text
        self.context = context
        self.history = history
        self.agent : BaseAgent = None

    def generate_article(self):
        self.make_agent(self.article_type)
        return self.agent.invoke(self.text, self.context, self.history)

    def make_agent(self, type_id:int):
        if type_id is None:
            raise AttributeError("type not set")

        if type_id == 1:
            self.agent = ArticleFrequentAskedQuestionAgent()
        elif type_id == 2:
            self.agent = ArticleTroubleshootingGuideAgent()
        elif type_id == 3:
            self.agent = ArticleTroubleshootingGuideAgent()
        else:
            raise NotImplementedError

    def set_text(self, text:str):
        self.text = text
        return self
    def set_context(self, context:str):
        self.context = context
        return self
    def set_history(self, history:str):
        self.history = history
        return self
