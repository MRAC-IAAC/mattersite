Mattersite
==========

This repo contains a set of tools from the research stage of the Mattersite project. This technology primarily covers two phases, predemolition analysis, and post-demolition design with recovered materials. 

---

Pre-Demolition Analysis
-----------------------

### Components
Predemolition Analysis covers two main stages; 2d material localization for captured images, and 3d site reconstruction and assocation with localized material maps.

### Requirements
#### Material Localization
This system was tested under Ubuntu 18.04, with Python 3.8, primarily using OpenCV 4.2 and Numpy 1.18  
Full python environment is listed in requirements.txt  
Some util scripts also require Processing 3.
#### Geometric Reconstruction


### Usage
#### Material Localization
##### Setup

To process the input images and train the classifier, run

`./setup_model`

The script will look for input images in the path data/s2g1_dataset/images, organized in directories by category name.

This may take ~30 minutes to run, mostly due to sampling the database during the feature clustering step.

This will produce several files in the 'model/' folder: 

- **hs-db.hdf5** : Averaged hue and saturation histograms for each category of the input dataset
- **features.hdf5** : Raw list of all features detected in input set
- **bovw.hdf5** : Results of clusterization of image features
- **vocab.cpickle** : Association of visual words with categories
- **model.cpickle** : Classification model trained from above results
- **idf.cpickle** : Inverse Document Frequency information, contains weighting information for the importance of different features. 

##### Localization

To perform material localization, run 

`./localize`
 
Ensure the '--images' argument in the call to localize.py is properly set for the folder of images to process. 

The time to process each image depends on the kernel_size and thus patch_size variables in the localization script. Each classification window at minimum 100 pixels, so the patch size is determined by dividing 100 by the kernel size. (e.g. the default kernel_size is 4, which leads to a final resolution of classification patches 25px on a side)

This will write images with category colors overlayed to the 'output/localization' folder, as well as text files containing the heuristically weighted category scores for each image subpatch. 

Not these are currently not re-normalized, and will often be negative, due to the way heuristics are applied.
#### Geometric Reconstruction
### Database Access
The site_reconstruction grasshopper file includes functionality to upload extracted data to a MySQL database. To authenticate, it looks for a file in the same directory called 'connection.txt'. This file should follow the following format:  
- Database URL
- Database Username (user requires, INSERT, SELECT, DELETE, UPDATE, and EXECUTE permissions)
- Database Password
- Database Schema Name

---

Post-Demolition Design Demonstrator
-----------------------------------
### Components
The demonstrator is split into two parts, adaptive design and resulting fabrication, using the 'Design for Fabrication + Database' and 'mattersite_demonstrator_fabrication' componenents respectively.  
The Design script create semi-reciprocal structures based on simple parametric input surfaces, using a two-layer approach. The input form and specifics are adapted based on material availability from an associated database. 
The Fabrication script creates CAM files for these designs using a Kuka industrial robot. 
### Requirements
#### Design : Grasshopper Plugins
- NGon : Reciprocal Structures
- Heteroptera : Visualization
- Karamba : Structural Analysis
- Pufferfish : Design Mesh Editing
- Tarsier : Visualization
- Human : Interface
- HumanUI : Interface
- Slingshot : MySQL Connection
- Octopus : Multigoal Optimization
- LunchBox : Geometry
- Fologram : Interface Utility
- Meshedit2000 : Geometry
- Telepathy : Interface

#### Fabrication : Grasshopper Plugins
- KukaPRC : Kuka Programming
- Telepathy : Interface

### Usage
#### Design
The initial surface is set by the controls in the 'Create Raw Surface' group. These controls are also automatically set by the optimizer later. Available materials are selected from the database using the controls in the popup UI. Controls for which parts of the process are visualized appear in the RPC tab in the Rhino window. 

Finally, the 'Extract Fabrication Numbers' group is used to create internalized panels to copy to the Fabrication script, containing the specifics of the connectors to be fabricated. 

#### Fabrication 
After copying the panels from the Design script, they are plugged into Design group in the beginning. This covers the length of each element, the critical angles, and the ids of which components it connects to. 
No other user input is necessary until exporting the final Kuka .SRC script. Part selection, feedback and previewing controls are also added to the Rhino RCP tab. 

### Database Access 
The Design for Fabrication grasshopper file includes functionality to read available elements from a MySQL databasae. To authenticate, it looks for a file in the same directory called 'connection.txt'. This file should follow the following format:  
- Database URL
- Database Username (user requires, SELECT and EXECUTE permissions)
- Database Password
- Database Schema Name