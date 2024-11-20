from PIL import Image

# 打开两张图片
image1 = Image.open(r"C:\Users\10035\Pictures\Camera Roll\0-GYj38ElW4AAKb8_.jpg")

for i in range(5):
    image2 = Image.open(r"C:\Users\10035\Pictures\Camera Roll\0-GYj38ElW4AAKb8_.jpg")

    # 确定拼接后的图片大小
    width = image1.width + image2.width
    height = max(image1.height, image2.height)

# 创建一个新的空白图片，大小与拼接后的图片一致
new_image = Image.new('RGB', (width, height))

# 在新图片上粘贴原来的两张图片
new_image.paste(image1, (0, 0))
new_image.paste(image2, (image1.width, 0))

# 保存拼接后的图片
new_image.save("merged_image.jpg")