from operator import itemgetter
from collections import Counter
from itertools import ifilter, imap, tee

# data for use_subvalues=True should be an iterable with entries of the form:
# {
#  ltag: (l_sub0, l_sub1, ... l_subn), 
#  rtag: (r_sub0, r_sub1, ... r_subm), 
#  ...            
# }            

class ImageData(object):
    
    def __init__(self, 
                 data, 
                 ltag, 
                 rtag, 
                 use_subvalues_left=False, 
                 use_subvalues_right=False, 
                 **kwargs):

        self.data = data
        self.ltag = ltag
        self.rtag = rtag

        if (kwargs.get('filter')):
            self.data = ifilter(kwargs['filter'], self.data)

        # Convert all tags to tuples if only one is a tuple on input.
        if use_subvalues_left and not use_subvalues_right:
            self.data = convert_to_tuples(self.data, self.rtag)
        if use_subvalues_right and not use_subvalues_left:
            self.data = convert_to_tuples(self.data, self.ltag)

        self.use_subvalues = (use_subvalues_right or use_subvalues_left)
        self.compute_counts()

    def compute_counts(self):

        # The use_subvalues flag signifies that our data entries are
        # tuples of primitives, and we want to count the entries in
        # the tuples rather than the tuples themselves.
        if self.use_subvalues:
            
            self.data, copy0, copy1 = tee(self.data, 3)
            l_max, r_max = compute_max_entry_length(copy0, self.ltag, self.rtag)

            self.lcounts, self.rcounts, self.pair_counts = \
                compute_counts_subvalues(copy1, self.ltag, self.rtag, l_max, r_max)

        else:
            self.data, copy = tee(self.data, 2)

            self.lcounts, self.rcounts, self.pair_counts = \
                compute_counts_primitives(copy, self.ltag, self.rtag)
        
def compute_counts_primitives(data, ltag, rtag):
    
    copy0, copy1, copy2 = tee(data, 3)

    lvalues = (str(entry[ltag]) for entry in copy0)
    lvalue_counts = Counter(lvalues)

    rvalues = (str(entry[rtag]) for entry in copy1)
    rvalue_counts = Counter(rvalues)
    
    # Returns tuples of the form: (entry[ltag], entry[rtag]).

    value_pairs = ( (str(entry[ltag]), str(entry[rtag])) for entry in copy2 )
    value_pair_counts = Counter(value_pairs)

    lvalue_totals = sum(count for count in lvalue_counts.itervalues())
    rvalue_totals = sum(count for count in rvalue_counts.itervalues())
    pair_totals = sum(count for count in value_pair_counts.itervalues())

    assert(lvalue_totals == rvalue_totals == pair_totals)

    return lvalue_counts, rvalue_counts, value_pair_counts

def compute_max_entry_length(data, ltag, rtag):

    lval_max = 0
    rval_max = 0

    for entry in data:

        if len(entry[ltag]) > lval_max:
            lval_max = len(entry[ltag])

        if len(entry[rtag]) > rval_max:
            rval_max = len(entry[rtag])

    return lval_max, rval_max

def compute_counts_subvalues(data, ltag, rtag, lval_max, rval_max):

    base_units = lval_max * rval_max

    lvalue_counts = Counter()
    rvalue_counts = Counter()
    value_pair_counts = Counter()

    # Returns a stream of tuples containing (entry[ltag], entry[rtag])
    # for each entry.
    tag_values = imap(itemgetter(ltag, rtag), data)
    
    for lvalue, rvalue in tag_values:

        total_pairs = len(lvalue) * len(rvalue)

        assert(isinstance(lvalue, tuple)), "Non-tuple entry: (%s %r)" % (ltag, lvalue)
        assert(isinstance(rvalue, tuple)), "Non-tuple: (%s %r)" % (rtag, rvalue)
        
        # Compute counts of distinct l_subvalue. The base unit per entry
        # is spread across each sub-value of lvalue.
        for l_subvalue in lvalue:
            
            lvalue_counts[l_subvalue] += (base_units / (len(lvalue) * 1.0))

            # While we're here, compute counts of (lvalue, rvalue)
            # pairs.  The base unit per entry is spread across all
            # possible pairs of sub-values between lvalue and rvalue.
            for r_subvalue in rvalue:
                value_pair_counts[(l_subvalue, r_subvalue)] += (base_units / (total_pairs * 1.0))

        # Compute counts of distinct r_subvalues.
        for r_subvalue in rvalue:
            rvalue_counts[r_subvalue] += (base_units / (len(rvalue) * 1.0))

    lvalue_total = sum(count for count in lvalue_counts.itervalues())
    rvalue_total = sum(count for count in rvalue_counts.itervalues())
    pair_total = sum(count for count in rvalue_counts.itervalues())

    # Convert the counts to ints so that circos can parse them correctly.
    intify_counts(lvalue_counts)
    intify_counts(rvalue_counts)
    intify_counts(value_pair_counts)

    assert(lvalue_total == rvalue_total == pair_total)
    
    return lvalue_counts, rvalue_counts, value_pair_counts

def intify_counts(counter):
    
    for key in counter.iterkeys():
        counter[key] = int(counter[key])
    
def convert_to_tuples(gen, key):

    for entry in gen:
        entry[key] = tuple([entry[key]])
        yield entry
