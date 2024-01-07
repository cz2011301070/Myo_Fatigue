from EMGFeatureDetector import *
def read_emg_csv(parent_folder):
    for file in os.listdir(parent_folder):
        path = os.path.join(parent_folder, file)
        if os.path.exists(path):
            df = pd.read_csv(path)
            filtered_df = df[(df['Marker'] == "START").idxmax():(df['Marker'] == 'STOP').idxmax() + 1]
            return filtered_df
        else:
            return None
#=================================================================================================================
#                                        Read Data
#=================================================================================================================
parent_folder_path = './Data'
EMG_Dataset = read_emg_csv(parent_folder_path)
            

#=================================================================================================================
#                                        Filter Data
#=================================================================================================================
# participant here is "P02_Data"
x = EMG_Dataset.values[:,0:-1]    # ['ControllerAndPen', 'TwoControllers', 'TwoHand']
# x_f = butter_bandpass_filter(x, fs=200, lowcut=20, highcut=90, axis=0)
x_f = butter_bandpass_filter(x, fs=200, lowcut=20, highcut=90)
x_rect = np.abs(x_f)
# x_smooth = savgol_filter(x_rect, window_length=10, polyorder=2, axis=0, mode='interp')
maximum_voluntary_contraction = np.max(x_rect, axis=0)
x_norm = x_rect/maximum_voluntary_contraction
# plot_emg([x], fig_size=(12,10))

x_win = window_emg_data(x_f, fs=200, window_length=0.15, overlap=0.075)

print(f'data shape: {x.shape} | windowed: {x_win.shape}')

#=================================================================================================================
#                                        Calculate features
#=================================================================================================================
x_features = []
for i in range(x_win.shape[1]):
    # x_features.append(cal_integrated_emg(x_win[:,i,:]))
    # x_features.append(cal_willison_amplitude(x_win[:,i,:],threshold=0.1))
    # x_features.append(cal_simple_square_integral(x_win[:,i,:]))
    # x_features.append(cal_mav(x_win[:,i,:]))
    # x_features.append(cal_mean_frequency(x_win[:,i,:], fs=200, nperseg=x_win.shape[0]))
    x_features.append(cal_median_frequency(x_win[:,i,:], fs=200, nperseg=x_win.shape[0]))
    # x_features.append(cal_root_mean_square(x_win[:,i,:]))
    # x_features.append(cal_sample_entropy(x_win[:,i,:]))
    # x_features.append(cal_slope_sign_changes(x_win[:,i,:]))
    # x_features.append(cal_spectral_moments(x_win[:,i,:]))
    # x_features.append(cal_zero_crossing_rate(x_win[:,i,:]))
    # x_features.append(cal_waveform_length(x_win[:,i,:]))
    
x_features = np.array(x_features)
print(x_features.shape)

# cal mean feature across all channels
input = np.mean(x_features, axis=1, keepdims=True)
result = np.mean(input) # send this to Unity to modify the virtual human behavior
channel_trend(input, regressor='linear')

print("test")