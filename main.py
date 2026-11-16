import math
import os
import struct
import zlib

W = H = 1024
pixels = bytearray(W * H * 3)

def blend(x, y, color, alpha=255):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        if alpha == 255:
            pixels[i:i+3] = bytes(color)
        else:
            a = alpha / 255.0
            pixels[i] = int(pixels[i] * (1-a) + color[0] * a)
            pixels[i+1] = int(pixels[i+1] * (1-a) + color[1] * a)
            pixels[i+2] = int(pixels[i+2] * (1-a) + color[2] * a)

def rect(x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            blend(x, y, color)

def disc(cx, cy, r, color, alpha=255):
    r2 = r*r
    for y in range(max(0, int(cy-r)), min(H, int(cy+r)+1)):
        dy = y-cy
        span = int(math.sqrt(max(0, r2-dy*dy)))
        for x in range(max(0, int(cx-span)), min(W, int(cx+span)+1)):
            blend(x, y, color, alpha)

def bezier(a, b, c, d, steps=160):
    out=[]
    for j in range(steps+1):
        t=j/steps; u=1-t
        out.append((u*u*u*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t*t*t*d[0],
                    u*u*u*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t*t*t*d[1]))
    return out

def polygon(points, color, alpha=255):
    miny=max(0,int(min(p[1] for p in points))); maxy=min(H-1,int(max(p[1] for p in points)))
    for y in range(miny,maxy+1):
        xs=[]
        for i in range(len(points)):
            x1,y1=points[i]; x2,y2=points[(i+1)%len(points)]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1+(y-y1)*(x2-x1)/(y2-y1))
        xs.sort()
        for k in range(0,len(xs)-1,2):
            for x in range(max(0,int(xs[k])),min(W,int(xs[k+1])+1)):
                blend(x,y,color,alpha)

def stroke(points, color, width, alpha=255):
    r=width/2
    for (x1,y1),(x2,y2) in zip(points,points[1:]):
        dx=x2-x1; dy=y2-y1; n=max(1,int(math.hypot(dx,dy)*1.4))
        for j in range(n+1):
            t=j/n; disc(x1+dx*t,y1+dy*t,r,color,alpha)

# Deep dusk gradient, with a darkened horizon for the town silhouette.
for y in range(H):
    t=y/(H-1)
    col=(int(7+10*t), int(13+5*t), int(39+20*t))
    rect(0,y,W,y+1,col)

# Fine stars and a few distant, quiet glints.
for i in range(145):
    x=(i*173+61)%W; y=(i*293+27)%560
    size=2 if i%11==0 else 1
    disc(x,y,size,(151,190,220),170 if i%4 else 235)

# Blood-orange moon halo and disc, deliberately low behind the curl.
disc(720,390,252,(180,39,31),28)
disc(720,390,214,(255,91,40),255)
disc(720,390,195,(255,116,49),255)
# Soft bands across the moon.
for yy,ww,aa in [(324,116,34),(367,174,30),(448,130,28)]:
    disc(720,yy,ww,(255,190,106),aa)

