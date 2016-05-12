# -*- coding: utf-8 -*-
import operator
import re
from os.path import join
import os
import sys
import time
from pymongo import MongoClient




def getQRel(f,q,n):

    tofind = str(q)+" 0 "+n
    #print tofind
    with open(f,'r') as fin:
        for line in fin:
            if tofind in line:
                #print line
                val = line.split(" ")[-1].strip()
                if "-" in val :
                    return "0"
                else :
                    return val
    return "0"





dirname = '/osirim/sig/PROJET/PRINCESS/code/scripts_experiments_cikm_letor/'
dirResult = '/osirim/sig/PROJET/PRINCESS/data/'



listCollection = ['indri_web2014clueweb12_adhoc_max50', 'indri_robust2004_max50']

for col in listCollection:

    print col

    if "web" in col:
        colDir = dirResult+"WEB2014"
        pathQRel = '/osirim/sig/PROJET/PRINCESS/qrels/WEB2014/qrels.txt'
    else :
        colDir = dirResult+"ROBUST2004"
        pathQRel = '/osirim/sig/PROJET/PRINCESS/qrels/ROBUST2004/qrels.txt'

    os.system("rm -r "+colDir)
    os.system("mkdir "+colDir)

    data = {}

    connection = MongoClient(host='co2-ni01.irit.fr', port=28018)
    db = connection.princess
    collection = db[col.lower()]
    queries = collection.distinct('query')

    with open(colDir+"/all.txt", "w") as fout:
        for q in queries:
            print q
            data.setdefault(q,{})
            qstr = str(q)
            list = collection.find({'query': qstr}, {'_id': 0, 'docs': 1})
            for i in list:
                # print i
                for d in i['docs']:
                    line = " qid:"+qstr
                    name = d['doc_name']
                    # list_feat = []
                    count = 1
                    t = [str(0.0)]*14
                    print t
                    #for f in d['features']:
                    for i in range(0,15):
                        if "f"+str(i+1)  in d['features']:
                            print d['features']["f"+str(i+1)]
                            t[i] = str(d['features']["f"+str(i+1)])
                            print "t[i]", t[i]

                    for ind, el in enumerate(t):
                        line+=" "+str(ind+1)+":"+el


                    line+=" #docid = "+name+"\n"
                    line = getQRel(pathQRel,q,name) + line
                    #print line
                    fout.write(line)


