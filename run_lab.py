import os
import sys
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import matplotlib.pyplot as plt
import librosa
import soundfile as sf

sys.stdout.reconfigure(encoding='utf-8')
plt.rcParams['figure.figsize'] = (10, 4)

base_dir = "d:/xuliamthanh/Lab01_2351260663_NguyenThiLinh"
audio_dir = os.path.join(base_dir, "audio")
figures_dir = os.path.join(base_dir, "figures")

os.makedirs(audio_dir, exist_ok=True)
os.makedirs(figures_dir, exist_ok=True)

# 1. Đọc trực tiếp từ thư mục audio
speech_input_wav = os.path.join(audio_dir, "speech_input.wav")
music_input_wav = os.path.join(audio_dir, "music_input.wav")

if not os.path.exists(speech_input_wav) or not os.path.exists(music_input_wav):
    print("Vui lòng tự thêm speech_input.wav và music_input.wav vào thư mục audio/")
    sys.exit(1)

def analyze_and_plot(wav_path, name_prefix):
    fs, data = wav.read(wav_path)
    
    # Metadata
    channels = data.shape[1] if data.ndim > 1 else 1
    duration = data.shape[0] / fs
    print(f"[{name_prefix}] Fs: {fs} Hz, Channels: {channels}, Duration: {duration:.3f} s")
    
    # Mono conversion and normalization
    if channels > 1:
        mono = data.mean(axis=1)
    else:
        mono = data.astype(float)
        
    x = mono / np.max(np.abs(mono))
    
    # --- Time domain ---
    time_axis = np.arange(len(x)) / fs
    return fs, x, time_axis

fs_s, x_s, t_s = analyze_and_plot(speech_input_wav, "Speech")
fs_m, x_m, t_m = analyze_and_plot(music_input_wav, "Music")

# Figure 01: Waveform Comparison
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(t_s, x_s, lw=0.5)
plt.title("Speech Waveform")
plt.ylabel("Amplitude")
plt.grid(True)
plt.subplot(2, 1, 2)
plt.plot(t_m, x_m, lw=0.5, color='orange')
plt.title("Music Waveform")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "01_waveform_comparison.png"))
plt.close()

# Figure 02: Time domain segments
idx_s = int(0.5 * fs_s)
idx_e = int(1.0 * fs_s)
seg_s = x_s[idx_s:idx_e]
t_seg_s = t_s[idx_s:idx_e]

plt.figure(figsize=(10, 4))
plt.plot(t_seg_s, seg_s, lw=0.5)
plt.title("Speech Segment (0.5 - 1.0s)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "02_time_domain_segments.png"))
plt.close()

# Figure 03: FFT Peaks NFFT compare (Music)
seg_m = x_m[int(0.5*fs_m):int(1.0*fs_m)]
w = np.hamming(len(seg_m))
seg_m_w = seg_m * w

N1 = 2048
X1 = 20 * np.log10(np.maximum(np.abs(np.fft.rfft(seg_m_w, n=N1)), 1e-12))
f1 = np.fft.rfftfreq(N1, 1/fs_m)

N2 = 8192
X2 = 20 * np.log10(np.maximum(np.abs(np.fft.rfft(seg_m_w, n=N2)), 1e-12))
f2 = np.fft.rfftfreq(N2, 1/fs_m)

plt.figure(figsize=(12, 5))
plt.plot(f2, X2, lw=0.5, label='NFFT=8192', color='orange')
plt.plot(f1, X1, lw=0.5, label='NFFT=2048', color='blue', alpha=0.7)
plt.title("Music Spectrum (0.5-1.0s) NFFT Comparison")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dB)")
plt.xlim(0, 5000)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "03_fft_peaks_nfft_compare.png"))
plt.close()

# Figure 04: Spectrogram frame lengths
fl1, hop1 = int(0.010 * fs_s), int(0.005 * fs_s)
fl2, hop2 = int(0.050 * fs_s), int(0.025 * fs_s)

f_s1, t_s1, Z1 = signal.spectrogram(x_s, fs=fs_s, window='hamming', nperseg=fl1, noverlap=fl1-hop1, nfft=1024, mode='magnitude')
f_s2, t_s2, Z2 = signal.spectrogram(x_s, fs=fs_s, window='hamming', nperseg=fl2, noverlap=fl2-hop2, nfft=2048, mode='magnitude')

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.pcolormesh(t_s1, f_s1, 20*np.log10(np.maximum(Z1, 1e-12)), shading='gouraud')
plt.title("10ms Frame (Wideband)")
plt.ylim(0, 8000)
plt.subplot(1, 2, 2)
plt.pcolormesh(t_s2, f_s2, 20*np.log10(np.maximum(Z2, 1e-12)), shading='gouraud')
plt.title("50ms Frame (Narrowband)")
plt.ylim(0, 8000)
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, "04_spectrogram_frame_lengths.png"))
plt.close()

# Figure 05: Window Rect vs Hamming
fr_len = 1024
fr = x_m[10000:10000+fr_len]
w_rect = np.ones(fr_len)
w_hamm = np.hamming(fr_len)
X_r = 20*np.log10(np.maximum(np.abs(np.fft.rfft(fr*w_rect, n=4096)), 1e-12))
X_h = 20*np.log10(np.maximum(np.abs(np.fft.rfft(fr*w_hamm, n=4096)), 1e-12))
f_w = np.fft.rfftfreq(4096, 1/fs_m)

