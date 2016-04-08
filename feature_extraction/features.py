from __future__ import division 
import sys
reload(sys);
sys.path.insert(0, "/projets/sig/PROJET/PRINCESS/code/libs/readability")
sys.setdefaultencoding("utf8")
import os
from readability import Readability
from bs4 import BeautifulSoup
import math
import warc
import subprocess
from subprocess import Popen
from subprocess import call
import sqlite3




# ********************************************
# UTILS
# ********************************************

def getDocContent(trecid):
    '''function en cours'''
    princess_dir = '/osirim/sig/PROJET/PRINCESS'
    corpus_dir   = '/osirim/sig/CORPUS/CLUEWEB12/ClueWeb12-Full'
    clue_web_dir = trecid[0:9] + '_' + trecid[10:12]
    #print clue_web_dir
    clue_web_dir = clue_web_dir.replace("clueweb","ClueWeb")
    warc_dir = trecid[10:16]
    #warc_file = warc_dir + '-' + trecid[19:21] + 'warc.gz'
    warc_file = corpus_dir+'/'+clue_web_dir+'/'+ warc_dir+"/"+warc_dir + '-' + trecid[17:19] + '.warc.gz'
    #docnum = trecid[20:]
    #print warc_file
    file = warc.open(warc_file)
    #loop through warc to get doc content 
    for record in file:
        #print record.header
        if "WARC-Trec-ID" in record.header:
    #   if record['WARC-TREC-ID'] == docNum:
            if record['WARC-Trec-ID'] == trecid:
                #print record.payload.read()
                html_doc =  record.payload.read()
                #soup = BeautifulSoup(html_doc, 'html.parser') # vire bien les balises mais plante sur </br />
                soup = BeautifulSoup(html_doc, 'html5lib') # peut garder des div, des a et img
                for script in soup(["script", "style","comment"]):
                    script.extract() 

                text = soup.get_text()
                # break into lines and remove leading and trailing space on each
                lines = (line.strip() for line in text.splitlines())
                # break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # drop blank lines
                text_clean = '\n'.join(chunk for chunk in chunks if chunk)

                #txt_unicode =  unicode(txt, 'utf-8')
                #txt_unicode = u""+txt
                #txt_unicode = txt.encode('utf8', 'replace')
                #print txt
                #return txt.encode('utf-8','ignore')
                text_clean = text_clean.replace(u"</br />","</br>")
                return text_clean
                #sys.exit(0)
                break



# ********************************************
# FEATURES DOCUMENT/TERM-DEPENDANT
# ********************************************


# f1, f2, f3,f10,f11,f12,f46,f47,f48
def tf(doc,dumpIndexT):

    res = Popen(["grep","-e","^"+doc+" ",dumpIndexT],stdout=subprocess.PIPE).stdout.read()
    tRes = res.split(" ")
    if  (len(tRes) > 1):
        return [int(tRes[1]),math.log10(int(tRes[1])),int(tRes[2])]
    else :
        return [0,0,0]


# ********************************************
# FEATURES TERM-DEPENDANT
# ********************************************

# f4, f5, f6, f49, f50, f51
def idf(dumpIndexT,nbDocsIndex) :
    nbLines = Popen(["wc","-l",dumpIndexT],stdout=subprocess.PIPE).stdout.read()
    tLines = nbLines.split(" ")
    n = int(tLines[0]) - 1
    if n > 0 :
        return [nbDocsIndex/n,math.log10(nbDocsIndex/n)]
    else :
        return [0,0]

# ********************************************
# FEATURES FEAT-DEPENDANT
# ********************************************

# f7, f8, f9 , f22, f23, f24
def tfidf(tab,val):
    v = float(val[tab[0]]) * float(val[tab[1]])
    return [v,math.log10(v)]


# f13, f14, f15, f16, f17, f18,f19,f20,f21
def normalizedbysize(tab,val):
    
    return float(val[tab[0]]) / float(val[tab[1]])



# ********************************************
# FEATURES QUERY-DEPENDANT
# ********************************************

# f28 -> f45
def retevalmodel(param):
    
    print "[Start RetEval]"
    command = "/osirim/sig/CORPUS-TRAV/TREC-ADHOC/lemur-4.12/bin/RetEval"
    print command+" "+param
    call([command,param]) # Appel de retEval
    print "[RetEval ended]"


