import os
import shutil

from collections import defaultdict

from filters import *
from config import *
from utils import make_color

from projects.williams.double_major import (clean_major_fields, 
                                            major_to_division)
from projects.williams.definitions import(ordered_majors, 
                                          ordered_industries)
from data import ImageData, CMapImageData
from mapping import CategoryMapping, color_dict_from_field
from pprint import pprint as pp

def original_image():
    reader = read_csv("projects/kenyon4.24.14/kenyonn.csv")
    catmap = CategoryMapping("projects/kenyon4.24.14/major.csv", 
                             "projects/kenyon4.24.14/industry.csv", 
                             "projects/kenyon4.24.14/order.csv")
    
    data = CMapImageData(reader, 
                         catmap)

    conf = CircosConfig(data, 
                        use_default_colors=True, 
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)
    conf.produce_image()

# Draw the standard image using a custom color dictionary.
# Unspecified colors will default to lgrey.
def highlight_image():
    
    reader = read_csv("projects/kenyon/salary.csv")
    catmap = CategoryMapping("projects/kenyon/major.csv", 
                             "projects/kenyon/industry.csv", 
                             "projects/kenyon/order.csv")
    data = CMapImageData(reader, 
                         catmap)
    colors = {'History': make_color('FFDA70'),
              'Mathematics': make_color('0048B9')}
    conf = CircosConfig(data, 
                        karyotype_colors = colors, # Use our explicit color dict.
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)
    conf.produce_image()

# Draw the standard image using a custom color and changing the
# default value for the unspecified colors.
def highlight_image_change_default_grey():
    
    reader = read_csv("projects/kenyon/kenyon-salary.csv")
    catmap = CategoryMapping("projects/kenyon/major.csv", 
                             "projects/kenyon/industry.csv", 
                             "projects/kenyon/order.csv")
    
    data = CMapImageData(reader, 
                         catmap)
    colors = {'History': make_color('FFDA70')}
    conf = CircosConfig(data, 
                        karyotype_colors = colors, # Use our explicit color dict.
                        grey_default='red', # Override default value for undefined colors.
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)
    conf.produce_image()

# Filter data to only compute with math majors.
def filter_data_math():

    reader = read_csv("projects/salary/salary.csv")
    catmap = CategoryMapping("projects/salary/major.csv", 
                             "projects/salary/industry.csv", 
                             "projects/salary/order.csv")

    def data_filter(entry):
        return ("Mathematics" in entry['Major'])
    
    data = CMapImageData(reader, 
                         catmap,
                         filter=data_filter)
    conf = CircosConfig(data, 
                        use_default_colors=True, 
                        lside_tag_order="Mathematics", 
                        rside_tag_order=catmap.right_order)
    conf.produce_image()

# Original image with full dataset, but only drawing math major links.
# Original image with full dataset, but only drawing math major links.
def filter_links_math():

    reader = read_csv("projects/salary/salary.csv")
    catmap = CategoryMapping("projects/salary/major.csv", 
                             "projects/salary/industry.csv", 
                             "projects/salary/order.csv")
    def only_math(ltag, rtag):
        return (ltag == "Mathematics")
		
    data = CMapImageData(reader, 
                         catmap)
						 
    conf = CircosConfig(data, 
                        use_default_colors=True, 
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order,
                        link_filter=only_math)
    conf.produce_image()
	
def filter_salary2_math():

    reader = read_csv("projects/salary2/salary2.csv")
    catmap = CategoryMapping("projects/salary2/major.csv", 
                             "projects/salary2/industry.csv", 
                             "projects/salary2/order.csv")
    def only_math(ltag, rtag):
        return (ltag == "Math-l")
		
    data = CMapImageData(reader, 
                         catmap)
						 
    conf = CircosConfig(data, 
                        color_palette="salaryy", 
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order,
                        link_filter=only_math)
    conf.produce_image()


