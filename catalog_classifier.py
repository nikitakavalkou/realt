# -*- coding: utf-8 -*-

from functions_kufar import *
import pprint


    


def ClassifyRequest(title):
    try:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["kufar"]
        mycol_catalog = mydb['catalog']
    except:
        ExceptionMessage("catalog_classifier.py - DB OPEN ERROR")
        return None

    for m in mycol_catalog.find({}):

        newvalues = {"$set": {"model": clearString(m['model'])}}
        mycol_catalog.update_one(m, newvalues)

    mycol_catalog.create_index([("manufacture", "text"), ("model", "text")])
    title = clearString(title)
    catalog=mycol_catalog.find({'$text': {'$search':title }}, {'score': {'$meta': "textScore"}})

    return catalog





def ClassifyAdCat(iteam,catalog_name):
    #t1 = time.perf_counter()
    #classify AD based on single catalog
    title=iteam['title']
    Result=[]
    

    try:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["kufar"]
        mycol_catalog = mydb[catalog_name]
    except:
        ExceptionMessage("catalog_classifier.py - DB OPEN ERROR")
        return None


    mycol_catalog.create_index([("manufacture", "text"), ("model", "text")])
    title = clearString(title)
    catalog=mycol_catalog.find({'$text': {'$search':title }}, {'score': {'$meta': "textScore"}})

    
   
    
    lastResult=0
    lastTanimoto=0
    for manufacture in catalog: # for each manufacturer
        

        
           
        mdl=clearString(manufacture['model'])      #remove extra characters from model title
                #remove extra characters from AD title
        compResult=compareStrings(mdl,title,0.9) # how many words are pretty the same
        tanimotoResult=compareWords(mdl,title)*tanimotok(mdl,title) # whats the difference between strings based on Livenstain*Tanimoto # whats the difference between strings based on Tanimoto

            
                        
        if len(compResult)>lastResult:  # compare how many identical words are in the model and title
            Result=[]
            lastResult=len(compResult)
            lastTanimoto=tanimotoResult
            Result.append([len(compResult),tanimotoResult,mdl,manufacture['manufacture'].strip().lower()])
        elif len(compResult)==lastResult:
            if tanimotoResult>lastTanimoto and tanimotoResult<1:
                lastTanimoto=tanimotoResult
                Result=[]
                Result.append([len(compResult),tanimotoResult,mdl,manufacture['manufacture'].strip().lower()])
            elif tanimotoResult==lastTanimoto:
                 Result.append([len(compResult),tanimotoResult,mdl,manufacture['manufacture'].strip().lower()])



                
    if len(Result)>0:
        return Result[0]
    else:
        return []




def ClassifyAd(iteam):
    try:
        return ClassifyAdCat(iteam,'catalog')
    except:
        return []
        
   






def ClearCatalog():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["kufar"]
    mycol_catalog = mydb['catalog']
    mycol_catalog.delete_many({'manufacture':'2017'})
    mycol_catalog.delete_many({'manufacture':'2018'})



for ad in ClassifyRequest('iphone 4s'):
    print(ad['model'])


    
    
   







    
            
    


            





    
    


    

