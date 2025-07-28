import numpy as np

class RCModel:
    def __init__(self, R=10.0, C_uF=100.0, Vin=3.3):
        self.R = R                    # ohm
        self.C = C_uF * 1e-6          # faradios
        self.r = R                    # copia en ohms (para GUI)
        self.c = C_uF                 # copia en µF  (para GUI)
        self.Vin = Vin
        self.t = 0
        self.dt = 1
        self.time_data = []
        self.vc_ideal_data = []
        self.vc_data = []
        self.vr_data = []
        self.vc0 = 0.0
        self.mode = "charge"

    def reset(self, start_from_vin=False):
        self.t = 0
        self.time_data.clear()
        self.vc_data.clear()
        self.vr_data.clear()
        self.vc_ideal_data.clear()
        self.vc0 = self.Vin if start_from_vin else 0

    def set_params(self, R, C_uF):
        self.R = R
        self.C = C_uF * 1e-6
        self.r = R          # asignar también para GUI
        self.c = C_uF       # asignar también para GUI

    def set_mode(self, mode):
        self.mode = mode

    def update(self):
        t_sec = self.t / 1000.0
        tau = self.R * self.C
        if self.mode == "charge":
            vc = self.vc0 + (self.Vin - self.vc0) * (1 - np.exp(-t_sec / tau))
        else:
            vc = self.vc0 * np.exp(-t_sec / tau)

        vr = self.Vin - vc

        self.time_data.append(self.t)
        self.vc_data.append(vc)
        self.vr_data.append(vr)

        self.t += self.dt

        finished = self.t >= 5 * tau * 1000
        return finished

    def get_data(self):
        return self.time_data, self.vc_data, self.vr_data
