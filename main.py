import math
import os
import struct
import zlib

W = H = 1024
pixels = bytearray(W * H * 3)


def blend(x, y, color, alpha=1.0):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        a = max(0.0, min(1.0, alpha))
        pixels[i] = int(pixels[i] * (1 - a) + color[0] * a)
        pixels[i + 1] = int(pixels[i + 1] * (1 - a) + color[1] * a)
        pixels[i + 2] = int(pixels[i + 2] * (1 - a) + color[2] * a)


def disc(cx, cy, r, color, alpha=1.0):
    x0, x1 = max(0, int(cx-r)), min(W-1, int(cx+r))
    y0, y1 = max(0, int(cy-r)), min(H-1, int(cy+r))
    rr = r*r
    for y in range(y0, y1+1):
        dy = y-cy
        for x in range(x0, x1+1):
            dx = x-cx
            if dx*dx+dy*dy <= rr:
                blend(x, y, color, alpha)


def line(x0, y0, x1, y1, color, width=1, alpha=1.0):
    dx, dy = x1-x0, y1-y0
    steps = max(1, int(max(abs(dx), abs(dy))))
    for n in range(steps+1):
        t = n/steps
        disc(x0+dx*t, y0+dy*t, width/2, color, alpha)


def polygon(points, color, alpha=1.0):
    ymin = max(0, int(min(p[1] for p in points)))
    ymax = min(H-1, int(max(p[1] for p in points)))
    for y in range(ymin, ymax+1):
        xs = []
        for i, (x1, y1) in enumerate(points):
            x2, y2 = points[(i+1) % len(points)]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y-y1)*(x2-x1)/(y2-y1))
        xs.sort()
        for j in range(0, len(xs)-1, 2):
            for x in range(max(0, int(xs[j])), min(W, int(xs[j+1])+1)):
                blend(x, y, color, alpha)


def chunk(tag, data):
    body = tag + data
    return struct.pack('>I', len(data)) + body + struct.pack('>I', zlib.crc32(body) & 0xffffffff)


# Dusk gradient, shaded from violet horizon into near-black indigo.
for y in range(H):
    t = y/(H-1)
    c = (int(12+10*t), int(17+3*t), int(48-14*t))
    start = y*W*3
    for x in range(W):
        k = start+x*3
        pixels[k:k+3] = bytes(c)

# Sparse sharp stars.
stars = [(92,91,2),(178,157,2),(286,92,2),(382,174,2),(492,105,2),
         (628,74,2),(748,145,2),(907,97,2),(963,221,2),(121,278,2),
         (303,247,2),(445,273,2),(801,237,2),(878,309,2),(218,342,2),
         (552,202,2),(696,263,2),(54,192,2)]
for x,y,r in stars:
    disc(x,y,r,(205,226,255),0.9)
    if r == 2:
        line(x-5,y,x+5,y,(105,157,224),1,0.55)

# Vast blood-orange moon and a restrained atmospheric rim.
disc(695, 416, 250, (255, 79, 37), 0.13)
disc(695, 416, 226, (243, 75, 42))
disc(695, 416, 214, (255, 112, 54))
disc(695, 416, 194, (255, 137, 63))
# Moon bands, kept subtle and clean.
for yy, rx in [(345,142),(397,186),(458,171),(510,119)]:
    line(695-rx, yy, 695+rx, yy, (222,83,54), 2, 0.28)

# Quiet coastal skyline: clustered roofs, towers, and warm windows.
polygon([(0,620),(80,606),(147,620),(218,594),(277,616),(350,588),(422,614),
         (489,600),(550,626),(617,605),(683,620),(751,594),(821,616),(894,599),
         (956,618),(1024,598),(1024,766),(0,766)], (12,20,45))
buildings = [(10,650,70,116),(88,630,92,136),(191,658,63,108),(257,620,88,146),
             (355,642,75,124),(443,625,96,141),(552,655,62,111),(623,624,86,142),
             (719,646,76,120),(803,617,99,149),(911,644,77,122),(986,627,38,139)]
