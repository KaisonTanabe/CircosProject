from definitions import majors
from csv_to_mongo import read_csv, filter_by_string, read_filled_csv
from collections import defaultdict

def math_double_major(input_filename, output_dirname):

    major_counter = defaultdict(int)
    industry_counter = defaultdict(int)

    reader = read_filled_csv(input_filename)
    filtered_reader = filter_by_string(reader, "Mathematics")

    for index, entry in enumerate(filtered_reader):
        pass
        
def count_double_majors(base_major = "Mathematics"):
    print "###############"
    print "Starting %s:" % base_major
    print "###############"

    major_counter = defaultdict(int)

    filtered_reader = filter_by_string(read_filled_csv(), base_major)
    
    for entry in filtered_reader:
        for major in (entry['Major1'], entry['Major2'], entry['Major3']):
            major_counter[major] += 1

    for key, value in major_counter.iteritems():
        if key != '':
            print "%s: %d" % (key, value)

    print "###############"
    print "Finished %s:" % base_major
    print "###############"
            

if __name__ == "__main__":
    
    for major in majors:
        count_double_majors(major)
