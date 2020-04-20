# Test python script for clarifying the 
# functionality of relative filepath and 
# read a file line-by-line

import os

xmac_filename = 'test_subdir/test_read2.txt'	#i2
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
xmac_abs_file_path = os.path.join(script_dir, xmac_filename)
fid = open(xmac_abs_file_path)

for line in fid:
	if line=='' or line=='\n':
		print('empty\n')
	else:
		print('not empty')
		print(line)

#fid_line = fid.readline()
#for x in fid_line:
#	print(x)

# Make sure to close the file
fid.close()