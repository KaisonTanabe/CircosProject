from collections import defaultdict

from filters import *
from config import *
from utils import make_color

from projects.williams.double_major import clean_major_fields, major_to_division
from projects.williams.definitions import(ordered_majors, 
                                          ordered_industries)
from data import ImageData, CMapImageData
from mapping import CategoryMapping
from pprint import pprint as pp

# Uses ordered ltags and rtags, default colors, left subvalues.
def original_image():
    
    reader = clean_major_fields(read_filled_csv())
    data = ImageData(reader, 
                     "Major", 
                     "Industry", 
                     use_subvalues_left=True)

    conf = CircosConfig(data, 
                        use_default_colors=True, 
                        lside_tag_order=ordered_majors,
                        rside_tag_order=ordered_industries)

    conf.produce_image()

# Same as above, but filtering data so that our universe contains only
# math majors.
def filter_data_math():
    
    reader = clean_major_fields(read_filled_csv())

    def data_filter(entry):
        
        if "Mathematics" in entry['Major']:
            return True
        else:
            return False
        
    data = ImageData(reader, 
                     "Major", 
                     "Industry", 
                     use_subvalues_left=True, 
                     filter=data_filter)

    conf = CircosConfig(data, 
                        use_default_colors=True, 
                        lside_tag_order=ordered_majors,
                        rside_tag_order=ordered_industries)
    conf.produce_image()

# Original image with full dataset, but only drawing math major links.
def filter_links_math():

    reader = clean_major_fields(read_filled_csv())

    def link_filter(ltag, rtag):
        return (ltag == 'Mathematics')
        
    data = ImageData(reader, 
                     "Major", 
                     "Industry",
                     use_subvalues_left=True)

    conf = CircosConfig(data, 
                        use_default_colors=True, 
                        lside_tag_order=ordered_majors, 
                        rside_tag_order=ordered_industries, 
                        link_filter=link_filter)
    conf.produce_image()

# Original image with full dataset, only drawing links for a single
# industry.  One for each industry.
def industry_set():
    
    for industry in ordered_industries:

        reader = clean_major_fields(read_filled_csv())

        def link_filter(ltag, rtag):
            return (rtag == industry)
            
        data = ImageData(reader, 
                         "Major", 
                         "Industry", 
                         use_subvalues_left=True)

        conf = CircosConfig(data, 
                            use_default_colors=True, 
                            link_filter=link_filter,
                            lside_tag_order=ordered_majors,
                            rside_tag_order=ordered_industries,
                            filename='industry-%s.png' % industry)
        conf.produce_image()
        print '------- Industry %s finished. -------' % industry

# Treat each double major pair as a unique tag instead of using
# sub-values.
def raw_tags_all():

    reader = clean_major_fields(read_filled_csv())

    data = ImageData(reader, 
                     "Major", 
                     "Industry")

    conf = CircosConfig(data, 
                        use_default_colors=False,
                        image_size='7000p')
                     
    conf.produce_image()

# Treat each double major pair as a unique tag, but restrict the
# dataset to only math majors

def math_double_majors():

    reader = clean_major_fields(read_filled_csv())

    def fix_labels(tup_str):

        tup = eval(tup_str)
        
        if len(tup) == 1:
            return tup[0]
        elif tup[0] == "Mathematics":
            return tup[1]
        else:
            assert tup[1] == "Mathematics"
            return tup[0]

    def fil(entry):
        return ("Mathematics" in entry['Major'])

    data = ImageData(reader, 
                     "Major", 
                     "Industry", 
                     filter=fil)

    conf = CircosConfig(data, 
                        use_default_colors=True, 
                        ltag_parse=fix_labels)

    conf.produce_image()

