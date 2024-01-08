from EMGFeatureDetector import *
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import math


# '''
# -get data(realtime or load from csv)
# -queue data(window)
# -filter the data
# -Apply fft to the windowed data
# -get the median frequency
# -plot real-time median frequency
# '''


# =================================================================================================================
#                                        Real Time Data
# =================================================================================================================
class OnlineFatigue:
    '''
    Online EMG fatigue detection
    - fs: sampling rate
    - num_channel channel numbers
    - window_size
        -  unit: seconds
        - the time length for raw EMG data caching
    - feature_window_size
        -  unit: seconds
        - the time length for EMG feature detection 
    '''

    def __init__(self, fs, num_channel: int, window_size, feature_window_size, step):
        self.sampling_rate = fs  # Myo band sampling rate
        self.num_channels = num_channel  # Myo band channel number
        self.feature_window_data_length = math.floor(feature_window_size * fs)
        self.maxlen = math.floor(window_size * fs)
        self.emg_data_queues = [queue.Queue(maxsize=self.maxlen) for _ in range(self.num_channels)]
        self.observers = []
        self.emg_data_deques = [deque() for _ in range(self.num_channels)]
        self.step = math.floor(step * fs)

    ###########################################################################################################################
    def update_data_deques(self, content):
        for i in range(self.num_channels):
            self.emg_data_deques[i].append(content[i])

    '''deque based feature extraction'''

    def cal_fatigue_features(self, content):
        self.update_data_deques(content)
        data_for_feature_list = self.fetch_data_for_feature_detection()
        if len(data_for_feature_list) > 0:
            # do feature detection
            emg_dataframe = pd.DataFrame(data_for_feature_list)
            x_f = butter_bandpass_filter(emg_dataframe.values, fs=self.sampling_rate, lowcut=20, highcut=90)
            x_rect = np.abs(x_f)
            # x_smooth = savgol_filter(x_rect, window_length=10, polyorder=2, axis=0, mode='interp')
            maximum_voluntary_contraction = np.max(x_rect, axis=0)
            x_norm = x_rect / maximum_voluntary_contraction
            # plot_emg([x], fig_size=(12,10))

            x_win = window_emg_data(x_f, self.sampling_rate, window_length=0.15, overlap=0.075)

            median = self.median_freq_index(x_win)
            rms = self.rms_index(x_win)

            wcf = cal_wcf(x_win)
            wcw = cal_wcw(x_win)
            wcr = cal_wcr(x_win)
            wcz = cal_wcz(x_win)
            wcm = cal_wcm(x_win)
            features = [rms, median, wcf, wcw, wcr, wcz, wcm]
            self.notify(features)

            # move forward
            self.move_forward()

    def fetch_data_for_feature_detection(self):
        data_for_feature_list = []
        if len(self.emg_data_deques) > 0:
            if len(self.emg_data_deques[0]) > self.feature_window_data_length:
                for i in range(self.feature_window_data_length):
                    data_for_feature_list.append([self.emg_data_deques[k][-(i + 1)] for k in range(self.num_channels)])
        return data_for_feature_list

    def move_forward(self):
        # move forward
        for i in range(self.num_channels):
            for _ in range(self.step):
                self.emg_data_deques[i].popleft()

    ############################################################################################################################
    def update_data_queues(self, content):
        for i in range(self.num_channels):
            if not self.emg_data_queues[i].full():
                self.emg_data_queues[i].put(content[i])
            else:
                self.emg_data_queues[i].get()  # get and remove queue first element
                self.emg_data_queues[i].put(content[i])

    '''queue based feature extraction'''

    def fatigue_indicator(self, content):
        self.update_data_queues(content)
        # calculate the feature
        if self.emg_data_queues[0].qsize() > self.feature_window_data_length:
            data_for_feature_list = []
            for _ in range(self.feature_window_data_length):
                data_for_feature_list.append([self.emg_data_queues[k].get() for k in
                                              range(self.num_channels)])  # fetch data for feature detection

            emg_dataframe = pd.DataFrame(data_for_feature_list)
            x_f = butter_bandpass_filter(emg_dataframe.values, fs=self.sampling_rate, lowcut=20, highcut=90)
            x_rect = np.abs(x_f)
            # x_smooth = savgol_filter(x_rect, window_length=10, polyorder=2, axis=0, mode='interp')
            maximum_voluntary_contraction = np.max(x_rect, axis=0)
            x_norm = x_rect / maximum_voluntary_contraction
            # plot_emg([x], fig_size=(12,10))

            x_win = window_emg_data(x_f, self.sampling_rate, window_length=0.15, overlap=0.075)

            median = self.median_freq_index(x_win)
            rms = self.rms_index(x_win)
            wcf = np.mean(cal_wcf(x_win))
            wcw = np.mean(cal_wcw(x_win))
            wcr = np.mean(cal_wcr(x_win))
            wcz = np.mean(cal_wcz(x_win))
            wcm = np.mean(cal_wcm(x_win))
            features = [rms, median, wcf, wcw, wcr, wcz, wcm]
            # features = []
            # features.append(rms)
            # features.append(median)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.notify(features)

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify(self, data: list):
        for observer in self.observers:
            observer(data)

    def median_freq_index(self, win: np.array):
        x_features = []
        for i in range(win.shape[1]):  # traverse all windows
            x_features.append(cal_median_frequency(win[:, i, :], self.sampling_rate, nperseg=win.shape[0]))
        # cal mean feature across all channels
        input = np.mean(x_features, axis=1, keepdims=True)
        result = np.mean(input)  # send this to Unity to modify the virtual human behavior
        return result

    def rms_index(self, win: np.array):
        x_features = []
        for i in range(win.shape[1]):  # traverse all windows
            x_features.append(cal_root_mean_square(win[:, i, :]))
        # cal mean feature across all channels
        input = np.mean(x_features, axis=1, keepdims=True)
        result = np.mean(input)  # send this to Unity to modify the virtual human behavior
        return result


        # x_features = []
        # for i in range(x_win.shape[1]): # traverse all windows
        #     # x_features.append(cal_integrated_emg(x_win[:,i,:]))
        #     # x_features.append(cal_willison_amplitude(x_win[:,i,:],threshold=0.1))
        #     # x_features.append(cal_simple_square_integral(x_win[:,i,:]))
        #     # x_features.append(cal_mav(x_win[:,i,:]))
        #     # x_features.append(cal_mean_frequency(x_win[:,i,:], self.sampling_rate, nperseg=x_win.shape[0]))
        #     x_features.append(cal_median_frequency(x_win[:,i,:], self.sampling_rate, nperseg=x_win.shape[0]))
        #     # x_features.append(cal_root_mean_square(x_win[:,i,:]))
        #     # x_features.append(cal_sample_entropy(x_win[:,i,:]))
        #     # x_features.append(cal_slope_sign_changes(x_win[:,i,:]))
        #     # x_features.append(cal_spectral_moments(x_win[:,i,:]))
        #     # x_features.append(cal_zero_crossing_rate(x_win[:,i,:]))
        #     # x_features.append(cal_waveform_length(x_win[:,i,:]))

        # # cal mean feature across all channels
        # input = np.mean(x_features, axis=1, keepdims=True)
        # result = np.mean(input) # send this to Unity to modify the virtual human behavior
