# Programme permettant d'extraire les features d'une collection
# Parametre : Fichier parametre
import sys
import os
import re
import glob
import pymongo
import ConfigParser
import subprocess
import time
import math
import features
import numpy as np
import warc
import bz2

from scipy import stats
from pymongo import MongoClient
from subprocess import call
from subprocess import Popen






# ***************************************************************************
# Commande type : python extract_feature.py ../../param/config_features_test normType
# normType = max (division par le max), lee (normalisation de Lee (CombMNZ), discWidth, discFreq, stdz (Standardization (centrage-reduction))
# ***************************************************************************


functionMapping = {"f1" : features.tf,"f2" : features.tf,"f3" : features.tf, "f4" : features.idf,"f5":features.idf,
                    "f6" : features.idf, "f13":features.normalizedbysize,"f14":features.normalizedbysize,
                    "f15":features.normalizedbysize, "f16":features.normalizedbysize, "f17":features.normalizedbysize,
                    "f18":features.normalizedbysize, "f19":features.normalizedbysize, "f20":features.normalizedbysize,
                    "f21":features.normalizedbysize, "f28":features.runquerymodel, "f29":features.runquerymodel, 
                    "f30":features.runquerymodel, "f31":features.runquerymodel, "f32":features.runquerymodel,
                    "f33":features.runquerymodel,"f34":features.runquerymodel, "f35":features.runquerymodel,
                    "f36":features.runquerymodel,"f37":features.runquerymodel,"f38":features.runquerymodel, 
                    "f39":features.runquerymodel,"f40":features.runquerymodel, "f41":features.runquerymodel,
                    "f42":features.runquerymodel,"f43":features.runquerymodel,"f44":features.runquerymodel,
                    "f45":features.runquerymodel,"f52":features.readability, "f60":features.pagerank, "f61":features.spam,
                    "f62":features.averageproximity,"f63":features.mitra, "f64":features.entropy}





# lecture du fichier parametre

# ********************************************
# GLOBAL VARIABLE DECLARATION (BEGIN)
# ********************************************

normType = sys.argv[2]
nbBins = 10


queryTerms ={}
infoFeatures = [{}]*100 # Info sur les features
independantFeatures = {} # contient la valeur de la feature si elle est independante
featuresValues = {} 
independantFeatureValues={}
indexAll=""
indexBody=""
indexTitle=""
queriesFile = ""
pathIndriParam = ""
pr = {}
resultIndri = ""
 
collName = ""
maxRes = ""
indexValues = {}
indexSplit = {}
dumpIndex = ""

idFeatTF = {"BodyIndex":"f1", "TitleIndex":"f2", "FullIndex":"f3" }

#functionMapping[0](10)





# ********************************************
# FUNCTIONS (BEGIN)
# ********************************************


#CONVERT A VALUE INTO ITS CORRESSPONDING INTERVAL
def valToBin(n,bounds):
    i=1
    while i < len(bounds) and n >bounds[i] :
        i+=1
    return i




#READ PARAMETER FILE
def readParams(configFile) :

    global indexAll,indexTitle,indexBody,queriesFile,infoFeatures,independantFeatures,collName,maxRes,resultIndri,dumpIndex,normType
    Config = ConfigParser.ConfigParser()
    Config.read(sys.argv[1])

    if Config.has_option('paths','FullIndex') : indexValues["FullIndex"]=Config.get('paths', 'FullIndex')
    if Config.has_option('paths','BodyIndex') : indexValues["BodyIndex"]=Config.get('paths', 'BodyIndex')
    if Config.has_option('paths','TitleIndex') : indexValues["TitleIndex"]=Config.get('paths', 'TitleIndex')

    if Config.has_option('paths','FullIndexSplit') : indexSplit["FullIndex"]=Config.get('paths', 'FullIndexSplit')
    if Config.has_option('paths','FullIndexSplit') : indexSplit["BodyIndex"]=Config.get('paths', 'FullIndexSplit')
    if Config.has_option('paths','TitleIndexSplit') : indexSplit["TitleIndex"]=Config.get('paths', 'TitleIndexSplit')


    queriesFile = Config.get('paths', 'queries')
    resultIndri = Config.get('paths', 'ResultsIndri')
    collName = Config.get('paths','CollName')
    maxRes = Config.get('paths','MaxRes')
    dumpIndex = Config.get('paths','DumpIndex')

    resultIndri += "." + normType + maxRes

    #print resultIndri+"\n"
    #print maxRes+"\n"

    for opt in Config.sections():
        if opt != "paths":

