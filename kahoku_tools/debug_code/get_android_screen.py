import subprocess

import subprocess

def capture_screenshot():
    # 检查设备连接状态
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    if "device" not in result.stdout:
        print("没有检测到已连接的设备。")
        return

    # 截取屏幕并保存到设备的临时文件
    subprocess.run(['adb', 'shell', 'screencap', '-p', '/sdcard/screenshot.png'])

    # 将截图文件从设备拉取到电脑
    subprocess.run(['adb', 'pull', '/sdcard/screenshot.png', './pictures/screenshot.png'])

    # 可选：删除设备上的截图文件
    subprocess.run(['adb', 'shell', 'rm', '/sdcard/screenshot.png'])

    print("screenshot save to ^^^  ./pictures/screenshot.png")

capture_screenshot()
