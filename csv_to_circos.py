import os
import subprocess

from definitions import majors, double_majors, student_csv, circos_command
from csv_to_mongo import read_csv, filter_by_major, read_filled_csv
from itertools import chain
from collections import defaultdict

def math_major_image():
    
    try:
        os.mkdir('./tmp')
    except OSError:
        print "Warning: ./tmp already exists"
        
    link_data = open('./tmp/linkdata.txt', 'w')
    industries, major_pairs, combinations = count_double_majors("Mathematics")

    produce_linked_image(major_pairs, industries)

    link_id = 0
    
    major_template = "id{id} {name} {start} {end} color=c{colornum}\n"
    industry_template = "id{id} {name} {start} {end} color=grey\n"

    for major_count, pair in enumerate(major_pairs.keys()):

        major_name = "lside{count}".format(count=major_count)

        for industry_count, industry in enumerate(industries.keys()):
            ribbon_width = combinations.get(tuple([pair[0], pair[1], industry]), 0)
            # No data for this combination
            if ribbon_width == 0:
                #print "No data for combination %s %s %s" % tuple([pair[0], pair[1], industry])
                continue
            
            # Don't bother to increment link_id for entries with no data.
            link_id += 1
            
            # Write the line defining the "major" half of the link.
            major_end = major_pairs[pair]
            major_start = major_end - ribbon_width
            major_line = major_template.format(id=link_id, 
                                               name=major_name,
                                               start=major_start,
                                               end=major_end, 
                                               colornum=major_count + 1)
            link_data.write(major_line)

            # Reduce the number of remaining majors in this major pair
            # for the next iteration.
            major_pairs[pair] = major_start

            # Write the line defining the "industry" half of the link
            industry_name = 'rside{count}'.format(count = industry_count)
            industry_end = industries[industry]
            industry_start = industry_end - ribbon_width
            link_data.write(industry_template.format(id=link_id, 
                                                     name=industry_name,
                                                     start=industry_start,
                                                     end=industry_end, 
                                                     ))
            
            # Reduce the number of remaining majors in this major pair
            # for the next iteration.
            industries[industry] = industry_start

        assert major_pairs[pair] == 0, "major pair count should be zero"
        print "Finished pair %s %s" % pair
        
    for count in industries.itervalues():
        assert count == 0, "industry pair count should be zero"
    run_circos()
    
def produce_linked_image(lside, rside, **kwargs):
    
    assert_valid_input(lside, rside)
    
    # Define and format chromosome names.
    lside_chroms = gen_chromosome_names('l', len(lside))
    rside_chroms = gen_chromosome_names('r', len(rside))
    all_chroms = chain(lside_chroms, rside_chroms)
    chroms_formatted = ';'.join(all_chroms)

    # Get color information.
    color = 'grey'
    color_dict = kwargs.get('colors')

    try:
        os.mkdir('./tmp')
    except OSError:
        print "Warning: ./tmp already exists"
    
    # Write karyotype data.
    karyotype_conf = open('./tmp/karyotype.conf', 'w')
    line_template = 'chr - {l_or_r}side{index} {tag} {start} {end} color={color}\n'
    
    # Write left side karyotypes.
    for (index, (tag, amount)) in enumerate(lside.iteritems()):
        
        if color_dict:
            color = color_dict.get(tag, 'grey')
        
        # hard-coded special case for math major, fix later
        if isinstance(tag, tuple):
            if tag[0] in ['', "Mathematics"]:
                tag = tag[1]
            else:
                tag = tag[0]

        karyotype_conf.write(line_template.format(l_or_r='l',
                                                  index=index,
                                                  tag=tag, 
                                                  start=0, 
                                                  end=amount, 
                                                  color=color
        ))

    # Write right side karyotypes.
    for (index, (tag, amount)) in enumerate(rside.iteritems()):
        
        if color_dict:
            color = color_dict.get(tag, 'grey')

        karyotype_conf.write(line_template.format(l_or_r='r',
                                                  index=index,
                                                  tag=tag, 
                                                  start=0, 
                                                  end=amount, 
                                                  color=color
        ))
        
    karyotype_conf.close()
    write_circos_conf(chroms_formatted)
    write_ticks_conf(chroms_formatted)
    
