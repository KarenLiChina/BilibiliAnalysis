import asyncio
import datetime
import json
import os
from typing import List

import aiohttp
from bilibili_api import video, Credential
from dotenv import load_dotenv
from langchain_core.documents import Document

load_dotenv()


class BilibiliLoader:
    def __init__(self):
        """
        初始化，设置登录凭证。
        凭证获取方法：登录B站后，在浏览器开发者工具的Application标签页查看Cookies[citation:1]。
        """
        self.credential = Credential(
            sessdata=os.getenv("SESSDATA"),
            bili_jct=os.getenv("BILI_JCT"),
            buvid3=os.getenv("BUVID3")
        )

    async def _get_subtitle_for_page(self, bvid: str) -> List[Document]:
        """获取指定BV号和分P序号的字幕，并合并为文本。"""
        v = video.Video(bvid=bvid, credential=self.credential)
        info = await v.get_info()
        base_metadata = {
            'bvid': bvid,
            'video_title': info['title'],
            'video_author': info['owner']['name'],
            'video_url': f"https://www.bilibili.com/video/{bvid}",
            'total_pages': len(info.get('pages', [])) or 1
        }
        # 1. 定位到具体分P的cid
        pages = info.get('pages', [])

        # 如果是单P视频，pages为空，我们就用主cid创建一个类似分P的结构以便统一处理
        if not pages:
            pages = [{'page': 1, 'cid': info['cid'], 'part': info['title']}]

        documents = []
        # 遍历每一个page
        for page in pages:
            page_number = page['page']  # 分P序号，对应URL中的 p=5 里的5
            cid = page['cid']  # 该分P的cid，是获取字幕的关键
            part_title = page['part']  # 分P的标题
            timestamp = page['ctime']
            utc_time = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

            # 生成该分P的完整元数据
            page_metadata = base_metadata.copy()
            page_metadata.update({
                'page_number': page_number,
                'part_title': part_title,
                'cid': cid,
                'publish_data': utc_time
            })

            # 2. 获取字幕列表 (以下代码逻辑与你之前使用的类似)
            subtitles_info = await v.get_subtitle(cid=cid)
            page_text_parts = []

            if subtitles_info and subtitles_info['subtitles']:
                for sub in subtitles_info['subtitles']:
                    if sub['lan_doc'] == '中文':  # 这里以中文字幕为例
                        subtitle_url = sub.get('subtitle_url')
                        if subtitle_url and isinstance(subtitle_url, str):
                            if subtitle_url.startswith('//'):
                                subtitle_url = 'https:' + subtitle_url
                            # 下载并解析字幕文件
                            async with aiohttp.ClientSession() as session:
                                try:
                                    async with session.get(subtitle_url) as resp:
                                        if resp.status == 200:
                                            content = await resp.text()
                                            data = json.loads(content)
                                            # 提取所有content字段
                                            body_list = data.get("body", [])
                                            if not body_list and 'data' in data:
                                                body_list = data['data'].get("body", [])
                                            page_text = [item["content"] for item in body_list if 'content' in item]
                                            page_text_parts.extend(page_text)
                                except Exception as e:
                                    print(f"获取字幕文件出错: {e}")
            if page_text_parts:
                full_page_content = '\n'.join(page_text_parts)
                # 你可以根据需要，决定是按整P存储，还是按更细的粒度（如每段字幕）存储。
                # 此处示例是按整P合并存储。
                doc = Document(page_content=full_page_content, metadata=page_metadata)
                documents.append(doc)
            else:
                print(f"视频 {bvid} 第 {page_number} 分P未找到中文字幕。")
                pass
        return documents

    async def load(self, bvids: List[str]) -> List[Document]:
        tasks = []
        for bvid in bvids:
            if bvid:
                task = self._get_subtitle_for_page(bvid)
                tasks.append(task)
        # 并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_documents = []
        for r in results:
            if isinstance(r, Exception):
                print(f"加载过程中出错: {r}")
            elif isinstance(r, list):
                all_documents.extend(r)
            else:
                print(f"警告：收到未知类型的返回结果: {type(r)}")
        return all_documents
