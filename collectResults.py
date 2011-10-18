import os, string, json

path="results"

successAll=[]
failedAll=[]

# Collate all failed and success items (defined by having those words in their filename).
dirList=os.listdir(path)
for fname in dirList:
    if string.find(fname, "success") > -1:
    	success=open("results/" +fname, 'r')
    	results=json.loads(success.read())
    	successAll.extend(results)
        success.close()
    
    if string.find(fname, "failed") > -1:
    	fail=open("results/" +fname, 'r')
    	failTxt=fail.read()
    	fail.close()
    	
    	# failed list may legitimately be empty.
    	if failTxt != "":
    		results=json.loads(failTxt)
    		failedAll.extend(results)
    
    # Write out in json format to final results files.	
    successOut=open("finalSuccessful.out", 'w')
    successOut.write(json.dumps(successAll))
    successOut.close()
    
    failOut=open("finalFailed.out", 'w')
    failOut.write(json.dumps(failedAll))
    failOut.close()