#           print "Reading "+opt+"..."

            dictTemp = {}
            dictTemp["name"] = "f"+opt
            dictTemp["description"] = Config.get(opt, 'description')
            dictTemp["index"] =  Config.get(opt, 'index')
            dictTemp["dependant"] =  Config.get(opt, 'dependant')
            infoFeatures[int(opt)] = dictTemp

#   print "[INFO FEATURES]"
#   for i in range(0,len(infoFeatures)):
#       print "Indice "+str(i)+" =>"+str(infoFeatures[i])
#   print "[/INFO FEATURES]"



#READ THE QUERY FILE AND FEED THE STRUCTURE QUERYTERMS
def feedQueryTerms():

    global queryTerms

    with open(queriesFile,'r') as qf :
        qLines = qf.readlines();
        for line in qLines :
            if (line.startswith("<number>")):
                #tempTab = line.split(" ");
                tempTab = line;
                idQuery = tempTab.replace("<number>","").replace("</number>","").replace("\n","")
                queryTerms[idQuery]=[]
            else :
                if (not line.startswith("<")):
                    line = line.replace("\n","")
                    queryTerms[idQuery].extend(re.split(" |\-",line))




# GET THE NUMBER OF DOCUMENTS IN THE CURRENT INDEX
def getNumberDocs(pathIndex):
    command = dumpIndex+" "+pathIndex+" stats > "+pathTempFile
    #print command
    os.system(command)
    with open(pathTempFile) as tempFile:
        stats = tempFile.read()
        tabStats = stats.split("\n")
        lineNbDoc = tabStats[1]
        tLineNbDoc = lineNbDoc.split("\t")
        nbDocs  = int(tLineNbDoc[1])
        return nbDocs


# GENERATE THE INDRI PARAMETER FILE BASED ON THE USER CONFIG
def generateIndriParam(currIndex,retModel,resFile,paramFile,curr,nbres):

    with open(paramFile,"w") as fileParam:
        fileParam.write("<parameters>\n")
        fileParam.write("<memory>8G</memory>\n")
        if curr not in indexSplit :
            fileParam.write("<index>"+currIndex+"</index>\n")
        else :
            for d in glob.glob(indexSplit[curr]+"/*") :
                fileParam.write("<index>"+d+"</index>\n")
        if retModel != "indri":
            fileParam.write("<baseline>"+retModel+"</baseline>\n")
        #fileParam.write("<textQuery>"+queriesFile+"</textQuery>\n")
        #fileParam.write("<resultFile>"+resFile+"</resultFile>\n")
        fileParam.write("<count>"+nbres+"</count>\n")
        fileParam.write("<runID>"+"run"+retModel+"</runID>\n")
        #fileParam.write("<trecFormat>3col</trecFormat>\n")
        fileParam.write("<trecFormat>true</trecFormat>\n")
        fileParam.write("</parameters>\n")

# RETURNS WHETHER FEAT NEEDS SOME OTHER(S) FEATURE VALUE(S) TO BE CALCULATED
def isDependantFeature(i) :

    if "f" in infoFeatures[i]["dependant"] :
        return 1
    else :
        return 0

# RETURNS THE SET OF DEPENDANT FEATURES
def getDependantFeatures(currIndex):
    tab = []

    # test
    for i in range(0,len(infoFeatures)):
        if (infoFeatures[i] != {} and infoFeatures[i]["index"] ==  currIndex and isDependantFeature(i)) :
            tab.append(i)
    return tab


# ********************************************
# INITIALIZATION
# ********************************************

readParams(sys.argv[1])
feedQueryTerms()
#loadPageRank()

# ********************************************
# CONNEXION DANS MONGODB
# ********************************************
connection = MongoClient(host='co2-ni01.irit.fr',port=28018)
db = connection.princess
collection_name = collName + normType + maxRes
collection = db[collection_name]
collection.remove({})

# ********************************************
# TEMP FILES
# ********************************************

pathIndriParam = "/projets/sig/PROJET/PRINCESS/code/param/configIndri_" + collection_name + ".param"

