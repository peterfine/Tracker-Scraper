import requests, json, re
from selenium import webdriver

# Use Selenium to get the url source.
def seleniumGetSource(url, driver):

	driver.get(url)
	src = driver.page_source
	src = unicode.encode(src, 'ascii', 'replace')
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
	
	driver = webdriver.Firefox()
	results=[]
	for url in urls:

		foundBugs=[]
		# Note this will actually load firefox.
		rawText = seleniumGetSource(url, driver)
		for bug in bugs:

			try:
				reg = re.compile(bug['pattern'])
				if re.search(bug['pattern'], rawText):
					foundBugs.append(bug['name'])
			except re.error:
				0
		results.append([[url],foundBugs])
	return results

def main():
	bugs = readbugs("bugs.js")
	urlList = readURLs("top-1m.csv", 100)

	res = parse(urlList, bugs)
	print res
	
		
if __name__ == '__main__':
   main()
