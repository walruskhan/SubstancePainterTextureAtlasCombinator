import re

groupregex = re.compile(r'.*_(diffuse|basecolor|normal|height|specular|glossiness|id).*', re.IGNORECASE)
udimregex = re.compile(r'.*(\d{4}|u\d+_v\d+)\.', re.IGNORECASE)