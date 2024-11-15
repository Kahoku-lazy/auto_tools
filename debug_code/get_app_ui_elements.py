import uiautomator2 as u2
import subprocess
import xml.etree.ElementTree as ET  # Import the ElementTree module
from PIL import Image, ImageDraw
image = Image.open(r'D:\Kahoku\auto_tools\pictures\screenshot.png')
draw = ImageDraw.Draw(image)
def connect_device(device_id):
    # 连接到指定的 Android 设备
    return u2.connect(device_id)

def fetch_element_details(device):
    """
    获取手机页面的元素信息，优先级为 XPath > Text > ID
    :param device: uiautomator2 设备对象
    """
    # 获取当前页面的 XML
    xml = device.dump_hierarchy()
    with open("1.xml", 'w', encoding='utf-8') as file:
        file.write(xml)
    # 解析 XML 获取所有元素
    root = ET.fromstring(xml)
    elements_info = []

    for elem in root.iter():
        details = {}
        # 尝试获取 XPath，这里简化处理，实际中 XPath 需要根据元素的具体位置和属性计算
        xpath = elem.get('xpath')  # 假设有这样的属性，实际中需要自己计算
        text = elem.get('text')
        resource_id = elem.get('resource-id')

        if xpath:
            details['type'] = 'XPath'
            details['value'] = xpath
        elif text:
            details['type'] = 'Text'
            details['value'] = text
        elif resource_id:
            details['type'] = 'ID'
            details['value'] = resource_id
        else:
            continue  # 如果什么都没有，跳过这个元素

        bounds = elem.attrib['bounds']

        details['bounds'] = bounds
        # 解析 bounds 属性，格式为 "[left,top][right,bottom]"
        left, top, right, bottom = map(int, bounds.replace('[', '').replace(']', ',').split(',')[:-1])
        
        # 在截图上标记元素位置
        draw.rectangle([left, top, right, bottom], outline='red', width=2)

        elements_info.append(details)
    # 保存标记后的图片
    image.save('marked_screenshot.png')
    print("标记后的屏幕截图已保存为 marked_screenshot.png")

    return elements_info

def get_connected_devices():
    # 执行 adb devices 命令
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    # 获取命令输出
    output = result.stdout
    # 解析设备 ID
    lines = output.splitlines()
    device_ids = []
    for line in lines[1:]:  # 跳过第一行，它是标题行
        if "\tdevice" in line:
            device_id = line.split("\t")[0]
            device_ids.append(device_id)
    return device_ids

# 示例使用
device_ids = get_connected_devices()
# print("Connected devices:", device_ids)

# 示例使用
device_id = device_ids[0]  # 替换为你的设备 ID
print(f"Using device {device_id}")
device = connect_device(device_id)
elements_details = fetch_element_details(device)
for detail in elements_details:
    print(detail)
