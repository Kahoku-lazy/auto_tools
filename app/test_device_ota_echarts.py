from pyecharts.charts import Line
from pyecharts import options as opts

import pandas as pd
import numpy as np


def get_data(file_path):
    df = pd.read_csv(file_path)
    df = df.dropna(subset=['ota_percent'])

    df = df.fillna(0)
    df['ota_percent'] = df[df.ota_percent != "ota_percent"]['ota_percent'].astype(float)


    y = [int(i) if not np.isnan(i) else 0  for i in df['ota_percent'].to_list() ]

    return df["timer"].tolist(), y


file_path = r"h7148_ota_result.csv"
markpoint_max = 786     # OTA 下载终点

# 获取OTA时间戳, OTA下载进度作为图表的x，y轴数据
x, y = get_data(file_path)

# 创建折线图
line = (

    Line(init_opts=opts.InitOpts(width="100%", height="600%"))

    # 设置全局配置
    .set_global_opts(
        title_opts=opts.TitleOpts(title="Time Series Line Chart"),
        xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        yaxis_opts=opts.AxisOpts(),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")
    )

    .add_xaxis(xaxis_data=x)

    .add_yaxis(series_name="Value", y_axis=y, is_smooth=True, label_opts=opts.LabelOpts(is_show=False),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(y=markpoint_max, name="Success")],
                    linestyle_opts=opts.LineStyleOpts(color="green")),
    )

    .set_global_opts(
        datazoom_opts=[opts.DataZoomOpts(type_="slider", range_start=0, range_end=100)]
    )
)

line.render("line_chart.html")