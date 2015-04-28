# script to process a collection of patent files for natural language analysis:
# removes stop words, 
# stems words, 
# assembles lists of unigrams, bigrams and trigrams
# counts frequencies of specific n-grams in individual files and in all 10 files together
# alphabetizes output, writes to files, and copies files to S3 space

#imports necessary libraries

from nltk import PorterStemmer
import re
from collections import Counter
import subprocess
import boto
from boto.s3.key import Key
import boto.s3.connection

#reads in stop words

with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/stopwords.txt') as f:
    lines = f.read().splitlines()

# creates empty structures

d={}
alluni = []
allbi = []
alltri = []

# sets up a loop to run 10 times for each of the 10 patent files, conveniently names in numeric sequence

# removes stop words
for k in range(0,10):
	with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/633422'+str(k)+'.txt', 'r') as d["patent{0}".format(k)]:
		d["p{0}".format(k)] = d["patent{0}".format(k)].read().lower()
		d["p1{0}".format(k)] = re.sub('[\s][a-z]?[\)][\s]', ' ', d["p{0}".format(k)])
		d["p2{0}".format(k)] = re.sub('[^a-z\s]+', '', d["p1{0}".format(k)])
	d["pstop{0}".format(k)] = []
	d["pstop{0}".format(k)] = [word for word in d["p2{0}".format(k)].split() if word not in lines]

# stems words and produces list of unigrams

	d["stoplen{0}".format(k)] = len(d["pstop{0}".format(k)])
	d["unigram{0}".format(k)] = []
	for n in range(0,d["stoplen{0}".format(k)]):
		d["pstem{0}".format(k)] = PorterStemmer().stem_word(d["pstop{0}".format(k)][n])
		d["unigram{0}".format(k)].append(d["pstem{0}".format(k)])
		
# creates list of bigrams

	d["unilen{0}".format(k)] = len(d["unigram{0}".format(k)])
	pbis = []
	d["bigram{0}".format(k)] = []
	for i in range(0,d["unilen{0}".format(k)]-1):
		pbis = [d["unigram{0}".format(k)][i], d["unigram{0}".format(k)][i+1]]
		bi = ' '.join(pbis)
		d["bigram{0}".format(k)].append(bi)

# creates list of trigrams
		
	ptris = []
	d["trigram{0}".format(k)] = []
	for z in range(0,d["unilen{0}".format(k)]-2):
		ptris = [d["unigram{0}".format(k)][z], d["unigram{0}".format(k)][z+1], d["unigram{0}".format(k)][z+2]]
		tri = ' '.join(ptris)
		d["trigram{0}".format(k)].append(tri)

#determines frequencies of n-grams in individual lists
		
	d["unicount{0}".format(k)] = Counter(d["unigram{0}".format(k)])
	d["bicount{0}".format(k)] = Counter(d["bigram{0}".format(k)])
	d["tricount{0}".format(k)] = Counter(d["trigram{0}".format(k)])

#extends the consolidated list of n-grams with each loop

	alluni.extend(d["unigram{0}".format(k)])
	allbi.extend(d["bigram{0}".format(k)])
	alltri.extend(d["trigram{0}".format(k)])

#writes individual patent files to my hard drive and to my S3 bucket
	
	with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/Sandifer_assn2files/Sandifer_unigrams633422'+str(k)+'.txt', 'wb') as d["dstuni{0}".format(k)]:
		for x in sorted(d["unicount{0}".format(k)]):
			inputu = str(x)+","+str(d["unicount{0}".format(k)][x])+"\r\n"
			d["dstuni{0}".format(k)].write(inputu)
	subprocess.check_call("Aws s3 cp  C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/Sandifer_assn2files/Sandifer_unigrams633422"+str(k)+".txt s3://tracysandifer-bucket/", shell=True)
	with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/Sandifer_assn2files/Sandifer_bigrams633422'+str(k)+'.txt', 'wb') as d["dstbi{0}".format(k)]:
		for x in sorted(d["bicount{0}".format(k)]):
			inputb = str(x)+","+str(d["bicount{0}".format(k)][x])+"\r\n"
			d["dstbi{0}".format(k)].write(inputb)
	subprocess.check_call("Aws s3 cp  C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/Sandifer_assn2files/Sandifer_bigrams633422"+str(k)+".txt s3://tracysandifer-bucket/", shell=True)
	with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/Sandifer_assn2files/Sandifer_trigrams633422'+str(k)+'.txt', 'wb') as d["dsttri{0}".format(k)]:
		for x in sorted(d["tricount{0}".format(k)]):
			inputt = str(x)+","+str(d["tricount{0}".format(k)][x])+"\r\n"
			d["dsttri{0}".format(k)].write(inputt)
	subprocess.check_call("Aws s3 cp  C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/Sandifer_assn2files/Sandifer_trigrams633422"+str(k)+".txt s3://tracysandifer-bucket/", shell=True)
		
	k += 1

#determines frequencies of n-grams in consolidated lists
	
allunicount = Counter(alluni)
allbicount = Counter(allbi)
alltricount = Counter(alltri)

#writes consolidated patent files to my hard drive and to my S3 bucket

with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/Sandifer_assn2files/Sandifer_allunigrams.txt', 'wb') as allu:
	for y in sorted(allunicount):	
		writeu = str(y)+","+str(allunicount[y])+"\r\n"
		allu.write(writeu)
subprocess.check_call("Aws s3 cp  C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/Sandifer_assn2files/Sandifer_allunigrams.txt s3://tracysandifer-bucket/", shell=True)
with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/Sandifer_assn2files/Sandifer_allbigrams.txt', 'wb') as allb:
	for y in sorted(allbicount):
		writeb = str(y)+","+str(allbicount[y])+"\r\n"
		allb.write(writeb)
subprocess.check_call("Aws s3 cp  C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/Sandifer_assn2files/Sandifer_allbigrams.txt s3://tracysandifer-bucket/", shell=True)
with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/Sandifer_assn2files/Sandifer_alltrigrams.txt', 'wb') as allt:
	for y in sorted(alltricount):
		writetri = str(y)+","+str(alltricount[y])+"\r\n"
		allt.write(writetri)

#generates secure URL to be available for 48 hours (from 10pm on 4/27)
		
AWS_ACCESS_KEY_ID = '<redacted>'
AWS_SECRET_ACCESS_KEY = '<redacted>'
Bucketname = 'tracysandifer-bucket' 

conn = boto.s3.connect_to_region('us-west-2',
       aws_access_key_id=AWS_ACCESS_KEY_ID,
       aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
       is_secure=True)
temp_url = conn.generate_url(172800, 'GET', Bucketname, 'Sandifer_alltrigrams.txt')

print temp_url