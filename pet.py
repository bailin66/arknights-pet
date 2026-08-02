"""
arknights-pet v0.1 — 明日方舟桌面宠物
角色：苇草 (Reed)
"""

import sys
import math
import os
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QSystemTrayIcon
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QIcon


# ── 路径常量 ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, "images", "立绘_苇草_2.png")

# ── 宠物参数 ─────────────────────────────────────────────
PET_HEIGHT = 350          # 宠物显示高度 (像素)
FLOAT_AMPLITUDE = 8       # 浮动幅度 (像素)
FLOAT_SPEED = 2.5         # 浮动速度 (周期秒数)
CLICK_JUMP_HEIGHT = -25   # 点击跳起高度 (像素)


class PetWindow(QWidget):
    """桌面宠物主窗口 — 苇草"""

    def __init__(self):
        super().__init__()

        # ── 加载并缩放角色图片 ──
        self.original_pixmap = QPixmap(IMAGE_PATH)
        if self.original_pixmap.isNull():
            raise FileNotFoundError(f"无法加载图片: {IMAGE_PATH}")

        # 按高度等比缩放
        scaled = self.original_pixmap.scaledToHeight(
            PET_HEIGHT, Qt.SmoothTransformation
        )
        self.pet_width = scaled.width()
        self.pet_height = scaled.height()
        self.pet_pixmap = scaled

        # ── 窗口基础设置 ──
        self._setup_window()

        # ── 动画状态 ──
        self._base_x = 100          # 动画基准 X (拖拽后更新)
        self._base_y = 100          # 动画基准 Y (拖拽后更新)
        self._float_offset = 0.0    # 当前浮动偏移量
        self._float_phase = 0.0     # 浮动相位 (弧度)
        self._click_offset = 0.0    # 点击跳起偏移
        self._dragging = False      # 是否正在拖拽
        self._drag_offset = QPoint()
        self._press_pos = None      # 记录按下位置，判定点击/拖拽

        # ── 定时器 ──
        self._idle_timer = QTimer(self)
        self._idle_timer.timeout.connect(self._update_idle)
        self._idle_timer.start(16)  # ~60fps

        # ── 系统托盘 ──
        self._setup_tray()

        # ── 右键菜单 ──
        self._setup_menu()

        # ── 初始位置 ──
        screen = QApplication.primaryScreen().availableGeometry()
        self._base_x = screen.right() - self.pet_width - 80
        self._base_y = screen.bottom() - self.pet_height - 60
        self._sync_position()

    # ═══════════════════════════════════════════════════════
    # 窗口设置
    # ═══════════════════════════════════════════════════════

    def _setup_window(self):
        """初始化和配置窗口属性"""
        self.setWindowFlags(
            Qt.FramelessWindowHint      # 无边框
            | Qt.WindowStaysOnTopHint   # 始终置顶
            | Qt.Tool                   # 不显示在任务栏
            | Qt.SubWindow             # 不抢焦点
        )
        self.setAttribute(Qt.WA_TranslucentBackground)   # 透明背景
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)   # 显示但不激活

        self.setFixedSize(self.pet_width, self.pet_height)

    # ═══════════════════════════════════════════════════════
    # 系统托盘
    # ═══════════════════════════════════════════════════════

    def _setup_tray(self):
        """创建系统托盘图标"""
        # 用角色图片缩小版作为托盘图标
        tray_icon = self.original_pixmap.scaledToHeight(
            64, Qt.SmoothTransformation
        )
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(tray_icon))
        self.tray_icon.setToolTip("苇草 - 桌面宠物")

        # 托盘菜单
        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示 / 隐藏")
        show_action.triggered.connect(self._toggle_visible)
        quit_action = tray_menu.addAction("退出")
        quit_action.triggered.connect(self._quit_app)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        """托盘图标被双击时切换显示"""
        if reason == QSystemTrayIcon.DoubleClick:
            self._toggle_visible()

    def _toggle_visible(self):
        """切换宠物显示/隐藏"""
        if self.isVisible():
            self.hide()
        else:
            self.show()

    # ═══════════════════════════════════════════════════════
    # 右键菜单
    # ═══════════════════════════════════════════════════════

    def _setup_menu(self):
        """创建右键快捷菜单"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        """弹出右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2a2a2a;
                border: 1px solid #555;
                color: #ddd;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #c0392b;
            }
        """)

        hide_action = menu.addAction("💤 隐藏")
        hide_action.triggered.connect(self.hide)

        menu.addSeparator()

        about_action = menu.addAction("ℹ 关于 苇草 v0.1")
        about_action.triggered.connect(self._show_about)

        quit_action = menu.addAction("✕ 退出")
        quit_action.triggered.connect(self._quit_app)

        menu.exec_(self.mapToGlobal(pos))

    def _show_about(self):
        """显示关于信息 — 简易气泡"""
        from PyQt5.QtWidgets import QToolTip
        QToolTip.showText(
            self.mapToGlobal(QPoint(0, -40)),
            "🔥 苇草 · Reed\n"
            "明日方舟桌面宠物 v0.1\n"
            "种族：德拉克 | 职业：先锋",
            self
        )

    # ═══════════════════════════════════════════════════════
    # 空闲动画 (浮动)
    # ═══════════════════════════════════════════════════════

    def _update_idle(self):
        """每帧更新：浮动 + 回弹"""
        dt = 16 / 1000.0  # 帧间隔秒数
        self._float_phase += dt * (2 * math.pi / FLOAT_SPEED)
        self._float_offset = math.sin(self._float_phase) * FLOAT_AMPLITUDE

        # 点击跳跃回弹
        if self._click_offset < -0.5:
            self._click_offset += 1.2   # 向上回弹
        elif self._click_offset < 0:
            self._click_offset = 0.0    # 归位

        self._sync_position()

    def _sync_position(self):
        """将逻辑坐标同步到窗口位置"""
        y = int(self._base_y + self._float_offset + self._click_offset)
        self.move(self._base_x, y)

    # ═══════════════════════════════════════════════════════
    # 点击动画
    # ═══════════════════════════════════════════════════════

    def _start_click_animation(self):
        """点击触发跳跃 — 偏移量由 _update_idle 逐帧回弹"""
        self._click_offset = CLICK_JUMP_HEIGHT

    # ═══════════════════════════════════════════════════════
    # 鼠标事件 (拖拽)
    # ═══════════════════════════════════════════════════════

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_offset = event.globalPos() - self.pos()
            self._press_pos = event.globalPos()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging:
            new_pos = event.globalPos() - self._drag_offset
            self._base_x = new_pos.x()
            self._base_y = new_pos.y()
            # 拖拽中暂停浮动
            self._float_phase = math.pi / 2
            self._float_offset = FLOAT_AMPLITUDE
            self._sync_position()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            was_drag = self._dragging
            self._dragging = False
            self.setCursor(Qt.ArrowCursor)

            if was_drag and self._press_pos is not None:
                # 判定：移动距离 < 5px 视为点击
                dist = (event.globalPos() - self._press_pos)
                moved = abs(dist.x()) + abs(dist.y())
                if moved < 5:
                    self._start_click_animation()

            self._press_pos = None
        super().mouseReleaseEvent(event)

    # ═══════════════════════════════════════════════════════
    # 绘制
    # ═══════════════════════════════════════════════════════

    def paintEvent(self, event):
        """绘制角色图像"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(0, 0, self.pet_pixmap)
        painter.end()

    # ═══════════════════════════════════════════════════════
    # 退出
    # ═══════════════════════════════════════════════════════

    def _quit_app(self):
        """完全退出应用"""
        self.tray_icon.hide()
        QApplication.quit()


# ═══════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("arknights-pet")
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出，保留托盘

    pet = PetWindow()
    pet.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
