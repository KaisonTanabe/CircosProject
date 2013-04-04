import csv

from collections import defaultdict

from projects.williams.definitions import industry_map, major_map, student_csv

def read_csv(filename=student_csv):
    reader = csv.DictReader(open(filename))
    return reader

def read_filled_csv(filename=student_csv):
    reader = csv.DictReader(open(filename))
    return fill_majors(fill_industries(reader))

def fill_industries(reader):

    for entry in reader:
        # Skip entries that already have industry info.l
        if entry.get('Industry'):
            match = match_definitions(entry.get('Industry'))
            if match:
                entry['Industry'] = match
                yield entry
                continue
            
        if entry.get('Field of Work'):
            match = match_definitions(entry.get('Field of Work'))
            if match:
                entry['Industry'] = match
                yield entry
                continue
            
        if entry.get('Job Title'):
            match = match_definitions(entry.get('Job Title'))
            if match:
                entry['Industry'] = match
                yield entry   

def fill_majors(reader):

    for entry in reader:
        maj1_value = entry['Major1']
        maj2_value = entry['Major2']
        maj3_value = entry['Major3']
        
        matched = [False, False, False]

        for category_name, matches in major_map.iteritems():

            if maj1_value in matches:
                entry['Major1'] = category_name
                matched[0] = True

            if maj2_value in matches:
                entry['Major2'] = category_name
                matched[1] = True

            if maj3_value in matches:
                entry['Major3'] = category_name
                matched[2] = True

        # Ignore entries with no matched majors.
        if not any(matched):
            continue
                
        # Clear out unmatched data.
        if not matched[0]:
            entry['Major1'] = ''
        if not matched[1]:
            entry['Major2'] = ''
        if not matched[2]:
            entry['Major3'] = ''

        yield entry
                
def match_definitions(info_str):
    
    # if info_str in industry_map.keys():
    #     return info_str

    for industry, keywords in industry_map.items():
        for word in keywords:
            if word in info_str or info_str in word:
                return industry

def filter_by_major(reader, match_string):
    for entry in reader:
        if match_string in entry['Major1']:
            yield entry
        elif match_string in entry['Major2']:
            yield entry
        elif match_string in entry['Major3']:
            yield entry

def filter_by_any_field(reader, match_string):
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

def filter_no_industry(reader):
    return (entry for entry in reader if entry.get('Industry'))

def job_title_frequencies(reader):
    
    out_dict = defaultdict(int)
    for entry in filter_by_major_no_industry(reader):
        fow = entry.get('Field of Work', None)
        if fow:
            out_dict[fow] += 1
    return out_dict
    
if __name__ == "__main__":
    reader = read_filled_csv()
