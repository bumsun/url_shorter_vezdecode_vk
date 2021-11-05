import requests
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
import time

chars = "abcdefghijklmnopqrstuvwxyz"
url_list = []
short_url_list = []
success_get_url_list = []
def set_url_request(url):
    try:
        response = requests.post('http://137.184.70.55:88/set', data={'url':url},headers={'Content-Type':"application/x-www-form-urlencoded"}, timeout=1.0)
        json_response = response.json()
        short_url = json_response['short_url']
        return short_url
    except requests.exceptions.RequestException as e:
        pass
def get_url_request(url):
    try:
        response = requests.get(url, allow_redirects=False, timeout=1.0)
        return 1
    except requests.exceptions.RequestException as e:
        pass
      #  print("download_file e:",e)
def test_set_urls(count_url = 1000):
    global url_list
    global short_url_list
    global success_get_url_list
    url_list = []
    short_url_list = []
    success_get_url_list = []
    n = 10
    for i in range(5, n+1):
        
        for item in itertools.product(chars, repeat=i):
            if len(url_list) > count_url-1:
                break
            url_list.append("http://"+"".join(item)+".ru")

    threads= []
    

    start = time.time()
    with ThreadPoolExecutor(max_workers=1000) as executor:
        for url in url_list:
            threads.append(executor.submit(set_url_request, url))
            
        for task in as_completed(threads):
            short_url_list.append(task.result())
            # print(len(short_url_list))
    end = time.time()
    out = "Заняло "+str(end - start)+" секунд на добавление "+ str(len(short_url_list))+" ссылок\n"
    out += "Скорость: "+str(len(short_url_list)/(end - start))+" RPS\n"
    return out

def test_get_urls():
    threads= []
    start = time.time()
    with ThreadPoolExecutor(max_workers=1000) as executor:
        for url in short_url_list:
            threads.append(executor.submit(get_url_request, url))
            
        for task in as_completed(threads):
            success_get_url_list.append(task.result())
            # print(len(short_url_list))
    end = time.time()
    out = "Заняло "+str(end - start)+" секунд на открытие "+str(len(short_url_list))+" ссылок\n"
    out += "Скорость: "+str(len(short_url_list)/(end - start))+" RPS\n"
    return out
    




