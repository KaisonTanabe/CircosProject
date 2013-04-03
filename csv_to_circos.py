import os
import subprocess

from itertools import(chain, 
                      tee, 
                      imap, 
                      ifilter)

from collections import Counter
from operator import itemgetter

from definitions import circos_command

from csv_to_mongo import read_filled_csv
from templates import(circos_conf_header, 
                      circos_conf_links, 
                      ideogram_conf_template)

# Class storing all necessary information to create a set of circos
# configuration files.  Can be modified on the fly to change the
# produced image.

class CircosConfig(object):

    def __init__(self, data, ltag, rtag, **kwargs):
        
        # Save a 'copy' of the input data so that we can re-filter or
        # change tags later without creating a new object.
        self.data, self._data_copy = tee(data, 2)
        
        # No filter by default.
        self.filter = kwargs.get('filter', lambda x: True)
        self.data = ifilter(self.filter, self.data)

        if kwargs.get('weighted'):
            self.lcounts, self.rcounts, self.intersect_counts = \
                count_tags_weighted(self.data, ltag, rtag)
        else:
            self.lcounts, self.rcounts, self.intersect_counts = \
                count_tags(self.data, ltag, rtag)

        # Optional arguments for color dictionary and karyotype
        # ordering data.  By default we order from most to least
        # entries.  Order is followed clockwise from top of image for
        # rside, clockwise from the bottom for lside.

        self.lside_tag_order = kwargs.get('lside_tag_order', 
                                          self.lcounts.keys())
        self.rside_tag_order = kwargs.get('rside_tag_order', 
                                          self.rcounts.keys())
        # assert set(self.lside_tag_order) == set(self.lcounts.keys())
        # assert set(self.rside_tag_order) == set(self.rcounts.keys())
            
        self.colors = kwargs.get('colors', {})
        
        # If no color dictionary is supplied, assume we're coloring by
        # ltags using 'c{number}'-style coloring.
        
        if len(self.colors) == 0:
            for index, tag in enumerate(self.lside_tag_order):
                self.colors[tag] = 'c{index}'.format(index=index)

        # Define and format chromosome names.  These are always of the
        # form {r, l}side{0-length}.
        lside_chroms = gen_chromosome_names('l', len(self.lcounts))
        rside_chroms = gen_chromosome_names('r', len(self.rcounts))
        all_chroms = chain(lside_chroms, rside_chroms)        

        # Settings for circos.conf file template.
        self.circos_conf_settings = \
            {"chromosomes_units"     : 1, 
             "chromosomes"           : ';'.join(all_chroms),
             "show_ticks"            : "no", 
             "show_tick_labels"      : "no", 
             "filename"              : kwargs.get('filename', 'circos.png')}

        self.circos_conf_link_settings = \
            {"radius"                : "0.99r", 
             "bezier_radius"         : ".25r", 
             "crest"                 : ".3", 
             "bezier_radius_purity"  : ".95", 
             "show_by_default"       : "yes", 
             "ribbon"                : "yes", 
             "flat"                  : "no"}
        
        # Settings for ideogram_conf file template.
        self.ideogram_conf_settings = \
            {"default_spacing"       : "0.006r", 
             "break"                 : "0.2r", 
             "radius"                : "0.75r"}

    def write_config_files(self):
        
        # Open a scratch directory for us to work in.
        try:
            os.mkdir('./tmp')
        except OSError:
            print "Warning: ./tmp already exists"

        self.write_circos_conf()
        # self.write_ticks_conf()
        self.write_ideogram_conf()
        
        # Write karyotype data.
        self.write_karyotype_conf()
        
    # karyotype.conf controls how the outer ring of the circos image
    # is partitioned and colored.  Each line defines an arc with a
    # width, a color, and a tag used to identify the region by other
    # parts of the image configuration.
    def write_karyotype_conf(self):

        with open('./tmp/karyotype.conf', 'w') as karyotype_conf:
            
            line_template = \
                'chr\t-\t{l_or_r}side{index}\t{tag}\t{start}\t{end}\t{color}\n'
            
            # Right side karyotypes.
            for (index, tag) in enumerate(self.rside_tag_order):
                width = self.rcounts.get(tag, 0)

                # No data for this tag, move on to the next one.
                if width == 0:
                    print("Warning, no data for rside tag: %s" % tag)
                    continue
                
                color = self.colors.get(tag, 'grey')
                karyotype_conf.write(line_template.format(l_or_r='r',
                                                          index=index,
                                                          tag=tag, 
                                                          start=0, 
                                                          end=width, 
                                                          color=color
                                                          ))

            # Left side karyotypes.
            for (index, tag) in enumerate(self.lside_tag_order):
                width = self.lcounts.get(tag, 0)

                # No data for this tag, move on to the next one.
                if width == 0:
                    print("Warning, no data for rside tag: {tag}.".format(
                            tag=tag
                    ))
                    continue

                color = self.colors.get(tag, 'grey')
                karyotype_conf.write(line_template.format(l_or_r='l',
                                                          index=index,
                                                          tag=tag, 
                                                          start=0, 
                                                          end=width, 
                                                          color=color
                                                          ))
    
    def write_circos_conf(self):

        with open('./tmp/circos.conf', 'w') as circos_conf:

            header = circos_conf_header.format(**self.circos_conf_settings)
            circos_conf.write(header)
            link_block = circos_conf_links.format(**self.circos_conf_link_settings)
            circos_conf.write(link_block)

    def write_ideogram_conf(self):

        with open('./tmp/ideogram.conf', 'w') as ideogram_conf:
            config = ideogram_conf_template.format(**self.ideogram_conf_settings)
            ideogram_conf.write(config)

    # TODO: make this not destroy our data
    def write_linkdata(self):
        
        with open('./tmp/linkdata.txt') as link_data:
            
            link_id = 0
            line_template = "id{id}\t{name}\t{start}\t{end}\tcolor=c{colornum}\n"
            link_data = open('./tmp/linkdata.txt', 'w')

            # For each lside tag, iterate over all rside tags, drawing
            # a ribbon of width given by the number of data entries
            # matching both tags (as stored in self.combinations).
            for (l_index, l_tag) in enumerate(self.lside_tag_order):
                for (r_index, r_tag) in enumerate(self.rside_tag_order):

                    ribbon_width = self.intersect_counts.get((l_tag, r_tag), 0)
                    
                    # No data for this pair.
                    if ribbon_width == 0:
                        print "No data for combination %s %s" % (l_tag, r_tag)
                        continue
                        
                    # Write the line defining the left-side half of the ribbon.
                    end = self.lcounts[l_tag]
                    start = end - ribbon_width
                    lside_line = line_template.format(id=link_id, 
                                                      name="lside%d" % l_index, 
                                                      start=start, 
                                                      end=end,
                                                      colornum=l_index)
                    link_data.write(lside_line)
                    
                    # Resize the count of remaining entries for this
                    # left-side tag.
                    self.lcounts[l_tag] = start
                    
                    # Write the line defining the right-side half of the ribbon.
                    end = self.rcounts[r_tag]
                    start = end - ribbon_width
                    rside_line = line_template.format(id=link_id, 
                                                      name="rside%d" % r_index, 
                                                      start=start, 
                                                      end=end,
                                                      colornum=l_index)
                    link_data.write(rside_line)

                    # Resize the count of remaining entries for this
                    # right-side tag.
                    self.rcounts[r_tag] = start
                    link_id += 1
                    
                # End rside-loop.  We should have processed all
                # entries for this lside tag.
                assert self.lcounts[l_tag] == 0, l_tag
                print "Finished processing lside tag: {tag}".format(tag=l_tag)
                
            # End lside-loop
            for r_tag, count in self.rcounts.iteritems():
                assert count == 0, "%r %r" % (r_tag, count)

    def produce_image(self):
        self.write_config_files()
        self.write_linkdata()
        run_circos()