def runquerymodel(param, queryfile,resfile):
    
    print "[Start runquery]"
    command = "/osirim/sig/CORPUS-TRAV/TREC-ADHOC/indri-5.8/runquery/IndriRunQuery"
    print command+" "+param+" "+queryfile+" > "+resfile
    with open(resfile, "w") as outfile:
        call([command,param,queryfile],stdout=outfile) # Appel de Indrirunquery
    print "[runquery ended]"



# ********************************************
# FEATURES READIBILITY (f52->f59)
# ********************************************

#f52
def readability(id):
    r = {}
    text = getDocContent(id)
    #print text
    rd = Readability(text)

    r["ARI"] = rd.ARI()
    r["FleschReadingEase"] = rd.FleschReadingEase()
    r["FleschKincaidGradeLevel"] = rd.FleschKincaidGradeLevel()
    r["RIX"] = rd.RIX()
    r["GunningFogIndex"] = rd.GunningFogIndex()
    r["SMOGIndex"] = rd.SMOGIndex()
    r["ColemanLiauIndex"] = rd.ColemanLiauIndex()
    r["LIX"] = rd.LIX()

    return r


# ********************************************
# PAGE RANK(f60)
# ********************************************

def pagerank_loaded(id):
    conn = sqlite3.connect("/projets/sig/PROJET/PRINCESS/page_rank/pagerank.db")
    cursor = conn.cursor()
    cursor.execute("SELECT PR FROM PAGERANK WHERE ID='"+id+"';")
    res = cursor.fetchone()
    return res[0]


def pagerank(id):
    file = "/projets/sig/PROJET/PRINCESS/page_rank/pagerank.scoreOrder.bz2"
    command = ["bzgrep","-m1",id,file]
    print " ".join(command)
    res = Popen(["bzgrep","-m1",id,file],stdout=subprocess.PIPE).stdout.read()
    t = res.split(" ")
    pr = float(tLines[1])
    print "PageRank("+str(id)+"):"+str(pr)
    return pr



# ********************************************
# SPAM(f61)
# Attention : a verifier dans quel sens vont les features
# ********************************************

def spam(id):
    conn = sqlite3.connect("/projets/sig/PROJET/PRINCESS/spam_score/spam.db")
    cursor = conn.cursor()
    cursor.execute("SELECT PR FROM SPAM WHERE ID='"+id+"';")
    res = cursor.fetchone()
    return res[0]


# ********************************************
# AVERAGE PROXIMITY QUERY TERMS (f62)
# ********************************************
def averageproximity(pathIndex,q,dumpIndexT, idDoc,idQuery):

    #print q
    #print idDoc
    positions = {}
    for t in q:
        #print t
        outFile = dumpIndexT+"_"+t+".txt"
        outGloblal = dumpIndexT+"_"+idQuery+"_"+t+".txt"

        dumpIndex = "/osirim/sig/CORPUS-TRAV/TREC-ADHOC/indri-5.8/dumpindex/dumpindex"



        command = dumpIndex+" "+pathIndex+" tp "+t+" | grep -e ^"+idDoc+" > "+ outFile
        #tab = [dumpIndex,pathIndex, "tp", t,"|", "grep","-e","^"+idDoc]
        #print " ".join(tab)
        #sys.exit()
        #res = Popen(tab,stdout=subprocess.PIPE).stdout.read()
        #print res
        os.system(command)


        begin = True
        with open(outFile,"r") as f:
            tl = []
            for l in f:
                if not begin:
                    #print l
                    tl = l.split(" ")
                    if len(tl)>0 :
                        positions[t] = tl[3:-1]
                        with open(outGloblal,"a") as fout :
                            fout.write(tl[0]+"\n")
                else : begin=False


    num = 0
    #print positions
    if len(positions) > 1:
        for ti in positions:
            numti = 0
            for tj in positions:
                if ti != tj :
                    print ti + " "+ tj
                    nij = len(positions[ti]) * len(positions[tj])
                    distmin = 10000000000000000
                    for occt1  in positions[ti] :
                        for occt2 in positions[tj]:
                            if abs(int(occt1) - int(occt2)) < distmin :
                                distmin = abs(int(occt1) - int(occt2))
                    numti += distmin * nij
            
            val = float(numti) / float(len(q) - 1)
            valti = math.log(val,2)
            num += valti
        return 1 / (num/len(q))
    else :
        return -1

