import requests, json, re
from selenium import webdriver

# Use Selenium to get the webpage, driving Firefox - allowing pages to be parsed after 
# any onload js activity. Note this is subject to bugs and hangs, 
# and doesn't record output. Do not use, just here as a work in progress.
# See trackerScraper.py for a usable scraper, albiet one that doesn't parse javascript. 
def seleniumGetSource(url, driver):

	print "Get"
	driver.get(url)
	print "src"
	src = driver.page_source
	print "encode"
	src = unicode.encode(src, 'ascii', 'replace')
	print "done"
	return src

# Load bugs as found in the Ghostery chrome extension.
def readbugs(fileName):
	bugsTxt = open(fileName).read()
	# Read the list of bugs from the json.
	bugs = json.loads(bugsTxt).get('bugs')
	return bugs

# Load urls from alexa downloaded list.
def readURLs(fileName, num):
	
	urlList = []
	urlsFile = open(fileName)
	for i in range(num):
		url = re.search("(\S,)([\S]*)",urlsFile.readline()).group(2)
		urlList.append("http://" + url)
	return urlList

# The main loop - parse the urls with selenium and parse looking for ghostery bugs.	
def parse(urls, bugs):
	
	# Load the selenium driver.
	driver = webdriver.Firefox(timeout=5)
	driver.set_script_timeout(5)
	driver.implicitly_wait(5)
	results=[]
	for url in urls:

		foundBugs=[]
		# Note this will actually load firefox.
		rawText = seleniumGetSource(url, driver)
		for bug in bugs:

			try:
				# Check each bug pattern against the page source.
				reg = re.compile(bug['pattern'])
				if re.search(bug['pattern'], rawText):
					foundBugs.append(bug['name'])
			except re.error, theException:
				0
		results.append([[url],foundBugs])
	return results

def main():
	bugs = readbugs("bugs.js")
	urlList = readURLs("top-1m.csv", 100)

	res = parse(urlList, bugs)
	# result processing and storage not implemented yet.
	print res
	
		
if __name__ == '__main__':
   main()