def count_single_tag(data, tag):
    tag_values = (entry[tag] for entry in data)
    return Counter(tag_values)

# Iterate over data, counting unique values of entry[ltag],
# entry[rtag], and (entry[ltag], entry[rtag]).
def count_tags(data, ltag, rtag):

    copy0, copy1, copy2 = tee(data, 3)

    ltags = (entry[ltag] for entry in copy0)
    ltag_counts = Counter(ltags)

    rtags = (entry[rtag] for entry in copy1)
    rtag_counts = Counter(rtags)

    # Returns tuples of the form: (entry[ltag], entry[rtag]).
    combinations = imap(itemgetter(ltag, rtag), copy2)
    combination_counts = Counter(combinations)
    return ltag_counts, rtag_counts, combination_counts

def count_tags_weighted(data, ltag, rtag):
    
    copy0, copy1, copy2 = tee(data, 3)

    ltag_counts = Counter()
    rtag_counts = Counter()
    combination_counts = Counter()

    for entry in copy0:
        value = entry[ltag]
        assert iter(value)
        assert len(value)
        for sub_value in value:
            ltag_counts[sub_value] += (2 / len(value))

    for entry in copy1:
        # TODO: support multi-valent rtags as well.
        value = entry[rtag]
        rtag_counts[value] += 2
    
    combinations = imap(itemgetter(ltag, rtag), copy2)
    for entry in combinations:
        lval = entry[0]
        rval = entry[1]
        # Iterate over ltag sub-values.
        for sub_value in lval:
            combination_counts[(sub_value, rval)] += (2 / len(lval))

    return ltag_counts, rtag_counts, combination_counts

def gen_chromosome_names(l_or_r, count):
    assert(l_or_r in ('l', 'r'))
    for index in xrange(count):
        yield '{l_or_r}side{index}'.format(l_or_r=l_or_r, index=index)

def run_circos():
    subprocess.call(circos_command)
