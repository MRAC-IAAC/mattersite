import numpy as np

category_ids = {'brick' : 0,
                'concrete' : 1,
                'metal' : 2,
                'wood' : 3,
                'z_none' : 4}

category_colors = [(0,0,255),(255,0,0),(0,255,0),(0,255,255),(0,0,0)]
category_colors_np = np.array(category_colors)

category_colors_matplot = np.asarray([(1,0,0),(0,0,1),(0,1,0),(1,1,0),(0,0,0)])

category_names = ("brick","concrete","metal","wood","z_none")
