from filters import read_csv

def make_color(s):
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:], 16)
    return "%s,%s,%s" % (r,g,b)

def split_even_chunks(l, n):

    remainder = len(l) % n
    chunk_base_size = (len(l) - remainder) / n
    num_out = 0
    for i in xrange(n):
        if remainder > 0:
            yield l[num_out:num_out + chunk_base_size + 1]
            num_out += chunk_base_size+1
            remainder -= 1
        else:
            yield l[num_out:num_out + chunk_base_size]
            num_out += chunk_base_size

def average(l):
    return sum(l) / ((1.0) * len(l))
    
def verify_csv_whitespace(filename):
    csv = read_csv(filename)
    for (linenum, entry)  in enumerate(csv):
        for k, v in entry.iteritems():
            if stripable(k) or stripable(v):
                print "Line: %s, Column: %s, Value: %s" % (linenum +1, repr(k), repr(v))
            
def stripable(s):
    if s == '':
        return False
    else:
        return s[0].isspace() or s[-1].isspace()

