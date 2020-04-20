# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 14:42:13 2019

@author: 212566876
"""

import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

url = "http://www.usaee.org/usaee2019/program_concurrent.aspx#tbl5"

#If there is no such folder, the script will create one automatically
folder_location = r'C:\Users\212566876\Box Sync\Rotation 4\OPGEE Carbon Emissions\USAEE Conference Presentations\PDFs'
if not os.path.exists(folder_location):os.mkdir(folder_location)

response = requests.get(url)
soup= BeautifulSoup(response.text, "html.parser")     
for link in soup.select("a[href$='.pdf']"):
    #Name the pdf files using the last portion of each link which are unique in this case
    filename = os.path.join(folder_location,link['href'].split('/')[-1])
    with open(filename, 'wb') as f:
        f.write(requests.get(urljoin(url,link['href'])).content)