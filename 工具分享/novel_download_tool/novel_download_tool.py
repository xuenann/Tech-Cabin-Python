from ntpath import getsize
import os
import asyncio
import re
from playwright.async_api import async_playwright
from urllib.parse import urljoin
from tqdm import tqdm
import time
import json


# 数据预加载 - 模块导入时只加载一次
print("正在加载小说数据...")
_start_time = time.time()
with open('novel_links.json','r',encoding='utf-8') as f:
    _NOVEL_DATA = json.load(f)
_load_time = time.time() - _start_time
print(f"数据加载完成，耗时: {_load_time:.2f}秒，包含 {len(_NOVEL_DATA)} 本小说")

# 预处理：将小说名转换为小写，避免每次搜索时重复转换
_PREPROCESSED_NOVELS = {
    name.lower(): {
        'original_name': name,
        'info': info
    }
    for name, info in _NOVEL_DATA.items()
}

def search_novel(keyword):
    """
    搜索小说，使用预处理数据提高性能
    """
    keyword_lower = keyword.lower()
    
    # 使用生成器表达式减少内存使用
    matched_novels = [
        (novel['original_name'], novel['info']) 
        for name_lower, novel in _PREPROCESSED_NOVELS.items() 
        if keyword_lower in name_lower
    ]
    
    # 转换为字典格式返回
    return matched_novels


BASE_URL = "https://www.wodeshucheng.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
async def get_chapter_list(page, url):
    print(f"正在加载页面: {url}")
    # 增加超时设置和错误处理
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            await page.goto(url, timeout=60000)  # 增加超时到60秒
            await page.wait_for_load_state('networkidle', timeout=45000)
            print("页面加载完成")
            break
        except Exception as e:
            retry_count += 1
            print(f"  页面加载失败，正在重试 ({retry_count}/{max_retries}): {e}")
            if retry_count >= max_retries:
                raise
            await asyncio.sleep(2)  # 重试前等待
    
    chapter_list = []
    
    # 只获取正文部分的章节链接
    # 方法1：直接获取所有section-box，然后筛选包含正文的部分
    section_boxes = await page.query_selector_all('div.section-box')
    
    found_content = False
    
    for i, box in enumerate(section_boxes):
        # 获取section-box前的标题
        prev_element = await box.evaluate('element => { let prev = element.previousElementSibling; while (prev) { if (prev.tagName === "H2" && prev.classList.contains("layout-tit")) { return prev.textContent; } prev = prev.previousElementSibling; } return ""; }')
        
        if "正文" in prev_element:
            # 这是正文部分的section-box
            print(f"找到正文部分的章节列表 (第{i+1}个section-box)")
            
            # 获取该section-box中的所有章节链接
            links = await box.query_selector_all('ul.section-list.fix li a[href]')
            print(f"在正文部分找到 {len(links)} 个章节链接")
            
            for link in links:
                text = await link.text_content()
                href = await link.get_attribute('href')
                text = text.strip() if text else ""
                
                if text and href:
                    full_url = urljoin(BASE_URL, href)
                    chapter_list.append({
                        "title": text,
                        "url": full_url
                    })
            
            found_content = True
            break
    
    if not found_content:
        # 如果没有找到正文部分，使用原来的方法作为后备
        links = await page.query_selector_all('a[href]')
        print(f"未找到正文部分，使用通用方法，找到 {len(links)} 个链接")
        
        for link in links:
            text = await link.text_content()
            href = await link.get_attribute('href')
            text = text.strip() if text else ""
            
            if text.startswith("第") and "章" in text and href:
                full_url = urljoin(BASE_URL, href)
                chapter_list.append({
                    "title": text,
                    "url": full_url
                })
    
    print(f"筛选出 {len(chapter_list)} 个章节")
    return chapter_list

async def fetch_chapter(page, chapter):
    print(f"正在抓取章节: {chapter['title']}")
    # 增加超时设置和错误处理
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            await page.goto(chapter["url"], timeout=60000)  # 增加超时到60秒
            await page.wait_for_load_state('networkidle', timeout=45000)
            break
        except Exception as e:
            retry_count += 1
            print(f"  访问失败，正在重试 ({retry_count}/{max_retries}): {e}")
            if retry_count >= max_retries:
                raise
            await asyncio.sleep(2)  # 重试前等待
    
    title_element = await page.query_selector('h1')
    title = await title_element.text_content() if title_element else chapter["title"]
    title = title.strip() if title else chapter["title"]
    
    chapter_text = title + "\n\n"
    page_count = 1
    
    while True:
        print(f"  正在抓取第 {page_count} 页...")
        content_element = await page.query_selector('#content')
        if not content_element:
            content_element = await page.query_selector('.content')
        
        if content_element:
            paragraphs = await content_element.query_selector_all('p')
            if paragraphs:
                for p in paragraphs:
                    text = await p.text_content()
                    if text and text.strip():
                        chapter_text += text.strip() + "\n"
            else:
                text = await content_element.text_content()
                if text:
                    chapter_text += text.strip() + "\n"
        
        next_button = await page.query_selector('a:has-text("下一页")')
        if next_button:
            print(f"  找到下一页按钮，正在点击...")
            try:
                await next_button.click(timeout=60000)  # 增加超时设置
                await page.wait_for_load_state('networkidle', timeout=45000)
                page_count += 1
                time.sleep(0.5)
            except Exception as e:
                print(f"  点击下一页失败: {e}")
                # 点击下一页失败，放弃这章内容
                raise Exception(f"下一页点击失败，章节内容不完整: {e}")
        else:
            print(f"  没有找到下一页按钮，本章节共 {page_count} 页")
            break

    return chapter_text

