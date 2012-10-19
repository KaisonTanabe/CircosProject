import csv
import pymongo
import difflib

from collections import defaultdict

from db import connect
from definitions import industry_map, major_map, student_csv

def read_csv_to_mongo(filename=student_csv):
    reader = csv.DictReader(open(filename))
    return reader

def fill_industries(reader):

    for entry in reader:
        # Skip entries that already have industry info.l
        if entry.get('Industry'):
            yield entry
            
        if entry.get('Field of Work'):
            match = match_definitions(entry.get('Field of Work'))
            if match:
                entry['Industry'] = match
                yield entry
            
        if entry.get('Job Title'):
            match = match_definitions(entry.get('Job Title'))
            if match:
                entry['Industry'] = match
                yield entry   

def match_definitions(info_str):
    for industry, keywords in industry_map.items():
        for word in keywords:
            if info_str in word:
                return industry
        
def filter_by_string(reader, match_string):
    for entry in reader:
        for key, value in entry.items():
            if match_string in value:
                yield entry

def filter_by_major_no_industry(reader):
    for entry in reader:
        if (not entry.get('Industry')) and entry.get('Major1'):
            yield entry

def filter_no_major(reader):
    return (entry for entry in reader if entry.get('Major1'))

def job_title_frequencies(reader):
    
    out_dict = defaultdict(int)
    for entry in filter_by_major_no_industry(reader):
        fow = entry.get('Field of Work', None)
        if fow:
            out_dict[fow] += 1
    return out_dict
    
    
if __name__ == "__main__":
    
    reader = read_csv_to_mongo()
    
