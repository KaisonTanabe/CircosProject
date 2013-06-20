import csv
from collections import defaultdict, OrderedDict, deque
from itertools import ifilter, tee

from data import CMapImageData
from utils import split_even_chunks, average

"""
Class encapsulating the category mapping information stored in
client's csv input.
"""

class CategoryMapping(object):

    def __init__(self, left_csv, right_csv, order_csv, **kwargs):
                 
        self.left_mapping = read_transpose_dict(left_csv)
        self.right_mapping = read_transpose_dict(right_csv)
        self.left_order, self.right_order = parse_order(order_csv)

        self.left_output_key= kwargs.get('left_output_key', 'Major')
        self.right_output_key= kwargs.get('right_output_key', 'Industry')

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
            # Skip blank entries or entries containing only whitespace.
            if v == '' or v.isspace():
                continue
            elif v[0].isspace() or v[-1].isspace():
                print "Stripping whitespace from mapping pair: %s\nIn entry: %s" % \
                    (k, v)
                out_dict[k].append((v.strip()))
            else:
                out_dict[k].append(v)
    print "##############"
    
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

def color_dict_from_field(image_data,
                          ltag, 
                          rtag,
                          fieldname, 
                          color_list, 
                          cutoff_list = [],
                          verbose=False):
    assert(isinstance(image_data, CMapImageData))
    avg_dict = defaultdict(list)
    for entry in image_data:
        for lval in entry[ltag]:
            for rval in entry[rtag]:
                avg_dict[(lval, rval)].append(int(entry[fieldname]))
    for key in avg_dict.keys():
        avg_dict[key] = average(avg_dict[key])
        
    sorted_avgs = sorted(list(avg_dict.iteritems()), key=lambda x: x[1])
    color_dict = {}

    # Divide up data by pseudo-percentiles.
    if len(cutoff_list) == 0:
        chunked = split_even_chunks(sorted_avgs, len(color_list))
        for color, chunk in zip(color_list, chunked):
            for pair in chunk:
                color_dict[pair[0]] = color
            if verbose:
                print "Max value for %s at %s" % (color, chunk[-1][1])
    # Divide up data in accordance with supplied cutoffs.
    else:
        queue = deque(sorted_avgs)
        assert len(color_list) == len(cutoff_list) + 1, \
            """Supplied {color} colors and [cutoff] cutoffs.
             Number of colors should be one greater than
             the number of cutoffs.""".format(color=len(color_list), 
                                            cutoff=len(cutoff_list))
        # Fill values up to each cutoff.
        for index, cutoff in enumerate(cutoff_list):
            while len(queue) > 0 and queue[0][1] < cutoff:
                color_dict[queue[0][0]] = color_list[index]
                queue.popleft()
        # Fill values higher than the last cutoff.
        while len(queue) > 0:
            color_dict[queue[0][0]] = color_list[-1]
            queue.popleft()
    return color_dict
