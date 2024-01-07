import queue
import numpy as np
import pandas as pd
import os, pickle, time
import mne
import matplotlib.pyplot as plt
from scipy import signal
from utils import *
# %matplotlib qt
import neurokit2 as nk
from scipy.stats import entropy
from scipy import stats
from pyentrp import entropy as ent
# from scipy.signal import welch, find_peaks, savgol_filter, butter_bandpass_filter
from scipy.signal import welch, find_peaks, savgol_filter,butter
import scipy.signal as signal
from pyentrp import entropy as ent
from scipy.stats import moment
# from PyEMD import EMD
import pywt
import nolds
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA
plt.rcParams['figure.figsize'] = (10,8)
'''
The estimators implemented in this code is from the paper
"Weighted-Cumulated S-EMG Muscle Fatigue Estimator"
'''
class EMGFatigueEstimator:
    def __init__(self, sampling_rate, num_channels):
        self.__sampling_rate = sampling_rate
        self.__num_channels = num_channels
    '''
    Weighted-Cumulated Fourier Estimator(WCF)
    '''
    def WCF(self):
        pass

    '''
    Weighted-Cumulated Wavelet Estimator(WCW)
    '''
    def WCW(self):
        pass
    '''
    Weighted-Cumulated Root Mean Square (WCR)
    '''
    def WCR(self):
        pass
    '''
    Weighted-Cumulated Zero-Crossing Estimator (WCZ)
    '''
    def WCZ(self):
        pass

    '''
    Weighted-Cumulated MDF Estimator (WCM)
    '''
    def WCM(self):
        pass
    
#================================================================================
#                            [Band Pass Filter]
#================================================================================
def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.lfilter(b, a, data)    # 这个y的格式和data的格式一样
    return y

def butter_bandpass(lowcut, highcut, fs, order=5): # fs为采样频率
    nyq = 0.5 * fs 
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass') # 分子b，分母a
    return b, a


#================================================================================
#                            [Willison Amplitude]
#================================================================================
def cal_willison_amplitude(emg_data, threshold=0.1):
    'emg shape: [pnts, channel]'
    diff_data = np.diff(emg_data, axis=0)
    wamp = np.sum(np.abs(diff_data) > threshold, axis=0)
    return wamp

#================================================================================
#                            [Simple Square Integral]
#================================================================================
def cal_simple_square_integral(emg_data):
    'emg shape: [pnts, channel]'
    ssi = np.sum(emg_data**2, axis=0)
    return ssi
#================================================================================
#                            [Integrated EMG]
#================================================================================
def cal_integrated_emg(emg_data):
    'emg shape: [pnts, channel]'
    iemg = np.sum(np.abs(emg_data), axis=0)
    return iemg

#================================================================================
#                            [Mean Absolute Value]
#================================================================================

def cal_mav(emg_data):
    'emg shape: [pnts, channel]'
    mav = np.mean(np.abs(emg_data), axis=0)
    return mav

#================================================================================
#                            [Root Mean Square]
#================================================================================
def cal_root_mean_square(emg_data):
    'emg shape: [pnts, channel]'
    rms = np.sqrt(np.mean(emg_data**2, axis=0))
    return rms

#================================================================================
#                            [Median Frequency]
#================================================================================
def cal_median_frequency(emg_data, fs=200, nperseg=200):
    'emg shape: [pnts, channel]'
    mdf = []
    for elec_idx in range(emg_data.shape[1]):
        electrode_data = emg_data[:, elec_idx]
        freqs, Pxx = welch(electrode_data, fs, nperseg=nperseg)
        cumsum = np.cumsum(Pxx)
        median_freq = freqs[np.where(cumsum >= cumsum[-1] / 2)[0][0]]
        mdf.append(median_freq)
    mdf = np.array(mdf)
    return mdf

#================================================================================
#                            [Mean Frequency]
#================================================================================
def cal_mean_frequency(emg_data, fs=200, nperseg=200):
    'emg shape: [pnts, channel]'
    mnf = []
    for elec_idx in range(emg_data.shape[1]):
        f, Pxx = welch(emg_data[:, elec_idx], fs, nperseg=nperseg)
        mnf.append(np.sum(f * Pxx) / np.sum(Pxx))
    mnf = np.array(mnf)
    return mnf

#================================================================================
#                            [Peak Frequency]
#================================================================================
def cal_peak_frequency(emg_data, fs=200, nperseg=200):
    'emg shape: [pnts, channel]'
    pkf = []
    for ch_idx in range(emg_data.shape[1]):
        f, Pxx = welch(emg_data[:, ch_idx], fs, nperseg=nperseg)
        pkf.append(f[np.argmax(Pxx)])
    pkf = np.array(pkf)
    return pkf

