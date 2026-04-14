from langchain.tools import tool
import os
from datetime import datetime

# 原生函数
def text_to_image_raw(prompt: str) -> str:
    save_dir = "generated_images"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{save_dir}/image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    return f"✅ 图片生成成功！\n提示词：{prompt}\n路径：{filename}"

# Agent 工具
@tool
def text_to_image(prompt: str) -> str:
    """文生图工具，根据文字描述生成图片"""
    return text_to_image_raw(prompt)