# Produce a set of images similar to the above, one for each major.
# Note the use of the filename parameter to CircosConfig.
def double_major_set():

    for major in ordered_majors:

        # We use this function to sort the string representations of
        # our major pairs so that they correspond to the original
        # ordered major list.

        def get_other_major_index(tup_str):

            tup = eval(tup_str)

            if len(tup) == 1:
                return ordered_majors.index(major)

            other_major = tup[0] if tup[0] != major else tup[1]
            assert other_major != major
            return ordered_majors.index(other_major)

        def fix_labels(tup_str):

            tup = eval(tup_str)

            if len(tup) == 1:
                return tup[0]
            elif tup[0] == major:
                return tup[1]
            else:
                assert tup[1] == major
                return tup[0]

        reader = clean_major_fields(read_filled_csv())

        def fil(entry):
            return (major in entry['Major'])
            
        data = ImageData(reader, 
                         "Major", 
                         "Industry", 
                         filter=fil)
        
        conf = CircosConfig(data, 
                            use_default_colors=True, 
                            filename='%s-double-majors.png' % major, 
                            lside_tag_order=sorted(data.lcounts.keys(), key=get_other_major_index),
                            rside_tag_order=ordered_industries,
                            ltag_parse=fix_labels)

        conf.produce_image()
        print '------- %s double majors finished. -------' % major

def divisions_to_industries():
    
    reader = clean_major_fields(read_filled_csv())
    reader_mapped = major_to_division(reader)
    
    outer_colors = {'Division 1' : 'default_color12',
                    'Division 2' : 'default_color8',
                    'Division 3' : 'default_color1'}
    data = ImageData(reader_mapped, 
                     "Division", 
                     "Industry", 
                     use_subvalues_left=True)
    conf = CircosConfig(data, 
                        use_default_colors=False,
                        karyotype_colors = outer_colors,
                        rside_tag_order=ordered_industries)
    conf.produce_image()

def majors_to_some_industries():
    
    reader = clean_major_fields(read_filled_csv())

    def fil(entry):
        return (entry['Industry'] in ['College Education', 'Law', 'Health/Medicine'])

    data = ImageData(reader, 
                     "Major", 
                     "Industry",
                     use_subvalues_left=True, 
                     filter=fil)
    conf = CircosConfig(data, 
                        use_default_colors=True,
                        lside_tag_order=ordered_majors,
                        rside_tag_order=ordered_industries)
    conf.produce_image()

def divisions_to_some_industries():

    reader = clean_major_fields(read_filled_csv())
    reader_mapped = major_to_division(reader)
    
    outer_colors = {'Division 1' : 'default_color12',
                    'Division 2' : 'default_color8',
                    'Division 3' : 'default_color1'}

    def fil(entry):
        return (entry['Industry'] in ['College Education', 'Law', 'Health/Medicine'])

    data = ImageData(reader_mapped, 
                     "Division", 
                     "Industry",
                     use_subvalues_left=True, 
                     filter=fil)
    conf = CircosConfig(data, 
                        use_default_colors=False,
                        karyotype_colors = outer_colors,
                        lside_tag_order=['Division 1', 'Division 2', 'Division 3'],
                        rside_tag_order=ordered_industries)
    conf.produce_image()
    
def kenyon_image():
    reader = read_csv("projects/kenyon/kenyon.csv")
    catmap = CategoryMapping("projects/kenyon/major.csv", 
                             "projects/kenyon/industry.csv", 
                             "projects/kenyon/order.csv")
    
    data = CMapImageData(reader, 
                         catmap, 
                         filter=lambda x: x['Industry'] != 'Unlisted',
                         use_subvalues_left=True,
                         use_subvalues_right=True)

    colors = {'History': make_color('EF002A')}

    conf = CircosConfig(data, 
                        use_default_colors=False, 
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)

    conf.produce_image()
                   
if __name__ == "__main__":
    kenyon_image()
    # reader = read_csv("projects/kenyon/kenyon.csv")
    # catmap = CategoryMapping("projects/kenyon/major.csv", 
    #                          "projects/kenyon/industry.csv", 
    #                          "projects/kenyon/order.csv")
    
    # data = CMapImageData(reader, 
    #                      catmap, 
    #                      use_subvalues_left=True,
    #                      use_subvalues_right=True)

    # conf = CircosConfig(data, 
    #                     use_default_colors=True, 
    #                     lside_tag_order=catmap.left_order, 
    #                     rside_tag_order=catmap.right_order)

   #conf.produce_image()