#================================================================================
#                            [Mean Power]
#================================================================================
def cal_mean_power(emg_data, fs=200, nperseg =200):
    mnp = []
    for ch_idx in range(emg_data.shape[1]):
        f, Pxx = welch(emg_data[:, ch_idx], fs, nperseg=nperseg)
        mnp.append(np.mean(Pxx))
    
    mnp = np.array(mnp)
    return mnp

#================================================================================
#                            [Total Power]
#================================================================================
def cal_total_power(emg_data, fs=200, nperseg=200):
    ttp = []
    for ch_idx in range(emg_data.shape[1]):
        f, Pxx = welch(emg_data[:, ch_idx], fs, nperseg=nperseg)
        ttp.append(np.sum(Pxx))
    ttp = np.array(ttp)

    return ttp

#================================================================================
#                            [Waveform Lenght]
#================================================================================
def cal_waveform_length(emg_data):
    'emg shape: [pnts, channel]'
    wl = np.sum(np.abs(np.diff(emg_data, axis=0)), axis=0)
    return wl

#================================================================================
#                            [Sample Entropy]
#================================================================================
def cal_sample_entropy(emg_data, m=2, r=0.2):
    'emg shape: [pnts, channel]'
    sentropy = []
    for elec_idx in range(emg_data.shape[1]):
        se = ent.sample_entropy(emg_data[:, elec_idx], m, r)
        sentropy.append(se[-1])  # Use the last value (m = 2)
    return np.array(sentropy)

#================================================================================
#                            [Slop Sign Change]
#================================================================================
def cal_slope_sign_changes(emg_data):
    'emg shape: [pnts, channel]'
    diff_data = np.diff(emg_data, axis=0)
    ssc = np.sum((diff_data[:-1, :] * diff_data[1:, :]) < 0, axis=0)
    return ssc

#================================================================================
#                            [Zero Crossing Rate]
#================================================================================
def cal_zero_crossing_rate(emg_data):
    'emg shape: [pnts, channel]'
    zcr = np.sum((emg_data[:-1, :] * emg_data[1:, :]) < 0, axis=0)
    return zcr

#================================================================================
#                            [Hjorth]
#================================================================================
def cal_hjorth_parameters(emg_data):
    'emg shape: [pnts, channel]'
    first_derivative = np.diff(emg_data, axis=0)
    second_derivative = np.diff(first_derivative, axis=0)

    activity = np.mean(emg_data**2, axis=0)
    mobility = np.mean(first_derivative**2, axis=0) / activity
    complexity = (np.mean(second_derivative**2, axis=0) / np.mean(first_derivative**2, axis=0)) / mobility

    return activity, mobility, complexity

#================================================================================
#                            [Spectral Moments]
#================================================================================
def cal_spectral_moments(emg_data, fs=200, nperseg=200):
    'emg shape: [pnts, channel]'
    mean_frequency, variance_frequency  = [], []
    
    for elec_idx in range(emg_data.shape[1]):
        f, Pxx = welch(emg_data[:, elec_idx], fs=fs, nperseg=nperseg)
        mean_freq = np.sum(f * Pxx) / np.sum(Pxx)
        mean_frequency.append(mean_freq)
        variance_frequency.append(moment(Pxx, moment=2))
        
    mean_frequency = np.array(mean_frequency)
    variance_frequency = np.array(variance_frequency)

    return mean_frequency, variance_frequency

#================================================================================
#                            [Wavelet Transform]
#================================================================================

def cal_wavelet_transform(emg_data, wavelet='db4'):
    'emg shape: [pnts, channel]'

    wavelet_coeffs_list = pywt.wavedec(emg_data, wavelet, axis=0)

    return wavelet_coeffs_list

#================================================================================
#                            [Deterended Fluctuations Analysis]
#================================================================================

def cal_detrended_fluctuation_analysis(emg_data):
    'emg shape: [pnts, channel]'
    dfa = []
    for elec_idx in range(emg_data.shape[1]):
        dfa.append(nolds.dfa(emg_data[:, elec_idx]))
    return np.array(dfa)

#================================================================================
#                            [Windowing]
#================================================================================

def window_emg_data(emg_data, fs, window_length, overlap=0):
    'emg shape: [pnts, channel]'
    num_samples, num_electrodes = emg_data.shape
    window_length = int(window_length*fs)
    overlap = int(overlap * fs)
    step_size = window_length - overlap
    num_windows = (num_samples - overlap) // step_size

    windowed_emg_data = np.empty((window_length, num_windows, num_electrodes))

    for win_idx in range(num_windows):
        start_sample = win_idx * step_size
        end_sample = start_sample + window_length
        windowed_emg_data[:, win_idx, :] = emg_data[start_sample:end_sample, :]
    return windowed_emg_data

