"""
贴图脚本，批量生成图片
"""


from PIL import Image
import os

im_path = r"C:\Users\10035\Pictures\yandex\background"
images = os.listdir(im_path)
for im in images:
    print(im)
    bg = os.path.join(im_path , im)
    print(bg)
    background = Image.open(bg)
    bg_width, bg_height = background.size
    x, y = 0, 0
    # 打开PNG图片（需要贴上的透明背景图片）
    path =  r"C:\Users\10035\Pictures\yandex\png"
    for i in ["2_pixian_ai.png", "111_pixian_ai.png", "screenshot_pixian_ai.png", "1_pixian_ai.png"]:

        png = os.path.join(path, i)
        overlay = Image.open(png)

        width, height = overlay.size
        bg_width, bg_height = background.size
        print(width, height, bg_width, bg_height)

        # 确保背景图是RGBA模式以支持透明度
        background = background.convert("RGBA")

        # 将PNG图片放在JPG图片上某个位置
        # 这里的(50, 50)是PNG图片在JPG图片上的起始坐标
        background.paste(overlay, (x, y), overlay)
        x = x + width
        y = 50
        if x > bg_width:
            x = 0
            y += height
        if y > bg_height:
            break
    # 将结果保存为新的图片文件
    # 如果要保存为JPG，需要转换回RGB模式
    background = background.convert("RGB")
    output_path = r"C:\Users\10035\Pictures\yandex\images"
    background.save(os.path.join(r'C:\Users\10035\Pictures\yandex\images', im))

print("Image has been saved as result.jpg")