# Original image with full dataset, only drawing links for a single
# industry.  One for each industry.
def industry_set(data_filename, major_filename, industry_filename, order_filename):

    category_mapping = CategoryMapping(major_filename, 
                                       industry_filename, 
                                       order_filename)

    dirname = data_filename.replace('.csv', '')+"-Industries"
    try:
        os.mkdir(dirname)
    except OSError:
        print "Overwriting directory: %s" % dirname
        shutil.rmtree(dirname)
        os.mkdir(dirname)
    
    for industry in category_mapping.right_order:

        reader = read_csv(data_filename)

        def link_filter(ltag, rtag):
            return (rtag == industry)

        data = CMapImageData(reader, 
                             category_mapping)

        imagename=('%s' % industry).replace('/', '-')
        conf = CircosConfig(data, 
                            use_default_colors=True, 
                            link_filter=link_filter,
                            lside_tag_order=category_mapping.left_order,
                            rside_tag_order=category_mapping.right_order,
                            filename=imagename+'.png')
        conf.produce_image()
        print '------- Industry %s finished. -------' % industry
        shutil.move(imagename+'.png', dirname)
        os.remove(imagename+'.svg')
		
# Original image with full dataset, only drawing links for a single
# industry.  One for each industry.
def uva_industry_set():

    category_mapping = CategoryMapping("projects/uva/majornew.csv", 
                                       "projects/uva/industrynew.csv", 
                                       "projects/uva/ordernew.csv")

    dirname = "projects/uva/uva.csv".replace('.csv', '')+"-Industries"
	
    try:
        os.mkdir(dirname)
    except OSError:
        print "Overwriting directory: %s" % dirname
        shutil.rmtree(dirname)
        os.mkdir(dirname)
    
    for industry in category_mapping.right_order:

        reader = read_csv("projects/uva/uva.csv")

        def link_filter(ltag, rtag):
            return (rtag == industry)

        data = CMapImageData(reader, 
                             category_mapping)

        imagename=('%s' % industry).replace('/', '-')
        conf = CircosConfig(data, 
                            color_palette="uva", 
                            link_filter=link_filter,
                            lside_tag_order=category_mapping.left_order,
                            rside_tag_order=category_mapping.right_order,
                            filename=imagename+'.png')
        conf.produce_image()
        print '------- Industry %s finished. -------' % industry
        shutil.move(imagename+'.png', dirname)
        os.remove(imagename+'.svg')

# Original image with full dataset, only drawing links for a single
# industry.  One for each industry.
def kenyon_industry_set():

    category_mapping = CategoryMapping("projects/kenyon4.24.14/major.csv", 
                                       "projects/kenyon4.24.14/industry.csv", 
                                       "projects/kenyon4.24.14/order.csv")

    dirname = "projects/kenyon4.24.14/kenyonn.csv".replace('.csv', '')+"-Industries"
	
    try:
        os.mkdir(dirname)
    except OSError:
        print "Overwriting directory: %s" % dirname
        shutil.rmtree(dirname)
        os.mkdir(dirname)
    
    for industry in category_mapping.right_order:

        reader = read_csv("projects/kenyon4.24.14/kenyonn.csv")

        def link_filter(ltag, rtag):
            return (rtag == industry)

        data = CMapImageData(reader, 
                             category_mapping)

        imagename=('%s' % industry).replace('/', '-')
        conf = CircosConfig(data, 
                            color_palette="kenyon", 
                            link_filter=link_filter,
                            lside_tag_order=category_mapping.left_order,
                            rside_tag_order=category_mapping.right_order,
                            filename=imagename+'.png')
        conf.produce_image()
        print '------- Industry %s finished. -------' % industry
        shutil.move(imagename+'.png', dirname)
        os.remove(imagename+'.svg')
		
