#!/bin/python
'''
If you find this useful, https://www.buymeacoffee.com/brucepro
credit to https://old.reddit.com/user/AndrewVeee for the idea.
'''
import sys, os
import requests
import json
import time 
from pathlib import Path
from datetime import datetime
import random
from requests.auth import HTTPBasicAuth
import base64
from urlhandler import UrlHandler
import urllib.parse
import re

def env_or_def(env, default):
	if (env in os.environ):
		return os.environ[env]
	return default
AIurl = f"http://127.0.0.1:8080/completion"

with open('./persona/researcher.json', 'r') as file:
    persona = json.load(file)

researchdata = []
user_response = ""

def construct_search_url(query):
    query = urllib.parse.quote_plus(query)
    return f"https://lite.duckduckgo.com/lite/?q={query}"

def clean_ai_json_response(string):
	sep = '{'
	stripped = '{' + str(string.split(sep, 1)[1])
	sep = '}'
	cleaned_string = stripped.split(sep, 1)[0] + '}'
	return cleaned_string

def compile_answer():
	#take all the research and generate an answer to the question.
	#print(str(researchdata))
	starttime = time.time()
	prompt = str(persona)+ "Answer the question '" + str(user_response) + "' using the data provided by your research:" + str(researchdata) + ". State the facts from your data that support your answer. The answer to your question is..."
	req_json = {
    "stream": False,
    "n_predict": 24576,
    "temperature": 0.7,
    "stop": [
        "</s>",
    ],
    "repeat_last_n": 256,
    "repeat_penalty": 1,
    "top_k": 20,
    "top_p": 0.75,
    "tfs_z": 1,
    "typical_p": 1,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "mirostat": 0,
    "mirostat_tau": 5,
    "mirostat_eta": 0.1,
    "grammar": "",
    "n_probs": 0,
    "prompt": prompt
    }

	res = requests.post(AIurl, json=req_json)
	result = res.json()["content"]
	endtime = time.time()
	runtime = endtime - starttime
	print(f"Compile Answer Runtime: {runtime}s")
	return result

def create_subtask(task):
	task_item = task
	starttime = time.time()
	prompt = str(persona)+ "Generate a complete list of sub-tasks to complete the following task:" + str(task_item) + " . Output is in json format following the format {\"task\": task,\"subtasks\": [sub_task]}. Here is the output in json format..."
	req_json = {
    "stream": False,
    "n_predict": 24576,
    "temperature": 0.7,
    "stop": [
        "</s>",
    ],
    "repeat_last_n": 256,
    "repeat_penalty": 1,
    "top_k": 20,
    "top_p": 0.75,
    "tfs_z": 1,
    "typical_p": 1,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "mirostat": 0,
    "mirostat_tau": 5,
    "mirostat_eta": 0.1,
    "grammar": "",
    "n_probs": 0,
    "prompt": prompt
    }

	res = requests.post(AIurl, json=req_json)
	result = res.json()["content"]
	cleaned_result = clean_ai_json_response(result)
	print("-------------------------------------------------------")
	print("Outline of my thought process:" + str(cleaned_result))
	print("-------------------------------------------------------")
	endtime = time.time()
	runtime = endtime - starttime
	print(f"Creating Subtask Runtime: {runtime}s")
	data = run_subtask(cleaned_result)
	answer = compile_answer()
	return answer

def run_subtask(tasks):
	#print(str(tasks))
	tasklist = json.loads(tasks)
	#print("TASKLIST:" + str(tasklist))
	print("Working on task:" + str(tasklist['task']))
	for task_item in tasklist['subtasks']:
		print("TASK ITEM:" + str(task_item))
		starttime = time.time()
		prompt = str(persona)+ "Your task is to research the topic:" + str(task_item) + ". Generate a list of 3 search queries that will provide the data to answer the question='" + str(tasklist['task']) + "' . These queries will be used in your Search(query) function in another step. Output should be in json format following the format {\"query\": [query]}. Only print the output of the json. Here is the output in json format..."
		#print(prompt)
		req_json = {
	    "stream": False,
	    "n_predict": 24576,
	    "temperature": 0.7,
	    "stop": [
	        "</s>",
	    ],
	    "repeat_last_n": 256,
	    "repeat_penalty": 1,
	    "top_k": 20,
	    "top_p": 0.75,
	    "tfs_z": 1,
	    "typical_p": 1,
	    "presence_penalty": 0,
	    "frequency_penalty": 0,
	    "mirostat": 0,
	    "mirostat_tau": 5,
	    "mirostat_eta": 0.1,
	    "grammar": "",
	    "n_probs": 0,
	    "prompt": prompt
	    }

		res = requests.post(AIurl, json=req_json)
		result = res.json()["content"]
		endtime = time.time()
		runtime = endtime - starttime
		print(f"Run Subtask Runtime: {runtime}s")
		cleaned_result = clean_ai_json_response(result)
		data = research(str(task_item),cleaned_result)
		#print("Adding to my research data:" + str(data))
		researchdata.append(data)
	return

def research(question,querylist):
	researchlist = json.loads(querylist)
	#print("researchlist:" + str(researchlist))
	#for query_item in researchlist['search_query']:
	if 'query' in researchlist:
		searchqueries = ', '.join(researchlist['query'])
	if 'search_query' in researchlist:
		searchqueries = ', '.join(researchlist['search_query'])

	#assume the json might be wonky.
	if searchqueries in locals():
		print(f"Searching DuckDuckGo for: {searchqueries}")
		url = construct_search_url(str(searchqueries))
		search = UrlHandler()
		search_data = search.get_url(url,mode='output')
		search_data_cleaned = os.linesep.join([s for s in search_data.splitlines() if s])
		#2500 should return about 5 results from duckduckgo
		#print(search_data_cleaned[:2500])
		starttime = time.time()
		prompt = str(persona)+ "Your Search(query) function has returned the data. Answer the query based on the provided data, only answer the question and do not add additional comments. Search results:" + str(search_data_cleaned[:2500]) + "Answer the question: " + str(question) + ". The answer to your question is..."
		#print(prompt)
		req_json = {
		"stream": False,
		"n_predict": 24576,
		"temperature": 0.7,
		"stop": [
		    "</s>",
		],
		"repeat_last_n": 256,
		"repeat_penalty": 1,
		"top_k": 20,
		"top_p": 0.75,
		"tfs_z": 1,
		"typical_p": 1,
		"presence_penalty": 0,
		"frequency_penalty": 0,
		"mirostat": 0,
		"mirostat_tau": 5,
		"mirostat_eta": 0.1,
		"grammar": "",
		"n_probs": 0,
		"prompt": prompt
		}

		#print(prompt)
		res = requests.post(AIurl, json=req_json)
		result = res.json()["content"]
		#print(result)
		
		endtime = time.time()
		runtime = endtime - starttime
		print(f"Research Runtime: {runtime}s")
		return(result)

while True:
    user_response = input("Ask me a question, I will provide a list of sub-task that may allow me to do the research: ")
    bot_response = create_subtask(user_response)
    print("Here are the responses to your question:", bot_response)
    print("---------------------------------")
    print("Here is the research data I used. " + str(researchdata))
    print("---------------------------------")