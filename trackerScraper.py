import requests, re, json, cloud, os, math, sys

# Process the bugs (taken from the Ghostery Chrome extension) from their
# JSon text format to a set of name/regex patterns.
def readbugs(fileName):
	bugsTxt = open(fileName).read()
	# Read the list of bugs from the json.
	bugs = json.loads(bugsTxt).get('bugs')
	return bugs

# Read the URLs, as taken from the Alexa top sites download.
def readURLs(fileName, num):
	
	urlList = []
	urlsFile = open(fileName)
	for i in range(num):
		# Extract just the url text, and append www.
		url = re.search("(\S,)([\S]*)",urlsFile.readline()).group(2)
		urlList.append("http://www." + url)
	return urlList
		
# The main downloading and parsing loop, to operate on a set of some urls and all bugs.
# urlRanks is a list of the alexa ranks for this job, to aid success checking later.
def parse(urlRanks, urls, bugs):

	results=[]
	failed=[]
	
	for url in urls:

		try:
			# Use requests module to easily download the page html.
			site = requests.get(url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1'}, allow_redirects=True, timeout=10)
		except Exception, scrapeFailed:
			# Add exceptions to the failed list.
			failed.append([url,"Request Exception: " + str(scrapeFailed)])
			continue
		
		if site.error:
			# Record http errors.
			failed.append([url,"Error: " + str(site.error)])
			continue
		
		try:
			# Extract the raw text.
			rawText = site.content
		except Exception, scrapeFailed:
			# Sometimes encoding errors occur, these are not resolved for now.
			failed.append([url,"Content Exception: " + str(scrapeFailed)])
			continue
		# Find any bugs that match the regex from Ghostery
		foundBugs = []
		for bug in bugs:
			
			try:
				reg = re.compile(bug['pattern'])
				if re.search(bug['pattern'], rawText):
					foundBugs.append(bug['name'])
			except re.error:
				0
		# record the found trackers.
		results.append([url,foundBugs])
	return (urlRanks, results, failed)
	
# Arguments are 1) PiCloud ID 2) PiCloud Key (only needed if using the cloud setting below 
def main():
	
	useCloud = True 		# True to use PiCloud.com, False to use simulator
	start=0 				# 0 if loading all 100k
	numberOfSites = 100000 	# 100000 if loading all 100k 
	numJobs=500				# number of threads (simulator mode), or jobs (cloud mode)
	
	bugs = readbugs("bugs.js") # load bugs
	urlList = readURLs("top-1m.csv", 100000) # load urls
	
	urlsPerJob=int(math.ceil(float(numberOfSites)/float(numJobs)))
	urlListOfLists =[]
	rankListOfLists=[] # record the ranks per job for later debugging
	# Add the appropriate list of urls, nested numJobs times in the urlListOfLists
	for i in range(start,start+numberOfSites,urlsPerJob):
		urlListOfLists.append(urlList[i:min(start+numberOfSites,i+urlsPerJob)])
		rankListOfLists.append(range(i,min(start+numberOfSites,i+urlsPerJob)))
		
	if useCloud:
		cloud.setkey(int(sys.argv[1], sys.argv[2])
	else:
		cloud.start_simulator()
	
	ids = cloud.map(parse, rankListOfLists, urlListOfLists, [bugs]*len(urlListOfLists))
	
	# Iterate through the results. Note this blocks on each result finishing.
	resultNum=-1
	for result in cloud.iresult(ids, ignore_errors=True):
		resultNum=resultNum+1
		try:
			# Write the url rank list file
			if len(result[0]) > 0:
				theFile=open("results/ranks" + str(resultNum) + ".out","w")
				theFile.write(json.dumps(result[0]))
				theFile.close()
			
			# Write the success file
			if len(result[1]) > 0:
				theFile=open("results/success" + str(resultNum) + ".out","w")
				theFile.write(json.dumps(result[1]))
				theFile.close()
			
			# Write the failures file
			if len(result[2]) > 0:
				theFile=open("results/failed" + str(resultNum) + ".out","w")
				theFile.write(json.dumps(result[2]))
				theFile.close()
			
		# The result file failed
		except Exception, resultFailed:
			print "--Caught Result exception (job probably killed)--"
			print resultFailed
			print "--End of caught exception--"
	
	# Close any remaining picloud threads
	os._exit(1)
	
if __name__ == '__main__':
   main()
