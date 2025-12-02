import asyncio
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from bilibili_loader import BilibiliLoader

load_dotenv()

# 创建模型
model = ChatOpenAI(model=os.getenv("MODEL_NAME"),
                   api_key=os.getenv("OPENAI_API_KEY"),
                   base_url=os.getenv("BASE_URL"))
embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"),
                              base_url=os.getenv("BASE_URL"))
persist_dir = 'chroma_data_dir'  # 向量数据库的目录

# 初始化视频的连接
urls = ["BV1hwn7zqEKP",
        "BV1gG411f7zX"]

docs = []  # document 的数组
loader = BilibiliLoader()


async def load_documents():
    subtitles = await loader.load(urls)
    docs.extend(subtitles)


asyncio.run(load_documents())

print(len(docs))

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=30)
split_doc = text_splitter.split_documents(docs)
print(len(split_doc))

# 向量数据库的持久化
vectorstore = Chroma.from_documents(split_doc, embeddings, persist_directory=persist_dir)  # 并且把向量数据持久化到磁盘
