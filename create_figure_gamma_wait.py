"""
Power spectrum and autocorrelation of a process with waiting_time distributed waiting times.
"""

import numpy as np
from scipy import signal
import support_functions as sf
import fppanalysis as fa
import superposedpulses.forcing as frc
import superposedpulses.point_model as pm
import superposedpulses.pulse_shape as ps
import matplotlib.pyplot as plt
import cosmoplots

plt.style.use("cosmoplots.default")

fig, ax = cosmoplots.figure_multiple_rows_columns(1, 2)
cosmoplots.change_log_axis_base(ax[0], "y")

Beta = [1000, 100, 10]
beta_label = [r"$10^3$", r"$10^2$", r"$10$"]
waiting_time = 5
dt = 1e-2


class ForcingGammaDistribution(frc.ForcingGenerator):
    def __init__(self, beta):
        self.beta = beta

    def get_forcing(self, times: np.ndarray, waiting_time: float) -> frc.Forcing:
        total_pulses = int(max(times) / waiting_time)
        waiting_times = (
            np.random.gamma(
                self.beta, scale=(self.beta / waiting_time) ** (-1), size=total_pulses
            )
            * 100  # multiplied with inverse dt
        )
        arrival_times = np.add.accumulate(waiting_times)
        arrival_time_indx = np.rint(arrival_times).astype(int)
        arrival_time_indx -= arrival_time_indx[0]  # set first pulse to t = 0
        # check whether events are sampled with arrival time > times[-1]
        number_of_overshotings = len(arrival_time_indx[arrival_time_indx > times.size])
        total_pulses -= number_of_overshotings
        arrival_time_indx = arrival_time_indx[arrival_time_indx < times.size]

        amplitudes = np.random.default_rng().exponential(scale=1.0, size=total_pulses)
        durations = np.ones(shape=total_pulses)

        return frc.Forcing(
            total_pulses,
            times[arrival_time_indx],
            amplitudes,
            durations,
        )

    def set_amplitude_distribution(
        self,
        amplitude_distribution_function,
    ):
        pass

    def set_duration_distribution(self, duration_distribution_function):
        pass


model = pm.PointModel(waiting_time=waiting_time, total_duration=100000, dt=dt)
model.set_pulse_shape(ps.LorentzShortPulseGenerator(tolerance=1e-5))

for i, beta in enumerate(Beta):
    model.set_custom_forcing_generator(ForcingGammaDistribution(beta=beta))

    T, S = model.make_realization()
    forcing = model.get_last_used_forcing()
    # amp = forcing.amplitudes

    S_norm = S - S.mean()

    f, Pxx = signal.welch(x=S_norm, fs=1.0 / dt, nperseg=S.size / 30)
    ax[0].plot(f, Pxx, label=r"$\beta =$" + beta_label[i])  # , color=colors[i])

    tb, R = fa.corr_fun(S_norm, S_norm, dt=dt, norm=False, biased=True, method="auto")
    # divide by max to show normalized Phi
    ax[1].plot(
        tb[abs(tb) < 50],
        R[abs(tb) < 50] / np.max(R),
        label=r"$\beta =$" + beta_label[i],
    )  # , color=colors[i])


def Lorentz_PSD(theta):
    """PSD of a single Lorentz pulse with duration time td = 1"""
    return 2 * np.pi * np.exp(-2 * np.abs(theta))


def spectra_analytical(omega, gamma, A_rms, A_mean, beta):
    I_2 = 1 / (2 * np.pi)
    first_term = gamma * A_rms**2 * I_2 * Lorentz_PSD(omega)
    second_term = (
        gamma
        * A_mean**2
        * I_2
        * Lorentz_PSD(omega)
        * np.real(
            ((1 - 1.0j * omega / (gamma * beta)) ** beta + 1)
            / ((1 - 1.0j * omega / (gamma * beta)) ** beta - 1)
        )
    )
    return 2 * (first_term + second_term)


for label, ls, beta in zip(
    [r"$S_{{\Phi}}(\tau_\mathrm{d} f)$", None, None], ["--", "-.", ":"], Beta
):
    PSD = spectra_analytical(
        2 * np.pi * f, gamma=1 / waiting_time, A_rms=1, A_mean=1, beta=beta
    )
    ax[0].plot(f, PSD, ls + "k", label=label)

# PSD = PSD_periodic_arrivals(2 * np.pi * f, td=1, gamma=0.2, A_rms=1, A_mean=1, dt=0.01)
# ax1.plot(f, PSD, "--k", label=r"$S_{\widetilde{\Phi}}(\tau_\mathrm{d} f)$")

# t = np.linspace(0, 50, 1000)
# R_an = autocorr_periodic_arrivals(t, 0.2, 1, 1)
# ax2.plot(t, R_an, "--k", label=r"$R_{\widetilde{\Phi}}(t/\tau_\mathrm{d})$")


def Lorentz_AC_basic(t):
    return 4 / (4 + t**2)


tb = np.linspace(0, 50, 1000)
ax[1].plot(tb, Lorentz_AC_basic(tb), ":k", label=r"$\rho_\phi(t/\tau_\mathrm{d})$")

ax[0].set_xlim(-0.03, 1)
ax[0].set_ylim(1e-5, 1e1)
ax[0].set_xlabel(r"$\tau_\mathrm{d} f$")
ax[0].set_ylabel(r"$S_{\widetilde{\Phi}}(\tau_\mathrm{d} f)$")
ax[0].legend()

ax[1].set_xlim(0, 50)
ax[1].set_xlabel(r"$t/\tau_\mathrm{d}$")
ax[1].set_ylabel(r"$R_{\widetilde{\Phi}}(t/\tau_\mathrm{d})$")
ax[1].legend()

fig.savefig("gammawait.eps")
