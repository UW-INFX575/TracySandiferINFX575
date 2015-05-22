# script to process a collection of scientific abstracts for natural language analysis
#calculates jargon distanct per Vilhena et al using unigrams, bigrams, and trigrams
#models topics distributions on unigram bags-of-words

#imports necessary libraries for jargon distanct
from nltk import PorterStemmer
import re
from collections import Counter
import os
import math
import scipy

#imports additional necessary libraries for LDA
import logging, gensim, bz2
from gensim import corpora, models, similarities
import numpy

# get filenames

for files in os.walk("C:\\Users\\Tracy\\Documents\\DOH_Epi\\Classes\\INFX575\\assn3\\abstracts"):
	filelist = []
	filelist = files[2]
	listlen = len(filelist)
	
#reads in stop words

with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/stopwords.txt') as f:
    lines = f.read().splitlines()

# creates empty structures

d={}
alluni = []
allbi = []
alltri = []
meduni = []
medbi = []
medtri = []
techuni = []
techbi = []
techtri = []

# sets up a loop to iterative over availabe abstracts

# removes stop words
for k in range(0,listlen):
	with open("C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn3/abstracts/"+filelist[k], 'r') as d["patent{0}".format(k)]:
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

#extends the field-specific consolidated list of n-gram with each loop

	name = filelist[k]
	if name[0:3] == 'med':
		meduni.extend(d["unigram{0}".format(k)])
		medbi.extend(d["bigram{0}".format(k)])
		medtri.extend(d["trigram{0}".format(k)])
	elif name[0:4] == 'tech':
		techuni.extend(d["unigram{0}".format(k)])
		techbi.extend(d["bigram{0}".format(k)])
		techtri.extend(d["trigram{0}".format(k)])		
	
#extends the consolidated list of n-grams with each loop

	alluni.extend(d["unigram{0}".format(k)])
	allbi.extend(d["bigram{0}".format(k)])
	alltri.extend(d["trigram{0}".format(k)])

#determines frequencies of n-grams in consolidated lists
	
allunicount = Counter(alluni)
allbicount = Counter(allbi)
alltricount = Counter(alltri)

medunicount = Counter(meduni)
medbicount = Counter(medbi)
medtricount = Counter(medtri)

techunicount = Counter(techuni)
techbicount = Counter(techbi)
techtricount = Counter(techtri)

#get full corpus probabalities:
allunilen = len(alluni)
alluniprob = allunicount
for y in allunicount:
	alluniprob[y] = float(allunicount[y])/float(allunilen)
allbilen = len(allbi)
allbiprob = allbicount
for y in allbicount:
	allbiprob[y] = float(allbicount[y])/float(allbilen)
alltrilen = len(alltri)
alltriprob = alltricount
for y in alltricount:
	alltriprob[y] = float(alltricount[y])/float(alltrilen)

#make tech corpus with gap-adjusted probabilities: 0.99*prob of tech word being in tech n-gram list + 0.01*prob of tech word being in all n-gram list
techunilen = len(techuni)
techuniprob = techunicount.copy()
for y in techuniprob:
	techuniprob[y] = 0.99*(float(techuniprob[y])/float(techunilen))+(0.01*alluniprob[y])
techbilen = len(techbi)
techbiprob = techbicount.copy()
for y in techbicount:
	techbiprob[y] = 0.99*(float(techbicount[y])/float(techbilen))+0.01*allbiprob[y]
techtrilen = len(techtri)
techtriprob = techtricount.copy()
for y in techtricount:
	techtriprob[y] = 0.99*(float(techtricount[y])/float(techtrilen))+0.01*alltriprob[y]

#make med corpus with gap-adjusted probabilities: 0.99*prob of tech word being in med n-gram list + 0.01*prob of tech word being in all n-gram list
medunilen = len(meduni)
techmeduniprob = techunicount.copy()
for y in techunicount:
	if medunicount[y]:
		techmeduniprob[y] = 0.99*(float(medunicount[y])/float(medunilen))+0.01*alluniprob[y]
	else:
		techmeduniprob[y] = 0.01*alluniprob[y]

medbilen = len(medbi)
techmedbiprob = techbicount.copy()
for y in techbicount:
	if medbicount[y]:
		techmedbiprob[y] = 0.99*(float(medbicount[y])/float(medbilen))+0.01*allbiprob[y]
	else:
		techmedbiprob[y] = 0.01*allbiprob[y]

medtrilen = len(medtri)
techmedtriprob = techtricount.copy()
for y in techtricount:
	if medtricount[y]:
		techmedtriprob[y] = 0.99*(float(medtricount[y])/float(medtrilen))+0.01*alltriprob[y]
	else:
		techmedtriprob[y] = 0.01*alltriprob[y]
		
#calculate jargon distance using unigrams:
uninum = 0
for y in techuniprob:
	quant1 = techuniprob[y]*math.log(techuniprob[y],2)
	uninum += quant1
