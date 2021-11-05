from platform import python_version
import sys

import requests

sys.setrecursionlimit(10**6)
print(python_version())

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
# from urllib.parse import parse_qs
# from urllib.parse import parse_multipart

import urllib
import ast
import json
from time import time as timer
from multiprocessing.pool import ThreadPool
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from requests.exceptions import HTTPError
import io
import os
os.environ['NO_PROXY'] = '127.0.0.1'
import time
import cgi
import base64
import hashlib
import qrcode

import tarantool
import shutil
import requests
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
import time
import test



connection = tarantool.connect("localhost", 3301)
tarantool.connect("localhost", 3301, user="admin", password="password")
urls = connection.space('urls5')

# urls.delete("https://yandex.ru/", index=1)
# print("urls.select(4): ", urls.select(4))


class myHandler(BaseHTTPRequestHandler):
	def parse_POST(self):
		ctype, pdict = cgi.parse_header(self.headers['content-type'])

		if ctype == 'multipart/form-data':
			postvars = urllib.parse.parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers['content-length'])
			postvars = urllib.parse.parse_qs(self.rfile.read(length), keep_blank_values=1)
		else:
			postvars = {}
		return postvars
	def finish(self):
		if not self.wfile.closed:
		    self.wfile.flush()
		self.wfile.close()
		self.rfile.close()
	def do_POST(self):
		postvars = self.parse_POST()
		
		self.send_response(200, "OK")
		# self.send_header('Content-type','text/html')
		
		path = self.path

		
		
		if path == "/set":
			print("post set")
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			origin_url = str(postvars[b'url']).replace("[b'","").replace("']","")
			hasher = hashlib.sha1(str(origin_url).encode('utf-8'))
			hash_str = base64.urlsafe_b64encode(hasher.digest()[:10]).decode('ascii').replace("=","")
			try:
				parsed_uri = urlparse(origin_url)
				domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
				print("domain:",domain)

				print("self.client_address[0]:",self.client_address[0])
				urls.insert((hash_str, origin_url,self.client_address[0],domain,0))
			except Exception as e:
				pass

			extra_info = '[]'
			recomend_urls_out = ""
			try:
				extra_info = str(urls.select(hash_str))
				extra_info_arr = str(extra_info).replace('- ', '')
				extra_info_arr = ast.literal_eval(extra_info_arr)
				extra_info_arr = [str(n).strip() for n in extra_info_arr]
				
				print("extra_info_arr[3]:",extra_info_arr[3])
				recomend_urls = str(urls.select(extra_info_arr[3], index=1))
				recomend_urls = recomend_urls.replace('- ', '').split("\n")
				rec_url = ""
				for item in recomend_urls:
					rec_url = item.replace("\n","")
					rec_url = str(rec_url).replace("'",'"')
					# print("rec_url:",rec_url)
					# rec_url = ast.literal_eval(rec_url)
					rec_url = json.loads(rec_url)
					print(rec_url[1])
					# print("rec_url:",rec_url)
					recomend_urls_out += rec_url[1] + " "
				recomend_urls_out
				print("recomend_urls:",recomend_urls)
			except Exception as e:
				pass

			

			
			out = '{"short_url": "http://137.184.70.55:88/'+hash_str+'", "extra_info":'+extra_info.replace('- ', '').replace("'",'"')+',"recomend_urls":"'+recomend_urls_out+'"}'
			self.wfile.write(out.encode(encoding='utf_8'))
		if path == "/test":
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			count = str(postvars[b'count']).replace("[b'","").replace("']","")
			count = int(count)
			
			out = test.test_set_urls(count)
			print("out:",out)
			out += test.test_get_urls()
			
			print("out:",out)
			self.wfile.write(out.encode(encoding='utf_8'))

			

		# self.connection.close()
		# self.finish()

	# Handler for the GET requests
	def do_GET(self):
		path = self.path.replace('/','')
		if "get_qr_code" in path: 
			query_components = urllib.parse.parse_qs(urlparse(self.path).query)
			url = query_components["url"][0]
			img = qrcode.make(url)
			content_path = "some_file.png"
			img.save(content_path)

			self.send_response(200)
			self.send_header('Content-type', 'image/png')
			self.end_headers()


			with open(content_path, 'rb') as content:
			    shutil.copyfileobj(content, self.wfile)
			
		else:
			row = urls.select(path)
			print("row:",row)
			row = str(row).replace('- ', '')
			row = ast.literal_eval(row)
			row = [str(n).strip() for n in row]

			
			urls.update(row[0], [('+', 4, 1)])

			print("after update row:",urls.select(path))
	        
			self.wfile.write("".encode(encoding='utf_8'))

			self.send_response(301)
			self.send_header('Location',row[1]);
			self.end_headers()
			
	def end_headers(self):
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', '*')
		self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
		return super(myHandler, self).end_headers()



class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

server = ThreadingSimpleServer(('137.184.70.55', 88), myHandler)
server.serve_forever()



