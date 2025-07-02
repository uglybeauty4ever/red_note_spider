# 小红书笔记页爬虫

## 项目简介
本项目 `red_note_spider` 是一个用于爬取小红书笔记页信息的爬虫工具。它可以根据用户输入的关键词，搜索小红书上相关的笔记，并将笔记的详细信息保存到 CSV 文件中，同时支持下载笔记中的图片。

## 项目地址
[https://github.com/uglybeauty4ever/red_note_spider](https://github.com/uglybeauty4ever/red_note_spider)

## 环境配置
### 1. 安装依赖
项目使用了一些第三方库，需要先安装这些依赖。在项目根目录下有 `package.json` 文件，其中定义了项目的依赖项。可以使用以下命令安装依赖：
```bash
npm install
```
### 2. Python 环境
项目的主要逻辑是用 Python 实现的，需要确保已经安装了 Python 环境，并且安装了项目所需的 Python 库。可以使用以下命令安装 Python 依赖：
```bash
pip install requests loguru execjs
```

## 使用方法
### 1. 配置日志（可选）
在 `input_key_word.py` 文件中，有一段配置日志的代码，默认是注释掉的。如果需要配置日志，可以取消注释：
```python
# 配置日志
logger.remove()  # 移除默认的处理器
logger.add("logs/crawler.log", rotation="500 MB", level="INFO")
```
### 2. 输入关键词和其他参数
在 `input_key_word.py` 文件的 `if __name__ == '__main__':` 部分，可以修改搜索关键词、图片保存路径等参数：
```python
if __name__ == '__main__':
    keyword = '玉林路 city walk'  # 搜索关键词
    img_path = '图片'  # 图片保存的文件夹名称
```
### 3. 运行爬虫
在终端中运行 `input_key_word.py` 文件：
```bash
python input_key_word.py
```

## 代码说明
### 主要函数
- `convert_scientific_time`：将科学计数法表示的时间转换为可读的时间格式。
- `base36encode`：将数字转换为 36 进制字符串。
- `generate_search_id`：生成搜索 ID。
- `convert_to_int`：将包含“万”的数字转换为整数。
- `download_img`：下载笔记中的图片。
- `get_feed`：获取笔记的详细信息。
- `parse_data`：解析笔记数据并保存到 CSV 文件中。
- `search`：根据关键词进行搜索。
- `get_note_id`：获取笔记的 `xsec_token` 和 `note_id`。
- `get_data`：获取指定页数范围内的笔记数据。

### 依赖库
- `crypto-js`：用于加密相关操作。
- `sync-request`：用于同步请求。
- `requests`：用于发送 HTTP 请求。
- `loguru`：用于日志记录。
- `execjs`：用于执行 JavaScript 代码。

## 注意事项
- 本项目仅供学习和研究使用，请勿用于商业用途或违反小红书的使用条款。
- 由于小红书可能会更新其网站结构和接口，代码可能需要相应地进行调整。
- 在运行爬虫时，建议设置合理的请求间隔，避免对小红书服务器造成过大压力。

## 贡献
如果你对本项目有任何建议或改进意见，欢迎提交 Issues 或 Pull Requests。

## 许可证
本项目遵循 [MIT 许可证](https://opensource.org/licenses/MIT)。
