from psychopy import monitors
from scipy.constants import inch
from math import cos, atan, tan
from constants import monitor_constants


def make_monitor(monitor_name, diag_mon, pixels, viewing_distance):
    return monitors.Monitor(monitor_name,
                width=diag_mon * inch * cos(atan(pixels[1] / pixels[0])) * 100,  # compute width from
                distance=viewing_distance,  # distance to monitor in cm
                )


def pix2deg(pix, mon):
    return atan(mon.getDistance() / (pix / mon.getSizePix()[0] * mon.getWidth()))


def deg2pix(deg, mon):
    return tan(deg) * mon.getSizePix()[0]

mon = make_monitor(**monitor_constants)
mon.setSizePix(monitor_constants['pixels'])
mon.save()