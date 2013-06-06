import csv
from collections import defaultdict
from itertools import ifilter

"""
Class encapsulating the category mapping information stored in
client's csv input.
"""

class CategoryMapping(object):

    def __init__(self, 
                 left_csv, 
                 right_csv, 
                 order_csv, 
                 left_output_key="Major",
                 right_output_key="Industry"):
        
        self.left_mapping = read_transpose_dict(left_csv)
        self.right_mapping = read_transpose_dict(right_csv)
        self.left_order, self.right_order = parse_order(order_csv)
        self.left_output_key= left_output_key
        self.right_output_key="Industry"

    def apply(self, data):
        
        for entry in data:
            success = apply_to_entry(entry, 
                                     self.left_mapping, 
                                     self.left_mapping["Major Tags"], 
                                     self.left_output_key)
            # No match, skip to the next entry.
            if not success:
                continue

            success = apply_to_entry(entry, 
                                    self.right_mapping, 
                                    self.right_mapping["Industry Tags"], 
                                    self.right_output_key)
            if not success:
                import nose.tools; nose.tools.set_trace()
                continue
            
            # Insufficient or non-matching data for this entry.
            if entry != None:
                yield entry

def apply_to_entry(entry, mapping, tags, output_field):

    if entry == None:
        return entry

    matches = [''] * len(tags)

    for index, tag in enumerate(tags):
        if entry[tag] == '':
            continue
        
        matches[index] = find_match(entry[tag], mapping)
    
    # Filter out empty values and duplicates, then sort and make a tuple.
    all_matches = tuple(sorted(set(filter(lambda x: x != '', matches))))

    if len(all_matches) == 0:
        return False
    else:
        entry[output_field] = all_matches
        return True
        
"""Take a string and a dict with entries like {key : [values]}, and
return the first key either containing a value that is a substring
of in_str, or the first key with in_str as a substring of some
value, whichever comes first."""
def find_match(in_str, mapping):

    # Input matches a key directly.
    if in_str in mapping.keys():
        return in_str

    for category_name, keywords in mapping.iteritems():
        # Input matches a keyword.
        if in_str in keywords:
            return category_name

    # No match
    return ''

def read_transpose_dict(filename):
    
    reader = csv.DictReader(open(filename))
    out_dict = defaultdict(list)

    for entry in reader:
        for k, v in entry.iteritems():
            if v != '':
                out_dict[k].append(v)
    
    return dict(out_dict)
    
def fil_ws(s):
    return not (s.isspace() or s == '')

def parse_order(filename):

    left_order = []
    right_order = []
    reader = csv.DictReader(open(filename))
    
    for entry in reader:
        left_order.append(entry["Major Order"])
        right_order.append(entry["Industry Order"])
    
    # Make both orders go from top to bottom.
    left_order.reverse()
    return (filter(fil_ws, left_order), filter(fil_ws, right_order))

if __name__ == "__main__":

    from config import CircosConfig
    from data import ImageData, CMapImageData
    from projects.williams.double_major import clean_major_fields
    from filters import read_csv, fill_industries, read_filled_csv
    from projects.williams.definitions import(ordered_majors, 
                                              ordered_industries)

    reader = fill_industries(read_csv())
    catmap = CategoryMapping("major.csv", "industry.csv", "order.csv")

    data = CMapImageData(reader, 
                         catmap, 
                         filter=lambda x: x['Industry'] != 'Unlisted',
                         use_subvalues_left=True, 
                         use_subvalues_right=True)
    conf = CircosConfig(data, 
                        use_default_colors=True, 
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)
    conf.produce_image()
