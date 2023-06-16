import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from fit_function_RB_model import create_fit_U
import cosmoplots


axes_size = cosmoplots.set_rcparams_dynamo(plt.rcParams, num_cols=1, ls="thin")

# 2e6
# K = np.load("K.npy")
# U = np.load("U.npy")
# time = np.load("K_time.npy")
# remove first event in time series
# U = U[600:]
# time = time[600:]

K = np.load("K_4e5.npy")
U = np.load("U_4e5.npy")
time = np.load("K_time_4e5.npy")
K = K[:100000]
U = U[:100000]
time = time[:100000]

dt = time[1] - time[0]

U = (U - np.mean(U)) / np.std(U)

f, Pxx = signal.welch(U, 1 / dt, nperseg=len(U) / 5)

time_series_fit, symbols, _, forcing = create_fit_U(
    f, dt, U, time, "exp", 0.005, shuffled=False, low_R=True
)

f, Pxx_fit = signal.welch(time_series_fit, 1 / dt, nperseg=len(time_series_fit) / 5)


plt.plot(time, U)
plt.plot(time, time_series_fit, "--")
plt.xlabel(r"$t$")
plt.ylabel(r"$\widetilde{U}$")
plt.xlim(28, 29)
plt.savefig("U_fit_4e5.png", bbox_inches="tight")
plt.show()

plt.semilogy(f, Pxx)
plt.semilogy(f, Pxx_fit, "--")
plt.xlabel(r"$f$")
plt.ylabel(r"$S_{U}\left( f \right)$")
plt.xlim(-10, 200)
plt.ylim(1e-6, None)
plt.savefig("S_U_semilogy_4e5.png", bbox_inches="tight")
plt.show()
