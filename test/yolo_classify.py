from ultralytics import YOLO

# 加载模型（自动下载）
# model = YOLO("yolov8n.pt")  # nano
model = YOLO("yolov8s.pt")  # small
# model = YOLO("yolov8m.pt")      # medium
# model = YOLO("yolov8l.pt")      # large
# model = YOLO("yolov8x.pt")      # xlarge
# model = YOLO("yolo11n.pt")      # 2024.10 发布的新版

# 一行推理
results = model("../data/1.jpg")  # 支持路径、URL、PIL、numpy
# results = model(0)              # 打开摄像头
# results = model("folder/")      # 批量推理整个文件夹

# 显示结果
results[0].show()  # 弹窗显示
results[0].save()  # 保存到 runs/detect/
