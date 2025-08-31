import numpy as np
import math

# Convert GHI from W/m² with sunshine hours → MJ/m²/day
def convert_w_to_mj(ghi_w, sunshine_hours):
    return [(w * h * 3600) / 1e6 for w, h in zip(ghi_w, sunshine_hours)]

# Calculate extraterrestrial radiation Io (MJ/m²/day), declination, and delta_rad
def calculate_io(day_num, lat_deg):
    Gsc = 0.0820  # MJ/m²/min
    dr = 1 + 0.033 * np.cos(2 * np.pi * day_num / 365)
    delta = 23.45 * np.sin(2 * np.pi * (284 + day_num) / 365)
    delta_rad = np.radians(delta)
    phi_rad = np.radians(lat_deg)
    ws = np.arccos(-np.tan(phi_rad) * np.tan(delta_rad))
    io = (24 * 60 / np.pi) * Gsc * dr * (
        ws * np.sin(phi_rad) * np.sin(delta_rad) +
        np.cos(phi_rad) * np.cos(delta_rad) * np.sin(ws)
    )
    return io, delta, delta_rad

# Erbs model for diffuse fraction (Hd/H)
def erbs_diffuse_fraction(kt):
    if kt <= 0.22:
        return 1.0
    elif kt <= 0.8:
        return 1.0 - 1.13 * kt + 0.53 * (kt ** 2)
    else: 
        return 0.18

# HDKR model for tilted surface radiation
def calculate_hdkr(H, Hd, lat_rad, beta_rad, delta_rad, albedo=0.2):
    sin_phi = np.sin(lat_rad)
    cos_phi = np.cos(lat_rad)
    sin_delta = np.sin(delta_rad)
    cos_delta = np.cos(delta_rad)

    sin_phi_beta = np.sin(lat_rad - beta_rad)
    cos_phi_beta = np.cos(lat_rad - beta_rad)

    costheta = sin_delta * sin_phi_beta + cos_delta * cos_phi_beta
    costhetaz = sin_delta * sin_phi + cos_delta * cos_phi
    rb = costheta / costhetaz if costhetaz != 0 else 0

    Hd_H = Hd / H if H != 0 else 0
    Hb = H - Hd
    cos_beta = np.cos(beta_rad)

    # Individual components on tilted surface
    Hd_tilted = Hd * (1 + cos_beta) / 2
    Hb_tilted = Hb * rb
    H_reflected = H * albedo * (1 - cos_beta) / 2

    It = Hb_tilted + Hd_tilted + H_reflected

    return {
        'rb': rb,
        'Hb': Hb,
        'Hd': Hd,
        'Hd_H': Hd_H,
        'Hd_tilted': Hd_tilted,
        'Hb_tilted': Hb_tilted,   # now returned
        'It': It
    }

# Compute daily solar radiation results
def compute_daily_radiation(ghi_list_mj, lat, tilt_deg, albedo, start_day=1):
    results = []
    lat_rad = math.radians(lat)
    tilt_rad = math.radians(tilt_deg)

    for i in range(len(ghi_list_mj)):
        day_of_year = start_day + i
        H = ghi_list_mj[i]
        io, delta, delta_rad = calculate_io(day_of_year, lat)
        kt = H / io if io != 0 else 0
        hd_h = erbs_diffuse_fraction(kt)
        Hd = hd_h * H
        values = calculate_hdkr(H, Hd, lat_rad, tilt_rad, delta_rad, albedo)

        results.append({
            'day': day_of_year,
            'declination': round(delta, 2),
            'Io': round(io, 3),
            'Kt': round(kt, 3),
            'Hd_H': round(hd_h, 3),
            'Hd': round(values['Hd'], 2),
            'Hb': round(values['Hb'], 2),
            'rb': round(values['rb'], 3),
            'Hd_tilted': round(values['Hd_tilted'], 2),
            'Hb_tilted': round(values['Hb_tilted'], 2),  # added here
            'It': round(values['It'], 2)
        })
    return results

# Compute monthly radiation (using 12 fixed mid-month days)
def compute_monthly_radiation(ghi_monthly_mj, lat, tilt_deg, albedo):
    results = []
    month_mid_days = [15, 45, 74, 105, 135, 162, 198, 228, 258, 288, 318, 344]
    lat_rad = math.radians(lat)
    tilt_rad = math.radians(tilt_deg)

    for i, H in enumerate(ghi_monthly_mj):
        day_num = month_mid_days[i]
        io, delta, delta_rad = calculate_io(day_num, lat)
        kt = H / io if io != 0 else 0
        hd_h = erbs_diffuse_fraction(kt)
        Hd = hd_h * H
        values = calculate_hdkr(H, Hd, lat_rad, tilt_rad, delta_rad, albedo)

        results.append({
            'month': i + 1,
            'declination': round(delta, 2),
            'Io': round(io, 3),
            'Kt': round(kt, 3),
            'Hd_H': round(hd_h, 3),
            'Hd': round(values['Hd'], 2),
            'Hb': round(values['Hb'], 2),
            'rb': round(values['rb'], 3),
            'Hd_tilted': round(values['Hd_tilted'], 2),
            'Hb_tilted': round(values['Hb_tilted'], 2),  # added here
            'It': round(values['It'], 2)
        })
    return results
