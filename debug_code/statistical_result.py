import pandas as pd

# 文件路径
ota_csv_path = r"H7148_OTA/results/h7148_ota_result.csv"
sensor_csv_path = r"H7148_OTA/results/h7148_sensor_result.csv"

# 统计 sensor 次数
sensor_df = pd.read_csv(sensor_csv_path)
reversed_sensor_count = len(sensor_df[sensor_df.receive_status == "success"])
print(f">>> sensor 发送成功次数: {reversed_sensor_count}")

# 统计 OTA 次数
ota_df = pd.read_csv(ota_csv_path)
ota_df.fillna(-1, inplace=True)
ota_count = len(ota_df[ota_df.ota_percent == "30"])
# ota_success_count = len(ota_df[(ota_df.ota_status == "success") | (ota_df.ota_percent == ota_df.ota_maxsize)])
ota_success_count = len(ota_df[(ota_df.ota_status == "success")])
ota_timer = ota_df[(ota_df.OTA_times != -1) & (ota_df.OTA_times != "OTA_times")]["OTA_times"]
ota_timer = ota_timer.astype(float).mean()

try:
    print(f">>> OTA成功率: { (ota_success_count / ota_count) * 100} %;  OTA总次数: {ota_count}, OTA失败次数: {ota_count - ota_success_count}, OTA升级平均耗时(min): {ota_timer} ")
except ZeroDivisionError:
    print(f">>> OTA成功率: 0 %;  OTA总次数: {ota_count}, OTA失败次数: {ota_count - ota_success_count}, OTA升级平均耗时(min): {ota_timer} ")