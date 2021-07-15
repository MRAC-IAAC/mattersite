Mattersite
==========

This repo contains a set of tools from the research stage of the mattersite project. This technology primarily covers two phases, predemolition analysis, and post-demolition design with recovered materials. 

Pre-Demolition Analysis
-----------------------

### Requirements
### Usage
### Database Access
The site_reconstruction grasshopper file includes functionality to upload extracted data to a MySQL database. To authenticate, it looks for a file in the same directory called 'connection.txt'. This file should follow the following format:  
- Database URL
- Database Username (user requires, INSERT, SELECT, DELETE, UPDATE, and EXECUTE permissions)
- Database Password
- Database Schema Name



Post-Demolition Design
----------------------

### Requirements
### Usage
### Database Access 
The Design for Fabrication grasshopper file includes functionality to read available elements from a MySQL databasae. To authenticate, it looks for a file in the same directory called 'connection.txt'. This file should follow the following format:  
- Database URL
- Database Username (user requires, SELECT and EXECUTE permissions)
- Database Password
- Database Schema Name