from csv_to_mongo import read_csv, filter_by_string
from collections import defaultdict

def math_double_major(input_filename, output_dirname):

    major_counter = defaultdict(int)
    industry_counter = defaultdict(int)

    reader = read_filled_csv(input_filename)
    filtered_reader = filter_by_string(reader, "Mathematics")

    for index, entry in enumerate(filtered_reader):
        
        
        
        
        
        
        
        
        


