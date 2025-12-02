## python环境要求
```bash
pip install -r requirements.txt
```
需要安装bilibili-api-python， 以及异步请求库aiohttp 

## 配置环境变量

创建 `.env`文件，在.env文件中的设置 `MODEL_NAME`,`OPENAI_API_KEY` 和 `BASE_URL` 为自己的 key 和 url
`LANGCHAIN_TRACING_V2`设置为true，`LANGCHAIN_PROJECT`设置为项目名称，不配置默认为default，`LANGCHAIN_API_KEY`设置为LangSmith的API Key，可以在LangSmith中查看调用大模型使用情况，不需要也可以不配置这两个变量

# langsmith的检测数据
配置`LANGCHAIN_TRACING_V2`，`LANGCHAIN_API_KEY`后可以在https://smith.langchain.com/ Tracing Projects中查看调用大模型的使用情况

# bilibili 登录凭证设置
在 `.env` 中增加 `SESSDATA`,`BILI_JCT`,`BUVID3` 提供登录凭证，获取这些信息的方式：
1. 登录你的B站账号。
2. 在B站主页按 F12 打开开发者工具。
3. 切换到 “应用程序” (Application) 或 “存储” (Storage) 标签页。
4. 在左侧找到 “Cookies” 并点击你当前访问的B站域名（如 www.bilibili.com）。
5. 在右侧列表中找到 SESSDATA、bili_jct 和 buvid3 这三项，将它们的值复制出来，填入代码中。


## 加载bilibili字幕，通过bvid 来获取相同bvid下的不同page，给每个page的字幕生成一个Document，最终返回Document的list
bilibili_loader.py