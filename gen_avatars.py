#!/usr/bin/env python3
import base64, json, subprocess, sys, time, urllib.request
from pathlib import Path

KEY = "AIzaSyBUntgYpyZPi7XisY4UmTRVYx3_DZxbYmc"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-pro-preview:generateContent?key={KEY}"
OUT = Path(__file__).parent / "avatars"
OUT.mkdir(exist_ok=True)

GREEN, CYAN, VIOLET = "emerald green (#34d399)", "electric cyan (#22d3ee)", "violet purple (#7C5CFF)"

AGENTS = {
    "emma": (VIOLET, "a confident cheerful futuristic cowgirl sheriff woman with a sleek cyber cowboy hat and sheriff star badge"),
    "image_maker": (GREEN, "a creative young artist with paint-smudged cheeks, a holographic paintbrush and floating colour swatches"),
    "image_checker": (GREEN, "a bright curious inspector with a fun oversized magnifier monocle over one eye"),
    "cs_bot": (GREEN, "a warm friendly receptionist woman wearing a glowing headset, mid-laugh"),
    "cs_checker": (GREEN, "a kind meticulous editor with thin rectangular glasses and a reassuring smile"),
    "carol": (GREEN, "a cosy grandmotherly bookkeeper with round glasses, cardigan with neon trim, and a knowing smile"),
    "ad_checker": (GREEN, "a sharp but friendly film-critic type with a stylish heads-up-display visor pushed up on his forehead"),
    "ad_maker": (GREEN, "an energetic grinning street artist holding a neon spray can, playful paint splashes of light"),
    "meta_copilot": (GREEN, "a cool easygoing pilot with aviator sunglasses pushed up and a flight jacket"),
    "sage": (GREEN, "a serene gentle botanist woman with glowing leaf patterns woven into her braided hair"),
    "pitch": (GREEN, "a charismatic winking salesman in a sharp suit with a loosened neon tie"),
    "sage_fitness": (CYAN, "an upbeat athletic coach woman with a sweatband, ponytail and encouraging grin"),
    "devon_hq": (CYAN, "a calm friendly organizer guy with tousled hair and a small floating holographic calendar"),
}

TMPL = ("Friendly stylized 3D avatar portrait of {persona}, in the style of a charming animated movie "
        "character. Warm genuine smile, big expressive friendly eyes, soft rounded features, likeable and "
        "approachable — NOT uncanny, NOT robotic skin, NOT creepy. Head and shoulders, centered, facing "
        "viewer. Very dark near-black background (#0A0A0F) with subtle aurora glow. Glowing {clr} neon rim "
        "lighting and futuristic accent details on clothing. Full-bleed edge to edge, no frame or border, "
        "square format, no text, no watermark.")


def gen(aid, clr, persona):
    body = json.dumps({
        "contents": [{"parts": [{"text": TMPL.format(persona=persona, clr=clr)}]}],
        "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1"}},
    }).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.load(r)
    for part in resp["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            raw = OUT / f"{aid}_raw.png"
            raw.write_bytes(base64.b64decode(part["inlineData"]["data"]))
            final = OUT / f"{aid}.jpg"
            subprocess.run(["sips", "-Z", "256", "-s", "format", "jpeg", "-s", "formatOptions", "80",
                            str(raw), "--out", str(final)], capture_output=True, check=True)
            raw.unlink()
            return final.stat().st_size
    raise RuntimeError("no image in response")


for aid, (clr, persona) in AGENTS.items():
    if (OUT / f"{aid}.jpg").exists():
        print(f"{aid}: exists, skip")
        continue
    for attempt in (1, 2):
        try:
            sz = gen(aid, clr, persona)
            print(f"{aid}: ok {sz}b")
            break
        except Exception as e:
            print(f"{aid}: attempt {attempt} failed: {e}")
            time.sleep(5)
    else:
        sys.exit(f"FAILED {aid}")
print("ALL DONE")