pathIndriParamOkapi = "/projets/sig/PROJET/PRINCESS/code/param/configIndriOkapi_" + collection_name + ".param"
pathIndriParamTfidf = "/projets/sig/PROJET/PRINCESS/code/param/configIndriTfidf_" + collection_name + ".param"
pathIndriParamIndri = "/projets/sig/PROJET/PRINCESS/code/param/configIndrimodel_" + collection_name + ".param"
pathTempFilteredFile = "/projets/sig/PROJET/PRINCESS/code/princess/feature_extraction/temp/filteredIndri_" + collection_name + ".txt"
pathTempFile = "/projets/sig/PROJET/PRINCESS/code/princess/feature_extraction/temp/fileIndri_" + collection_name + ".txt"

resultModelOkapi = "/projets/sig/PROJET/PRINCESS/code/princess/feature_extraction/temp/resultIndriModelOkapi_" + collection_name + ".txt"
resultModelTfidf = "/projets/sig/PROJET/PRINCESS/code/princess/feature_extraction/temp/resultIndriModelTfidf_" + collection_name + ".txt"
resultModelIndri = "/projets/sig/PROJET/PRINCESS/code/princess/feature_extraction/temp/resultIndriModelIndri_" + collection_name + ".txt"

modelMapping = {"f28": ["okapi",resultModelOkapi, pathIndriParamOkapi],"f29": ["okapi",resultModelOkapi, pathIndriParamOkapi],"f30": ["okapi",resultModelOkapi, pathIndriParamOkapi], "f31": ["tfidf",resultModelTfidf, pathIndriParamTfidf], "f32": ["tfidf",resultModelTfidf, pathIndriParamTfidf],"f33": ["tfidf",resultModelTfidf, pathIndriParamTfidf], "f43": ["indri",resultModelIndri, pathIndriParamIndri], "f44": ["indri",resultModelIndri, pathIndriParamIndri],"f45": ["indri",resultModelIndri, pathIndriParamIndri] }


# ********************************************
# MAIN
# ********************************************

maxFeat = {} 
minFeat = {}
docsInCurrIndex = {}


begin = time.time()
print "Start"

for q in queryTerms.keys() :  # Initialisation
    featuresValues[q] = {}