#================================================================================
#                            [Plot EMG]
#================================================================================

def plot_emg(data_list, fig_size=(12, 8), scale=1.01, ylim=None):
    'data is a list of inputs with shape of [pnts, channel]'
    
    channel= data_list[0].shape[1]
    channel_max = 0.0
    fig, ax = plt.subplots(channel, 1, sharex=True, figsize=fig_size)
    for i in range(channel):
        for j in range(len(data_list)):
            data = data_list[j]
            ax[i].plot(data[:, i], linewidth=0.5)
            if ylim is None:
                channel_max_cur = np.max(np.abs(data[:,i])) * scale
                if channel_max_cur>channel_max:
                    channel_max = channel_max_cur
                ax[i].set_ylim(-channel_max, channel_max)
            else:
                ax[i].set_ylim(ylim[0], ylim[1])
            ax[i].set_ylabel(f'Channel {i+1}')
            if i == channel-1:
                ax[i].set_xlabel('Time')
    plt.tight_layout()
    plt.show()
    

#================================================================================
#                            [EMG Trend]
#================================================================================ 

def channel_trend(data, fs=200, regressor='linear'):
    'data shape: [pnts, channel]'
    time = np.arange(0, len(data))
    num_channels = data.shape[1]
    
    regression_models = []
    for i in range(num_channels):
        channel_data = data[:, i].reshape(-1, 1)
        time_reshaped = time.reshape(-1, 1)
        
        if regressor=='linear':
            # linear regressor
            model = LinearRegression()
            model.fit(time_reshaped, channel_data)
            regression_models.append(model)
            
        elif regressor=='svr':
            # Support vector regressor 
            model = SVR(kernel='rbf', C=1e3, gamma=0.1)
            model.fit(time_reshaped, channel_data.ravel())
            regression_models.append(model)
            
        elif regressor=='rf':
            # RF regressor 
            model = RandomForestRegressor(n_estimators=100, random_state=0)
            model.fit(time_reshaped, channel_data.ravel())
            regression_models.append(model)
        else:
            raise 'TypeError' "current regressors are 'linear' | 'svr' | 'rf'"

    # Visualize the fitted regression curves
    # fitted_curve = np.array([model.predict(time_reshaped).squeeze() for model in regression_models])
    # plot_emg([data, fitted_curve.T])
    if num_channels == 1:
        fig, ax = plt.subplots(figsize=(10, 5))
        axs = [ax]
    else:
        fig, axs = plt.subplots(num_channels, 1, figsize=(10, 5 * num_channels))
    
    # fig, axs = plt.subplots(num_channels, 1, figsize=(10, 5 * num_channels))
    for i, model in enumerate(regression_models):
        channel_data = data[:, i]
        fitted_curve = model.predict(time_reshaped)

        axs[i].plot(time, channel_data, label='EMG Channel {}'.format(i+1))
        axs[i].plot(time, fitted_curve, label='Fitted Regression Curve', linestyle='--')
        axs[i].set_xlabel('Window_Num')
        axs[i].set_ylabel('Amplitude')
        axs[i].legend()

    plt.tight_layout()
    plt.show() 


#================================================================================
#                            [WCF Estimator]
#================================================================================ 
def cal_wcf(emg_data_windows, window_func=np.hanning):
    num_samples, num_windows, num_channels = emg_data_windows.shape
    wcf = np.empty((num_windows, num_channels))

    # calculate gamma for each channel
    gamma = np.zeros(num_channels)
    for channel in range(num_channels):
        first_window_data = emg_data_windows[:, 0, channel] * window_func(num_samples)
        first_window_fft = np.fft.fft(first_window_data)
        gamma[channel] = np.sqrt(np.sum((num_samples - np.arange(1, num_samples)) *
                                        (np.abs(first_window_fft[1:])**2)) / (num_samples - 1))

        if gamma[channel] < 0.0001:
            print(f'gamma too small for channel {channel+1}')

    # calculate wcf for each window and channel
    for channel in range(num_channels):
        for window_id in range(num_windows):
            window_data = emg_data_windows[:, window_id, channel]
            # apply window function
            windowed_data = window_data * window_func(num_samples)
            # calculate fft
            dft_window = np.fft.fft(windowed_data, axis=0)
            dft_magnitude_squared = np.abs(dft_window[1:])**2
            # calculate wcf 
            wcf_cur = np.sqrt(np.sum((num_samples - np.arange(1, num_samples)) * dft_magnitude_squared) / (num_samples - 1))
            wcf[window_id, channel] = 2 * (window_id + 1) - (1 / gamma[channel]) * wcf_cur
            
    return wcf

