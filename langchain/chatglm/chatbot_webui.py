import gradio as gr

from langchain_community.llms import ChatGLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

CHATGLM_URL = "http://127.0.0.1:8001"

# 全局变量存储会话历史
chat_history_store = {}

def get_session_history(session_id: str):
    """获取或创建会话历史"""
    if session_id not in chat_history_store:
        chat_history_store[session_id] = ChatMessageHistory()
    return chat_history_store[session_id]

def init_chatbot():
    llm = ChatGLM(
        endpoint_url=CHATGLM_URL,
        max_token=80000,
        history=[],
        top_p=0.9,
        model_kwargs={"sample_model_args": False},
    )

    # 创建提示模板，包含历史消息
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    # 使用 LCEL 创建链
    chain = prompt | llm

    # 使用 RunnableWithMessageHistory 包装链以支持会话历史
    global CHATGLM_CHATBOT
    CHATGLM_CHATBOT = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
        verbose=True
    )
    return CHATGLM_CHATBOT

def chatglm_chat(message, history):
    # 使用固定的 session_id，因为 Gradio 管理单个会话
    # history 参数由 Gradio 提供但不使用，因为 RunnableWithMessageHistory 内部管理会话历史
    ai_message = CHATGLM_CHATBOT.invoke(
        {"input": message},
        config={"configurable": {"session_id": "default_session"}}
    )
    return ai_message

def launch_gradio():
    demo = gr.ChatInterface(
        fn=chatglm_chat,
        title="ChatBot (Powered by ChatGLM)",
        chatbot=gr.Chatbot(height=600),
    )

    demo.launch(share=True, server_name="0.0.0.0")

if __name__ == "__main__":
    # 初始化聊天机器人
    init_chatbot()
    # 启动 Gradio 服务
    launch_gradio()
