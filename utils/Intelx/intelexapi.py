#!/usr/bin/env python3

import requests
import time
import json
import sys
import re
import os

from utils.commonFunctions import randomUserAgent

class intelx:

	# If an API key isn't supplied, it will use the free API key (limited functionality)
	def __init__(self, key ="8134168d-053b-4042-adbe-19ab981d82aa" , ua=randomUserAgent("utils/userAgentsList.txt")):
		"""
		Initialize API by setting the API key.
		"""
		if key == "01a61412-7629-4288-b18a-b287266f2798" or key == "ac572eea-3902-4e9a-972d-f5996d76174c":
			self.API_ROOT 	= "https://public.intelx.io"
		else:
			self.API_ROOT 	= "https://2.intelx.io"

		self.API_KEY = key
		self.USER_AGENT = ua

	def get_error(self, code):
		"""
		Get error string by respective HTTP response code.
		"""
		if code == 200:
			return "200 | Success"
		if code == 204:
			return "204 | No Content"
		if code == 400:
			return "400 | Bad Request"
		if code == 401:
			return "401 | Unauthorized"
		if code == 402:
			return "402 | Payment required."
		if code == 404:
			return "404 | Not Found"
		"""
		Show a treeview of an item that has multiple files/folders
		"""
		try:
			r = requests.get(f"{self.API_ROOT}/file/view?f=12&storageid={id}&k={self.API_KEY}", timeout=5)
			if "Could not generate" in r.text:
				return False
			return r.text
		except:
			return False

	def INTEL_SEARCH(self, term, maxresults=100, buckets=[], timeout=5, datefrom="", dateto="", sort=4, media=0, terminate=[]):
		"""
		Launch an Intelligence X Search
		"""
		h = {'x-key' : self.API_KEY, 'User-Agent': self.USER_AGENT}
		p = {
			"term": term,
			"buckets": buckets,
			"lookuplevel": 0,
			"maxresults": maxresults,
			"timeout": timeout,
			"datefrom": datefrom,
			"dateto": dateto,
			"sort": sort,
			"media": media,
			"terminate": terminate
		}
		r = requests.post(self.API_ROOT + '/intelligent/search', headers=h, json=p)
		if r.status_code == 200:
			return r.json()['id']
		else:
			return r.status_code

	def INTEL_SEARCH_RESULT(self, id, limit):
		"""
		Return results from an initialized search based on its ID
		"""
		h = {'x-key' : self.API_KEY, 'User-Agent': self.USER_AGENT}
		r = requests.get(self.API_ROOT + f'/intelligent/search/result?id={id}&limit={limit}', headers=h)
		if(r.status_code == 200):
			return r.json()
		else:
			return r.status_code

	def INTEL_TERMINATE_SEARCH(self, uuid):
		"""
		Terminate a previously initialized search based on its UUID.
		"""
		h = {'x-key' : self.API_KEY, 'User-Agent': self.USER_AGENT}
		r = requests.get(self.API_ROOT + f'/intelligent/search/terminate?id={uuid}', headers=h)
		if(r.status_code == 200):
			return True
		else:
			return r.status_code
	
		"""
		Fetch results from a phonebook search based on ID.
		"""
		h = {'x-key' : self.API_KEY, 'User-Agent': self.USER_AGENT}
		r = requests.get(self.API_ROOT + f'/phonebook/search/result?id={id}&limit={limit}&offset={offset}', headers=h)
		if(r.status_code == 200):
			return r.json()
		else:
			return r.status_code

	def query_results(self, id, limit):
		"""
		Query the results from an intelligent search.
		Meant for usage within loops.
		"""
		results = self.INTEL_SEARCH_RESULT(id, limit)
		return results

	def search(self, term, maxresults=100, buckets=[], timeout=5, datefrom="", dateto="", sort=4, media=0, terminate=[]):
		"""
		Conduct a simple search based on a search term.
		Other arguments have default values set, however they can be overridden to complete an advanced search.
		"""
		results = []
		done = False
		search_id = self.INTEL_SEARCH(term, maxresults, buckets, timeout, datefrom, dateto, sort, media, terminate)
		if(len(str(search_id)) <= 3):
			print(f"[!] intelx.INTEL_SEARCH() Received {self.get_error(search_id)}")
			sys.exit()
		while done == False:
			time.sleep(1) # lets give the backend a chance to aggregate our data
			r = self.query_results(search_id, maxresults)
			for a in r['records']:
				results.append(a)
			maxresults -= len(r['records'])
			if(r['status'] == 1 or r['status'] == 2 or maxresults <= 0):
				if(maxresults <= 0):
					self.INTEL_TERMINATE_SEARCH(search_id)
				done = True
		return {'records': results}


		stats = {}
		for record in search['records']:
			if record['bucket'] not in stats:
				stats[record['bucket']] = 1
			else:
				stats[record['bucket']] += 1
		return json.dumps(stats)

	def emailOrPhoneSearch(self, target):
		search = self.search(target)
		for record in search['records']:
			print(f"Found media type {record['media']} in {record['bucket']} with an id {record['storageid']}")
		return search