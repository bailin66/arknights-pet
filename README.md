# 🔥 arknights-pet

> 明日方舟桌面宠物 — 使用 PyQt5 开发

## v0.1 · 苇草 (Reed)

![version](https://img.shields.io/badge/version-v0.1-red)
![python](https://img.shields.io/badge/python-3.8+-blue)

### 角色信息

| 项目 | 内容 |
|------|------|
| **代号** | 苇草 (Reed) |
| **种族** | 德拉克 (Draco) |
| **职业** | 先锋 ★★★★★ |
| **画师** | STAR影法师 |
| **CV** | 能登麻美子 |

> *"就是叫我苇草吧……就像池边的芦苇，怎么样，都可以的……"*

### 功能 (v0.1)

- ✅ 桌面角色展示（透明背景、始终置顶）
- ✅ 空闲浮动动画（呼吸感上下摆动）
- ✅ 鼠标拖拽移动位置
- ✅ 左键点击触发跳跃互动
- ✅ 右键菜单（隐藏 / 关于 / 退出）
- ✅ 系统托盘驻留，双击托盘图标切换显示

### 安装与运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行
python main.py
```

### 项目结构

```
arknights-pet/
├── main.py           # 入口
├── pet.py            # 宠物核心逻辑
├── requirements.txt  # 依赖列表
├── images/
│   └── 立绘_苇草_2.png
└── README.md
```

### 路线图

- [x] `v0.1` — 苇草基础桌面宠物（静态立绘 + 浮动动画）
- [ ] `v0.2` — 多动作帧动画 / 语音播放
- [ ] `v0.3` — 更多干员角色支持
- [ ] `v0.4` — 交互对话系统

---

🤖 Developed with PyCharm + DeepSeek
