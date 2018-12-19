"""
Routes and views for the flask application.
"""
from smART import app
from flask import Flask, render_template, request, redirect, url_for
#from init import app
import urllib
import os
import sys
import random
reload(sys)
sys.setdefaultencoding('utf8')
def get_page(url):
	try:
		f = urllib.urlopen(url)
		page = f.read()
		f.close()
		return page
	except:	
		return ""
	return ""
def union(a,b):
	for e in b:
		if e not in a:
			a.append(e)

def get_next_url(page):
	start_link=page.find("a href")
	if(start_link==-1):
		return None,0
	start_quote=page.find('"',start_link)
	end_quote=page.find('"',start_quote+1)
	url=page[start_quote+1:end_quote]
	return url,end_quote
def get_all_links(seed, main_url, page):
	links=[]
	while(True):
		url,end_quote=get_next_url(page)
		u = str(url)
		x = u.find("/")
		
		if x == 0:
			url = main_url  + url[1:]
		page=page[end_quote:]
		if url:
			links.append(url)
		else:
			return links
def Look_up(index,keyword):
	
	if keyword in index:
		return index[keyword]
	return []
def add_to_index(index,url,keyword):

	if keyword in index:
		if url not in index[keyword]:
			index[keyword].append(url)
		return
	index[keyword]=[url]
def add_page_to_index(index,url,content):
	for i in content.split():
		add_to_index(index,url,i)

def compute_ranks(graph):
	d=0.8
	numloops=10
	ranks={}
	npages=len(graph)
	for page in graph:
		ranks[page]=1.0/npages
	for i in range(0,numloops):
		newranks={}
		for page in graph:
			newrank=(1-d)/npages
			for node in graph:
				if page in graph[node]:
					newrank=newrank+d*ranks[node]/len(graph[node])
			newranks[page]=newrank
		ranks=newranks
	return ranks

def Crawl_web(seed, max_limit):
	tocrawl=[seed]
	crawled=[]
	index={}
	graph={}
	while tocrawl:
		p=tocrawl.pop()
		if len(tocrawl) % 3 == 0:
			random.shuffle(tocrawl)
		if p not in crawled:
			max_limit-=1
			if max_limit<=0:
				break
			c=get_page(p)
			add_page_to_index(index,p,c)
			f=get_all_links(seed, p, c)
			union(tocrawl,f)
			graph[p]=f
			crawled.append(p)
	return index,graph



def QuickSort(pages,ranks):
	if len(pages)>1:
		piv=ranks[pages[0]]
		i=1
		j=1
		for j in range(1,len(pages)):
			if ranks[pages[j]]>piv:
				pages[i],pages[j]=pages[j],pages[i]
				i+=1
		pages[i-1],pages[0]=pages[0],pages[i-1]
		QuickSort(pages[1:i],ranks)
		QuickSort(pages[i+1:len(pages)],ranks)

def Look_up_new(index,ranks,keyword):
	pages=Look_up(index,keyword)
	urls = []
	print '\nPrinting the results as is with page rank\n'
	for i in pages:
		print i+" --> "+str(ranks[i])
	QuickSort(pages,ranks)
	print "\nAfter Sorting the results by page rank\n"
	for i in pages:
		urls.append(i)
	return urls


def final(seed_page, search_term,max_limit):
    index,graph=Crawl_web(seed_page,max_limit)
    ranks = compute_ranks(graph)
    a = Look_up_new(index,ranks,search_term)
    if a == []:
        return None
    return a[::-1]
def lucky_search(seed_page, search_term,max_limit):
        b=final(seed_page, search_term,max_limit)
        if b == None:
                return None
        return b[0]
def get_title(urls):
	if urls == None:
		return None
	titles = []
	for url in urls:
		x = urllib.urlopen(url)
		page = x.read()
		start_title = page.find('<title>')
		end_title = page.find('</', start_title+1)
		title = page[start_title+7:end_title]
		titles.append([url, title])
	return titles
def get_pictures(urls):
        if urls == None:
                return None
        pictures = []
        for url in urls:
                x = urllib.urlopen(url)
                page = x.read()
                start_pic = page.find('<img src=')
                start_pic_url=page.find('"',start_pic)
                end_pic = page.find('"', start_pic_url+1)
                picture = page[start_pic_url:end_pic+1]
                pictures.append([url, picture])
        return pictures

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/about")
def about():
        return render_template("about.html")
@app.route("/advise")
def advise():
        return render_template("suggestions.html")
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
@app.route("/search", methods = ["GET", "POST"])
def search():
    if request.method == "POST":
        if request.form["action"] == "search":
                seed = request.form.get("seed")
                keyword = request.form.get("keyword")
                max_limit = int(request.form.get("searching_limit"))
                urllist = final(seed, keyword, max_limit)
                urlwhittitle = get_title(urllist)
                pic_url = get_pictures(urllist)
                return render_template("chosesite.html", urlwhittitle = urlwhittitle ,pic_url = pic_url )
        elif request.form["action"] == "luck":
                seed = request.form.get("seed")
                keyword = request.form.get("keyword")
                max_limit = int(request.form.get("searching_limit"))
                bisey  = lucky_search(seed, keyword,max_limit)
                print os.system("start chrome " + bisey  + "/&amp;")
                return render_template("chosesite.html", urllist = final(seed, keyword,max_limit))
                
                

    else:
        return redirect(url_for("index"))
