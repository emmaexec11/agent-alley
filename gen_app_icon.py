"""
Agent Alley app icon generator.
Deep-space CoS orb cluster — one violet core, 5 orbital agents.
Writes app-icon-1024.png / 512 / 192 / apple-touch-180 into dashboard/.
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
S = 1024
BG_TOP = (14, 10, 32)
BG_BOT = (3, 2, 10)

CORE = (139, 108, 255)
RING = (124, 92, 255, 90)

AGENTS = [
    (240,  90, 190),
    (120, 220, 255),
    (255, 170, 90),
    (160, 255, 180),
    (255, 110, 110),
]

def radial_bg(size):
    img = Image.new("RGB", (size, size), BG_BOT)
    cx, cy = size/2, size/2
    maxr = math.hypot(cx, cy)
    px = img.load()
    for y in range(size):
        for x in range(size):
            d = math.hypot(x-cx, y-cy) / maxr
            t = min(1.0, d*1.1)
            r = int(BG_TOP[0]*(1-t) + BG_BOT[0]*t)
            g = int(BG_TOP[1]*(1-t) + BG_BOT[1]*t)
            b = int(BG_TOP[2]*(1-t) + BG_BOT[2]*t)
            px[x,y] = (r,g,b)
    return img

def glow_dot(size, color, radius, blur):
    layer = Image.new("RGBA", (size, size), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    cx, cy = size/2, size/2
    d.ellipse([cx-radius, cy-radius, cx+radius, cy+radius],
              fill=(*color, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return layer

def put_glow(canvas, cx, cy, color, radius, blur, alpha=255):
    layer = Image.new("RGBA", canvas.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx-radius, cy-radius, cx+radius, cy+radius],
              fill=(*color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(layer)

def main():
    img = radial_bg(S).convert("RGBA")

    cx = cy = S/2
    orbit_r = S*0.30

    put_glow(img, cx, cy, CORE, S*0.18, blur=60, alpha=120)
    put_glow(img, cx, cy, CORE, S*0.11, blur=20, alpha=220)

    ring = Image.new("RGBA", img.size, (0,0,0,0))
    rd = ImageDraw.Draw(ring)
    rw = 3
    rd.ellipse([cx-orbit_r, cy-orbit_r, cx+orbit_r, cy+orbit_r],
               outline=RING, width=rw)
    ring = ring.filter(ImageFilter.GaussianBlur(1.2))
    img.alpha_composite(ring)

    rd2 = ImageDraw.Draw(img)
    rd2.ellipse([cx-S*0.085, cy-S*0.085, cx+S*0.085, cy+S*0.085],
                fill=(255,255,255,255))
    put_glow(img, cx, cy, (255,255,255), S*0.085, blur=4, alpha=180)
    rd2 = ImageDraw.Draw(img)
    rd2.ellipse([cx-S*0.075, cy-S*0.075, cx+S*0.075, cy+S*0.075],
                fill=CORE)

    for i, color in enumerate(AGENTS):
        ang = -math.pi/2 + i*(2*math.pi/5)
        ox = cx + orbit_r*math.cos(ang)
        oy = cy + orbit_r*math.sin(ang)
        put_glow(img, ox, oy, color, S*0.065, blur=28, alpha=170)
        put_glow(img, ox, oy, color, S*0.045, blur=8,  alpha=255)
        d = ImageDraw.Draw(img)
        d.ellipse([ox-S*0.035, oy-S*0.035, ox+S*0.035, oy+S*0.035],
                  fill=(255,255,255,255))
        d.ellipse([ox-S*0.028, oy-S*0.028, ox+S*0.028, oy+S*0.028],
                  fill=color)

    img.save(os.path.join(HERE, "app-icon-1024.png"))
    img.resize((512,512), Image.LANCZOS).save(os.path.join(HERE,"app-icon-512.png"))
    img.resize((192,192), Image.LANCZOS).save(os.path.join(HERE,"app-icon-192.png"))
    img.resize((180,180), Image.LANCZOS).save(os.path.join(HERE,"apple-touch-icon.png"))
    print("wrote app-icon-1024/512/192 + apple-touch-icon.png")

if __name__ == "__main__":
    main()