for x,y,w,h in buildings:
    polygon([(x,y),(x+w//2,y-18),(x+w,y),(x+w,y+h),(x,y+h)],(10,17,38))
    for wx in range(x+12,x+w-7,24):
        for wy in range(y+25,y+h-15,31):
            if ((wx*7+wy*3) % 5) in (0,1):
                polygon([(wx,wy),(wx+7,wy),(wx+7,wy+11),(wx,wy+11)],(255,174,85),0.82)
polygon([(0,754),(1024,754),(1024,1024),(0,1024)],(7,14,35))

# Mountainous aurora wave. Layered shapes make the curl read as a single
# enormous breaking crest, with a deep hollow and bright edge.
polygon([(0,716),(105,694),(220,678),(333,650),(424,607),(505,551),(570,482),
         (615,408),(646,337),(677,272),(721,225),(772,211),(817,232),(843,272),
         (842,318),(816,352),(779,366),(742,352),(723,323),(713,286),(696,267),
         (674,280),(660,321),(650,379),(626,445),(591,511),(546,573),(486,628),
         (414,675),(324,712),(215,746),(98,778),(0,803)],(16,113,145))
polygon([(0,758),(116,727),(233,704),(339,673),(433,627),(515,567),(579,493),
         (621,416),(651,344),(684,290),(721,256),(759,247),(791,263),(806,289),
         (803,318),(785,337),(760,336),(744,316),(733,291),(717,286),(703,301),
         (688,342),(674,397),(647,464),(607,531),(554,591),(491,643),(416,686),
         (325,720),(215,753),(101,786),(0,812)],(31,190,188))
polygon([(0,777),(117,745),(231,723),(339,692),(432,649),(510,590),(573,520),
         (615,447),(647,377),(676,328),(705,299),(728,299),(745,313),(753,331),
         (770,345),(787,342),(798,329),(794,349),(768,370),(738,365),(715,344),
         (696,337),(684,368),(669,422),(642,485),(602,546),(549,601),(487,650),
         (412,691),(322,726),(211,761),(96,795),(0,823)],(44,74,151))

# Electric crest filament, a clean sweeping diagonal into the curl.
crest = [(0,723),(104,700),(218,682),(329,653),(423,611),(504,556),(568,490),
         (610,418),(642,350),(669,300),(696,271),(722,257),(748,256),(770,268)]
for a,b in zip(crest,crest[1:]):
    line(a[0],a[1],b[0],b[1],(156,255,224),8,0.18)
    line(a[0],a[1],b[0],b[1],(160,255,222),3,0.92)
line(771,268,796,288,(211,255,226),3,0.9)

# Fine flowing aurora ribbons along the face, following the wave's sweep.
ribbons = [
    ([(0,748),(124,719),(246,698),(355,668),(449,626),(526,574),(588,510),(629,441)],(95,235,227),5),
    ([(18,778),(143,747),(259,724),(365,694),(455,653),(526,605),(580,552),(618,496)],(161,99,230),4),
    ([(72,799),(188,770),(296,746),(392,716),(481,679),(542,637),(584,594)],(224,86,196),3),
    ([(4,733),(125,709),(242,687),(351,656),(444,616),(519,563)],(247,185,111),2),
    ([(184,740),(289,714),(387,682),(467,642),(530,600)],(114,241,202),2),
]
for pts,col,wd in ribbons:
    for a,b in zip(pts,pts[1:]):
        line(a[0],a[1],b[0],b[1],col,wd,0.72)

# Long streaks of sea foam add scale and directional speed.
for pts in [[(14,839),(110,815),(196,798)],[(65,869),(154,844),(225,827)],
            [(286,806),(368,776),(442,744)],[(390,840),(477,808),(538,775)],
            [(540,744),(586,706),(623,662)],[(617,565),(646,519),(663,474)]]:
    for a,b in zip(pts,pts[1:]):
        line(a[0],a[1],b[0],b[1],(111,222,227),2,0.56)

# One small wooden boat and its lone rider, silhouetted at the break.
# Boat sits around the 80-pixel scale against the immense curl.
polygon([(548,702),(632,697),(620,718),(570,724)],(36,20,31))
line(552,703,628,699,(240,168,105),3,0.95)
polygon([(585,699),(589,680),(594,677),(599,699)],(9,15,30))
disc(592,674,5,(255,205,139))
line(589,685,580,698,(10,17,35),4,1)
line(594,685,603,698,(10,17,35),4,1)
line(581,692,605,692,(10,17,35),4,1)
line(558,728,623,725,(255,172,100),2,0.65)

# Small glints at the curl's lip and wake.
for x,y,r in [(757,251,3),(780,261,2),(798,282,2),(622,441,2),(478,651,2),
              (344,698,2),(188,735,2),(667,478,2),(605,544,2)]:
    disc(x,y,r,(218,255,240),0.9)

raw = b''.join(b'\x00' + bytes(pixels[y*W*3:(y+1)*W*3]) for y in range(H))
png = (b'\x89PNG\r\n\x1a\n' +
       chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)) +
       chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
out = os.environ.get('OUTPUT_PATH', '/output/entry.png')
os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
with open(out, 'wb') as f:
    f.write(png)
