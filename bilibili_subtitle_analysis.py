import asyncio
import json
import os

import aiohttp
from bilibili_api import video, sync, Credential
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from bilibili_loader import BilibiliLoader

load_dotenv()

# 创建模型
model = ChatOpenAI(model=os.getenv("MODEL_NAME"),
                   api_key=os.getenv("OPENAI_API_KEY"),
                   base_url=os.getenv("BASE_URL"))

persist_dir = 'chroma_data_dir'  # 向量数据库的目录

# 初始化视频的连接
urls = []

docs = []  # document 的数组



# 使用示例
async def main():
    # 1. 初始化Loader，填入你的cookie信息
    loader = BilibiliLoader()
    # 2. 准备要处理的B站视频URL列表
    urls = [
        "BV1hwn7zqEKP",
        "BV1gG411f7zX"
        # ... 可以添加更多
    ]
    # 3. 加载字幕
    subtitles = await loader.load(urls)
    print(subtitles)
    # 4. 打印结果
    for doc in subtitles:
        print(f"分P {doc.metadata.get('page_number')}: {doc.metadata.get('part_title')}: {doc.page_content}")
        print("-" * 40)


# 运行
if __name__ == "__main__":
    asyncio.run(main())
