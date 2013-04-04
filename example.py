from filters import *
from config import *
from projects.williams.double_major import *
from data import ImageData

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

# Same as above, but filtering to only draw Mathematics majors.
def original_image_filtered():
    
    reader = clean_major_fields(read_filled_csv())

    def fil(entry):
        
        if "Mathematics" in entry['Major']:
            return True
        else:
            return False

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

def all_double_majors():

    reader = clean_major_fields(read_filled_csv())

    data = ImageData(reader, 
                     "Major", 
                     "Industry")

    conf = CircosConfig(data, 
                        use_default_colors=False)
                     
    conf.produce_image()

def math_double_majors():

    reader = clean_major_fields(read_filled_csv())

    def fil(entry):
        
        if "Mathematics" in entry['Major']:
            return True
        else:
            return False

    data = ImageData(reader, 
                     "Major", 
                     "Industry", 
                     filter=fil)

    conf = CircosConfig(data, use_default_colors=True)
                        

    conf.produce_image()
