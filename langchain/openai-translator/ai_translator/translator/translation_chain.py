from langchain_openai import ChatOpenAI

from utils import LOG
from langchain_core.prompts import ChatPromptTemplate

class TranslationChain:
    def __init__(self, model_name: str = "gpt-3.5-turbo", verbose: bool = True):

        # 翻译任务指令始终由 System 角色承担
        system_template = (
            "You are a translation expert, proficient in various languages.\n"
            "Translates {source_language} to {target_language}."
        )

        # 待翻译文本由 Human 角色输入
        human_template = "{text}"

        # 使用 System 和 Human 角色的提示模板构造 ChatPromptTemplate
        chat_prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", human_template)
        ])

        # 为了翻译结果的稳定性，将 temperature 设置为 0
        chat = ChatOpenAI(model_name=model_name, temperature=0, verbose=verbose)

        # 使用 LCEL 模式构建链
        self.chain = chat_prompt_template | chat

    def run(self, text: str, source_language: str, target_language: str) -> (str, bool):
        result = ""
        try:
            # 使用 invoke 方法替代 run
            response = self.chain.invoke({
                "text": text,
                "source_language": source_language,
                "target_language": target_language,
            })
            result = response.content
        except Exception as e:
            LOG.error(f"An error occurred during translation: {e}")
            return result, False

        return result, True