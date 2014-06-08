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
	
colors = color_dict_from_field(data, 
                                   'Major', 
                                   'Industry', 
                                   'Salary', 
                                   ['red', 'yellow', 'green'],
                                   verbose=True)

    for major in category_mapping.left_order:

        reader = read_csv("projects/uva/uva.csv")

        def link_filter(ltag, rtag):
            return (ltag == major)

        data = CMapImageData(reader, 
                             category_mapping)

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