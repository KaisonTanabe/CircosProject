
circos_command = ['perl', '/Applications/circos-0.62-1/bin/circos', '-conf', './tmp/circos.conf']

circos_conf_header = \
"""
<colors>
  <<include ./colors.conf>>
  <<include etc/brewer.conf>>
</colors>

<fonts>
  <<include etc/fonts.conf>>
</fonts>

<<include ./tmp/ideogram.conf>>
<<include ticks.conf>>

karyotype   = ./tmp/karyotype.conf

<image>
  background = white
  dir   = .
  file  = {filename}
  png   = yes
  svg   = yes
  # radius of inscribed circle in image
  radius         = 3000p

  # by default angle=0 is at 3 o'clock position
  angle_offset      = -90

  auto_alpha_colors = yes
  auto_alpha_steps  = 5
</image>

chromosomes_units = {chromosomes_units}
chromosomes = {chromosomes}
chromosomes_display_default = yes
show_ticks = {show_ticks}
show_tick_labels = {show_tick_labels}
housekeeping = yes
"""

circos_conf_links = \
"""
<links>

z = 0
radius = {radius}
bezier_radius = {bezier_radius}
crest = {crest}
bezier_radius_purity = {bezier_radius_purity}

<link all_links>
show   = {show_by_default}
ribbon = {ribbon}
flat   = {flat}
file = ./tmp/linkdata.txt
</link>

</links>

<<include ./tmp/housekeeping.conf>>
"""

ideogram_conf_template = \
"""
<ideogram>

<spacing>
default = {default_spacing}
break   = {break}
</spacing>

<<include ideogramposition.conf>>
<<include ideogramlabel.conf>>

radius  = {radius}

</ideogram>
"""
