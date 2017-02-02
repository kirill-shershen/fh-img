# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import os, sys
from urlparse import urlparse, urljoin
from tempfile import NamedTemporaryFile

class FH():
	
	def __init__(self, url, login, password):
		self.login = login
		self.password = password
		self.url = urlparse(url)
		self.url_prefix = 'https://'
		self.base_url = self.url_prefix + self.url.netloc
		self.auth_url = self.base_url + '/auth/login'
		self.session = None
		self.total_pages = 0
		self.auth()
		self.init_params()

	def init_params(self):
		self.total_pages = self.get_total_pages(self.get_html(self.url.geturl()))

	def auth(self):
		try:
			self.session = requests.Session()
			# получаем куки
			resp = self.session.get(self.auth_url)
			self.session.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
			token = re.findall(r'<meta.*?value=\"(.*)\">', resp.text)[0]
			print 'лоигинмся...'
			resp = self.session.post(self.auth_url,
							params=dict(login=self.login, password=self.password, _token=token))
			print 'успешно залогинились'
		except:
			print 'FH:login error'

	def get_html(self, url):
		return self.session.get(url).text

	def get_file(self, url):
		return self.session.get(url, stream = True)

	def get_total_pages(self, html):
		print 'получаем количество страниц по базовому урл'
		res = 0
		soup = BeautifulSoup(html, 'lxml')

		pages = soup.find('div', class_='PageNav').find('nav').find_all('a')[-2].text
		try:
			res = int(pages) if int(pages) > 0 else 0
		except:
			res = 0
		return res

	def get_page_data(self, html):
		soup = BeautifulSoup(html, 'lxml')

		imgs = soup.find_all('a', class_='LbTrigger')
		for img in imgs:
			self.save_image(self.get_file(urljoin(self.base_url, img.get('href'))))

	def save_image(self, obj):
		f = NamedTemporaryFile(mode='w+b', delete=False, suffix='.jpg', dir=os.getcwd())
		for chank in obj.iter_content(8192):
			f.write(chank)
		f.close()

def main():
	if len(sys.argv) == 1 or len(sys.argv) < 4:
		print 'нужно указать урл, логин и пароль'
		exit()
	URL = sys.argv[1]
	login = sys.argv[2]
	password = sys.argv[3]
	if not URL or not login or not password:
		print 'указаны не все параметры'
		exit(0)
	fh = FH(URL, login, password)
	total_pages = fh.total_pages
	print 'начинаем просматривать страницы...'
	for page in range(1, total_pages + 1):
		url = URL + 'page-' + str(page)
		html = fh.get_html(url)
		print 'parsing %s...' % url
		fh.get_page_data(html)
	print 'готово'



if __name__ == '__main__':
	main()