# ********************************************
# MITRA(f63)
# ********************************************

def mitra(q,idf,dumpIndexT,idQuery,idDoc):


    print "MITRA"

    def proba(ti,tj):
        pr = float(len(listDocs[ti]&listDocs[tj]))/float(len(listDocs[tj]))
        print "pr=>"+str(pr)
        return pr

    def calc_min(i):
        m = 1000000
        for j in range(0,i):
            prob = proba(q[i],q[j])
            if (1 - prob) < m:
                m = (1-prob)
        print "m=>"+str(m)
        return m 

    listDocs = {}

    for t in q:
        d = set()
        outGloblal = dumpIndexT+"_"+idQuery+"_"+t+".txt"
        with open(outGloblal,"r") as fin:
            for l in fin:
                if l != "\n":
                    d.add(l.replace("\n",""))
        listDocs[t] = d

    #print listDocs
    idft1 = 0

    if idDoc in listDocs[q[0]]: idft1 = idf[q[0]]

    s = idft1
    for i,ti in enumerate(q):
        if i > 0 and idDoc in listDocs[ti]:
            idfi = idf[ti]
            mi = calc_min(i) 
            s += (idfi * mi)
    print s
    return s
        



# ********************************************
# Entropie(f64)
# ********************************************

def entropy(idDoc,dumpIndex,pathIndex,dumpIndexT):
    # faire le dumpindex dv
    out = dumpIndexT+"_"+idDoc+".txt"
    command = dumpIndex+" "+pathIndex+" dv "+idDoc +" > "+out
    doc_size = 0
    os.system(command)
    term_count = {}
    entropy_term = {}
    freq_term_total = {}
    ok = False
    with open(out, "r") as f :
        for line in f:
            if not ok:
                if "--- Terms ---" in line:
                    ok = True
            else :
                if "[OOV]" not in line :
                    tl = line.split(" ")
                    term = tl[2].replace("\n","")
                    term_count.setdefault(term,0)
                    term_count[term] += 1
                    doc_size +=1

    s2d = 0.0

    for t in term_count:

        tfti = 0.0

        # Calcul du nombre d'occurence
        outterm = dumpIndexT+"_"+idDoc+"_"+t+".txt"
        commandterm = dumpIndex+" "+pathIndex+" x "+t +" > "+outterm
        os.system(commandterm)
        freq_term_tot = 0
        with open(outterm,"r") as f:
            for l in f:
                if l != "\n":
                    tl = l.split(":")
                    #print tl
                    count = tl[1].replace("\n","")
                    freq_term_total[t] = int(count)

        # Il faut recuperer les documents dans lesquel t apparraissent
        outtermdoc = dumpIndexT+"_"+idDoc+"_"+t+"_doc.txt"
        commandterm = dumpIndex+" "+pathIndex+" t "+t+" > "+ outtermdoc
        os.system(commandterm)
        listDocsTerm = set()
        begin = True
        with open(outtermdoc,"r") as f:
            tl = []
            for l in f:
                if not begin:
                    #print l
                    tl = l.split(" ")
                    listDocsTerm.add(tl[0]+"-"+tl[1])
                    if tl[0] == idDoc :
                        tfti = float(tl[1])
                else : begin=False

        # On peut calculer l'entropie
        entropy_term[t] = 0     
        for doc_count in listDocsTerm:
            tdoc = doc_count.split("-")
            tf_doc = int(tdoc[1])

            member = float(tf_doc)/float(freq_term_total[t])
            entropy_term[t] += member * math.log(member,2)

        #entropy_term[t] = - entropy_term[t]
        #print entropy_term[t]
        #print "tfti==>" + str(tfti)
        s2d += tfti * entropy_term[t]
    s2d = -1.0 * s2d / float(doc_size)
    print "s2d ==>" + str(s2d)
    if s2d != 0.0 :
        return (s2d,1/s2d)
    else :
        return (0.0,0.0)







