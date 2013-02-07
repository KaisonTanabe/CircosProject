from double_major import *
from csv_to_circos import *
from pprint import pprint as pp

if __name__ == "__main__":
    
    yearly_totals = count_single_tag(clean_major_fields(read_filled_csv()), 'Class')
    interval_starts = range(1960, 2006, 5)
    filename_template = '{start}-{end}--Count-{total}.png'

    for start in interval_starts:
        end = start + 4
        interval_years = range(start, end+1)
        total = sum([yearly_totals[str(year)] for year in interval_years])

        r = clean_major_fields(read_filled_csv())
        
        # Filter for entries with years between start and end (inclusive).
        fil = lambda entry: int(entry['Class']) >= start \
            and int(entry['Class']) <= end

        filename = filename_template.format(start=start, 
                                        end=end, 
                                        total=total)
        conf = CircosConfig(r, 
                            'Major', 
                            'Industry',
                            lside_tag_order=ordered_majors,
                            rside_tag_order=ordered_industries,
                            weighted=True, 
                            filter=fil, 
                            filename=filename)
        conf.produce_image()
        subprocess.call('open {filename}'.format(filename=filename).split())

    fil = lambda entry: int(entry['Class']) < 1960
    total = sum([yearly_totals.get(str(year), 0) for year in xrange(1930, 1960)])

    filename = filename_template.format(start="~1930", 
                                        end="1959", 
                                        total=total)

    r = clean_major_fields(read_filled_csv())
    conf = CircosConfig(r, 
                        'Major', 
                        'Industry',
                        lside_tag_order=ordered_majors,
                        rside_tag_order=ordered_industries,
                        weighted=True, 
                        filter=fil, 
                        filename=filename)
    conf.produce_image()
    subprocess.call('open {filename}'.format(filename=filename).split())