for currIndex in indexValues.keys() :  # Pour chaque type d'index

    #print currIndex
    dependantFeatures = getDependantFeatures(currIndex)
    #print dependantFeatures


    nbDocsIndex = getNumberDocs(indexValues[currIndex])
    #print "NbDocsIndex => "+str(nbDocsIndex)

    maxFeat = {}
    minFeat = {}
    valFeat = {}
    idf = {}

    mappingDoc = {}
    #loadMappingIdDoc()
    generateIndriParam(indexValues[currIndex],"indri",resultIndri,pathIndriParam,currIndex,maxRes) # On commence par generer le fichier de param d'Indri (avec le modele Indri)
    print "[Start Indrirunquery] modele Indri"
    #command = "/osirim/sig/CORPUS-TRAV/TREC-ADHOC/Indri-4.12/bin/RetEval"
    command = "/osirim/sig/CORPUS-TRAV/TREC-ADHOC/indri-5.8/runquery/IndriRunQuery"
    #print command+" "+pathIndriParam
    with open(resultIndri, "w") as resoutfile:
        call([command,pathIndriParam,queriesFile],stdout=resoutfile) # Appel de IndriRunQuery

    print "[Indrirunquery ended]"


    for q in queryTerms.keys() :  # Pour chaque requete

        print "Traitement requete :",q

        docsInCurrIndex[q] = []
        #docsInIndex[q][currIndex] = []
        #docsInIndex.setdefault(q,{})
        #docsInIndex[q].setdefault(currIndex,[])

        isFirstTerm = 1
        tempDocs = ()
        command = "awk -F \" \" '$1 ~ "+q+"{print}' "+resultIndri+" > "+pathTempFilteredFile
        #print command
        os.system(command)
        #call(["awk","-F","\" \"","'$1 ~ "+q+"{print}'",resultIndri,">",pathTempFilteredFile])
        dumpIndexT = "/projets/sig/PROJET/PRINCESS/code/princess/feature_extraction/temp/dumpIndexT_" + normType + maxRes + ".txt"

        termInDoc = {}

        for t in queryTerms[q]:
            t = t.replace("\n","")


            #print "[Term "+t+"]\n"
            #print "[Start dumpIndex for "+t+"]"
            #os.system("rm "+dumpIndexT)
            command = dumpIndex+" "+indexValues[currIndex]+" t "+t+" > "+dumpIndexT
            #print command
            os.system(command)
            #print "[End dumpIndex for "+t+"]"

            # Calcul de l'idf
            termDependant = {}
            for i in range(0,len(infoFeatures)):
                if infoFeatures[i] != {} :
                    feat = infoFeatures[i]["name"]
                    if (infoFeatures[i]["index"] ==  currIndex and infoFeatures[i]["dependant"] == "term"):
                        termInDoc[t] =[]
                        if i not in range(49,52) and feat not in termDependant.keys():
                            termDependant[feat] = functionMapping[feat](dumpIndexT,nbDocsIndex)
                            idf.setdefault(t,termDependant[feat][1])


            # Pour chaque document retourne par retEval sur l'index en cours
            with open(pathTempFilteredFile) as tempFile:
                text=tempFile.read()
                tempDocs=text.split("\n")
                for currLine in tempDocs :

                    if (currLine != ""):
                        arrLine = currLine.split(" ")
                        #currDoc = arrLine[1]
                        currDoc = arrLine[2]
                        #print "document => "+currDoc


                        #if (isFirstTerm or currDoc not in mappingDoc.keys()):
                        if (isFirstTerm):
                            docId = Popen(["/osirim/sig/CORPUS-TRAV/TREC-ADHOC/indri-5.8/dumpindex/dumpindex",indexValues[currIndex],"di", "docno",currDoc],stdout=subprocess.PIPE).stdout.read()
                            docId = docId.replace("\n","")
                            #print docId
                            mappingDoc[currDoc] = docId
                            docsInCurrIndex[q].append(currDoc)

                        else :
                            docId = mappingDoc[currDoc]

                        if currDoc not in featuresValues[q].keys():
                            featuresValues[q][currDoc] ={}


                        for i in range(0,len(infoFeatures)) :
                            if infoFeatures[i] != {} :

                                feat = infoFeatures[i]["name"]
                                # si tf
                                if (infoFeatures[i]["index"] ==  currIndex and infoFeatures[i]["dependant"] == "document-term"):
                                    if feat in functionMapping.keys():
                                        #os.system('read -s -n 1 -p "Press any key to continue..."')
                                        if feat not in featuresValues[q][currDoc].keys():
                                            featuresValues[q][currDoc][feat]= 0
                                            if (currIndex == "TitleIndex") :
                                                featuresValues[q][currDoc]["f11"] = 0
                                                featuresValues[q][currDoc]["f8"] = 0
                                                featuresValues[q][currDoc]["f23"] = 0
                                                featuresValues[q][currDoc]["f26"] = 0
                                            elif (currIndex == "BodyIndex"):
                                                featuresValues[q][currDoc]["f10"] = 0
                                                featuresValues[q][currDoc]["f7"] = 0
                                                featuresValues[q][currDoc]["f22"] = 0
                                                featuresValues[q][currDoc]["f25"] = 0
                                            else:
                                                featuresValues[q][currDoc]["f12"] = 0
                                                featuresValues[q][currDoc]["f9"] = 0
                                                featuresValues[q][currDoc]["f24"] = 0
                                                featuresValues[q][currDoc]["f27"] = 0

                                        #print feat, docId
                                        value = functionMapping[feat](docId,dumpIndexT)
                                        featuresValues[q][currDoc][feat] += value[0]

                                        if (value[2] > 0):
                                            if (currIndex == "TitleIndex") :
                                                featuresValues[q][currDoc]["f47"]=value[2]
                                                featuresValues[q][currDoc]["f11"] += value[1]
                                                featuresValues[q][currDoc]["f8"] += value[0] * termDependant["f5"][0]
                                                featuresValues[q][currDoc]["f23"] += math.log10(value[0] * termDependant["f5"][0])
                                                featuresValues[q][currDoc]["f26"] += value[0] * termDependant["f5"][1]
                                            elif (currIndex == "BodyIndex"):
                                                featuresValues[q][currDoc]["f46"]=value[2]
                                                featuresValues[q][currDoc]["f10"] += value[1]
                                                featuresValues[q][currDoc]["f7"] += value[0] * termDependant["f4"][0]
                                                featuresValues[q][currDoc]["f22"] += math.log10(value[0] * termDependant["f4"][0])
                                                featuresValues[q][currDoc]["f25"] += value[0] * termDependant["f4"][1]
                                            else:
                                                featuresValues[q][currDoc]["f48"]=value[2]
                                                featuresValues[q][currDoc]["f12"] += value[1]
                                                featuresValues[q][currDoc]["f9"] += value[0]  * termDependant["f6"][0]
                                                featuresValues[q][currDoc]["f24"] += math.log10(value[0] * termDependant["f6"][0])
                                                featuresValues[q][currDoc]["f27"] += value[0] * termDependant["f6"][1]



                                        if (feat == idFeatTF[currIndex]):
                                            if value[0] > 0 :
                                                termInDoc[t].append(currDoc)

                                else:
                                    if (infoFeatures[i]["index"] ==  currIndex and infoFeatures[i]["dependant"] == "term" and currDoc in termInDoc[t]):
                                        if feat in functionMapping.keys():
                                            if feat not in featuresValues[q][currDoc].keys():
                                                featuresValues[q][currDoc][feat]= 0
                                                if (currIndex == "TitleIndex") :
                                                    featuresValues[q][currDoc]["f50"] = 0
                                                elif (currIndex == "BodyIndex"):
                                                    featuresValues[q][currDoc]["f49"] = 0
                                                else:
                                                    featuresValues[q][currDoc]["f51"] = 0

                                            value = termDependant[feat]
                                            featuresValues[q][currDoc][feat] += value[0]

                                            if (currIndex == "TitleIndex") :
                                                featuresValues[q][currDoc]["f50"] += value[1]
                                            elif (currIndex == "BodyIndex"):
                                                featuresValues[q][currDoc]["f49"] += value[1]
                                            else:
                                                featuresValues[q][currDoc]["f51"] += value[1]

                                    else :
                                        if infoFeatures[i]["index"] ==  currIndex and infoFeatures[i]["dependant"] == "document" and isFirstTerm:
                                            
                                            if feat in functionMapping:
                                                if feat == "f52": 
                                                    print currDoc
                                                    r = functionMapping[feat](currDoc)
                                                    print r
                                                    featuresValues[q][currDoc]["f52"] = r["ARI"]
                                                    featuresValues[q][currDoc]["f53"] = r["FleschReadingEase"]
                                                    featuresValues[q][currDoc]["f54"] = r["FleschKincaidGradeLevel"]
                                                    featuresValues[q][currDoc]["f55"] = r["RIX"]
                                                    featuresValues[q][currDoc]["f56"] = r["GunningFogIndex"]
                                                    featuresValues[q][currDoc]["f57"] = r["SMOGIndex"]
                                                    featuresValues[q][currDoc]["f58"] = r["ColemanLiauIndex"]
                                                    featuresValues[q][currDoc]["f59"] = r["LIX"]

                                                elif feat == "f60": #page rank
                                                    print currDoc
                                                    featuresValues[q][currDoc]["f60"] = functionMapping[feat](currDoc)

                                                elif feat == "f61": #spam score
                                                    print currDoc
                                                    featuresValues[q][currDoc]["f61"] = functionMapping[feat](currDoc)
                                                elif feat == "f64": # entropy
                                                    print currDoc
                                                    dumpIndexT = "/projets/sig/PROJET/PRINCESS/code/princess/feature_extraction/temp/dumpIndexT_" + normType + maxRes
                                                    f64,f65 = functionMapping[feat](mappingDoc[currDoc],dumpIndex,indexValues[currIndex],dumpIndexT)
                                                    featuresValues[q][currDoc]["f64"] = f64
                                                    featuresValues[q][currDoc]["f65"] = f65


            isFirstTerm = 0


    print "idf"
    print idf

    # Pour les modeles
    for i in range(0,len(infoFeatures)):
        if infoFeatures[i] != {} :
            feat = infoFeatures[i]["name"]
            #print feat
            if (infoFeatures[i]["index"] ==  currIndex and infoFeatures[i]["dependant"] == "query"):
                dumpIndexT = "/projets/sig/PROJET/PRINCESS/code/princess/feature_extraction/temp/dumpIndexT_" + normType + maxRes
                if feat == "f62":
                    for q in queryTerms.keys() :
                        for doc in docsInCurrIndex[q] :
                            val =  functionMapping[feat](indexValues[currIndex],queryTerms[q],dumpIndexT,mappingDoc[doc],q)
                            if val > 0 : 
                                print val
                                featuresValues[q][doc][feat] = val
                elif feat == "f63":
                    for q in queryTerms.keys() :
                        for doc in docsInCurrIndex[q] :
                            val =  functionMapping[feat](queryTerms[q],idf,dumpIndexT,q,mappingDoc[doc])
                            #if val > 0 : 
                            #    print val
                            #    featuresValues[q][doc][feat] = val
                else : 
                    # On commence par generer le fichier de param d'Indri
                    #print modelMapping[feat][0],modelMapping[feat][1],modelMapping[feat][2]
                    generateIndriParam(indexValues[currIndex],modelMapping[feat][0],modelMapping[feat][1],modelMapping[feat][2], currIndex,"2000")
                    functionMapping[feat](modelMapping[feat][2],queriesFile,modelMapping[feat][1])
                    for q in queryTerms.keys() :
                        command = "awk -F \" \" '$1 ~ "+q+"{print}' "+modelMapping[feat][1]+" > "+pathTempFilteredFile
                        os.system(command)
                        for doc in docsInCurrIndex[q] :
                            #print "document => "+doc
                            res = Popen(["grep","-e"," "+doc+" ",pathTempFilteredFile],stdout=subprocess.PIPE).stdout.read()
                            #print "("+res+")"
                            tRes = res.split(" ")
                            #print tRes
                            if len(tRes) > 1 :
                                #featuresValues[q][doc][feat] = float(tRes[2])
                                #print tRes[2],tRes[4]
                                featuresValues[q][doc][feat] = float(tRes[4])

                            # Pour certains modeles le max = 0 avant normalisation
                            #else :
                            #   featuresValues[q][doc][feat] = 0.0

    for ind in getDependantFeatures(currIndex):
        feat = infoFeatures[ind]["name"]
        if feat in functionMapping:
            for q in queryTerms :
                #for doc in featuresValues[q].keys() :
                for doc in docsInCurrIndex[q] :
                    #print "document => "+doc
                    s = infoFeatures[ind]["dependant"]
                    tab = s.split(",")
                    if tab[0] in featuresValues[q][doc] :
                        value = functionMapping[feat](tab,featuresValues[q][doc])
                        featuresValues[q][doc][feat] = value


    #for q in queryTerms.keys() :
        #print "FeatureValue de "+q+" = "
        #print featuresValues[q]




