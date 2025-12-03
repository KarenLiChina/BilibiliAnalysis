import os
from typing import Optional

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic.v1 import BaseModel, Field

load_dotenv()

# 创建模型
model = ChatOpenAI(model=os.getenv("MODEL_NAME"),
                   api_key=os.getenv("OPENAI_API_KEY"),
                   base_url=os.getenv("BASE_URL"))
embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"),
                              base_url=os.getenv("BASE_URL"))

persist_dir = 'chroma_data_dir'  # 向量数据库的目录，生成数据后，文件夹下的所有文件都不要删除

# 向量数据库的持久化
vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)  # 从此磁盘中加载向量数据库
# result = vectorstore.similarity_search_with_score('机器学习的主要算法有什么')

system_prompt = """你是一个将用户问题转换为数据库查询的专家，
你可以访问关于基于‘机器学习算法与人工智能视频字幕’的chroma向量数据库。
给定一个问题，返回一个数据库查询优化列表，以检索最相关的结果。
如果有你不熟悉的缩略词或单词，不要试图改变它们。
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{question}")
])


# pydantic 是一个专门用来做数据管理的库，包括数据验证，数据的定义
class Search(BaseModel):
    """
    定义一个数据模型，可以作为结构化的搜索或者输出的数据模型
    """
    # 根据内容的相似性和发布时间
    query: str = Field(None, description='搜索视频字幕中的相似度')
    publish_year: Optional[int] = Field(None, description='视频发布年份')


chain = {'question': RunnablePassthrough()} | prompt | model.with_structured_output(Search)
# 此时chain 生成基于用户问题的 指令，没有真正的对向量数据库进行检索
resp1 = chain.invoke('机器学习的算法有什么？')
print(resp1)  # 输出结果为：query='机器学习的算法' publish_year=None
resp1 = chain.invoke('2025年发布的视频介绍机器学习算法有哪些？')
print(resp1)  # 输出结果为： query='机器学习算法' publish_year='2025'


def retrieval(search: Search):
    _filter = None
    if search.publish_year:
        # 根据publish_year 存在得到一个检索条件
        # "$eq" 是Chroma向量数据库固定的语法，表示等于
        _filter = {'publish_year': {"$eq": search.publish_year}}
    return vectorstore.similarity_search(search.query, filter=_filter)

new_chain = chain | retrieval

result = new_chain.invoke('2025年发布的视频介绍机器学习算法有哪些？')
print([(doc.metadata) for doc in result])