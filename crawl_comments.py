import requests
import pandas as pd
import time
import random
from tqdm import tqdm

# Tạo session để tái sử dụng kết nối và retry
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=3)
session.mount('http://', adapter)
session.mount('https://', adapter)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'vi-VN,vi;q=0.9',
    'Referer': '',  # Sẽ cập nhật động https://tiki.vn/architecture-concept-book-an-inspirational-guide-to-cre-the-p276672265.html?spid=276672266
    'x-guest-token': 'undefined'
}

params = {
    'limit': '5',
    'include': 'comments,contribute_info,attribute_vote_summary',
    'sort': 'score|desc,id|desc,stars|all',
    'page': 1,
    # 'spid': 127538916
    'product_id': '',
    'seller_id': 1
}

def get_detail_comment(json, id_product):
    m = dict()
    try: 
        m['id_comment'] = json.get('id')
        m['title'] = json.get('title')
        m['content'] = json.get('content')
        m['rating'] = json.get('rating')
        m['id_product'] = id_product
        m['timeline'] = json.get('timeline').get('review_created_date')
    except Exception as e:
            print(f"⚠️ Error : {e}")
    return m
df_detail_product = pd.read_excel('detail_product.xlsx')
df_products = df_detail_product[['id','url_path']]
detail_comments = []
ind = 1
for index, row in df_products.iterrows():
    params['product_id'] = row['id']
    headers['Referer'] =  'https://tiki.vn/' + row['url_path']
    print(f"✅ Crawler product {row['id']} - link {row['url_path']}")
    print(f"Crawler {ind}")
    for i in range(1, 10000):
        params['page'] = i
        try:
            response = session.get('https://tiki.vn/api/v2/reviews', headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', [])
                if not data:
                    break  # Không còn sản phẩm
                for record in data:
                    detail_comments.append(get_detail_comment(record, row['id']))
                print(f"✅ Done page {i} - {len(data)} comments")
            else:
                print(f"❌ Status {response.status_code} on id {i}")
        except Exception as e:
            print(f"⚠️ Error on page {i}: {e}")
        time.sleep(random.uniform(3, 5))
        # print(params['product_id'], headers['Referer'])
    ind += 1 
df_detail_comments = pd.DataFrame(detail_comments)
df_detail_comments.to_excel('detail_comments.xlsx')
