import uiautomator2 as u2
from appium import webdriver

d = u2.connect()

texts = {
    "search": "Поиск",
    "小岩": "Маленьк скал",
    "柱状灯": "Цилиндрический лампа",
    "观影":"Наблюден за тен",
    "色温": "Цвет тепл",
}


# text = texts["色温"]
# d.send_keys(text)


# adb shell input text "Маленьк скал"