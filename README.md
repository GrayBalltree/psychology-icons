# 心理学图标库

一组心理学 / 神经科学主题的图标，初衷很简单：**做 PPT 的时候，能有简明扼要的图标直接可用。**

**在线使用（点击图标即可复制，直接粘贴进 PPT）：**
https://grayballtree.github.io/psychology-icons/

## 这里有什么

169 个图标，全部为 **PNG · 512×512**，风格统一（手绘涂鸦风、深蓝描边、柔和配色）；其中 127 个为透明背景，45 幅「ZJU NOBEL」手绘科学肖像为纸面底色。

## 分类（10 个，共 169 个图标）

| 分类 | 数量 |
|---|---|
| 神经科学 | 21 |
| 神经技术 | 9 |
| 测量与统计 | 11 |
| 认知与情绪 | 14 |
| 心理健康与治疗 | 28 |
| 人格与社会 | 23 |
| 发展与生命周期 | 6 |
| 计算与工程心理学 | 4 |
| 心理学名家 | 8 |
| ZJU NOBEL | 45 |

## 维护：新增图标

仓库根目录有一键脚本 `add-icon.py`（需要 python3 + Pillow）：

```bash
# 常规图标（非正方形自动透明补边，不裁内容）
python3 add-icon.py --slug attention --zh 注意 --cat 认知过程 --img ~/Downloads/注意.png

# 肖像类（居中裁剪）
python3 add-icon.py --slug nobel-46 --zh "NOBEL 46" --cat "ZJU NOBEL" --img 46.jpeg --fit crop

# 加 --push 自动提交并推送（Pages 1-2 分钟后自动部署）
python3 add-icon.py --slug xxx --zh 某某 --cat 某分类 --img 某图.png --push
```

脚本会自动：处理图片为 512×512 PNG（保留透明背景）→ 写入 manifest2.json →
生成 256px WebP 缩略图 → 更新本 README 的统计与分类表。
