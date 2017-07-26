# -*- coding: utf-8 -*-
import argparse
import json
import os
from rosette.api import API, DocumentParameters, RosetteException
import unicodedata
from SECEdgar.crawler import SecCrawler
import re, os, sys, time, glob, argparse, json
from bs4 import BeautifulSoup


COMPANY_COUNT = 8
date = "20170608"
count = "1"
mydir = ''
newest_year = 17


def clean_html_tags(filepath):
    with open(filepath, "r") as myfile:
        read_string = myfile.read()
    soup = BeautifulSoup(read_string,"lxml")
    uni_str = soup.get_text()
    ascii_str = unicodedata.normalize('NFKD', uni_str).encode('ascii', 'ignore')
    return str(ascii_str)


def extract_relations(relationships_text_data, key, altUrl='https://api.rosette.com/rest/v1/'):
    # Create an API instance
    api = API(user_key=key, service_url=altUrl)
    params = DocumentParameters()
    params["content"] = relationships_text_data
    api.set_option('accuracyMode', 'PRECISION')
    try:
        return api.relationships(params)
    except RosetteException as e:
        print(e)


def extract_entities(entities_text_data, key, altUrl='https://api.rosette.com/rest/v1/'):
    # Create an API instance
    api = API(user_key=key, service_url=altUrl)
    params = DocumentParameters()
    params["content"] = entities_text_data
    params["genre"] = "social-media"
    try:
        return api.entities(params)
    except RosetteException as e:
        print(e)


def extractor(text_path, key, url):
    t1 = time.time()
    # create object
    #seccrawler = SecCrawler()
    # read companies.txt
    with open(text_path) as f:
        content = f.readlines()
    # parse companies.txt and download their DEF 14A
    for line in content:
        line = line.replace("\n", "")
        pair = line.split(' ')
        mydir = os.path.join("SEC-Edgar-Data", pair[0], pair[1], "DEF 14A")
        #TODO can i move filing def14a in this script
        #seccrawler.filing_def14a(pair[0], pair[1], date, count)
        allfiles = glob.glob(mydir + '/*.txt')
        #print allfiles
        year = newest_year
        #Perform relationship extraction on each file under company>file_type
        for one_file in allfiles:
            in_str = clean_html_tags(one_file)
            #print len(in_str)
            first_str = in_str[0:50000]
            relation_result = extract_relations(first_str, key, url)
            entity_result = extract_entities(first_str, key, url)
            concat_dict(in_str,entity_result,relation_result,key,url)
            with open(os.path.join("SEC-relations", (pair[0] +"_"+str(year) + "_relations.json")), 'w') as outfile:
                outfile.write((json.dumps(relation_result, indent=2, ensure_ascii=False, sort_keys=True).encode("utf8")))
            with open(os.path.join("SEC-entities", (pair[0] + "_"+str(year) + "_entities.json")), 'w') as outfile:
                outfile.write((json.dumps(entity_result, indent=2, ensure_ascii=False, sort_keys=True).encode("utf8")))
            year = year - 1
    t2 = time.time()
    print ("Total Time taken: "),
    print (t2 - t1)
    print "done"


def concat_dict(total_str,entity_dict,relation_dict,key,url):
    index=50001
    length=len(total_str)
    print length
    while(index<length):
        input_str = total_str[index:min(length-1,index+50000)]
        en_result=extract_entities(input_str,key,url)
        re_result = extract_relations(input_str, key, url)
        print "index is "
        print index
        print type(en_result)
        print type(re_result)
        #entity_dict["entities"] += en_result["entities"]
        #print (json.dumps(entity_dict, indent=2, ensure_ascii=False, sort_keys=True).encode("utf8"))
        #relation_dict["relationships"]+=re_result["relationships"]
        #print (json.dumps(relation_dict, indent=2, ensure_ascii=False, sort_keys=True).encode("utf8"))
        index+=50000
        print "inwhile loop"
    print "finished concat"





if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Calls the ' + os.path.splitext(os.path.basename(__file__))[
                                         0] + ' endpoint')
    parser.add_argument('-k', '--key', help='Rosette API Key', required=True)
    parser.add_argument('-u', '--url', help="Alternative API URL", default='https://api.rosette.com/rest/v1/')
    parser.add_argument('-f', '--file', help="data.txt file", required=True)
    args = parser.parse_args()
    extractor(args.file, args.key, args.url)
