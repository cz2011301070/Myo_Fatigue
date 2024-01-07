import queue
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class PlotEMGFeatures:
    def __init__(self, window_size, feature_num):
        self.feature_window = window_size
        self.feature_queues = [queue.Queue(maxsize=window_size) for _ in range(feature_num)]
        self.fig, self.axs = plt.subplots(feature_num, 1, figsize=(10, 8))
        self.lines_feature = [ax.plot([0] * window_size)[0] for ax in self.axs]
        for ax in self.axs:
            ax.set_ylim(0, 80)  # Adjust RMS y-limits as needed
        self.anim = animation.FuncAnimation(self.fig, self.update_feature, interval= 1000, blit=True)
    def get_emg_data_from_queue(self, q):
        data = []
        while not q.empty():
            data.append(q.get())
        return data

    def update_feature(self, frame):
        for i, line in enumerate(self.lines_feature):
            new_data = self.get_emg_data_from_queue(self.feature_queues[i])
            if new_data:
                print(f"Updating feature plot for channel {i} with data: {new_data[-1:]}")  # Last 5 data points for checking
            else:
                print(f"No new feature data for channel {i}")
            
            current_data = line.get_ydata()
            updated_data = list(current_data[len(new_data):]) + new_data
            line.set_ydata(updated_data)
            
        return self.lines_feature
    
    def update_feature_queues(self, features:list):
        for i in range(len(features)):
            if not self.feature_queues[i].full():
                self.feature_queues[i].put(features[i])
            else:
                self.feature_queues[i].get()
                self.feature_queues[i].put(features[i])

    def show_plot(self):
        plt.show()

