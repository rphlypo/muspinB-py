from math import cos, sin

def intensity_contrast(alpha, mu, c, dutycyle):
    surf = [dutycyle ** 2, (1 - dutycycle) ** 2]

    contrast = 2 * (alpha * c[0] + (1 - alpha) * c[1])

    intensity = alpha * mu[0] + (1-alpha) * mu[1]
    intensity += (surf[0] - surf[1]) * contrast / 2

    return intensity, contrast
