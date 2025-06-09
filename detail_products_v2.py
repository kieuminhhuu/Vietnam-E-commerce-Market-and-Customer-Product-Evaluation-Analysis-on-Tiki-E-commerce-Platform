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
    'Referer': 'https://tiki.vn/dien-thoai-may-tinh-bang/c1789',  # Sẽ cập nhật động
    'x-guest-token': 'undefined'
}

params = {
    'limit': '40',
    'include': 'advertisement',
    'aggregations': '2',
    'version': 'home-persionalized',
    'trackity_id': 'c1ba669b-801b-2819-3454-2ea1e9f0841e',
    'category': '1789',  # cập nhật động
    'page': '1',
    'urlKey': 'dien-thoai-may-tinh-bang',  # cập nhật động
}
def get_detail_product(json):
    try:
        d = dict()
        d['id'] = json.get('id')
        d['name'] = json.get('name')
        d['url_path'] = json.get('url_path')
        d['brand_name'] = json.get('brand_name')
        d['price'] = json.get('price')
        d['rating_average'] = json.get('rating_average')
        d['discount'] = json.get('discount')
        d['discount_rate'] = json.get('discount_rate')
        d['quantity_sold'] = json.get('quantity_sold').get('value')
    except Exception as e:
        print(f"⚠️ Error : {e}")
    return d

detail_product = []
for i in range(1, 26):  # 5 trang
    params['page'] = i
    try:
        response = session.get('https://tiki.vn/api/personalish/v1/blocks/listings', headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json().get('data', [])
            if not data:
                break  # Không còn sản phẩm
            for record in data:
               detail_product.append(get_detail_product(record))
            print(f"✅ Done page {i} - {len(data)} products")
        else:
            print(f"❌ Status {response.status_code} on page {i}")
    except Exception as e:
        print(f"⚠️ Error on page {i}: {e}")
    time.sleep(random.uniform(3, 5))
df_detail_product = pd.DataFrame(detail_product)
df_detail_product.to_excel('detail_product.xlsx')
print(df_detail_product)