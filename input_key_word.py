import csv
import re
import os
import json
import time
import random
import execjs
import requests
from loguru import logger
from datetime import datetime


def convert_scientific_time(time_str):

    timestamp = float(time_str)

    timestamp_in_seconds = timestamp / 1000

    readable_time = datetime.fromtimestamp(timestamp_in_seconds).strftime('%Y年%m月%d日 %H:%M:%S')

    return readable_time

def base36encode(number, digits='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    base36 = ""
    while number:
        number, i = divmod(number, 36)
        base36 = digits[i] + base36
    return base36.lower()

def generate_search_id():
    timestamp = int(time.time() * 1000) << 64
    random_value = int(random.uniform(0, 2147483646))
    return base36encode(timestamp + random_value)


# # 配置日志
# logger.remove()  # 移除默认的处理器
# logger.add("logs/crawler.log", rotation="500 MB", level="INFO")

def convert_to_int(value):
    if '万' in value:
        value = value.replace('万', '')
        return float(value) * 10000  # 转换为万单位的整数
    else:
        return value

def download_img(data, user_id, note_id):
    image_list = data["data"]["items"][0]["note_card"]["image_list"]
    image_urls = [img["url_default"] for img in image_list]
    output_dir = os.path.join("images", user_id, note_id)
    os.makedirs(output_dir, exist_ok=True)
    for idx, url in enumerate(image_urls):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(os.path.join(output_dir, f"image_{idx + 1}.jpg"), "wb") as f:
                    f.write(response.content)
                    logger.info(f"图片下载成功: {os.path.join(output_dir, f'image_{idx + 1}.jpg')}")
        except Exception as e:
            logger.error(f"图片下载出错: {e}")

def get_feed(source_note_id,xsec_token,cookies):


    url = "https://edith.xiaohongshu.com/api/sns/web/v1/feed"
    api_endpoint = '/api/sns/web/v1/feed'

    data = {
        "source_note_id": source_note_id,
        "image_formats": ["jpg", "webp", "avif"],
        "extra": {"need_body_topic": "1"},
        "xsec_source": "pc_feed",
        "xsec_token": xsec_token
            }
    a1_value = cookies['a1']

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://www.xiaohongshu.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.xiaohongshu.com/",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "rsec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "x-b3-traceid": "9cbac8e2b8562aa3"
    }
    with open('GenXsAndCommon_56.js', 'r', encoding='utf-8') as f:
        js_script = f.read()
        context = execjs.compile(js_script)
        sign = context.call('getXs', api_endpoint, data, a1_value)
    headers['x-s'] = sign['X-s']
    headers['x-t'] = str(sign['X-t'])
    data = json.dumps(data, separators=(',', ':'))
    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    return response.status_code,response.json()


def parse_data(data, keyword, xsec_token):
    fieldnames = [
        "笔记id", "xsec_token","笔记链接","笔记类型", "笔记标题", "笔记正文", "笔记标签",
        "发布时间", "笔记最后更新时间", "图片链接", "点赞数", "收藏数",
        "评论数", "分享数", "用户名", "用户id", "用户ip", "用户头像"
    ]
    file_name = f"{keyword}.csv"
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        item = data['data']['items'][0]
        note_card = item['note_card']
        note_id = item["id"]
        note_url = 'https://www.xiaohongshu.com/explore/' + note_id + '?xsec_token=' + xsec_token + '&xsec_source=pc_feed'
        note_type = item["model_type"]
        desc = note_card.get("desc", "")
        tags = re.findall(r"#([^#]+?)(?=\[话题\])", desc)
        tags = ", ".join(tags)
        interact_info = note_card.get("interact_info", {})
        publish_time = note_card.get("time")
        title = note_card.get("title", "")
        user_info = note_card.get("user", {})
        user_avatar = user_info.get("avatar", "")
        user_name = user_info.get('nickname', '')
        user_id = user_info.get('user_id', '')
        last_updated_time = note_card.get("last_update_time", "")
        like_count = interact_info.get("liked_count", 0)
        collect_count = interact_info.get("collected_count", 0)
        comment_count = interact_info.get("comment_count", 0)
        share_count = interact_info.get("share_count", 0)
        ip = note_card.get("ip_location", "")
        image_url = ""
        if note_card.get("image_list"):
            image_url = note_card["image_list"][0]["info_list"][0]["url"]

        writer.writerow({
            "笔记id": note_id,
            "笔记链接":note_url,
            "xsec_token":xsec_token,
            "笔记类型": note_type,
            "笔记标题": title,
            "笔记正文": desc,
            "笔记标签": tags,
            "发布时间": convert_scientific_time(publish_time),
            "笔记最后更新时间": convert_scientific_time(last_updated_time),
            "图片链接": image_url,
            "点赞数": convert_to_int(like_count),
            "收藏数": convert_to_int(collect_count),
            "评论数": convert_to_int(comment_count),
            "分享数": convert_to_int(share_count),
            "用户名": user_name,
            "用户id": user_id,
            "用户ip": ip,
            "用户头像": user_avatar
        })
    return note_id,user_id

