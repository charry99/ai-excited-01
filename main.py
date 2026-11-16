import math
import os
import struct
import zlib

W = H = 1024
pixels = bytearray(W * H * 3)


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        pixels[i:i + 3] = bytes(color)


def blend(x, y, color, a=1.0):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        for k in range(3):
            pixels[i + k] = int(pixels[i + k] * (1 - a) + color[k] * a)


def disk(cx, cy, r, color, feather=0):
    x0, x1 = max(0, int(cx-r-1)), min(W, int(cx+r+2))
    y0, y1 = max(0, int(cy-r-1)), min(H, int(cy+r+2))
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = math.hypot(x-cx, y-cy)
            if d <= r:
                blend(x, y, color, min(1, r-d+0.5) if feather else 1)


def polygon(points, color):
    ymin = max(0, int(min(p[1] for p in points)))
    ymax = min(H-1, int(max(p[1] for p in points)))
    for y in range(ymin, ymax+1):
        xs = []
        for j in range(len(points)):
            x1, y1 = points[j]
            x2, y2 = points[(j+1) % len(points)]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y-y1) * (x2-x1) / (y2-y1))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            lo, hi = max(0, int(a)), min(W-1, int(b))
            for x in range(lo, hi+1):
                put(x, y, color)


def bezier(p0, p1, p2, p3, n=120):
    out = []
    for i in range(n+1):
        t = i/n
        u = 1-t
        out.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0],
                    u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
    return out


# Deep dusk gradient and a restrained horizon glow.
for y in range(H):
    t = y / H
    for x in range(W):
        glow = max(0, 1 - math.hypot((x-520)/650, (y-480)/600))
        pixels[(y*W+x)*3:(y*W+x)*3+3] = bytes((int(8+10*t+28*glow), int(13+13*t+15*glow), int(43+21*t+25*glow)))

# Fine stars, placed on a fixed geometric rhythm.
for row in range(13):
    for col in range(17):
        x = 34 + col*59 + (row*37 % 29)
        y = 35 + row*37 + (col*19 % 17)
        if y < 505 and not (350 < x < 690 and 190 < y < 520):
            disk(x, y, 1.3 + ((row*7+col*3)%4)*0.35, (110, 206, 226))

# Huge low ember moon, with a crisp disc and a thin hot rim.
disk(515, 385, 218, (246, 77, 43))
disk(515, 385, 210, (255, 112, 54))
for yy in range(230, 540):
    for xx in range(310, 721):
        d = math.hypot(xx-515, yy-385)
        if d < 203:
            stripe = (int(yy*0.29) % 23 == 0) or (int((xx+yy)*0.11) % 47 == 0)
            if stripe:
                blend(xx, yy, (255, 158, 73), 0.16)

# Far coastal ridges and sleeping town.
polygon([(0,610),(140,558),(260,585),(370,545),(470,580),(610,550),(760,590),(900,552),(1024,580),(1024,780),(0,780)], (14,24,55))
for i in range(16):
    x = i*70-10
    base = 704 + (i*23 % 41)
    ww = 42 + i*7 % 26
    hh = 48 + i*31 % 58
    polygon([(x,base),(x,base-hh),(x+ww//2,base-hh-19),(x+ww,base-hh),(x+ww,base)], (9,18,42))
    for wx in range(x+8, x+ww-4, 15):
        wy = base - 23 - ((wx+i*5) % max(20, hh-22))
        if wy < base-8:
            put(wx, wy, (255, 183, 88))
            put(wx+1, wy, (255, 183, 88))

# The luminous breaker: a long rising shoulder that folds back into a hollow curl.
outer = bezier((-80,1010),(130,830),(225,410),(542,503),150)
outer += bezier((542,503),(721,554),(778,744),(1048,690),120)[1:]
polygon(outer + [(1048,1050),(-80,1050)], (12,116,151))
inner = bezier((-40,1018),(151,850),(241,545),(470,566),140)
inner += bezier((470,566),(642,581),(682,734),(1019,720),100)[1:]
polygon(inner + [(1020,1040),(-40,1040)], (18,53,104))
# Curl hollow, a dark open eye that makes the breaking shape read clearly.
hollow = bezier((442,592),(503,548),(649,565),(707,655),80)
hollow += bezier((707,655),(749,721),(828,724),(943,710),60)[1:]
hollow += [(940,756),(785,769),(665,737),(554,674)]
polygon(hollow, (10,21,58))

# Flowing aurora ribbons follow the shoulder in tapered, smooth strokes.
def ribbon(p0,p1,p2,p3,width,color):
    line = bezier(p0,p1,p2,p3,180)
    for j,(x,y) in enumerate(line):
        taper = math.sin(math.pi*j/(len(line)-1))**0.55
        r = width*taper
        disk(x,y,r,color,1)

ribbon((-16,927),(191,775),(213,478),(477,515),25,(35,232,211))
ribbon((20,966),(197,810),(248,537),(491,551),12,(122,255,222))
ribbon((82,1014),(307,818),(314,586),(530,581),19,(102,93,232))
ribbon((497,518),(658,524),(727,684),(1004,657),20,(42,220,221))
ribbon((514,544),(663,550),(727,703),(1008,686),9,(212,255,226))
ribbon((555,492),(671,475),(741,589),(827,633),13,(184,106,244))

# White turquoise crest spray, arcing over the fold.
crest = bezier((287,490),(365,420),(470,420),(563,492),100)
for j,(x,y) in enumerate(crest):
    disk(x,y, 4.5 + 2*math.sin(j/100*math.pi), (207,255,235), 1)
for x,y,r in [(310,468,5),(340,445,3),(375,425,4),(415,418,3),(451,428,5),(493,450,3),(535,480,4),(562,506,3)]:
    disk(x,y,r,(224,255,246),1)

# Little boat, deliberately readable against the illuminated sea.
polygon([(404,760),(593,760),(558,796),(444,796)], (47,25,37))
polygon([(414,756),(583,756),(562,774),(437,774)], (222,125,56))
for x in range(430,570,25):
    put(x,765,(255,195,112))
polygon([(491,654),(493,748),(555,748)], (248,230,190))
polygon([(495,674),(495,744),(543,744)], (202,210,209))
polygon([(481,748),(503,748),(499,705),(489,705)], (12,13,28))
disk(492,695,10,(8,12,29))
polygon([(485,706),(499,706),(503,748),(477,748)], (8,12,29))
polygon([(486,716),(477,754),(466,762),(487,760),(497,729)], (8,12,29))

# Foreground shadow bands and a few luminous wakes point toward the boat.
for k in range(7):
    y = 832 + k*25
    polygon([(0,y),(95+k*15,y-8),(211+k*12,y),(0,y+7)], (15,73+k*4,112+k*3))
for p0,p1,p2,p3 in [((-20,870),(140,850),(260,866),(368,833)),((15,930),(143,910),(284,919),(370,889)),((36,1000),(193,971),(300,990),(408,953))]:
    ribbon(p0,p1,p2,p3,3,(52,196,207))

def png_bytes():
    raw = b''.join(b'\x00' + pixels[y*W*3:(y+1)*W*3] for y in range(H))
    def chunk(tag, data):
        body = tag + data
        return struct.pack('!I',len(data)) + body + struct.pack('!I',zlib.crc32(body)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR',struct.pack('!2I5B',W,H,8,2,0,0,0)) + chunk(b'IDAT',zlib.compress(raw,9)) + chunk(b'IEND',b'')


out = os.environ.get('OUTPUT_PATH', '/output/entry.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'wb') as f:
    f.write(png_bytes())