end = time.time()
print ("Time = "+str(end-begin)+" s" )



# ********************************************
# CALCUL DU MAX ET DU MIN
# ********************************************
dictBounds = {}
dictAvg = {}
dictStdDev = {}
mappingForDoc = {}

for q in featuresValues.keys():   # q => la requete courante / indexe une collection de documents
    maxFeat[q] = {}
    minFeat[q] = {}
    valFeat[q] = {}
    #print "nbDocs => "+str(len(featuresValues[q].keys() ))
    for doc in featuresValues[q].keys() : # doc un document / indexe un ensemble de features

        for f in featuresValues[q][doc].keys() : # f la feature
            val = featuresValues[q][doc][f]
            valFeat[q].setdefault(f,[])
            mappingForDoc[q+"@"+doc+"@"+f] = len(valFeat[q][f])
            valFeat[q][f].append(val)
            if f not in maxFeat[q] or maxFeat[q][f] < val :
                maxFeat[q][f] = val
            if f not in minFeat[q] or minFeat[q][f] > val :
                minFeat[q][f] = val

#print "valfeat"
#print valFeat


# Calcul des histogrammes
if normType == "discWidth":
    for q in valFeat.keys() :
        dictBounds[q]={}
        for f in valFeat[q].keys() : # f la feature
            dictBounds[q][f] = np.histogram(valFeat[q][f],nbBins)[1]
