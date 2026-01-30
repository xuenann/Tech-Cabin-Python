import requests
from bs4 import BeautifulSoup
import re
import time
from tqdm import tqdm
import json


def get_novel_link(results):
    """
    从小说链接中提取所有章节链接
    """

    base_url = "http://www.wodeshucheng.net"

    page_links = ['index.html']+[f'{i}.html' for i in range(2,2334)]
    # page_links = ['index.html']+[f'{i}.html' for i in range(23,2334)]

    print(f"开始搜索 {len(page_links)} 个页面...")
    i=0
    for page_link in tqdm(page_links, desc="搜索进度"):
        try:
            i+=1
            # if i<1530:
            #     continue
            url = f"{base_url}/map/{page_link}"
            response = requests.get(url,headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            page_soup = BeautifulSoup(response.text, 'html.parser')

            # 添加请求间隔，避免过快请求
            time.sleep(1)  # 1秒间隔

            # 提取小说列表
            content_div = page_soup.find('div', id='content')
            if content_div:
                for ul in content_div.find_all('ul'):
                    for li in ul.find_all('li'):
                        a = li.find('a', href=True)
                        if a:
                            novel_title = a.get_text(strip=True)
                            novel_link = a['href']
                            
                            # 过滤无效链接
                            if not novel_title or not novel_link:
                                continue
                            
                            results.setdefault(novel_title,{'page': i,
                                                            'link': f"{base_url}{novel_link}" if novel_link.startswith('/') else novel_link })
            # break
        except Exception as e:
            print(f"请求页面 {i} {url} 时出错: {e}")
            return results
    
    return results
    
                    


if __name__ == '__main__':
    with open('novel_links.json','r',encoding='utf-8') as f:
        results = json.load(f)
    print(len(results))
    results = get_novel_link(results)
    
    with open('novel_links.json','w',encoding='utf-8') as f:
        json.dump(results,f,ensure_ascii=False,indent=4)
