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
    