# Original image with full dataset, only drawing links for a single
# major.  One for each major.
def kenyon_major_set():

    category_mapping = CategoryMapping("projects/kenyon4.24.14/major.csv", 
                                       "projects/kenyon4.24.14/industry.csv", 
                                       "projects/kenyon4.24.14/order.csv")

    dirname = "projects/kenyon4.24.14/kenyonn.csv".replace('.csv', '')+"-Majors"
	
    try:
        os.mkdir(dirname)
    except OSError:
        print "Overwriting directory: %s" % dirname
        shutil.rmtree(dirname)
        os.mkdir(dirname)
    
    for major in category_mapping.left_order:

        reader = read_csv("projects/kenyon4.24.14/kenyonn.csv")

        def link_filter(ltag, rtag):
            return (ltag == major)

        data = CMapImageData(reader, 
                             category_mapping)

        imagename=('%s' % major).replace('/', '-')
        conf = CircosConfig(data, 
                            color_palette="kenyon", 
                            link_filter=link_filter,
                            lside_tag_order=category_mapping.left_order,
                            rside_tag_order=category_mapping.right_order,
                            filename=imagename+'.png')
        conf.produce_image()
        print '------- Major %s finished. -------' % major
        shutil.move(imagename+'.png', dirname)
        os.remove(imagename+'.svg')	
		
# Original image with full dataset, only drawing links for a single
# major.  One for each major.
def major_set(data_filename, major_filename, industry_filename, order_filename):

    category_mapping = CategoryMapping(major_filename, 
                                       industry_filename, 
                                       order_filename)
    
    dirname = data_filename.replace('.csv', '')+"-Majors"

    try:
        os.mkdir(dirname)
    except OSError:
        print "Overwriting directory: %s" % dirname
        shutil.rmtree(dirname)
        os.mkdir(dirname)

    for major in category_mapping.left_order:

        reader = read_csv(data_filename)

        def link_filter(ltag, rtag):
            return (ltag == major)

        data = CMapImageData(reader, 
                             category_mapping)

        imagename=('%s' % major).replace('/', '-')
        conf = CircosConfig(data, 
                            use_default_colors=True, 
                            link_filter=link_filter,
                            lside_tag_order=category_mapping.left_order,
                            rside_tag_order=category_mapping.right_order,
                            filename=imagename+'.png')
        conf.produce_image()
        print '------- Major %s finished. -------' % major
        shutil.move(imagename+'.png', dirname)
        os.remove(imagename+'.svg')


# Original image with full dataset, only drawing links for a single
# major.  One for each major.
def uva_major_set():

    category_mapping = CategoryMapping("projects/uva/majornew.csv", 
                             "projects/uva/industrynew.csv", 
                             "projects/uva/ordernew.csv")
    
    dirname = "projects/uva/uva.csv".replace('.csv', '')+"-Majors"

    try:
        os.mkdir(dirname)
    except OSError:
        print "Overwriting directory: %s" % dirname
        shutil.rmtree(dirname)
        os.mkdir(dirname)

    for major in category_mapping.left_order:

        reader = read_csv("projects/uva/uva.csv")

        def link_filter(ltag, rtag):
            return (ltag == major)

        data = CMapImageData(reader, 
                             category_mapping)

        imagename=('%s' % major).replace('/', '-')
        conf = CircosConfig(data, 
                            color_palette="uva", 
                            link_filter=link_filter,
                            lside_tag_order=category_mapping.left_order,
                            rside_tag_order=category_mapping.right_order,
                            filename=imagename+'.png')
        conf.produce_image()
        print '------- Major %s finished. -------' % major
        shutil.move(imagename+'.png', dirname)
        os.remove(imagename+'.svg')
   		
def kenyon_alternate_palette():
    reader = read_csv("projects/kenyon4.24.14/kenyonn.csv")
    catmap = CategoryMapping("projects/kenyon4.24.14/major.csv", 
                             "projects/kenyon4.24.14/industry.csv", 
                             "projects/kenyon4.24.14/order.csv")
    
    data = CMapImageData(reader, 
                         catmap)

    conf = CircosConfig(data, 
                        color_palette="kenyon",
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)

    conf.produce_image()
	   

def bilal():
    reader = read_csv("projects/bilal/bilal.csv")
    catmap = CategoryMapping("projects/bilal/major.csv", 
                             "projects/bilal/industry.csv", 
                             "projects/bilal/order.csv")
    
    data = CMapImageData(reader, 
                         catmap)

    conf = CircosConfig(data, 
                        color_palette="bilal",
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)

    conf.produce_image()
