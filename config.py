import os
import subprocess
import platform

from copy import deepcopy
from itertools import(chain, 
                      tee, 
                      imap, 
                      ifilter)
from collections import Counter
from operator import itemgetter

from templates import (osx_circos_command,
                       cygwin_circos_command,
                       svg_to_png_command)

from filters import read_filled_csv
from templates import(circos_conf_header,
                      circos_conf_links,
                      ideogram_conf_template)

# Class storing all necessary information to create a set of circos
# configuration files.  Can be modified on the fly to change the
# produced image.

class CircosConfig(object):

    def __init__(self, data, **kwargs):

        self.data = data
        self.link_filter = kwargs.get('link_filter', lambda x, y: True)

        self.ltag_parse = kwargs.get('ltag_parse', lambda x: x)
        self.rtag_parse = kwargs.get('rtag_parse', lambda x: x)
        
        self.lside_tag_order = kwargs.get('lside_tag_order', 
                                          self.data.lcounts.keys())
        self.rside_tag_order = kwargs.get('rside_tag_order', 
                                          self.data.rcounts.keys())
        
        # ----------------------------------------
        # ----- Setup for Color Dictionaries -----
        # ----------------------------------------
        self.karyotype_colors = kwargs.get('karyotype_colors', {})
        self.link_colors = kwargs.get('link_colors', {})
        build_links = (self.link_colors == {})
        
        self.use_default_colors = kwargs.get('use_default_colors', False)
        open('tmp/customcolors.conf', 'w').close() # clear custom colors
        # Default colors using 'default_color{num}'
        if self.use_default_colors:
            for index, ltag in enumerate(self.lside_tag_order):
                self.karyotype_colors[ltag] = 'default_color{index}'.format(index=index)
                if build_links:
                    for rtag in self.rside_tag_order:
                        self.link_colors[(ltag, rtag)] = 'default_color{index}'.format(index=index)
        # Pre-fab color palette using '{palette_name}{num}'
        elif kwargs.get('color_palette', False):
            palette = kwargs.get('color_palette')
            for index, ltag in enumerate(self.lside_tag_order):
                self.karyotype_colors[ltag] = '{palette}{index}'.format(index=index, palette=palette)
                if build_links:
                    for rtag in self.rside_tag_order:
                        self.link_colors[(ltag, rtag)] = '{palette}{index}'.format(index=index, palette=palette)
        # Custom dictionary, default to grey for missing entries.
        else:
            # This needs to happen first because it changes the values
            # stored in the color dictionary.
            self.write_custom_colors()

            # Color links by ltag if only karyotype colors are specified.
            if build_links and self.karyotype_colors != {}:
                for ltag in self.lside_tag_order:
                    for rtag in self.rside_tag_order:
                        self.link_colors[(ltag, rtag)] = self.karyotype_colors.get(ltag, 'grey')

        # -----------------------------
        # ----- Verify Tag Orders -----
        # -----------------------------
        if set(self.lside_tag_order) != set(data.lcounts.keys()):
            print "Warning: lside tag order does not match lcount key set."
            print self.lside_tag_order
            print data.lcounts.keys()
            print set(self.lside_tag_order).symmetric_difference(set(data.lcounts.keys()))

        if set(self.rside_tag_order) != set(data.rcounts.keys()):
            print "Warning: rside tag order does not match rcount key set."
            print self.rside_tag_order
            print data.rcounts.keys()
            print set(self.rside_tag_order).symmetric_difference(set(data.rcounts.keys()))

        # Define and format chromosome names.  These are always of the
        # form {r, l}side{0-length}.
        lside_chroms = gen_chromosome_names('l', len(self.data.lcounts))
        rside_chroms = gen_chromosome_names('r', len(self.data.rcounts))
        all_chroms = chain(lside_chroms, rside_chroms)        

        # Settings for circos.conf file template.
        self.circos_conf_settings = \
            {"chromosomes_units"     : 1,
             "chromosomes"           : ';'.join(all_chroms),
             "show_ticks"            : "no",
             "show_tick_labels"      : "no",
             "image_size"            : kwargs.get('image_size', '3000p'),
             "filename"              : kwargs.get('filename', 'circos.png')}

        self.circos_conf_link_settings = \
            {"radius"                : "0.99r", 
             "bezier_radius"         : ".25r", 
             "crest"                 : ".4", 
             "bezier_radius_purity"  : ".8", 
             "show_by_default"       : "yes", 
             "ribbon"                : "yes", 
             "flat"                  : "no", 
             "grey_default"          : kwargs.get("grey_default", 'lgrey')}
        
        # Settings for ideogram_conf file template.
        self.ideogram_conf_settings = \
            {"default_spacing"       : "0.006r", 
             "break"                 : "0.2r", 
             "radius"                : "0.75r"}

    def write_config_files(self):
                
        self.write_circos_conf()
        self.write_ideogram_conf()
        self.write_karyotype_conf()

    def write_custom_colors(self):

        with open('./tmp/customcolors.conf', 'w') as colors:
            if self.use_default_colors:
                return
            
            for index, key in enumerate(self.karyotype_colors.keys()):
                line = "custom{i} = {value}\n".format(i=index,
                                                    value=self.karyotype_colors[key])
                colors.write(line)
                self.karyotype_colors[key] = "custom%s" % index
                

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
        
    # karyotype.conf controls how the outer ring of the circos image
    # is partitioned and colored.  Each line defines an arc with a
    # width, a color, and a tag used to identify the region by other
    # parts of the image configuration.
    def write_karyotype_conf(self):

        with open('./tmp/karyotype.conf', 'w') as karyotype_conf:
            
            line_template = \
                'chr\t-\t{l_or_r}side{index}\t{name}\t{start}\t{end}\t{color}\n'

            # Right side karyotypes.
            for (index, tag) in enumerate(self.rside_tag_order):
                width = self.data.rcounts.get(tag, 0)

                # No data for this tag, move on to the next one.
                if width == 0:
                    print("Warning, no data for rside tag: %s" % tag)
                    continue
                
                color = self.karyotype_colors.get(tag, 'grey')
                karyotype_conf.write(line_template.format(l_or_r='r',
                                                          index=index,
                                                          name=self.rtag_parse(tag), 
                                                          start=0, 
                                                          end=width, 
                                                          color=color
                                                          ))

            # Left side karyotypes.
            for (index, tag) in enumerate(self.lside_tag_order):
                width = self.data.lcounts.get(tag, 0)

                # No data for this tag, move on to the next one.
                if width == 0:
                    print("Warning, no data for rside tag: {tag}.".format(
                            tag=tag
                    ))
                    continue

                color = self.karyotype_colors.get(tag, 'grey')
                karyotype_conf.write(line_template.format(l_or_r='l',
                                                          index=index,
                                                          name=self.ltag_parse(tag), 
                                                          start=0, 
                                                          end=width, 
                                                          color=color
                                                          ))

    # The meat of the work done by this class occurs here.  Writes two
    # lines for each (lvalue, rvalue) pair.  The lines generate a link
    # whose width is given by the count stored in
    # self.data.pair_counts.  

    def write_linkdata(self):
        
        # Make copies of the stored data so we can decrement and check
        # correctness at the end.
        lcounts = deepcopy(self.data.lcounts)
        rcounts = deepcopy(self.data.rcounts)

        with open('./tmp/linkdata.txt') as link_data:
            
            link_id = 0
            line_template = "{hide_link}id{id}\t{name}\t{start}\t{end}\tcolor={color}\n"
            link_data = open('./tmp/linkdata.txt', 'w')

            # For each lside tag, iterate over all rside tags, drawing
            # a ribbon of width given by the number of data entries
            # matching both tags (as stored in self.data.pair_counts).
            for (l_index, l_tag) in enumerate(self.lside_tag_order):
                for (r_index, r_tag) in enumerate(self.rside_tag_order):

                    # We prepend a # symbol to comment out the line if
                    # we don't want to actually show this link.
                    hide_link = '' if self.link_filter(l_tag, r_tag) else '#'

                    ribbon_width = self.data.pair_counts.get((l_tag, r_tag), 0)
                    color = self.link_colors.get((l_tag, r_tag), 'grey')
                    # No data for this pair.
                    if ribbon_width == 0:
                        print "No data for combination %s %s" % (l_tag, r_tag)
                        continue

                    # ------------------------------------

                    # Write the line defining the left-side half of the ribbon.
                    end = lcounts[l_tag]
                    start = end - ribbon_width
                    lside_line = line_template.format(id=link_id, 
                                                      name="lside%d" % l_index, 
                                                      start=start, 
                                                      end=end,
                                                      color=color, 
                                                      hide_link=hide_link)

                    link_data.write(lside_line)
                    # Resize the count of remaining entries for this
                    # left-side tag.
                    lcounts[l_tag] = start
                    
                    # ------------------------------------

                    # Write the line defining the right-side half of the ribbon.
                    end = rcounts[r_tag]
                    start = end - ribbon_width
                    rside_line = line_template.format(id=link_id, 
                                                      name="rside%d" % r_index, 
                                                      start=start, 
                                                      end=end,
                                                      color=color, 
                                                      hide_link=hide_link)
                    link_data.write(rside_line)
                    # Resize the count of remaining entries for this
                    # right-side tag.
                    rcounts[r_tag] = start

                    # ------------------------------------

                    link_id += 1
                    
                # End rside-loop.  We should have processed all
                # entries for this lside tag.
                assert lcounts[l_tag] == 0, l_tag
                print "Finished processing lside tag: {tag}".format(tag=l_tag)
                
            # End lside-loop
            for r_tag, count in rcounts.iteritems():
                assert count == 0, "%r %r" % (r_tag, count)

    def produce_image(self):
        self.write_config_files()
        self.write_linkdata()
        self.run_circos()

    def run_circos(self):

        # If you are on OSX
        if platform.system() == 'Darwin':
            subprocess.call(osx_circos_command)

        # If you are on Windows via Cygwin.
        elif platform.system().startswith('CYGWIN'):
            subprocess.call(cygwin_circos_command)
            
            # If you are Kaison and your computer doesn't know about white.
            if platform.system().endswith('WOW64'):
                print "-----------------------"
                print "Converting .svg to .png"
                print "-----------------------"
                # Cut off the .png or .svg extension.
                filename = self.circos_conf_settings['filename'].replace('.png', '')
                subprocess.call(svg_to_png_command(filename))

def count_single_tag(data, tag):
    tag_values = (entry[tag] for entry in data)
    return Counter(tag_values)

def gen_chromosome_names(l_or_r, count):
    assert(l_or_r in ('l', 'r'))
    for index in xrange(count):
        yield '{l_or_r}side{index}'.format(l_or_r=l_or_r, index=index)


            
