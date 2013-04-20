from filters import read_csv, read_filled_csv
from definitions import division_map

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

def get_division(major):
    
    for div, major_list in division_map.iteritems():
        if major in major_list:
            return div

    assert False, "Couldn't map major (%s)" % major
    

def major_to_division(student_gen):
    
    for entry in student_gen:
        entry["Division"] = tuple(map(get_division, entry["Major"]))
        yield entry
        
            
            
        
