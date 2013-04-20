import os
from itertools import combinations

student_csv = 'projects/williams/majors.csv'

# Map from industry categories to keywords to fuzzy match.
industry_map = \
    {'Arts/Entertainment'               : [
        'Art',
        'Film'
        'Musician', 
        'Painter',
        'Graphic',
        'Acting',
        'Architect',
        'Art History',
        'Museum/Gallery',
        'Sculptor',
        'Dancing',
        'Choreograph',
        'Design',
        'Film', 
        'Television', 
        'Radio'
        ],
     'Writing/Communication'            : [
        'Writ',
        'Media',
        'Author',
        'Communications',
        'Publish',
        'Reporter',
        'News', 
        'Documentary',
        'Columnist'
        ],
     'Social/Religious Services'        : [
        'Priest', 
        'Nun',
        'Bishop',
        'Divinity',
        'Social',
        'Relig',
        'Charit',
        'Environmental',
        'Forestry',
        'Conservation'
        'Library',
        'Philanthrop', 
        'Foundations',
        ],
     'Government'                       : [
        'Senat',
        'Elected',
        'Civil',
        'State',
        'Representative',
        'Policy',
        'Utility',
        'Transportation',
        'Govern',
        'Homeland',
        'Ambassador',
        'Military',
        'Law Enforcement',
        'Foreign Service'
        ],
     'Law'                              : [
        'Law',
        'Legal',
        'Court',
        'Attorney',
        ],
     'Sales'                            : [
        'Sales',
        'Advertising',
        'Marketing',
        'Real Estate',
        'Retail',
        'Wholesale',
        'Travel',
        'Public Relations',
        'Hospitality',
        'Food Service'
        ],
     'Consulting'                       : [
        'Consult',
        ],
     'Banking/Financial'                : [
        'Financ',
        'Bank',
        'Capital',
        'Invest', 
        'Hedge',
        'Fund'
        'Analyst', 
        'High Yield',
        'Wealth', 
        'Retirement'],
     'Insurance/Management'             : [
        'Manag',
        'Insur',
        'Accounting',
        'Auditing',
        'Bookeeping',
        'Professional Organization',
        'Portfolio', 
        'Actuary',
        'Business Administration',
        'Clerk', 
        'Administrative Assistant', 
        'Hotel', 
        'Resort'
        ],
     'K-12 Education'                   : [
        'Teach',
        'Kindergarten',
        'Grade',
        'Educ',
        'Pre-school',
        'Head of School',
        'Educator'
        ],
     'College Education'                : [
        'College',
        'Universal',
        'Professor', 
        'Economist', 
        'Mathematic', 
        'Education Administrator', 
        'Education - College/University'
        ],
     'Health/Medicine'                  : [
        'Health',
        'Dental',
        'Massage',
        'Therap',
        'Medic',
        'Doctor',
        'Nurse', 
        'Hospital',
        'Physician',
        'Psychiatrist', 
        'Optometrist', 
        'Dentist', 
        'Urologist', 
        'Obstetrician',
        'Oncologist', 
        'Neurologist',
        'Surgeon', 
        'Cardiologist', 
        'Nephrologist', 
        'Rheumatistologist', 
        'Endocrinologist', 
        'Gastrologist', 
        'Cardiologist', 
        ],
     'Engineering/Construction'         : [
        'Engin',
        'Contractor'
        'Construct',
        'Manufactur',
        'Mining',
        'Oil',
        'Natural Gas',
        'Energy',
        'Agriculture',
        ],
     'Technology'                       : [
        'Tech',
        'Comput', 
        'Information'
        ],
     'Other'                            : [
        'Farm',
        'Geo', 
        'Entrepreneur', 
        'Homemaker'
        ],
     }

major_map = {
    'History'                           : [
        'History',
        'History of Ideas',
        'Ideologies',
        'American History',
        'American History & Literature',
        'American Civilization',
        'Music History', 
        'English History', 
        'Social Studies', 
        'European History',
        'African History'
        ],
    'Culture Studies'                   : [
        'Anthropology',
        'Urban Studies',
        'Sociology',
        'Asian Studies',
        'American Studies',
        'Arab Studies',
        'Latin American Studies',
        "Women's and Gender Studies",
        "Women's Studies", 
        "Afro-American Studies", 
        'East Asia/Japan', 
        'African Education', 
        'Latin America Studies',
        ],
    'Art/Music'                         : [
        'Architecture',
        'Art',
        'Art History', # Maybe should be in history?
        'Design',
        'Fine Arts', 
        'Studio Art',
        'Music',
        'Theatre',
        'Landscape'
        ],
    'Physics/Astronomy'                 : [
        'Physics',
        'Astronomy',
        'Physics and Astronomy',
        'Astronomy and Physics',
        'Astrophysics',
        'Electrical Engineering'
        ],
    'Geosciences'                       : [
        "Geology",
        "Geology & Mineralogy",
        "Geosciences",
        "Natural Resources",
        "Environmental Studies",
        ],
    'Biology'                          : [
        "Biology",
        "Neuroscience",
        ],
    'Chemistry'                        : [
        "Chemistry",
        "Organic Chemistry",
        "Physical Chemistry",
        "Biochemistry",
        'Biogeochemistry'
        ],
    'Languages'                        : [
        "French",
        "Spanish",
        "French Literature",
        "German",
        "Russian",
        "Russian Area Studies",
        "Chinese",
        "Japanese",
        "Linguistics", 
        'Greek'
        ],
    'Computer Science'                 : [
        'Computer Science'
        ],
    'Economics'                        : [
        'Economics', 
        'Business'
        ],
    'English/Literature'               : [
        "English",
        "English Literature",
        "Comparative Literature",
        "Literary Studies",
        "Classics",
        "Latin", 
        'Chinese Literature',
        'German Literature'
        ],
    'Political Studies'                : [
        "Political Economy",
        "Political Philosophy",
        "Political Science",
        "International Relations",
        "Environmental Policy"
        ],
    'Mathematics'                      : [
        'Mathematic Sciences',
        'Mathematics', 
        'Statistics'
        ],
    'Philosophy/Religion'              : [
        'Philosophy',
        'Religion',
        'Theology'
        ],
    'Psychology'                       : [
        'Psychology', 
        'Clinical Psychology'
        ]
    }

division_map = {
    "Division 1": ["Art/Music", 
                   "Languages", 
                   "English/Literature"], 
    
    "Division 2": ["Philosophy/Religion", 
                   "Culture Studies", 
                   "History", 
                   "Political Studies", 
                   "Economics", 
                   "Psychology"],
    "Division 3": ["Geosciences", 
                   "Biology", 
                   "Chemistry", 
                   "Physics/Astronomy", 
                   "Computer Science", 
                   "Mathematics"]
    }

majors = major_map.keys()

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