elif normType == "discFreq" :
    for q in valFeat.keys() :
        dictBounds[q]= {}
        for f in valFeat[q].keys() : # f la feature
            X = valFeat[q][f]
            nobs = len(X)
            dictBounds[q][f] = np.ceil(nbBins * stats.rankdata(X)/nobs)
    #print "dictBounds"
    #print dictBounds
elif normType == "stdz" :
    for q in valFeat.keys() :
        dictStdDev[q]= {}
        dictAvg[q]= {}
        for f in valFeat[q].keys() : # f la feature
            dictAvg[q][f] = np.mean(valFeat[q][f], dtype=np.float64)
            #print "valFeat["+ str(q) + "]["+str(f)+"] = "+str(valFeat[q][f])
            #print "dictAvg["+ str(q) + "]["+str(f)+"] = "+str(dictAvg[q][f])
            dictStdDev[q][f] = np.std (valFeat[q][f], dtype=np.float64)
            #print "dictStdDev["+ str(q) + "]["+str(f)+"] = "+str(dictStdDev[q][f])
else :
    valFeat={}



# ********************************************
# INSERTION
# ********************************************


#data=collection.save(featuresValues)

if normType == 'max' :
    for q in featuresValues.keys():   # q => la requete courante / indexe une collection de documents
        req = {}
        req["query"]=q
        req["docs"] = []
        for doc in featuresValues[q].keys() : # doc un document / indexe un ensemble de features
            docH = {}
            docH["doc_name"] = doc
            docH["features"] = {}
            for f in featuresValues[q][doc].keys() : # f la feature
                val = featuresValues[q][doc][f]

                if maxFeat[q][f] > 0 :
                    docH["features"][f] = float(val) / float(maxFeat[q][f])
                else :
                    #print "Attention max(feat "+f+") = 0"
                    if minFeat[q][f] == 0:
                        #print "Attention minFeat(feat "+f+") = 0"
                        docH["features"][f]= float(val)
                    else:
                        docH["features"][f]= 1 - (float(val) / float(minFeat[q][f]))
            req["docs"].append(docH)
        data=collection.save(req)