def search(keyword,page,cookies,note_type):
    print(page)
    print('----------------------------------------------------------------')
    search_data = {
        "keyword":keyword,
        "page": str(page),
        "page_size": 20,
        "search_id": generate_search_id(),
        "sort": "popularity_descending",  # popularity_descending,time_descending,general
        "note_type":str(note_type)
    }

    headers = {
        'sec-ch-ua': 'Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Content-Type': 'application/json;charset=UTF-8',
        'sec-ch-ua-mobile': '?0',
        'Referer': 'https://www.xiaohongshu.com/',
        'sec-ch-ua-platform': 'macOS',
        'Origin': 'https://www.xiaohongshu.com',
        'Cookie': ";".join([f"{key}={value}" for key, value in cookies.items()]),
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    url = 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes'
    api_endpoint = '/api/sns/web/v1/search/notes'
    a1_value = cookies['a1']

    with open('GenXsAndCommon_56.js', 'r', encoding='utf-8') as f:
        js_script = f.read()
        context = execjs.compile(js_script)
        sign = context.call('getXs', api_endpoint, search_data, a1_value)

    GREEN = "\033[1;32;40m  %s  \033[0m"

    headers['x-s'] = sign['X-s']
    headers['x-t'] = str(sign['X-t'])
    headers['X-s-common'] = sign['X-s-common']


    response = requests.post(url, headers=headers,
                             data=json.dumps(search_data, separators=(",", ":"), ensure_ascii=False).encode('utf-8'))
    return response.json(),response.status_code


def get_note_id(note):
    xsec_token = note.get('xsec_token')
    note_id = note.get('id')
    return xsec_token,note_id


def get_data(keyword, start_page, end_page, cookies, img_path, is_download_img,note_type):
    logger.info(f"开始获取数据: 关键词={keyword}")
    for page in range(int(start_page),int(end_page)+1):
        logger.info(f"正在获取第 {page} 页")
        data,code = search(keyword,page,cookies,note_type)
        print(data)
        # print(data)
        if code == 200:
            notes = data.get('data', {}).get('items', [])
            logger.info(f"第 {page} 页找到 {len(notes)} 条笔记")
            for note in notes:
                xsec_token,note_id=get_note_id(note)
                error=''
                try:
                    status_code,result=get_feed(note_id,xsec_token,cookies)
                    error=result
                    if status_code==200:
                        note_id,user_id=parse_data(result, keyword, xsec_token)
                        logger.info(f"笔记 {note_id} 获取成功")
                        if is_download_img=='是':
                            download_img(result, user_id, note_id)
                            logger.info(f"笔记 {note_id} 的图片下载成功")
                    else:
                        logger.error(f"获取笔记失败: {status_code}:{result}")
                except:
                    logger.error(f"笔记获取失败：{error}")
            logger.success(f"{keyword} 第 {page} 页获取成功")
        else:
            logger.error(f"获取页面失败: {code}:{data}")
    logger.success(f"任务完成: {keyword}")

if __name__ == '__main__':
    keyword = '玉林路 city walk'#搜索关键词
    img_path='图片'#图片保存的文件夹名称
    is_download_img='否'#是否下载图片；"是"或"否"
    start_page=1
    end_page=11
    note_type=0 #1是视频 2是图文 0是综合
    cookies ={}

    get_data(keyword,start_page,end_page,cookies,img_path,is_download_img,note_type)