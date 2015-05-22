# script to process a collection of scientific abstracts for natural language analysis:
# removes stop words, 
# stems words, 
# assembles lists of unigrams, bigrams and trigrams
# counts frequencies of specific n-grams in individual files and in all files together
# alphabetizes output and writes to files

#imports necessary libraries

import re
from collections import Counter
import os
import math
from copy import deepcopy
import numpy as np
import scipy
import pylab
import scipy.cluster.hierarchy as sch

#reads in stop words
with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn3b/forclassMay19/stopwords.txt') as f:
    lines = f.read().splitlines()

#reads in group declaration file
with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn3b/forclassMay19/groups.txt') as gr:
    groups = (line.split('\t') for line in gr)
    groupdict = {row[0]:row[1:] for row in groups}

# reads in abstract IDs and text
with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn3b/forclassMay19/abstracts.txt') as abs:
    abstracts = (line.split('\t') for line in abs)
    absdict = {row[0]:row[1:] for row in abstracts}

dictlen = len(absdict)

#creates empty structures
d={}
alluni = []
uni=[]
for m in range(0,10):
	l = []
	uni.append(l)

# removes stop words
for k in absdict:
	d["text{0}".format(k)] = [word for word in str(absdict[k]).replace('\\n','').split() if word not in str(lines).replace('"',"'")]
	#print str(k) + ":" + str(d["text{0}".format(k)])
	if d["text{0}".format(k)] == ["['null\\n']"] or d["text{0}".format(k)] == ["['null']"]:
		d["text{0}".format(k)] = [] 

#determines frequencies of n-grams in individual lists
	d["textcount{0}".format(k)] = Counter(d["text{0}".format(k)])

#extends the field-specific consolidated list of n-gram with each loop
	if groupdict[k] == ['1\n']:
		uni[0].extend(d["text{0}".format(k)])
	elif groupdict[k] == ['2\n']:
		uni[1].extend(d["text{0}".format(k)])
	elif groupdict[k] == ['3\n']:
		uni[2].extend(d["text{0}".format(k)])
	elif groupdict[k] == ['4\n']:
		uni[3].extend(d["text{0}".format(k)])
	elif groupdict[k] == ['5\n']:
		uni[4].extend(d["text{0}".format(k)])
	elif groupdict[k] == ['6\n']:
		uni[5].extend(d["text{0}".format(k)])
	elif groupdict[k] == ['7\n']:
		uni[6].extend(d["text{0}".format(k)])
	elif groupdict[k] == ['8\n']:
		uni[7].extend(d["text{0}".format(k)])
	elif groupdict[k] == ['9\n']:
		uni[8].extend(d["text{0}".format(k)])
	elif groupdict[k] == ['10\n']:
		uni[9].extend(d["text{0}".format(k)])

#extends the consolidated list of n-grams with each loop

	alluni.extend(d["text{0}".format(k)])
	
#determines frequencies of n-grams in consolidated lists

allunicount = Counter(alluni)
unicount=[]

for m in range(0,10):
	c = Counter(uni[m])
	unicount.append(c)

#get full corpus probabalities:
alluniprob = allunicount.copy()
uniprob = deepcopy(unicount)
for y in allunicount:
	alluniprob[y] = float(allunicount[y])/float(len(alluni))

#make list of all x corpora with gap-adjusted probabilities: 0.99*prob of w word being in x n-gram list + 0.01*prob of w word being in all n-gram list
for x in range(0,10):
	for w in uniprob[x]:
		uniprob[x][w] = 0.99*(float(uniprob[x][w])/float(len(uni[x])))+(0.01*alluniprob[w])

#make xy corpora
uniprobxy = {}
for x in range(0,10):
	for y in range(0,10):
		for w in unicount[x]:
			uniprobxy[(x,y,w)] = 0

for x in range(0,10):
	for y in range(0,10):
		for w in unicount[x]:
			if unicount[y][w]:
				uniprobxy[(x,y,w)] = 0.99*(float(unicount[y][w])/float(len(uni[y])))+(0.01*alluniprob[w])
			else:
				uniprobxy[(x,y,w)] = 0.01*alluniprob[w]

#calculate xy jargon distance:
numerator = {}
for x in range(0,10):
	numerator[(x)] = 0
for x in range(0,10):
	for w in uniprob[x]:
		quantn = uniprob[x][w]*math.log(uniprob[x][w],2)
		numerator[(x)] += quantn
			
denominator = {}
for x in range(0,10):
	for y in range(0,10):
		denominator[(x,y)] = 0
for x in range(0,10):
	for y in range(0,10):
		for w in uniprob[x]:
			quantd = uniprob[x][w]*math.log(uniprobxy[(x,y,w)],2)
			denominator[(x,y)] += quantd

measure = {}
for x in range(0,10):
	for y in range(0,10):
		measure[(x,y)] = numerator[(x)]/denominator[(x,y)]

hole = {}
for x in range(0,10):
	for y in range(0,10):
		hole[(x,y)] = 1-measure[(x,y)]

hole_matrix = []
for x in range(0,10):
	hole_matrix.append([])
	for y in range(0,10):
		hole_matrix[x].append(hole[(x,y)])

import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt
 
real_matrix = np.array(hole_matrix)

linkage_matrix = linkage(real_matrix, "single")

plt.clf()

ddata = dendrogram(linkage_matrix,
                   color_threshold=1,
                   labels=["Ecol", "Molec", "Econ", "Soc","Prob", "Org", "Law", "Anth","Poli", "Edu"])
ax = plt.gca()
xlbls = ax.get_xmajorticklabels()

plt.show()

#runtime = 22 seconds