def bilal_major_set():

    category_mapping = CategoryMapping("projects/bilal/major.csv", 
                             "projects/bilal/industry.csv", 
                             "projects/bilal/order.csv")
    
    dirname = "projects/bilal/bilal.csv".replace('.csv', '')+"-Majors"

    try:
        os.mkdir(dirname)
    except OSError:
        print "Overwriting directory: %s" % dirname
        shutil.rmtree(dirname)
        os.mkdir(dirname)

    for major in category_mapping.left_order:

        reader = read_csv("projects/bilal/bilal.csv")

        def link_filter(ltag, rtag):
            return (ltag == major)

        data = CMapImageData(reader, 
                             category_mapping)

        imagename=('%s' % major).replace('/', '-')
        conf = CircosConfig(data, 
                            color_palette="bilal", 
                            link_filter=link_filter,
                            lside_tag_order=category_mapping.left_order,
                            rside_tag_order=category_mapping.right_order,
                            filename=imagename+'.png')
        conf.produce_image()
        print '------- Major %s finished. -------' % major
        shutil.move(imagename+'.png', dirname)
        os.remove(imagename+'.svg')
def kenyon_transparent():
    reader = read_csv("projects/kenyon/kenyon.csv")
    catmap = CategoryMapping("projects/kenyon/major.csv", 
                             "projects/kenyon/industry.csv", 
                             "projects/kenyon/order.csv")
    
    data = CMapImageData(reader, 
                         catmap)

    conf = CircosConfig(data, 
                        use_default_colors='True', 
                        transparency_level=4,
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)
    conf.produce_image()

def color_by_salary():
    reader = read_csv("projects/salary/salary.csv")
    catmap = CategoryMapping("projects/salary/major.csv", 
                             "projects/salary/industry.csv", 
                             "projects/salary/order.csv")
	
    data = CMapImageData(reader, 
                         catmap)
    colors = color_dict_from_field(data, 
                                   'Major', 
                                   'Industry', 
                                   'Salary', 
                                   ['vvlgrey', 'grey', 'vvdgrey'],
                                   verbose=True)
								  
    def salary_filter(color):
        return (color == 'grey')
		
    conf = CircosConfig(data, 
                        salary_filter=salary_filter,
                        use_default_colors=True,
                        link_colors=colors,
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)

    conf.produce_image()
	
def color_by_salary3():
    reader = read_csv("projects/salary2/salary3.csv")
    catmap = CategoryMapping("projects/salary2/major.csv", 
                             "projects/salary2/industry.csv", 
                             "projects/salary2/order.csv")
	
    data = CMapImageData(reader, 
                         catmap)
    colors = color_dict_from_field(data, 
                                   'Major', 
                                   'Industry', 
                                   'salary', 
                                   ['vvdgrey', 'grey', 'vvlgrey'],
                                   verbose=True)

		
    conf = CircosConfig(data, 
                        use_default_colors=True,
                        link_colors=colors,
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)

    conf.produce_image()
	
def color_by_salary_majors():

    category_mapping = CategoryMapping("projects/salary/major.csv", 
                             "projects/salary/industry.csv", 
                             "projects/salary/order.csv")
    
    dirname = "projects/salary/salary.csv".replace('.csv', '')+"-Majors"

    try:
        os.mkdir(dirname)
    except OSError:
        print "Overwriting directory: %s" % dirname
        shutil.rmtree(dirname)
        os.mkdir(dirname)

    for major in category_mapping.left_order:

        reader = read_csv("projects/salary/salary.csv")

        def link_filter(ltag, rtag):
            return (ltag == major)

        data = CMapImageData(reader, 
                             category_mapping)
	colors = color_dict_from_field(data,
									'Major', 
                                   'Industry', 
                                   'Salary', 
                                   ['red', 'yellow', 'green'],
                                   verbose=True)					 
							 
        imagename=('%s' % major).replace('/', '-')
        conf = CircosConfig(data, 
                            use_default_colors=True,
							link_colors=colors,
                            link_filter=link_filter,
                            lside_tag_order=category_mapping.left_order,
                            rside_tag_order=category_mapping.right_order,
                            filename=imagename+'.png')
        conf.produce_image()
        print '------- Major %s finished. -------' % major
        shutil.move(imagename+'.png', dirname)
        os.remove(imagename+'.svg')

