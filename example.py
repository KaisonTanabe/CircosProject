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


def all_double_majors():

    reader = clean_major_fields(read_filled_csv())

    data = ImageData(reader, 
                     "Major", 
                     "Industry")

    conf = CircosConfig(data, 
                        use_default_colors=False)
                     
    conf.produce_image()
