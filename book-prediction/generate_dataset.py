import random

no_samples = 1000

fields = ['price','pages','year','type','cover','color','quality_paper']

types = {
    'childen' : [10,50],
    'fiction' : [50,500],
    'love_story' : [100,250],
    'textbook' : [300,1000],
    'album' : [50,150]
}

out_simple = open('book-simple.csv','w')
out_simple.write(','.join(['price','pages','year'])+'\n')

out = open('book-full.csv','w')
out.write(','.join(fields)+'\n')

for _ in range(no_samples):
    type = random.choice(list(types.keys()))
    pages = random.randint(types[type][0],types[type][1])
    quality = random.choice([0,1])
    year = random.randint(1990,2018)
    cover = random.choice(['hard','soft'])
    color = random.choice([0,1])
    aux1,aux2=1,0
    if type == 'children':
        quality = random.choice([0,1,1,1,1])
        color = random.choice([0,1,1,1])
        aux1,aux2=2,100
    if type == 'textbook':
        color = 0
        quality = random.choice([0,0,0,0,1])
    if type == 'album':
        color = 1
        quality = 1
        cover = 'hard'
        aux1,aux2=2.5,300
    if type == 'fiction':
        quality = random.choice([0, 0, 0, 1, 1])
        color = random.choice([0, 0, 0, 0, 1])
    if type == 'love_story':
        quality = 0
        color = 0
        cover = random.choice(['soft','soft','soft','hard'])

    ppp = random.gauss(1.1,0.2) if quality==0 else random.gauss(2.2,0.3)
    cp = random.gauss(20,5) if cover=='soft' else random.gauss(50,15)
    if color: ppp*=2
    price = ppp*pages + cp
    price = price*aux1+aux2
    discount = (year-1990)/(2018-1990)
    discount = 0.5+discount*0.5
    price = price*discount
    price = int(price)

    price_simple = random.gauss(1.1,0.2)*pages+random.gauss(20,5)
    price_simple*= discount

    d = [price,pages,year,type,cover,color,quality]
    d = map(str,d)
    out.write(','.join(d)+'\n')

    d = [price_simple,pages,year]
    d = map(str,d)
    out_simple.write(','.join(d)+'\n')

out.close()
out_simple.close()
