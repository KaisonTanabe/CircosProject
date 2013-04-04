from filters import read_csv, read_filled_csv

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

ordered_majors = [
    'Mathematics',  
    'Computer Science',
    'Physics/Astronomy',
    'Chemistry',
    'Biology',
    'Geosciences',
    'Psychology',
    'Economics',                       
    'Political Studies',
    'History',
    'Culture Studies',
    'Philosophy/Religion',
    'English/Literature',
    'Languages',
    'Art/Music'
    ]

ordered_industries = [
    'Arts/Entertainment',
    'Writing/Communication',
    'Social/Religious Services',
    'Government',
    'Law',
    'Sales',
    'Consulting',
    'Banking/Financial',
    'Insurance/Management',
    'K-12 Education',
    'College Education',
    'Health/Medicine',
    'Engineering/Construction',
    'Technology',
    'Other',
    ]
