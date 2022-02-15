import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import cosmoplots
from support_functions import *
import model.forcing as frc
import model.point_model as pm
import model.pulse_shape as ps

axes_size = cosmoplots.set_rcparams_dynamo(plt.rcParams, num_cols=1, ls="thin")

fig_PSD = plt.figure()
ax1 = fig_PSD.add_axes(axes_size)
fig_AC = plt.figure()
ax2 = fig_AC.add_axes(axes_size)


class ExpAmp(frc.ForcingGenerator):
    def __init__(self):
        pass

    def get_forcing(self, times: np.ndarray, gamma: float) -> frc.Forcing:
        total_pulses = int(max(times) * gamma)
        arrival_time_indx = np.arange(start=0, stop=99994, step=5) * 100
        amplitudes = np.random.default_rng().exponential(scale=1.0, size=total_pulses)
        durations = np.ones(shape=total_pulses)
        return frc.Forcing(
            total_pulses, times[arrival_time_indx], amplitudes, durations
        )

    def set_amplitude_distribution(
        self,
        amplitude_distribution_function,
    ):
        pass

    def set_duration_distribution(self, duration_distribution_function):
        pass


model = pm.PointModel(gamma=0.2, total_duration=100000, dt=0.01)
# model.set_pulse_shape(ps.StandardPulseGenerator("lorentz"))
model.set_pulse_shape(ps.LorentzShortPulseGenerator(tolerance=1e-5))
model.set_custom_forcing_generator(ExpAmp())

T, S = model.make_realization()
amp = np.random.default_rng().exponential(scale=1.0, size=1999)

S_norm = (S - S.mean()) / S.std()
t, R_an = calculate_R_an(1, 1, 0.2)
f, Pxx = signal.welch(x=S_norm, fs=100, nperseg=S.size / 10)

ax1.semilogy(f, Pxx, label=r"$A \sim \mathrm{Exp}$")
PSD = PSD_periodic_arrivals(
    2 * np.pi * f, td=1, gamma=0.2, Arms=amp.std(), Am=np.mean(amp), S=S
)
ax1.semilogy(
    f, PSD, "--k", label=r"$S_{\widetilde{\Phi}}(f), \, \langle A \rangle \ne 0$"
)

tb, R = corr_fun(S_norm, S_norm, dt=0.01, norm=False, biased=True, method="auto")
ax2.plot(tb, R, label=r"$A \sim \mathrm{Exp}$")
ax2.plot(t, R_an, "--k", label=r"$R_{\widetilde{\Phi}}(t),\, \langle A \rangle \ne 0$")


class AsymLaplaceAmp(frc.ForcingGenerator):
    def __init__(self):
        pass

    def get_forcing(self, times: np.ndarray, gamma: float) -> frc.Forcing:
        total_pulses = int(max(times) * gamma)
        arrival_time_indx = np.random.randint(0, len(times), size=total_pulses)
        kappa = 0.5
        amplitudes = sample_asymm_laplace(
            alpha=0.5 / np.sqrt(1.0 - 2.0 * kappa * (1.0 - kappa)),
            kappa=kappa,
            size=total_pulses,
        )
        durations = np.ones(shape=total_pulses)
        return frc.Forcing(
            total_pulses, times[arrival_time_indx], amplitudes, durations
        )

    def set_amplitude_distribution(
        self,
        amplitude_distribution_function,
    ):
        pass

    def set_duration_distribution(self, duration_distribution_function):
        pass


model = pm.PointModel(gamma=0.2, total_duration=100000, dt=0.01)
# model.set_pulse_shape(ps.StandardPulseGenerator("lorentz"))
model.set_pulse_shape(ps.LorentzShortPulseGenerator(tolerance=1e-5))
model.set_custom_forcing_generator(AsymLaplaceAmp())

T, S = model.make_realization()
kappa = 0.5
amp = sample_asymm_laplace(
    alpha=0.5 / np.sqrt(1.0 - 2.0 * kappa * (1.0 - kappa)),
    kappa=kappa,
    size=10000,
)

S_norm = (S - S.mean()) / S.std()
t, R_an = calculate_R_an(0, 1, 0.2)
f, Pxx = signal.welch(x=S_norm, fs=100, nperseg=S.size / 10)

ax1.semilogy(f, Pxx, label=r"$A \sim \mathrm{Laplace}$")
PSD = PSD_periodic_arrivals(
    2 * np.pi * f, td=1, gamma=0.2, Arms=amp.std(), Am=np.mean(amp), S=S
)
ax1.semilogy(
    f, PSD, "--g", label=r"$S_{\widetilde{\Phi}}(f), \, \langle A \rangle = 0$"
)

tb, R = corr_fun(S_norm, S_norm, dt=0.01, norm=False, biased=True, method="auto")
ax2.plot(tb, R, label=r"$A \sim \mathrm{Laplace}$")
ax2.plot(t, R_an, "--g", label=r"$R_{\widetilde{\Phi}}(t), \, \langle A \rangle = 0$")

ax1.set_xlim(-0.2, 12)
ax1.set_ylim(1e-14, 1e3)
ax1.set_xlabel(r"$f$")
ax1.set_ylabel(r"$S_{\widetilde{\Phi}}(f)$")

ax1.legend()
ax1.set_xlim(-0.03, 1)
ax1.set_ylim(1e-4, 1e3)
ax2.set_xlim(0, 50)
ax2.set_xlabel(r"$t$")
ax2.set_ylabel(r"$R_{\widetilde{\Phi}}(t)$")
ax2.legend()
cosmoplots.change_log_axis_base(ax1, "y", base=10)

fig_PSD.savefig("PSD_exp_lap.eps", bbox_inches="tight")
fig_AC.savefig("AC_exp_lap.eps", bbox_inches="tight")

plt.show()
