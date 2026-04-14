from langchain.tools import tool
import os
from datetime import datetime

# 原生函数
def text_to_video_raw(prompt: str) -> str:
    save_dir = "generated_videos"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{save_dir}/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    return f"✅ 视频生成成功！\n提示词：{prompt}\n路径：{filename}"

# Agent 工具
@tool
def text_to_video(prompt: str) -> str:
    """文生视频工具，根据文字描述生成视频"""
    return text_to_video_raw(prompt)