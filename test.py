from double_major import *
from csv_to_mongo import *
from csv_to_circos import *

if __name__ == "__main__":

    data = clean_major_fields(read_filled_csv())

    conf = CircosConfig(data, 
                        "Major", 
                        "Industry",
                        filename="test.png",
                        weighted=False)
    conf.colors = {key: 'grey' for key, value in conf.colors.iteritems()}
    import nose.tools; nose.tools.set_trace()
    

    conf.produce_image()
