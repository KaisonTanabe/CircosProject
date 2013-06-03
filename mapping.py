import csv
from collections import defaultdict
from itertools import ifilter

"""

Class encapsulating the category mapping information stored in
client's csv input.

Major and Industry CSV files should begin with a line of the form:

{Major/Industry} Tags, Tag1, Tag2, Tag3, ...

for example:

Major Tags, Major1, Major2, Major3, ...
Industry Tags, Industry, ...

The remaining lines should be of the form:

Category Name, Match1, Match2, Match3, ...

for example:

Languages, French, Spanish, Chinese, ...
Sales, Sales, Advertising, Marketing, Retail, ...

The Order CSV file should have the values "Major Order" and "Industry
Order" as the entries of its first row.  The remaining rows should
generate two columns defining an order for placing categories around
the cirle diagram.  Major tags will be placed clockwise from the bottom
of the diagram; right tags will be placed clockwise from the top.

"""

class CategoryMapping(object):

    def __init__(self, left_csv, right_csv, order_csv):
        
        self.left_mapping = read_transpose_dict(left_csv)
        self.right_mapping = read_transpose_dict(right_csv)
        self.left_order, self.right_order = parse_order(order_csv)

    def apply(self, data):
        
        for entry in data:
            import nose.tools; nose.tools.set_trace()
            apply_to_entry(entry, self.left_mapping, self.left_mapping["Major Tags"], "Major")
            apply_to_entry(entry, self.right_mapping, self.right_mapping["Industry Tags"], "Industry")
            
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
    
    all_matches = tuple(sorted(filter(lambda x: x != '', matches)))

    if len(all_matches) == 0:
        entry = None
    else:
        entry[output_field] = all_matches
        
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
    
def parse_order(filename):

    left_order = []
    right_order = []
    reader = csv.DictReader(open(filename))
    
    for entry in reader:
        left_order.append(entry["Major Order"])
        right_order.append(entry["Industry Order"])
        
    return (left_order, right_order)

if __name__ == "__main__":

    from filters import read_csv, fill_industries

    # 'ADV-ID': '0010037246'
    
    r = ifilter(lambda x: x['ADV-ID'] == '0010037246', fill_industries(read_csv()))

    catmap = CategoryMapping("major.csv", "industry.csv", "order.csv")
    mapped = catmap.apply(r)

    
    

