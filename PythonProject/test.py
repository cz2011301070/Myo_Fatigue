import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import PublicData
class RealTimePlot:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], marker='o')
        self.data = [[0, 0]]  # 初始化包含两个元素的列表

        # 设置动画
        self.animation = FuncAnimation(self.fig, self.update_plot, init_func=self.init_plot, blit=True,
                                       interval=1000)  # 更新间隔为1秒

    def init_plot(self):
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        return self.line,

    def update_plot(self, frame):
        # 在这里检测列表是否发生变化
        if self.data[-1] != PublicData.updated_list:
            self.data.append(PublicData.updated_list)

        x_data, y_data = zip(*self.data)
        self.line.set_data(x_data, y_data)

        return self.line,

    def show_plot(self):
        plt.show()

# # 示例：更新列表的值
# def update_list():
#     global updated_list
#     while True:
#         # 模拟列表值的变化
#         updated_list = [np.random.randint(0, 10), np.random.randint(0, 10)]

# # 启动更新列表的线程
# import threading
# threading.Thread(target=update_list, daemon=True).start()

# # 实例化 RealTimePlot 类并运行动画
# real_time_plot = RealTimePlot()
# real_time_plot.show_plot()
