import os
import asyncio
import re
import time
import json
import argparse
from urllib.parse import urljoin

import aiohttp
from lxml import etree
from tqdm import tqdm

# =========================
# 数据预加载
# =========================
print("正在加载小说数据...")
_start_time = time.time()
with open('novel_links.json', 'r', encoding='utf-8') as f:
    _NOVEL_DATA = json.load(f)
_load_time = time.time() - _start_time
print(f"数据加载完成，耗时: {_load_time:.2f}秒，包含 {_NOVEL_DATA.__len__()} 本小说")

_PREPROCESSED_NOVELS = {
    name.lower(): {
        'original_name': name,
        'info': info
    }
    for name, info in _NOVEL_DATA.items()
}

def search_novel(keyword):
    keyword_lower = keyword.lower()
    return [
        (novel['original_name'], novel['info'])
        for name_lower, novel in _PREPROCESSED_NOVELS.items()
        if keyword_lower in name_lower
    ]


# =========================
# 网络配置
# =========================
BASE_URL = "https://www.wodeshucheng.net"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# =========================
# HTTP 工具函数
# =========================
async def fetch_html(session, url, retries=3):
    for i in range(retries):
        try:
            async with session.get(url, headers=HEADERS, timeout=30) as resp:
                return await resp.text(encoding="utf-8", errors="ignore")
        except Exception as e:
            if i == retries - 1:
                raise
            await asyncio.sleep(1)


# =========================
# 章节列表解析
# =========================
async def get_chapter_list(session, url):
    print(f"正在加载章节列表页: {url}")
    html = await fetch_html(session, url)
    tree = etree.HTML(html)

    chapter_list = []

    # 找正文 section-box
    boxes = tree.xpath('//div[@class="section-box"]')
    for box in boxes:
        prev = box.getprevious()
        while prev is not None:
            if prev.tag == 'h2' and 'layout-tit' in prev.attrib.get('class', ''):
                if '正文' in ''.join(prev.itertext()):
                    links = box.xpath('.//ul[@class="section-list fix"]//a')
                    for a in links:
                        title = ''.join(a.itertext()).strip()
                        href = a.attrib.get('href')
                        if title and href:
                            chapter_list.append({
                                "title": title,
                                "url": urljoin(BASE_URL, href)
                            })
                    return chapter_list
                break
            prev = prev.getprevious()

    # 兜底方案
    links = tree.xpath('//a[contains(text(),"章")]')
    for a in links:
        title = ''.join(a.itertext()).strip()
        href = a.attrib.get('href')
        if title.startswith("第") and href:
            chapter_list.append({
                "title": title,
                "url": urljoin(BASE_URL, href)
            })

    return chapter_list


# =========================
# 章节内容抓取（支持“下一页”）
# =========================
async def fetch_chapter(session, chapter,chapter_no):
    print(f"正在抓取章节: {chapter_no}-{chapter['title']}")
    content = "\n"
    url = chapter["url"]

    while True:
        html = await fetch_html(session, url)
        tree = etree.HTML(html)

        texts = tree.xpath('//div[@id="content"]//text()')
        if not texts:
            texts = tree.xpath('//div[@class="content"]//text()')

        for t in texts:
            t = t.strip()
            if t:
                content += t + "\n"

        next_links = tree.xpath('//a[text()=" 下一页"]/@href')

        if next_links:
            url = urljoin(BASE_URL, next_links[0])
            await asyncio.sleep(0.3)
        else:
            break

    return content


# =========================
# 主逻辑
# =========================
async def main(novel_name, info):
    os.makedirs(novel_name, exist_ok=True)

    file_list = [
        f for f in os.listdir(novel_name)
        if os.path.getsize(os.path.join(novel_name, f)) > 20
    ]

    info['link'] = info['link'].replace('http://', 'https://').replace('books', 'book')
    link_num = info['link']
    chapter_no = 0

    async with aiohttp.ClientSession() as session:
        while True:
            chapters = await get_chapter_list(session, link_num)
            if not chapters:
                break

            # for ch in tqdm(chapters, desc="抓取章节"):
            for ch in chapters:
                chapter_no += 1
                fname = f"{chapter_no}-{ch['title'].replace('/', '_')}.txt"
                if fname in file_list:
                    continue

                try:
                    text = await fetch_chapter(session, ch ,chapter_no)
                    if not text.strip():
                        continue

                    for kw in ['我的书城', 'www.wodeshucheng.com']:
                        text = re.sub(f'\n.*?{re.escape(kw)}.*?\n', '', text)

                    with open(os.path.join(novel_name, fname), "w", encoding="utf-8") as f:
                        f.write(fname.replace('.txt', '') + '\n\n' + text)

                except Exception as e:
                    print(f"抓取失败: {ch['title']} => {e}")
            
            html = await fetch_html(session, link_num)
            tree = etree.HTML(html)

            next_links = tree.xpath('//a[text()="下一页"]/@href')
            if next_links:
                link_num = urljoin(BASE_URL, next_links[0])
            else:
                break

            # link_num = f"{info['link']}{page_index}/"
            # page_index += 1


# =========================
# 合并章节
# =========================
def merge_txt(novel_name):
    files = sorted(
        os.listdir(novel_name),
        key=lambda x: int(x.split('-')[0])
    )

    with open(f"{novel_name}.txt", "w", encoding="utf-8") as out:
        for f in tqdm(files, desc="合并章节"):
            try:
                with open(os.path.join(novel_name, f), "r", encoding="utf-8") as fr:
                    out.write(fr.read() + "\n\n")
            except Exception as e:
                print("合并失败:", f, e)


# =========================
# CLI 入口
# =========================
if __name__ == "__main__":
    print("小说搜索工具")
    print("=" * 50)

    while True:
        keyword = input("请输入要搜索的小说名（输入 'q' 退出）: ").strip()
        if keyword.lower() == 'q':
            break

        matched = search_novel(keyword)
        if not matched:
            print("未找到小说")
            continue

        for i, (name, info) in enumerate(matched[:50], 1):
            print(f"{i}. {name}")
            print(f"   链接: {info['link']}")
            print("-" * 30)

        sel = input("请输入要下载的小说编号（q 退出）: ").strip()
        if sel.lower() == 'q':
            break

        idx = int(sel) - 1
        novel_name, info = matched[idx]

        asyncio.run(main(f"save_data/{novel_name}", info))
        merge_txt(f"save_data/{novel_name}")
