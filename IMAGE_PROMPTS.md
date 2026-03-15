# ネコスイ 立ち絵生成プロンプト

## 共通スタイル指定（毎回先頭につける）

```
cute tabby cat, game character sprite, chibi style, simple clean illustration,
white background, flat color, soft shading, no outline clutter,
full body visible, centered composition
```

---

## 18枚のプロンプト一覧

### sit（座ってる）× normal
```
cute tabby cat sitting upright, looking forward, calm neutral expression,
game character sprite, chibi style, simple clean illustration, white background
```

### sit × happy
```
cute tabby cat sitting upright, eyes narrowed happily, slight smile, content expression,
game character sprite, chibi style, simple clean illustration, white background
```

### sit × annoyed
```
cute tabby cat sitting upright, ears flattened back, displeased expression, narrowed eyes,
game character sprite, chibi style, simple clean illustration, white background
```

---

### lie（寝転んでる）× normal
```
cute tabby cat lying on side, relaxed, eyes half open, calm expression,
game character sprite, chibi style, simple clean illustration, white background
```

### lie × happy
```
cute tabby cat lying on side, eyes closed happily, purring expression, relaxed smile,
game character sprite, chibi style, simple clean illustration, white background
```

### lie × annoyed
```
cute tabby cat lying on side, ears back, one eye open glaring, unamused expression,
game character sprite, chibi style, simple clean illustration, white background
```

---

### curl（丸まって寝てる）× normal
```
cute tabby cat curled up into a ball, sleeping peacefully, eyes closed,
game character sprite, chibi style, simple clean illustration, white background
```

### curl × happy
```
cute tabby cat curled up, sleeping with a tiny smile, very relaxed, cozy,
game character sprite, chibi style, simple clean illustration, white background
```

### curl × annoyed
```
cute tabby cat curled up tightly, tail wrapped around body, ignoring, sulking pose,
game character sprite, chibi style, simple clean illustration, white background
```

---

### stand（立ってる）× normal
```
cute tabby cat standing on all fours, alert, looking forward, neutral expression,
game character sprite, chibi style, simple clean illustration, white background
```

### stand × happy
```
cute tabby cat standing up excitedly, tail raised high, ears perked, happy expression,
game character sprite, chibi style, simple clean illustration, white background
```

### stand × annoyed
```
cute tabby cat standing with fur slightly puffed, ears flat, hissing pose,
game character sprite, chibi style, simple clean illustration, white background
```

---

### nuzzle（すりすりしてる）× normal
```
cute tabby cat rubbing its cheek affectionately, nuzzling pose, eyes closed gently,
game character sprite, chibi style, simple clean illustration, white background
```

### nuzzle × happy
```
cute tabby cat nuzzling and rubbing its face, very affectionate, eyes closed with joy,
game character sprite, chibi style, simple clean illustration, white background
```

### nuzzle × annoyed
```
cute tabby cat doing a half-hearted nuzzle, looking away, tsundere expression,
game character sprite, chibi style, simple clean illustration, white background
```

---

### groom（毛づくろい中）× normal
```
cute tabby cat grooming itself, licking paw, ignoring surroundings, focused expression,
game character sprite, chibi style, simple clean illustration, white background
```

### groom × happy
```
cute tabby cat grooming contentedly, relaxed and happy while licking paw,
game character sprite, chibi style, simple clean illustration, white background
```

### groom × annoyed
```
cute tabby cat aggressively grooming, avoiding eye contact, clearly ignoring someone,
game character sprite, chibi style, simple clean illustration, white background
```

---

## 毛色差分の指定語

同じプロンプトの `tabby cat` の部分を差し替えるだけ：

| 毛色 | 差し替え語 |
|------|-----------|
| キジトラ（デフォルト） | `tabby cat` |
| しろ | `white cat` |
| くろ | `black cat` |
| みけ | `calico cat` |
| サビ | `tortoiseshell cat` |

---

## 生成のコツ

- サイズ: **512×512** か **1024×1024** の正方形で生成
- 背景が白じゃなかったら「remove background」で透過にする
- ポーズのブレが大きい場合は `--seed` を固定して再生成
- 全部同じシードで生成すると顔の一貫性が上がりやすい
