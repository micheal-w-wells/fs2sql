# fs2sql
A utility to create a sqlite3 database of OpenVMS filesystems for analysis.  File spec attributes are parsed from directory listings.


# EDIT 2019 Oct:  In case anyone ever does find themselves wanting to use this:
You need to output dir listings to a file with all file attributes.  
That file acts as an input.  Other things I would have changed would have been to use named groups  instead of comments for 
the regex as well as add a test to make sure the file input includes the right attributes.  It was a decade ago and I was an 
intern cut me some slack :P.
