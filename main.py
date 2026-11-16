#!/usr/bin/env python3
"""Moonwake: a deterministic, standard-library-only poster renderer."""
import math
import os
import struct
import zlib

W = H = 1024


class Canvas:
    def __init__(self):
        self.p = bytearray(W * H * 3)

    def pixel(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.p[i:i+3] = bytes(c)

    def rect(self, x0, y0, x1, y1, c):
        x0, x1 = max(0, int(x0)), min(W, int(x1))
        y0, y1 = max(0, int(y0)), min(H, int(y1))
        row = bytes(c) * max(0, x1-x0)
        for y in range(y0, y1):
            i = (y * W + x0) * 3
            self.p[i:i+len(row)] = row

    def disc(self, cx, cy, r, color):
        x0, x1 = max(0, int(cx-r-1)), min(W, int(cx+r+2))
        y0, y1 = max(0, int(cy-r-1)), min(H, int(cy+r+2))
        rr = r*r
        for y in range(y0, y1):
            dy = y + .5 - cy
            for x in range(x0, x1):
                dx = x + .5 - cx
                if dx*dx + dy*dy <= rr:
                    self.pixel(x, y, color)

    def poly(self, pts, color):
        lo = max(0, int(min(y for x, y in pts)))
        hi = min(H-1, int(max(y for x, y in pts)))
        for y in range(lo, hi+1):
            scan = y + .5
            xs = []
            for i, (x1, y1) in enumerate(pts):
                x2, y2 = pts[(i+1) % len(pts)]
                if (y1 <= scan < y2) or (y2 <= scan < y1):
                    xs.append(x1 + (scan-y1) * (x2-x1) / (y2-y1))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                self.rect(math.ceil(a), y, math.ceil(b), y+1, color)

    def line(self, x0, y0, x1, y1, width, color):
        steps = int(max(abs(x1-x0), abs(y1-y0))) + 1
        for i in range(steps+1):
            t = i / steps
            self.disc(x0+(x1-x0)*t, y0+(y1-y0)*t, width/2, color)

    def png(self):
        raw = b''.join(b'\x00' + self.p[y*W*3:(y+1)*W*3] for y in range(H))
        def chunk(kind, data):
            body = kind + data
            return struct.pack('>I', len(data)) + body + struct.pack('>I', zlib.crc32(body) & 0xffffffff)
        return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def bezier(a, b, c, d, t):
    u = 1-t
    return (u*u*u*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t*t*t*d[0],
            u*u*u*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t*t*t*d[1])


def main():
    im = Canvas()
    # Deep dusk field, gently lifted behind the moon.
    for y in range(H):
        f = y / H
        col = (int(8+7*f), int(13+8*f), int(42+20*f))
        im.rect(0, y, W, y+1, col)

    # Radial halo and oversized ember moon.
    for r in range(270, 0, -3):
        t = 1-r/270
        im.disc(735, 365, r, (int(20+28*t), int(27+29*t), int(72+18*t)))
    im.disc(735, 365, 205, (244, 91, 53))
    im.disc(735, 365, 188, (255, 133, 69))
    im.disc(735, 365, 165, (255, 166, 91))
    # Moon striations, clipped naturally by placing only short quiet marks.
    for y, x, length in [(285,650,110),(322,775,70),(390,620,82),(435,740,120),(475,675,60)]:
        im.line(x, y, x+length, y, 3, (238, 126, 83))

    # Stars as small warm and cool pinpricks.
    for x, y, r in [(95,142,3),(184,250,2),(313,104,2),(492,184,3),(901,131,2),
                    (864,252,3),(571,334,2),(106,377,2),(928,419,2),(362,281,2)]:
        im.disc(x, y, r, (191,218,239))

    # Far coastal ridge and sleeping town silhouette.
    im.poly([(0,620),(118,600),(228,622),(340,590),(457,619),(580,600),(690,624),(830,589),(1024,612),(1024,1024),(0,1024)], (12,20,49))
    # Roofs, narrow houses, and a few lit windows.
    for x, base, wid, h in [(18,678,83,84),(112,658,95,104),(220,681,72,77),(300,650,106,111),
                             (420,677,82,87),(515,653,94,107),(625,679,70,78),(710,650,110,105),
                             (834,669,82,91),(925,646,96,112)]:
        im.poly([(x,base-h*.58),(x+wid*.5,base-h),(x+wid,base-h*.58),(x+wid,base),(x,base)], (18,29,59))
        im.rect(x+wid*.38, base-31, x+wid*.50, base-13, (243,151,83))
        im.rect(x+wid*.68, base-43, x+wid*.78, base-26, (227,139,83))

    # Curling aurora wave: sampled Bezier creates smooth, flowing edge.
    outer = [(0,760),(180,690),(290,526),(492,519)]
    inner = [(492,519),(640,520),(768,694),(1018,736)]
    crest = [(0,760),(142,704),(276,555),(442,544)]
    curl = [(442,544),(549,540),(646,449),(642,352)]
    crown = [(642,352),(637,262),(530,263),(493,338)]
    return_curve = [(493,338),(454,398),(502,451),(568,460)]
    edge = []
    for seg in (outer, inner):
        edge.extend(bezier(*seg, i/80) for i in range(81))
    wavepts = edge + [(1024,1024),(0,1024)]
    im.poly(wavepts, (17,102,139))
    # Inner rolling body, layered as broad smooth bands.
    innerwave = []
    for seg in (crest, curl, crown, return_curve):
        innerwave.extend(bezier(*seg, i/55) for i in range(56))
    innerwave += [(568,460),(684,500),(777,668),(1024,713),(1024,1024),(0,1024)]
    im.poly(innerwave, (23,72,129))
    # Luminous turquoise face sweeping toward the curled lip.
    glow = [(12,748),(160,697),(284,579),(431,570),(537,562),(612,491),(610,402),
            (603,333),(549,313),(518,353),(488,404),(528,437),(586,440),
            (656,451),(713,545),(776,678),(1008,717),(1024,842),(0,887)]
    im.poly(glow, (26,169,183))
    # Deep violet underside gives the wave a dramatic rolled shadow.
    shadow = []
    shadow_curves = [((0,849),(180,793),(305,710),(443,650)),
                     ((443,650),(535,623),(596,552),(680,518)),
                     ((680,518),(733,533),(767,612),(820,698)),
                     ((820,698),(887,720),(956,743),(1024,754))]
    for seg in shadow_curves:
        shadow.extend(bezier(*seg, i/70) for i in range(71))
    shadow += [(1024,1024),(0,1024)]
    im.poly(shadow, (36,48,111))
    # Bright foam contours trace the curl and forward shoulder.
    for seg, width, col in [(curl,17,(113,251,231)),(crown,20,(195,255,230)),
                            (return_curve,13,(105,239,227)),(crest,8,(76,218,220))]:
        pts = [bezier(*seg, i/150) for i in range(151)]
        for a,b in zip(pts,pts[1:]):
            im.line(*a,*b,width,col)
    # Spray arcs and scattered droplets radiate from the luminous break.
    for x,y,r in [(439,537,11),(471,504,7),(500,478,5),(533,459,8),(574,445,5),
                  (605,412,7),(604,376,5),(583,341,6),(548,327,4),(483,579,5),
                  (389,571,4),(342,596,6),(282,634,4),(661,472,5)]:
        im.disc(x,y,r,(177,255,238))
    # Flow lines add directional speed across the face.
    for a,b,c,d in [((70,766),(171,725),(246,663),(328,645)),
                    ((154,811),(269,761),(364,702),(477,675)),
                    ((246,850),(374,797),(486,740),(586,690)),
                    ((644,565),(701,588),(730,636),(754,680))]:
        pts=[bezier(a,b,c,d,i/100) for i in range(101)]
        for p,q in zip(pts,pts[1:]): im.line(*p,*q,3,(74,211,211))

    # A clearly readable boat and lone rider, lifted against the bright sea.
    im.poly([(213,725),(347,719),(326,754),(242,755)], (8,16,35))
    im.line(228,723,339,722,5,(239,175,107))
    im.disc(280,683,12,(9,17,35))
    im.line(280,697,281,723,9,(9,17,35))
    im.line(279,704,260,716,6,(9,17,35))
    im.line(282,704,301,714,6,(9,17,35))
    im.line(277,720,267,730,6,(9,17,35))
    im.line(284,720,295,728,6,(9,17,35))
    # Fine moonlit edge on hull and seat.
    im.line(244,755,326,754,3,(239,167,99))

    out = os.environ.get('OUTPUT_PATH', '/output/entry.png')
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    with open(out, 'wb') as f:
        f.write(im.png())


if __name__ == '__main__':
    main()
