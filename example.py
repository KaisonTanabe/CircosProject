from filters import *
from config import *
from projects.williams.double_major import *
from data import ImageData

if __name__ == "__main__":
    
    reader = clean_major_fields(read_filled_csv())
    data = ImageData(reader, "Major", "Industry", use_subvalues_left=True)

    conf = CircosConfig(data, use_default_colors=True)
    conf.produce_image()