print uninum
unidenom = 0
for y in techuniprob:
	quant2 = techuniprob[y]*math.log(techmeduniprob[y],2)
	unidenom += quant2
print unidenom
unimeasure = uninum / unidenom
uni_cult_hole = 1 - unimeasure
print 'Cultural hole from tech abstracts to biomed abstracts, as measured by unigrams, is ' + str(uni_cult_hole)

#calculate jargon distance using bigrams:
binum = 0
for y in techbiprob:
	quant1 = techbiprob[y]*math.log(techbiprob[y],2)
	binum += quant1
bidenom = 0
for y in techbiprob:
	quant2 = techbiprob[y]*math.log(techmedbiprob[y],2)
	bidenom += quant2
bimeasure = binum / bidenom
bi_cult_hole = 1 - bimeasure
print 'Cultural hole from tech abstracts to biomed abstracts, as measured by bigrams, is ' + str(bi_cult_hole)

#calculate jargon distance using trigrams:
trinum = 0
for y in techtriprob:
	quant1 = techtriprob[y]*math.log(techtriprob[y],2)
	trinum += quant1
tridenom = 0
for y in techtriprob:
	quant2 = techtriprob[y]*math.log(techmedtriprob[y],2)
	tridenom += quant2
trimeasure = trinum / tridenom
tri_cult_hole = 1 - trimeasure
print 'Cultural hole from tech abstracts to biomed abstracts, as measured by trigrams, is ' + str(tri_cult_hole)


###################################
#LDA analysis#
###################################


# get filenames

for files in os.walk("C:\\Users\\Tracy\\Documents\\DOH_Epi\\Classes\\INFX575\\assn3\\abstracts"):
	filelist = []
	filelist = files[2]
	listlen = len(filelist)
	
#reads in stop words

with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn2/stopwords.txt') as f:
    lines = f.read().splitlines()

# creates empty structures

d={}
meduni = []
techuni = []

# sets up a loop to iterative over availabe abstracts

# removes stop words
for k in range(0,listlen):
	with open("C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn3/abstracts/"+filelist[k], 'r') as d["patent{0}".format(k)]:
		d["p{0}".format(k)] = d["patent{0}".format(k)].read().lower()
		d["p1{0}".format(k)] = re.sub('[\s][a-z]?[\)][\s]', ' ', d["p{0}".format(k)])
		d["p2{0}".format(k)] = re.sub('[^a-z\s]+', '', d["p1{0}".format(k)])
	d["pstop{0}".format(k)] = []
	d["pstop{0}".format(k)] = [word for word in d["p2{0}".format(k)].split() if word not in lines]
	#print d["pstop{0}".format(k)]

# stems words and produces list of unigrams

	d["stoplen{0}".format(k)] = len(d["pstop{0}".format(k)])
	d["unigram{0}".format(k)] = []
	for n in range(0,d["stoplen{0}".format(k)]):
		d["pstem{0}".format(k)] = PorterStemmer().stem_word(d["pstop{0}".format(k)][n])
		d["unigram{0}".format(k)].append(d["pstem{0}".format(k)])

#appends content of each document to appropriate corpus array

	name = filelist[k]
	if name[0:3] == 'med':
		meduni.append(list(d["unigram{0}".format(k)]))
	elif name[0:4] == 'tech':
		techuni.append(list(d["unigram{0}".format(k)]))

#form corpora
medcorpus = []
techcorpus = []

meddict = corpora.Dictionary(meduni)
techdict = corpora.Dictionary(techuni)
for k in range(0,listlen):
	name = filelist[k]
	if name[0:3] == 'med':
		medcorpus.append(meddict.doc2bow(list(d["unigram{0}".format(k)])))
	elif name[0:4] == 'tech':
		techcorpus.append(techdict.doc2bow(list(d["unigram{0}".format(k)])))

corpora.MmCorpus.serialize('/tmp/medmm.mm',medcorpus)
corpora.MmCorpus.serialize('/tmp/techmm.mm',techcorpus)
medmm = gensim.corpora.MmCorpus('/tmp/medmm.mm')
techmm = gensim.corpora.MmCorpus('/tmp/techmm.mm')
# model topics per corpus
ldamed = gensim.models.ldamodel.LdaModel(corpus=medmm, id2word=meddict, num_topics=6, update_every=0, passes=10)
ldatech = gensim.models.ldamodel.LdaModel(corpus=techmm, id2word=techdict, num_topics=6, update_every=0, passes=10)
#write modeled topics to files:
with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn3/Sandifer_assn3files/Sandifer_medtopics2.txt', 'wb') as medtop2:
	for y in range (0,2):
		writemedtop2 = str(ldamed.print_topics(y)) + '\r\n'
		medtop2.write(writemedtop2)
with open('C:/Users/Tracy/Documents/DOH_Epi/Classes/INFX575/assn3/Sandifer_assn3files/Sandifer_techtopics2.txt', 'wb') as techtop2:
	for y in range (0,2):
		writetechtop2 = str(ldatech.print_topics(y)) + '\r\n'
		techtop2.write(writetechtop2)