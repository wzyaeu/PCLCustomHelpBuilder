---
title: "页脚"
index: 3
---

# 页脚

你可以创建`文档目录/.config/footer.md`来修改页脚。

## 动态替换语法

动态替换语法是页脚的特殊语法，可以替换各类数据。

```markdown
[](post!...)
[](post!...!...)
[](attr!...)
```

### 文章元数据替换

获取文章的元数据。

格式：
```markdown
[](post!{attr})
[](post!{attr}!{default})
[](post!{attr1}!{attr2}!...!{default})
```

`[](post!{attr})`格式用于获取文章元数据，例如元数据
```markdown
---
docattr: aaa
---
```
使用`[](post!docattr)`即可替换成`aaa`。格式为纯文本。

---

`[](post!{attr}!{default})`格式用于获取文章元数据并指定默认文本，例如元数据
```markdown
---
docattr1: a1
---
```
使用`[](post!docattr2!a2)`即可替换成默认文本`a2`。

---

`[](post!{attr1}!{attr2}!...!{default})`格式用于文章元数据更复杂的获取，根据顺序依次获取。例如元数据
```markdown
---
docattr1: a1
docattr2: a2
---
```
使用`[](post!docattr3!docattr2!docattr1!d)`，按照顺序最终获取到`docattr2`的`a2`。

使用`[](post!docattr3!docattr1!docattr2!d)`，按照顺序最终获取到`docattr1`的`a1`。

### 配置元数据替换

获取项目的数据。

格式：
```markdown
[](attr!{key})
```

`[](attr!{key})`格式用于获取项目的数据，`{key}`为键。目前有以下键可替换：
- `name`: PCLCustomHelpBuilder的名称。
- `version`: PCLCustomHelpBuilder的版本。

例如`[](attr!name)`替换为`PCLCustomHelpBuilder`