def run_circos():
    subprocess.call(circos_command)

def write_ticks_conf(all_chroms_string):
    
    header = """
<ticks>

chromosomes_display_default = yes

chromosomes = {all_chroms}

radius = dims(ideogram, radius_outer)
orientation = out
label_multiplier = 1
</ticks>
""".format(all_chroms=all_chroms_string)

    ticks_conf = open('./tmp/ticks.conf', 'w')
    ticks_conf.write(header)
    ticks_conf.close()

def write_circos_conf(all_chroms_string):

    circos_conf = open('./tmp/circos.conf', 'w')
    
    header = """
<colors>
  <<include ./colors.conf>>
  <<include etc/brewer.conf>>
</colors>

<fonts>
  <<include etc/fonts.conf>>
</fonts>

<<include ideogram.conf>>
<<include ticks.conf>>

karyotype   = ./karyotype.conf

<image>
  <<include ./image.conf>>
</image>

chromosomes_units = 1
chromosomes = {all_chroms}
chromosomes_display_default = yes
show_ticks = yes
show_tick_labels = yes
""".format(all_chroms=all_chroms_string)

    circos_conf.write(header)

    link_block = """
<links>

z = 0
radius = 0.99r
bezier_radius = 0.25r
crest = 0.4
bezier_radius_purity = 0.8

<link all_links>
show = yes
ribbon = yes
file = ./tmp/linkdata.txt
</link>

</links>

<<include etc/housekeeping.conf>>
"""
    circos_conf.write(link_block)
    circos_conf.close()

def gen_chromosome_names(l_or_r, count):
    assert(l_or_r in ('l', 'r'))
    for index in xrange(count):
        yield '{l_or_r}side{index}'.format(l_or_r=l_or_r, index=index)
    
def assert_valid_input(lside, rside):

    assert isinstance(lside, defaultdict)
    assert isinstance(rside, defaultdict)
    assert(lside.default_factory() == 0)
    assert(rside.default_factory() == 0)

    # Counter dicts may not share tags
    assert(set(lside.keys()).intersection(set(rside.keys())) == set()), \
        "Counter dictionaries may not share tags"
    

def count_all_double_majors(input_filename=student_csv):

    major_counter = defaultdict(int)
    industry_counter = defaultdict(int)

    reader = read_filled_csv(input_filename)

    for entry in reader:

        if entry['Major3'] or not entry['Major2']:
            continue
        
        industry_counter[entry['Industry']] += 1
        major_counter[tuple(sorted([entry['Major1'], 
                                   entry['Major2']]))] += 1
        
    return major_counter, industry_counter
        

def count_double_majors(base_major = "Mathematics"):
    print "###############"
    print "Starting %s:" % base_major
    print "###############"
    
    # Map counting instances of each double major with base_major.
    major_counter = defaultdict(int)

    # Map counting total students in each industry.
    industry_counter = defaultdict(int)

    # Map counting students from each double major in each industry.
    combination_counter = defaultdict(int)
    
    filtered_reader = filter_by_major(read_filled_csv(), base_major)
    
    for student in filtered_reader:
        
        # Ignore triple majors
        if student['Major3']:
            continue
        
        industry = student['Industry']
        if student["Major1"] == student["Major2"]:
            student["Major2"] = ""

        major_pair = tuple(sorted([student['Major1'], student['Major2']]))
        combination = tuple([major_pair[0], major_pair[1], industry])

        industry_counter[industry] += 1
        major_counter[major_pair] += 1
        combination_counter[combination] += 1
        
    print "###############"
    print "Finished %s:" % base_major
    print "###############"
    
    return industry_counter, major_counter, combination_counter

if __name__ == "__main__":
    
    for major in majors:
        count_double_majors(major)
