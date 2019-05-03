import argparse
import os
import json
from datetime import datetime

import cogvision

def average(l):
    return sum(l)/len(l)

def get_main_emo(e):
    mx = -1
    me = ''
    for em,v in e.items():
        if v>mx:
            me = em
            mx = v
    return me

parser = argparse.ArgumentParser()

parser.add_argument('--image-path', dest='path', action='store', required=True)
parser.add_argument('--face-path', dest='csv', action='store', required=True)
parser.add_argument('--picture-path', dest='csvpix', action='store', required=True)
parser.add_argument('--cognitive-key', dest='key', action='store', required=True)
parser.add_argument('--cognitive-reg', dest='reg', action='store', default='westus')

args = parser.parse_args()

print("Processing pictures")

cv = cogvision.CognitiveServicesVision(args.key,args.reg)
cf = cogvision.CognitiveServicesFace(args.key,args.reg)

data = {}
faces = {}
tags = {}
for k in os.listdir(args.path):
    if not k.endswith(".jpg"): continue
    print("Processing {}".format(k))
    f = os.path.join(args.path,k)
    # Tags
    d = os.path.join(args.path,k+".vis.json")
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
    # Faces
    d = os.path.join(args.path,k+".face.json")
    if os.path.isfile(d):
        with open(d,'r') as fi:
            dat = json.loads(fi.read())
    else:
        dat = cf.detect_file(f,attributes="age,gender,facialHair,glasses,emotion")
        with open(d,'w') as fi:
            fi.write(json.dumps(dat))
    faces[k[:-4]]=dat

tags = [t for t,v in tags.items() if v>10]

print("Important tags: "+','.join(tags))

print("Writing output")

out_file_faces = open(args.csv,'w')
out_file_pictures = open(args.csvpix,'w')

fields = ['age','gender','main_emotion','happiness','surprise','sadness','fear','no_people']+tags
out_file_faces.write(','.join(fields)+'\n')
out_file_pictures.write(','.join(fields)+'\n')

for k,v in data.items():
    if len(faces[k])==0:
        print(" + Skipping {}, no faces".format(k))
        continue
    av_age = average([ i['faceAttributes']['age'] for i in faces[k]])
    av_happiness = average([ i['faceAttributes']['emotion']['happiness'] for i in faces[k]])
    av_surprise = average([i['faceAttributes']['emotion']['surprise'] for i in faces[k]])
    av_sadness = average([i['faceAttributes']['emotion']['sadness'] for i in faces[k]])
    av_fear = average([i['faceAttributes']['emotion']['fear'] for i in faces[k]])
    fields = [av_age, '', '', av_happiness, av_surprise, av_sadness, av_fear, len(faces[k])]

    vtags = [x['name'] for x in v['tags']]
    for t in tags: # add one-hot encoded tags
        fields.append(1 if t in vtags else 0)
    fields1 = map(str,fields)
    out_file_pictures.write(','.join(fields1)+'\n')
    for f in faces[k]:
        fields[0] = f['faceAttributes']['age']
        fields[1] = f['faceAttributes']['gender']
        fields[2] = get_main_emo(f['faceAttributes']['emotion'])
        fields[3] = f['faceAttributes']['emotion']['happiness']
        fields[4] = f['faceAttributes']['emotion']['surprise']
        fields[5] = f['faceAttributes']['emotion']['sadness']
        fields[6] = f['faceAttributes']['emotion']['fear']
        fields[7] = len(faces[k])
        fields1 = map(str,fields)
        out_file_faces.write(','.join(fields1)+'\n')

out_file_pictures.close()
out_file_faces.close()