def color_by_salary_industries():

    category_mapping = CategoryMapping("projects/salary/major.csv", 
                             "projects/salary/industry.csv", 
                             "projects/salary/order.csv")
    
    dirname = "projects/salary/salary.csv".replace('.csv', '')+"-Industries"

    try:
        os.mkdir(dirname)
    except OSError:
        print "Overwriting directory: %s" % dirname
        shutil.rmtree(dirname)
        os.mkdir(dirname)

    for industry in category_mapping.right_order:

        reader = read_csv("projects/salary/salary.csv")

        def link_filter(ltag, rtag):
            return (rtag == industry)

        data = CMapImageData(reader, 
                             category_mapping)
	colors = color_dict_from_field(data,
									'Major', 
                                   'Industry', 
                                   'Salary', 
                                   ['red', 'yellow', 'green'],
                                   verbose=True)					 
							 
        imagename=('%s' % industry).replace('/', '-')
        conf = CircosConfig(data, 
                            use_default_colors=True,
							link_colors=colors,
                            link_filter=link_filter,
                            lside_tag_order=category_mapping.left_order,
                            rside_tag_order=category_mapping.right_order,
                            filename=imagename+'.png')
        conf.produce_image()
        print '------- Industries %s finished. -------' % industry
        shutil.move(imagename+'.png', dirname)
        os.remove(imagename+'.svg')
		
def color_by_salary_explicit_cutoffs():
    reader = read_csv("projects/kenyon/kenyon-salary.csv")
    catmap = CategoryMapping("projects/kenyon/major.csv", 
                             "projects/kenyon/industry.csv", 
                             "projects/kenyon/order.csv")
    
    data = CMapImageData(reader, 
                         catmap)
    colors = color_dict_from_field(data, 
                                   'Major', 
                                   'Industry', 
                                   'Salary', 
                                   ['dred', 'red', 'orange', 'yellow', 'lblue', 'vdgreen', 'green', 'vlgreen'],
                                   cutoff_list=[100000,200000,300000,400000,500000,600000,700000])
    conf = CircosConfig(data, 
                        use_default_colors=True,
                        link_colors=colors,
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)

    conf.produce_image()

# # Treat each double major pair as a unique tag instead of using
# # sub-values.
# # Deprecated
# def raw_tags_all():

#     reader = clean_major_fields(read_filled_csv())

#     data = ImageData(reader, 
#                      "Major", 
#                      "Industry")

#     conf = CircosConfig(data, 
#                         use_default_colors=False,
#                         image_size='7000p')
                     
#     conf.produce_image()

# # Treat each double major pair as a unique tag, but restrict the
# # dataset to only math majors
# # Deprecated
# def math_double_majors():

#     reader = clean_major_fields(read_filled_csv())

#     def fix_labels(tup_str):

#         tup = eval(tup_str)
        
#         if len(tup) == 1:
#             return tup[0]
#         elif tup[0] == "Mathematics":
#             return tup[1]
#         else:
#             assert tup[1] == "Mathematics"
#             return tup[0]

#     def fil(entry):
#         return ("Mathematics" in entry['Major'])

#     data = ImageData(reader, 
#                      "Major", 
#                      "Industry", 
#                      filter=fil)

#     conf = CircosConfig(data, 
#                         use_default_colors=True, 
#                         ltag_parse=fix_labels)

#     conf.produce_image()

# # Produce a set of images similar to the above, one for each major.
# # Note the use of the filename parameter to CircosConfig.
# # Deprecated
def double_major_set():
    
    for major in ordered_majors:
        
        #         # We use this function to sort the string representations of
        #         # our major pairs so that they correspond to the original
        #         # ordered major list.
        
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

def uva():
    reader = read_csv("projects/uva/uva.csv")
    catmap = CategoryMapping("projects/uva/majornew.csv", 
                             "projects/uva/industrynew.csv", 
                             "projects/uva/ordernew.csv")
    
    data = CMapImageData(reader, 
                         catmap)

    conf = CircosConfig(data, 
                        color_palette="uva",
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order)

    conf.produce_image()