plt.figure(figsize=(10,4))
plt.plot(f_w, X_r, label='Rectangular', lw=0.7)
plt.plot(f_w, X_h, label='Hamming', lw=0.7)
plt.title("Window Comparison")
plt.xlim(0, 4000)
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(figures_dir, "05_window_rectangular_vs_hamming.png"))
plt.close()

# Filter Design
b_lpf = signal.firwin(201, cutoff=2000, fs=fs_s, window='hamming')
b_hpf = signal.firwin(201, cutoff=1000, fs=fs_m, window='hamming', pass_zero=False)

w_lpf, H_lpf = signal.freqz(b_lpf, worN=4096, fs=fs_s)
w_hpf, H_hpf = signal.freqz(b_hpf, worN=4096, fs=fs_m)

plt.figure(figsize=(12,4))
plt.plot(w_lpf, 20*np.log10(np.maximum(np.abs(H_lpf), 1e-12)), label='LPF 2kHz')
plt.plot(w_hpf, 20*np.log10(np.maximum(np.abs(H_hpf), 1e-12)), label='HPF 1kHz')
plt.title("FIR Filter Responses")
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(figures_dir, "06_fir_filter_response.png"))
plt.close()

x_s_lpf = signal.lfilter(b_lpf, [1.0], x_s)
x_m_lpf = signal.lfilter(b_lpf, [1.0], x_m)
x_m_hpf = signal.lfilter(b_hpf, [1.0], x_m)

sf.write(os.path.join(audio_dir, "filtered_speech_lpf_2k.wav"), x_s_lpf, fs_s)
sf.write(os.path.join(audio_dir, "filtered_music_lpf_2k.wav"), x_m_lpf, fs_m)
sf.write(os.path.join(audio_dir, "filtered_music_hpf_1k.wav"), x_m_hpf, fs_m)

# Figure 07: Filter Spectrum Comparison
plt.figure(figsize=(10,4))
orig_spec = 20*np.log10(np.maximum(np.abs(np.fft.rfft(x_s[idx_s:idx_e])), 1e-12))
filt_spec = 20*np.log10(np.maximum(np.abs(np.fft.rfft(x_s_lpf[idx_s:idx_e])), 1e-12))
ff = np.fft.rfftfreq(len(orig_spec)*2-1, 1/fs_s)
plt.plot(ff, orig_spec, label='Original', lw=0.5, alpha=0.7)
plt.plot(ff, filt_spec, label='LPF 2kHz', lw=0.5)
plt.title("Spectrum Before and After LPF")
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(figures_dir, "07_filter_spectrum_comparison.png"))
plt.close()

# Quantization
def quantize(x_in, B):
    q = 2**(B-1)-1
    return np.round(np.clip(x_in, -1, 1)*q)/q

for B in [4, 8, 16]:
    xq = quantize(x_m, B)
    sf.write(os.path.join(audio_dir, f"quantized_music_{B}bit.wav"), xq, fs_m)

# SNR plot
bits = [4, 6, 8, 12, 16]
snrs = []
for B in bits:
    xq = quantize(x_m, B)
    e = xq - x_m
    snrs.append(10*np.log10(np.sum(x_m**2)/np.sum(e**2)))

plt.figure(figsize=(8,4))
plt.plot(bits, snrs, marker='o')
plt.title("SNR vs Bit Depth")
plt.xlabel("Bits")
plt.ylabel("SNR (dB)")
plt.grid(True)
plt.savefig(os.path.join(figures_dir, "08_snr_vs_bitdepth.png"))
plt.close()

# Resampling
x_s_8k = librosa.resample(y=x_s, orig_sr=fs_s, target_sr=8000)
x_m_16k = librosa.resample(y=x_m, orig_sr=fs_m, target_sr=16000)
x_m_8k = librosa.resample(y=x_m, orig_sr=fs_m, target_sr=8000)

sf.write(os.path.join(audio_dir, "resampled_speech_8k.wav"), x_s_8k, 8000)
sf.write(os.path.join(audio_dir, "resampled_music_16k.wav"), x_m_16k, 16000)
sf.write(os.path.join(audio_dir, "resampled_music_8k.wav"), x_m_8k, 8000)

# Figure 09
plt.figure(figsize=(10,4))
plt.magnitude_spectrum(x_s, Fs=fs_s, scale='dB', color='blue', alpha=0.5, label='Original')
plt.magnitude_spectrum(x_s_8k, Fs=8000, scale='dB', color='red', alpha=0.8, label='Resampled 8kHz')
plt.title("Resampling Spectrum Comparison")
plt.legend()
plt.savefig(os.path.join(figures_dir, "09_resampling_spectrum_comparison.png"))
plt.close()

# Figure 10: dummy pie chart for sizes
sizes = [10.09, 0.92]
labels = ['PCM 16-bit 44.1kHz (10.09MB)', 'MP3 128kbps (0.92MB)']
plt.figure(figsize=(6,6))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['lightblue', 'lightgreen'])
plt.title("Compression Ratio (~11:1)")
plt.savefig(os.path.join(figures_dir, "10_bitrate_and_compression_ratio.png"))
plt.close()

print("All tasks completed.")
