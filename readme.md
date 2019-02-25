# KanColleConverter

### 环境
Win10 + Python3

### 依赖
* opencv-python: 进行模板匹配等一系列图像识别、绘制工作
* pywin32: 获取窗口信息、截图(bitblt)
* mss: 高效地截窗口

安装：
```
pip install opencv-python pywin32 mss
```

### 开始运行
* 主程序
```
python3 main.py
```

### Trouble Shooting
* 使用bitblt截取的poi窗口是黑屏，解释详见[stackoverflow-20601813](https://stackoverflow.com/questions/20601813/trouble-capturing-window-with-winapi-bitblt-for-some-applications-only):
```
mixing DWM (i.e. Aero) and non-GDI applications (OpenGL, for example) makes BiBlt a unpredictable/unreliable.
```
解决方法是在poi的基本设置中关闭硬件加速。
如果使用硬件加速，使用mss截图（但是这样poi被遮挡就看不到了）

### 联系我
* Email: lostxine@gmail.com