elif normType == 'lee' :
    for q in featuresValues.keys():   # q => la requete courante / indexe une collection de documents
            req = {}
            req["query"]=q
            req["docs"] = []
            for doc in featuresValues[q].keys() : # doc un document / indexe un ensemble de features
                docH = {}
                docH["doc_name"] = doc
                docH["features"] = {}
                for f in featuresValues[q][doc].keys() : # f la feature
                    val = featuresValues[q][doc][f]
                    if (float(maxFeat[q][f]) - float(minFeat[q][f])) == 0:
                        #print "Attention minFeat(feat "+f+") et maxFeat(feat "+f+") = 0"
                        docH["features"][f]= 1.0
                    else:
                        docH["features"][f]= (float(val) - float(minFeat[q][f])) / (float(maxFeat[q][f]) - float(minFeat[q][f]))
                req["docs"].append(docH)
            data=collection.save(req)
elif normType == 'discWidth' :
    for q in featuresValues.keys():   # q => la requete courante / indexe une collection de documents
            req = {}
            req["query"]=q
            req["docs"] = []
            for doc in featuresValues[q].keys() : # doc un document / indexe un ensemble de features
                docH = {}
                docH["doc_name"] = doc
                docH["features"] = {}
                for f in featuresValues[q][doc].keys() : # f la feature
                    val = featuresValues[q][doc][f]
                    docH["features"][f]= valToBin(val,dictBounds[q][f])

                req["docs"].append(docH)
            data=collection.save(req)
elif normType == 'discFreq' :
    for q in featuresValues.keys():   # q => la requete courante / indexe une collection de documents
            req = {}
            req["query"]=q
            req["docs"] = []
            for doc in featuresValues[q].keys() : # doc un document / indexe un ensemble de features
                docH = {}
                docH["doc_name"] = doc
                docH["features"] = {}

                for f in featuresValues[q][doc].keys() : # f la feature
                    position = mappingForDoc[q+"@"+doc+"@"+f]
                    val = featuresValues[q][doc][f]
                    #print  f
                    #print dictBounds[q][f]
                    #print position
                    if f in dictBounds[q] :
                        toInsert = dictBounds[q][f][position]
                        docH["features"][f]= toInsert

                req["docs"].append(docH)
            data=collection.save(req)
elif normType == 'stdz' :
    for q in featuresValues.keys():   # q => la requete courante / indexe une collection de documents
            req = {}
            req["query"]=q
            req["docs"] = []
            for doc in featuresValues[q].keys() : # doc un document / indexe un ensemble de features
                docH = {}
                docH["doc_name"] = doc
                docH["features"] = {}
                for f in featuresValues[q][doc].keys() : # f la feature
                    val = featuresValues[q][doc][f]
                    if (dictStdDev[q][f]) == 0:
                        #print "Attention minFeat(feat "+f+") et maxFeat(feat "+f+") = 0"
                        docH["features"][f]= 0.0
                    else:
                        docH["features"][f]= (float(val) - float(dictAvg[q][f])) / float(dictStdDev[q][f])

                req["docs"].append(docH)
            data=collection.save(req)

# ********************************************
# END
# ********************************************




