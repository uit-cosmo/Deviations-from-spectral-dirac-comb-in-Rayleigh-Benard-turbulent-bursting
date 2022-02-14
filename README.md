# Lorenz-system-time-series

Contains python scripts to generate and plot data of Lorenz system used in Manuscript "Dirac comb and exponential frequency spectra in nonlinear dynamics" (arXiv:2106.15904).

# Requirements
 - `numpy`
 - `scipy`
 - `matplotlib`
 - `click`
 - `superposed-pulses`
 - `cosmoplots`

 # Use

Time series are generated by running

```console
python create_time_series.py 
```

Plots are created by 
```console
python plot_time_series.py       # Figure 1
python plot_time_series.py --fit # Figure 5
```
