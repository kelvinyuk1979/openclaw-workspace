#!/bin/bash
# 监控视频文件，一旦恢复就自动剪辑

VIDEO_PATH="/Users/kelvin/Desktop/一人公司 (1)/油管大神 Dan Koe：2026 年一人公司新模式.mp4"
CLIPS_DIR="/Users/kelvin/Desktop/一人公司 (1)/clips"

echo "🔍 开始监控视频文件..."
echo "目标：$VIDEO_PATH"

while true; do
    if [ -f "$VIDEO_PATH" ]; then
        echo "✅ 视频文件已恢复！开始剪辑..."
        
        # 确保 clips 目录存在
        mkdir -p "$CLIPS_DIR"
        
        # 剪辑 6 个片段
        clips=(
            "00:01:30:00:02:30:clip1_traditional.mp4"
            "00:02:30:00:03:30:clip2_creator.mp4"
            "00:05:00:00:06:00:clip3_content.mp4"
            "00:13:40:00:14:30:clip4_learning.mp4"
            "00:17:50:00:18:40:clip5_coach.mp4"
            "00:28:35:00:29:30:clip6_advantage.mp4"
        )
        
        for clip in "${clips[@]}"; do
            IFS=':' read -r start end output <<< "$clip"
            echo "🎬 剪辑：$start - $end → $output"
            ffmpeg -y -i "$VIDEO_PATH" -ss "$start" -to "$end" -c:v libx264 -c:a aac "$CLIPS_DIR/$output" -loglevel quiet
        done
        
        echo "✅ 所有片段剪辑完成！"
        ls -lh "$CLIPS_DIR"
        
        # 发送通知
        osascript -e 'display notification "视频剪辑完成！" with title "Dan Koe 视频处理"'
        
        break
    else
        echo "⏳ 文件未找到，10 秒后重试..."
        sleep 10
    fi
done