async def main(novel_name,info):
    print("启动浏览器...")
    os.makedirs(novel_name, exist_ok=True)
    file_list=[file for file in os.listdir(novel_name) if os.path.getsize(f"{novel_name}/{file}")>20]
    if 'https' not in info['link']:
        info['link'] = info['link'].replace('http','https')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        chapter=0
        i=2
        link_num=info['link']
        try:
            while 1:
                print(f"正在访问章节列表页面: {link_num}")
                chapters = await get_chapter_list(page, link_num)
                print(f"发现 {len(chapters)} 个章节")

                if not chapters:
                    print(f"未找到章节:{link_num}")
                    break

                print(f"开始抓取 {len(chapters)} 个章节...")
                for ch in tqdm(chapters, desc="抓取章节"):
                    try:
                        chapter+=1
                        fname = f"{chapter}-{ch['title'].replace('/', '_')}.txt"
                        if fname in file_list:
                            print(f"跳过已下载章节：{ch['title']}")
                            continue

                        text = await fetch_chapter(page, ch)
                        if not text.strip():
                            print(f"跳过空内容章节: {ch['title']}")
                            continue

                        # 处理文本，删除包含指定关键词的整段
                        # 定义要匹配的关键词
                        keywords = ['我的书城', 'www.wodeshucheng.com']
                        
                        # 对每个关键词，删除从关键词开始到下一个换行符的整段
                        processed_text = text
                        for keyword in keywords:
                            # 正则表达式：匹配关键词开始到下一个换行符的所有内容
                            pattern = f'{re.escape(keyword)}.*?\n'
                            processed_text = re.sub(pattern, '', processed_text, flags=re.DOTALL)
                        
                        with open(os.path.join(novel_name, fname), "w", encoding="utf-8") as f:
                            f.write(ch['title'].replace('/', '_') + processed_text)
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"抓取失败: {ch['title']} => {e}")
                        import traceback
                        traceback.print_exc()
                print("抓取完成！")
                link_num=f"{info['link']}/{i}/"
                i+=1
        except Exception as e:
            print(f"发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()
        

def merge_txt(novel_name):
    file_list=sorted(os.listdir(novel_name),key=lambda x:int(x.split('-')[0]))
    no_num_list=[i for i in range(1,int(file_list[-1].split('-')[0])+1)]
    with open(f'{novel_name}.txt','w',encoding='utf-8') as f:
        for file in tqdm(file_list,desc='合并章节'):
            try:
                no_num_list.remove(int(file.split('-')[0]))
                with open(f'{novel_name}/{file}','r',encoding='utf-8') as fr:
                    f.write(fr.read()+'\n\n')
            except Exception as e:
                print(e)
                print(file)
                no_num_list.append(file)
                continue 
    
    return no_num_list


if __name__ == "__main__":
    print("小说搜索工具")
    print("=" * 50)
    
    while True:
        keyword = input("请输入要搜索的小说名（输入 'q' 退出）: ")
        
        if keyword.lower() == 'q':
            break
        
        if not keyword:
            print("请输入搜索关键词")
            continue
        
        print(f"正在搜索包含 '{keyword}' 的小说...")
        print("=" * 50)
        
        matched_novels = search_novel(keyword)
        
        if matched_novels:
            print(f"找到 {len(matched_novels)} 本匹配的小说:\n默认显示匹配到的前50本")
            print("=" * 50)
            
            for i, (novel_name, info) in enumerate(matched_novels, 1):
                if i==50:
                    break
                print(f"{i}. {novel_name}")
                print(f"   链接: {info['link']}")
                print(f"   所在页面: 第{info['page']}页")
                print("-" * 30)
            
            # 选择下载、重新搜索、或退出
            keyword = input("请输入要下载的小说编号，或输入 'f' 重新搜索、输入 'q' 退出: ")
            if keyword=='f' or int(keyword)>len(matched_novels) or int(keyword)<1:
                continue
            elif keyword=='q':
                break
            else:
                novel_name,info=matched_novels[int(keyword)-1]
                asyncio.run(main(novel_name,info))

                no_num_list=merge_txt(novel_name)
                print(f"未下载章节：{no_num_list}")
        else:
            print(f"未找到包含 '{keyword}' 的小说")
        
        print("=" * 50)