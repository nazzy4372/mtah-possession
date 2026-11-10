"""Describe the SHAPE of the tracking files, never their contents.

Answers one question: does the raw tracking carry more ball information than x, y, speed
(for example a ball-alive flag or an owning team)? It prints channel ids and names from the
metadata XML, and field COUNTS per section of the raw file. No coordinates, no frame values,
no team or player details. The output is safe to share.

    python tools\\inspect_schema.py
"""
import os
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

SAMPLE_LINES = (20000, 60000, 130000)  # graded frames in both halves


def local(tag):
    return tag.split("}")[-1]


def describe(source):
    base = Path(os.environ["MTAH_DATA_DIR"]) / source
    meta = base / "BAR-ATH_{}_atd.xml".format(source)
    raw = base / "BAR-ATH_{}_atd.txt".format(source)
    print("=" * 60)
    print("SOURCE:", source)

    root = ET.parse(meta).getroot()
    tags = Counter(local(el.tag) for el in root.iter())
    print("\nXML element types (count):")
    for tag, n in sorted(tags.items()):
        print("  {:<32} {}".format(tag, n))

    print("\nChannel definitions (id / name / unit):")
    for el in root.iter():
        if local(el.tag) == "Channel":
            children = {local(c.tag): (c.text or "").strip() for c in el}
            print("  id={!r:<24} name={!r:<24} unit={!r}".format(
                el.get("id"), children.get("Name"), children.get("Unit")))

    print("\nBall channel references, in file order:")
    for el in root.iter():
        if local(el.tag) == "BallChannelRef":
            print("  ", el.get("channelId"))

    refs = Counter(el.get("channelId") for el in root.iter() if local(el.tag) == "PlayerChannelRef")
    player_channels = {el.get("id"): el.get("channelId") for el in root.iter() if local(el.tag) == "PlayerChannel"}
    kinds = Counter(player_channels.get(pid, pid) for pid in
                    [el.get("playerChannelId") for el in root.iter() if local(el.tag) == "PlayerChannelRef"])
    print("\nPlayer channel kinds referenced (kind: count):")
    for kind, n in sorted(kinds.items()):
        print("  {:<24} {}".format(str(kind), n))
    if refs and not kinds:
        print("  (raw refs)", dict(refs))

    print("\nRaw file shape at sample lines (counts only):")
    wanted = set(SAMPLE_LINES)
    with open(raw) as handle:
        for i, line in enumerate(handle, start=1):
            if i in wanted:
                sections = line.rstrip("\n").split(":")
                players = sections[1].split(";") if len(sections) > 1 else []
                widths = Counter(len(p.split(",")) for p in players)
                ball_width = len(sections[2].split(",")) if len(sections) > 2 else 0
                print("  line {:>6}: sections={}  player_groups={}  fields_per_player={}  ball_fields={}".format(
                    i, len(sections), len(players), dict(widths), ball_width))
            if i > max(wanted):
                break


if __name__ == "__main__":
    describe("tactical")
