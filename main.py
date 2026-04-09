from core.plugin import BasePlugin, PluginContext
from .live2d_model import init_live2d, dispose_live2d, Live2DModel
import threading

import sys
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QApplication

from core.plugin import logger
import asyncio

class MyPlugin(BasePlugin):
    def __init__(self, ctx: PluginContext, cfg: dict):
        super().__init__(ctx, cfg)
        # self.ctx  -> PluginContext，访问系统各服务
        # self.plugin_cfg  -> dict，插件配置（来自 schema.json 或配置文件）
        self.qt_thread = None
        self.app = None
        self.model = None

        self.start_event = asyncio.Event()

    async def initialize(self):
        """插件加载时调用，在此初始化资源、注册事件等"""
        # 启动 Qt 线程（守护线程，主程序退出时自动结束）
        self.start_event.set()
        self.qt_thread = threading.Thread(target=self.run_qt_loop, daemon=True)
        self.qt_thread.start()
        # 等待 Qt 初始化完成
        await self.start_event.wait()

    async def terminate(self):
        """插件卸载时调用，在此释放资源、取消任务等"""
        # 清理Live2D引擎
        dispose_live2d()
        if self.app is not None:
            self.app.quit()
            if self.qt_thread and self.qt_thread.is_alive():
                self.qt_thread.join(timeout=1.0)

    def run_qt_loop(self):
        """在独立的事件循环中运行 Qt 窗口"""
        init_live2d()
        drag_mode = self.plugin_cfg.get('mode', 'move_window')
        model_path = self.plugin_cfg.get('model_path', '')
        model_scale = self.plugin_cfg.get('model_scale', 1.0)

        self.app = QApplication(sys.argv)

        # 设置垂直同步
        fmt = QSurfaceFormat.defaultFormat()
        fmt.setSwapInterval(0)
        QSurfaceFormat.setDefaultFormat(fmt)

        # 创建窗口
        self.model = Live2DModel()
        self.model.drag_mode = 0 if drag_mode == 'move_window' else 1
        self.model.model_path = model_path
        self.model.scale = model_scale
        self.model.show()
        self.exit_code = self.app.exec()

        self.start_event.clear()