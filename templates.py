import platform

greg_linux_circos_command = ['perl', '/home/gregkraken/Programming/circos-0.64/bin/circos', '-conf', './tmp/circos.conf']
osx_circos_command =    ['perl', '/Applications/circos-0.64/bin/circos', '-conf', './tmp/circos.conf']
cygwin_circos_command = ['perl', '../circos-0.64/bin/circos', '-conf', './tmp/circos.conf']

def svg_to_png_command(filename):
    return ['convert', filename+'.svg', filename+'.png']

circos_conf_header = \
"""
<colors>
  <<include ../conf/colors.conf>>
</colors>

<fonts>
  <<include ../conf/fonts.conf>>
</fonts>

<<include ./ideogram.conf>>
<<include ./ticks.conf>>

karyotype = ./tmp/karyotype.conf

<image>
  background = white
  dir   = .
  file  = {filename}
  png   = yes
  svg   = yes
  # radius of inscribed circle in image
  radius         = {image_size}

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

<rules>
<rule>
condition = var(color) eq "grey"
color = {grey_default}
z = -1
</rule>
</rules>

</link>

</links>

<<include ./conf/housekeeping.conf>>
"""

ideogram_conf_template = \
"""
<ideogram>

<spacing>
default      = {default_spacing}
break        = {break}
</spacing>

<<include ./conf/ideogramposition.conf>>
<<include ./conf/ideogramlabel.conf>>

radius  = {radius}

</ideogram>
"""
