import argparse
import os
import json
from datetime import datetime

import cogvision

def average(l):
    return sum(l)/len(l)

parser = argparse.ArgumentParser()

parser.add_argument('--image-path', dest='path', action='store', required=True)
parser.add_argument('--csv-path', dest='csv', action='store', required=True)
parser.add_argument('--cognitive-key', dest='key', action='store', required=True)
parser.add_argument('--cognitive-reg', dest='reg', action='store', default='westus')

args = parser.parse_args()

print("Reading data file {}".format(args.csv))

with open(args.csv, 'r') as csv_file:
    csv_lines = csv_file.readlines()

likes = {x.split(';')[0]: int(x.split(';')[1]) for x in csv_lines[1:]}

print("Processing pictures")

cv = cogvision.CognitiveServicesVision(args.key,args.reg)
data = {}
tags = {}
for k in os.listdir(args.path):
    if not k.endswith(".jpg"): continue
    if not k[:-4] in likes.keys():
        print("Warning: like info not found for {}".format(k))
        continue
    # print("Processing {}".format(k))
    f = os.path.join(args.path,k)
    d = os.path.join(args.path,k+".json")
    if os.path.isfile(d):
        with open(d,'r') as fi:
            dat = json.loads(fi.read())
    else:
        dat = cv.analyze_file(f)
        with open(d,'w') as fi:
            fi.write(json.dumps(dat))
    data[k[:-4]]=dat
    for t in dat['tags']:
        tags[t['name']]=1+tags.get(t['name'],0)

tags = [t for t,v in tags.items() if v>10]

print("Important tags: "+','.join(tags))

print("Writing output")

out_file = open('output.csv','w')

fields = ['likes','main_category','no_faces','avg_age','when','adult_score','color_fg','color_bg']+tags
out_file.write(','.join(fields)+'\n')

for k,v in data.items():
    fields = [likes[k]] # likes
    fields.append('None' if len(v['categories'])==0 else v['categories'][0]['name'].split('_')[0]) # main category
    fields.append(len(v['faces']))
    fields.append(0 if len(v['faces'])==0 else average([x['age'] for x in v['faces']]))
    y,m,d = (int(x) for x in k.split(' ')[0].split('-')) # get year,month,day of publication
    dt = (datetime(year=y,month=m,day=d)-datetime(year=2017,month=6,day=20)).days
    fields.append(dt) # time taken in days since beginning of data
    fields.append(v['adult']['adultScore']) # adult_score
    fields.append(v['color']['dominantColorForeground'])
    fields.append(v['color']['dominantColorBackground'])
    vtags = [x['name'] for x in v['tags']]
    for t in tags: # add one-hot encoded tags
        fields.append(1 if t in vtags else 0)
    fields = map(str,fields)
    out_file.write(','.join(fields)+'\n')

out_file.close()