# Sleeping coastal town: roofs, clustered houses, and tiny warm windows.
rect(0,650,1024,774,(10,18,43))
for x,w,h in [(18,84,80),(111,65,111),(191,99,72),(300,72,122),(384,95,85),(493,76,132),(578,91,75),(686,85,112),(787,100,82),(899,80,125),(984,48,79)]:
    top=650-h
    rect(x,top, min(1024,x+w),740,(12,22,47))
    polygon([(x-8,top+8),(x+w//2,top-24),(x+w+8,top+8)],(17,27,52))
    for wx in range(x+15,min(x+w-8,1024),27):
        for wy in range(top+28,720,35):
            rect(wx,wy,wx+6,wy+9,(255,173,94) if (wx+wy)%3 else (76,116,143))
rect(0,739,1024,770,(8,16,38))

# Water horizon glimmer, behind the wave.
for j in range(13):
    y=754+j*7; x0=450+(j*37)%180; length=90+(j*53)%210
    rect(x0,y,min(1024,x0+length),y+2,(46,94,134))

# Giant aurora wave: a single sweeping silhouette with a hooked crest.
outer = bezier((-80,1015),(135,856),(252,719),(445,690),150)
outer += bezier((445,690),(631,663),(693,550),(635,448),120)[1:]
outer += bezier((635,448),(578,339),(660,252),(781,273),110)[1:]
outer += bezier((781,273),(924,298),(937,438),(847,515),110)[1:]
outer += bezier((847,515),(789,563),(771,610),(825,660),80)[1:]
outer += bezier((825,660),(900,747),(1017,774),(1110,836),130)[1:]
outer += [(1110,1050),(-80,1050)]
polygon(outer,(12,54,91))

# Inner luminous body, inset and echoing the large curl.
inner = bezier((-30,956),(157,828),(280,745),(453,716),150)
inner += bezier((453,716),(620,690),(689,578),(630,475),120)[1:]
inner += bezier((630,475),(574,376),(664,298),(766,313),110)[1:]
inner += bezier((766,313),(864,326),(883,424),(811,489),110)[1:]
inner += bezier((811,489),(735,558),(743,628),(821,690),100)[1:]
inner += bezier((821,690),(898,750),(1003,787),(1070,837),100)[1:]
inner += [(1070,1050),(-30,1050)]
polygon(inner,(18,117,145))

# Turquoise and violet ribbons trace the curl like an aurora caught in surf.
stroke(bezier((-20,922),(190,800),(318,719),(472,704),150), (77,231,210),34,255)
stroke(bezier((467,704),(632,686),(718,584),(647,470),145), (120,246,221),28,255)
stroke(bezier((647,470),(584,365),(670,284),(778,298),130), (75,218,220),24,255)
stroke(bezier((778,298),(891,311),(914,430),(827,503),135), (178,120,245),20,255)
stroke(bezier((830,515),(762,590),(779,646),(856,699),100), (91,225,230),23,255)

# Crest foam ribbon, a sweeping pale line around the curl.
crest=bezier((424,674),(588,649),(650,544),(595,443),130)
crest+=bezier((595,443),(543,345),(619,257),(735,248),130)[1:]
crest+=bezier((735,248),(841,239),(921,313),(905,398),120)[1:]
stroke(crest,(206,255,239),15,255)
stroke(crest[15::3],(255,232,183),5,235)

# Spray beads around the crest, kept sparse and graphic.
for i in range(34):
    x=588+(i*47)%335; y=250+(i*71)%237
    if i%3 != 0:
        disc(x,y,2+(i%3),(177,248,239),210)

# Foreground wake strokes sweep toward the boat.
for i in range(8):
    y=856+i*20; start=60+i*37
    line=bezier((start,y),(250,y-70),(430,y+46),(613,y-36),100)
    stroke(line,(28+2*i,142+5*i,171+4*i),4 if i%2 else 6,205)

# Boat, clearly readable in silhouette, riding the bright inner shoulder.
polygon([(355,778),(523,778),(492,817),(392,817)],(29,21,37))
stroke([(359,778),(520,778)],(252,177,97),8)
stroke([(390,793),(495,793)],(115,65,42),4)
# Mast and short sail.
stroke([(439,775),(439,684)],(33,25,35),8)
polygon([(432,690),(432,761),(386,754)],(255,187,102))
polygon([(446,700),(446,762),(487,755)],(235,91,74))
stroke([(439,682),(439,777)],(255,205,143),3)
# Lone rider: head, torso, and seated legs.
disc(441,665,12,(18,22,41))
stroke([(441,678),(441,723)],(18,22,41),13)
stroke([(440,698),(420,716)],(18,22,41),9)
stroke([(442,721),(424,741)],(18,22,41),10)
stroke([(442,721),(461,740)],(18,22,41),10)

# Warm rim light separates the boat and person from the luminous water.
stroke([(389,820),(493,820)],(255,147,83),3,235)

def chunk(kind, data):
    return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)

raw=b''.join(b'\x00'+pixels[y*W*3:(y+1)*W*3] for y in range(H))
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',W,H,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
path=os.environ.get('OUTPUT_PATH','/output/entry.png')
os.makedirs(os.path.dirname(path) or '.',exist_ok=True)
with open(path,'wb') as f:
    f.write(png)