def uva_self_mapping():
    reader = read_csv("projects/uva/uva.csv")
    catmap = CategoryMapping("projects/uva/majornew.csv", 
                             "projects/uva/industrynew.csv", 
                             "projects/uva/ordernew-self.csv")
    
    data = CMapImageData(reader, 
                         catmap, False, False, True)

    conf = CircosConfig(data, 
                        color_palette="uva",
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order,
                        use_self_map=True)

    conf.produce_image()

def test_self_mapping():
    reader = read_csv("projects/self_map/self_map.csv")
    catmap = CategoryMapping("projects/self_map/major.csv", 
                             "projects/self_map/industry.csv", 
                             "projects/self_map/order.csv")
    
    data = CMapImageData(reader, 
                         catmap, False, False, True)

    conf = CircosConfig(data, 
                        color_palette="self_map_test",
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order,
                        use_self_map=True)

    conf.produce_image()

def williams_major_self_mapping():
    #reader = read_csv("projects/williams_double_major/williams_self_map.csv")
    reader = read_csv("projects/williams_double_major/williams_double_only.csv")
    catmap = CategoryMapping("projects/williams_double_major/major.csv", 
                             "projects/williams_double_major/industry.csv", 
                             "projects/williams_double_major/order.csv")
    
    data = CMapImageData(reader, 
                         catmap, False, False, True)

    conf = CircosConfig(data, 
                        color_palette="williams_double_major",
                        lside_tag_order=catmap.left_order, 
                        rside_tag_order=catmap.right_order,
                        use_self_map=True)

    conf.produce_image()

                # # Deprecated
# def majors_to_some_industries():
                    
#     reader = clean_major_fields(read_filled_csv())

#     def fil(entry):
#         return (entry['Industry'] in ['College Education', 'Law', 'Health/Medicine'])

#     data = ImageData(reader, 
#                      "Major", 
#                      "Industry",
#                      use_subvalues_left=True, 
#                      filter=fil)
#     conf = CircosConfig(data, 
#                         use_default_colors=True,
#                         lside_tag_order=ordered_majors,
#                         rside_tag_order=ordered_industries)
#     conf.produce_image()

# # Deprecated
# def divisions_to_some_industries():

#     reader = clean_major_fields(read_filled_csv())
#     reader_mapped = major_to_division(reader)
    
#     outer_colors = {'Division 1' : 'default_color12',
#                     'Division 2' : 'default_color8',
#                     'Division 3' : 'default_color1'}

#     def fil(entry):
#         return (entry['Industry'] in ['College Education', 'Law', 'Health/Medicine'])

#     data = ImageData(reader_mapped, 
#                      "Division", 
#                      "Industry",
#                      use_subvalues_left=True, 
#                      filter=fil)
#     conf = CircosConfig(data, 
#                         use_default_colors=False,
#                         karyotype_colors = outer_colors,
#                         lside_tag_order=['Division 1', 'Division 2', 'Division 3'],
#                         rside_tag_order=ordered_industries)
#     conf.produce_image()

    
if __name__ == "__main__":

    reader = read_csv("projects/kenyon/kenyon-salary.csv")
    catmap = CategoryMapping("projects/kenyon/major.csv", 
                             "projects/kenyon/industry.csv", 
                             "projects/kenyon/order.csv")
    
    # data = CMapImageData(reader, 
    #                      catmap)
    # colors = color_dict_from_field(data, 
    #                                'Major', 
    #                                'Industry', 
    #                                'Salary', 
    #                                ['default_color1', 'default_color6', 'purple', 'blue', 'green'])
    # conf = CircosConfig(data, 
    #                     use_default_colors=True,
    #                     link_colors=colors,
    #                     lside_tag_order=catmap.left_order, 
    #                     rside_tag_order=catmap.right_order)
    # conf.produce_image()

#uva()
#uva_self_mapping()
#highlight_image()
#test_self_mapping()
williams_major_self_mapping()