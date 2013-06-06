import csv

saved_values = ['major1', 'major2', 'Industry', 'gradyear']

def merge_and_clean(pair):
    data = pair[0]
    
    data.update(pair[1])
    if data['BUS_FIELD_OF_WORK_DESC'].isspace():
        data['Industry'] = 'Unlisted'
    else:
        data['Industry'] = data['BUS_FIELD_OF_WORK_DESC']
    
    #Clear out fields we don't care about.
    for k in data.keys():
        if k not in saved_values:
            del data[k]
    return data

if __name__ == "__main__":

    major_data = list(csv.DictReader(open("majordata.csv")))
    industry_data = list(csv.DictReader(open("workdata.csv")))

    major_ids = {entry['sid'] for entry in major_data}
    industry_ids = {entry['S_ID'] for entry in industry_data}
    both = major_ids.intersection(industry_ids)

    md_filtered = filter(lambda x: x['sid'] in both, major_data)
    id_filtered = filter(lambda x: x['S_ID'] in both, industry_data)
    zipped = zip(md_filtered, id_filtered)
    merged = map(merge_and_clean, zipped)
    
    with open("kenyon.csv", 'wb') as outfile:
        writer = csv.DictWriter(outfile, saved_values)
        writer.writeheader()
        writer.writerows(merged)

                            

