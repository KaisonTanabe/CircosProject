from csv_to_mongo import read_csv, read_filled_csv

# Copy from the input csv and map the Major1, Major2, Major3
# values to a single useful field.
def clean_major_fields(student_gen):
    
    for entry in student_gen:

        majors = {entry['Major1'], entry['Major2'], entry['Major3']}
        majors.discard('')

        # Skipping triple majors for now.
        if len(majors) > 2:
            continue

        else:
            entry['Major'] = tuple(sorted(majors))
            yield entry

def double_major_image(base_major = "Mathematics"):
    
    students = clean_major_fields(read_filled_csv())

    major_pairs, industries, combinations = count_tags('Major', 'Industry')

    write_circos_config(major_pairs, industries)
    link_id = 0
    
    line_template = "id{id} {name} {start} {end} color=c{colornum}\n"

    link_data = open('./tmp/linkdata.txt', 'w')

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
                                                     colornum=major_count + 1
                                                     ))
            
            # Reduce the number of remaining majors in this major pair
            # for the next iteration.
            industries[industry] = industry_start

        assert major_pairs[pair] == 0, "major pair count should be zero"
        print "Finished pair %s %s" % pair
        
    for count in industries.itervalues():
        assert count == 0, "industry pair count should be zero"
    link_data.close()
    run_circos()

ordered_majors = [
    'Mathematics',  
    #####
    'Computer Science',
    'Physics/Astronomy',
    'Chemistry',
    'Biology',
    'Geosciences',
    'Psychology',
    'Economics',                       
    #####
    'Political Studies',
    'History',
    #####
    'Culture Studies',
    'Philosophy/Religion',
    'English/Literature',
    'Languages',
    'Art/Music'
    ]

ordered_industries = [
    'Arts/Entertainment',
    'Writing/Communication',
    #####
    'Social/Religious Services',
    'Government',
    'Law',
    'Sales',
    'Consulting',
    'Banking/Financial',
    'Insurance/Management',
    #####
    'K-12 Education',
    #####
    'College Education',
    'Health/Medicine',
    'Engineering/Construction',
    'Technology',
    'Other',
    ]
