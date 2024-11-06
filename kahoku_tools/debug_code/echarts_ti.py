from pyecharts.charts import Line
from pyecharts import options as opts
import pandas as pd
import numpy as np

df = pd.read_csv(r"D:\Kahoku\H7148_OTA\results\h7148_ota_result.csv")
df = df.dropna(subset=['ota_percent'])
df = df[df.ota_percent != "ota_percent"]
df['ota_percent'] = df['ota_percent'].astype(float)

df.to_csv(r"1.csv", index=False)


x = df['timer'].to_list()
y  = df['ota_percent'].to_list()
flag = 786

# 创建折线图
line = (

    Line()

    # 设置全局配置
    .set_global_opts(
        title_opts=opts.TitleOpts(title="Time Series Line Chart"),
        xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        yaxis_opts=opts.AxisOpts(),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
    )

    .add_xaxis(xaxis_data=x)

    .add_yaxis( series_name="Value", y_axis=y, is_smooth=True, label_opts=opts.LabelOpts(is_show=False))
)


line.render("line_chart.html")