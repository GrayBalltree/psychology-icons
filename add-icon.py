#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心理学图标库 · 一键新增图标

用法:
  python3 add-icon.py --slug attention --zh 注意 --cat 认知过程 --img ~/Downloads/注意.png
  python3 add-icon.py --slug nobel-46 --zh NOBEL 46 --cat "ZJU NOBEL" --img 46.jpeg --fit crop

流程: 处理图片(512x512) -> 写入 manifest2.json -> 生成 WebP 缩略图 -> 更新 README -> 可选提交推送
"""
import argparse
import json
import os
import re
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SIZE = 512
THUMB = 256


def die(msg):
    sys.exit(f"错误: {msg}")


def process_image(src, slug, fit):
    im = Image.open(src)
    has_alpha = im.mode in ("RGBA", "LA", "PA") and (im.mode != "PA" or "transparency" in im.info)
    if im.mode == "P" and "transparency" in im.info:
        im = im.convert("RGBA")
        has_alpha = True
    elif im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if has_alpha else "RGB")
    w, h = im.size
    s = min(w, h)
    if fit == "crop":
        im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    else:  # pad：补边成正方形，不裁切内容
        canvas = Image.new("RGBA" if has_alpha else "RGB", (s, s),
                           (0, 0, 0, 0) if has_alpha else (255, 255, 255))
        canvas.paste(im, ((s - w) // 2, (s - h) // 2))
        im = canvas
    return im.resize((SIZE, SIZE), Image.LANCZOS)


def add_to_manifest(slug, zh, cat):
    p = os.path.join(ROOT, "manifest2.json")
    data = json.load(open(p, encoding="utf-8"))
    if any(d["slug"] == slug for d in data):
        die(f"slug '{slug}' 已存在")
    data.append({"slug": slug, "zh": zh, "cat": cat, "path": f"original-hd/{slug}.png"})
    text = open(p, encoding="utf-8").read()
    entry = (' {\n  "slug": "%s",\n  "zh": "%s",\n  "cat": "%s",\n  "path": "original-hd/%s.png"\n }'
             % (slug, zh, cat, slug))
    pos = text.rstrip().rfind("]")
    assert text[:pos].rstrip().endswith("}")
    new = text[:pos].rstrip() + ",\n" + entry + "\n]\n"
    open(p, "w", encoding="utf-8").write(new)
    json.load(open(p, encoding="utf-8"))  # 校验
    return len(data)


def make_thumb(slug):
    im = Image.open(os.path.join(ROOT, "original-hd", f"{slug}.png"))
    im.thumbnail((THUMB, THUMB), Image.LANCZOS)
    im.save(os.path.join(ROOT, "thumbs", f"{slug}.webp"), "WEBP", quality=78, method=6)


def update_readme():
    p = os.path.join(ROOT, "README.md")
    md = open(p, encoding="utf-8").read()
    data = json.load(open(os.path.join(ROOT, "manifest2.json"), encoding="utf-8"))
    total = len(data)
    cats, order = {}, []
    for d in data:
        if d["cat"] not in cats:
            order.append(d["cat"])
        cats[d["cat"]] = cats.get(d["cat"], 0) + 1

    def count_transparent():
        n = 0
        for f in os.listdir(os.path.join(ROOT, "original-hd")):
            if not f.endswith(".png"):
                continue
            im = Image.open(os.path.join(ROOT, "original-hd", f))
            if im.mode in ("RGBA", "LA") and im.getextrema()[-1][0] < 255:
                n += 1
        return n

    transparent = count_transparent()
    nobel = sum(1 for d in data if d["slug"].startswith("nobel-"))

    md = re.sub(r"^## 分类（\d+ 个，共 \d+ 个图标）",
                f"## 分类（{len(cats)} 个，共 {total} 个图标）", md, flags=re.M)
    intro_pat = re.compile(
        r"^\d+ 个图标，全部为 \*\*PNG · 512×512\*\*.*?纸面底色。",
        re.S | re.M)
    intro = (f"{total} 个图标，全部为 **PNG · 512×512**，风格统一"
             f"（手绘涂鸦风、深蓝描边、柔和配色）；其中 {transparent} 个为透明背景"
             f"，{nobel} 幅「ZJU NOBEL」手绘科学肖像为纸面底色。")
    md = intro_pat.sub(intro, md, count=1)

    rows = "\n".join(f"| {c} | {cats[c]} |" for c in order)
    tbl_pat = re.compile(r"\| 分类 \| 数量 \|\n\|[-|]+\|\n(?:\|[^\n]+\|\n)+")
    md = tbl_pat.sub("| 分类 | 数量 |\n|---|---|\n" + rows + "\n", md, count=1)
    open(p, "w", encoding="utf-8").write(md)


def main():
    ap = argparse.ArgumentParser(description="心理学图标库一键新增图标")
    ap.add_argument("--slug", required=True, help="英文标识，如 attention、nobel-46")
    ap.add_argument("--zh", required=True, help="中文显示名，如 注意 / NOBEL 46")
    ap.add_argument("--cat", required=True, help="分类名，须与现有分类一致或新分类")
    ap.add_argument("--img", required=True, help="源图片路径（png/jpeg 均可）")
    ap.add_argument("--fit", choices=["pad", "crop"], default="pad",
                    help="非正方形图片处理方式：pad 补边(默认,不裁内容) / crop 居中裁剪(适合肖像)")
    ap.add_argument("--push", action="store_true", help="提交并推送到 GitHub")
    a = ap.parse_args()

    if not os.path.exists(a.img):
        die(f"找不到图片 {a.img}")
    if not re.fullmatch(r"[a-z0-9-]+", a.slug):
        die("slug 只能用小写字母、数字、连字符")

    img = process_image(a.img, a.slug, a.fit)
    img.save(os.path.join(ROOT, "original-hd", f"{a.slug}.png"), optimize=True)
    n = add_to_manifest(a.slug, a.zh, a.cat)
    make_thumb(a.slug)
    update_readme()
    print(f"完成: {a.slug} ({a.zh}) 已加入分类「{a.cat}」，全库现有 {n} 个图标")

    if a.push:
        subprocess.run(["git", "-C", ROOT, "add", "-A"], check=True)
        subprocess.run(["git", "-C", ROOT, "commit", "-m",
                        f"新增图标: {a.zh} ({a.slug})"], check=True)
        subprocess.run(["git", "-C", ROOT, "push"], check=True)
        print("已提交并推送，Pages 将在 1-2 分钟后自动部署")


if __name__ == "__main__":
    main()
