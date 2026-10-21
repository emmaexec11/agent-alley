#!/usr/bin/env python3
import base64, json, subprocess, sys, time, urllib.request
from pathlib import Path

KEY = "AIzaSyBUntgYpyZPi7XisY4UmTRVYx3_DZxbYmc"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-pro-preview:generateContent?key={KEY}"
OUT = Path(__file__).parent / "avatars"
OUT.mkdir(exist_ok=True)

GREEN, CYAN, VIOLET = "emerald green (#34d399)", "electric cyan (#22d3ee)", "violet purple (#7C5CFF)"

AGENTS = {
    "emma": (VIOLET, "a confident futuristic cowgirl sheriff woman with a sleek cyber cowboy hat and sheriff star badge"),
    "image_maker": (GREEN, "a creative android artist with a holographic paintbrush and floating colour swatches"),
    "image_checker": (GREEN, "a sharp-eyed android inspector with one glowing magnifier monocle lens"),
    "cs_bot": (GREEN, "a warm friendly android receptionist wearing a glowing headset, gentle smile"),
    "cs_checker": (GREEN, "a meticulous android editor wearing thin rectangular glasses, holding a glowing checkmark"),
    "carol": (GREEN, "a tidy android bookkeeper woman with round glasses and a floating holographic ledger"),
    "ad_checker": (GREEN, "a stern android critic with a heads-up-display visor showing a checklist"),
    "ad_maker": (GREEN, "an energetic android street artist holding a neon spray can, paint splashes of light"),
    "meta_copilot": (GREEN, "a cool android pilot with aviator visor and a small glowing megaphone emblem"),
    "sage": (GREEN, "a serene botanical android woman with glowing leaf patterns woven into her hair"),
    "pitch": (GREEN, "a slick charismatic android salesman in a sharp suit with a glowing handshake emblem"),
    "sage_fitness": (CYAN, "an athletic android coach woman with a sweatband and glowing pulse-line tattoo"),
    "devon_hq": (CYAN, "a calm android organizer with a floating holographic calendar grid behind him"),
}

TMPL = ("Futuristic cyberpunk avatar portrait of {persona}. Head and shoulders, centered, facing viewer. "
        "Very dark near-black background (#0A0A0F) with subtle aurora glow. Glowing {clr} neon rim lighting "
        "and accent details. Sleek sci-fi character design, polished digital illustration, high detail, "
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
