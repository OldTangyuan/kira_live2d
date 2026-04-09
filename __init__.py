"""
模型模块 - 提供Live2D模型的加载和控制
"""

from .live2d_model import Live2DModel, init_live2d, dispose_live2d

__all__ = ['Live2DModel', 'init_live2d', 'dispose_live2d']