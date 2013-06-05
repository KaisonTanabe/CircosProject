def make_color(s):
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:], 16)
    return "%s,%s,%s" % (r,g,b)

    
