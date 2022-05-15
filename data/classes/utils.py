from math import sqrt


def is_viable_color(color: str):
    r, g, b = color[:2], color[2:4], color[4:6]
    try:
        int("0x" + r, 16)
        int("0x" + g, 16)
        int("0x" + b, 16)

    except ValueError:
        return False
    else:
        return True


def contrasting_color(color: str):
    r, g, b = int(color[:2], 16), int(color[2: 4], 16), int(color[4:6], 16)
    chosen = int((r + g + b) / 3)
    chosen = chosen + 125 if chosen <= 130 else chosen - 125
    chosen = hex(chosen).replace("0x", "")
    chosen = "0" + chosen if len(chosen) == 1 else chosen
    return chosen * 3


def hex_to_hsl(s: str):
    s = s.replace("#", "")
    r, g, b = int(s[:2], 16) / 255, int(s[2:4], 16) / 255, int(s[4:], 16) / 255
    m, M = min(r, g, b), max(r, g, b)
    L = (M + m) / 2
    if m == M:
        H, S = 0, 0
    else:
        if L <= 0.5:
            S = (M - m) / (M + m)
        else:
            S = (M - m) / (2 - M - m)

        if M == r:
            H = (g - b) / (M - m)
        elif M == g:
            H = 2 + (b - r) / (M - m)
        else:
            H = 4 + (r - g) / (M - m)

        H *= 60
        H = H + 360 if H < 0 else H

    return H, S, L


def hsl_to_hex(color: tuple):
    H, S, L = color
    if S == 0:
        r, g, b = L*255, L*255, L*255
    else:
        if L < 0.5:
            temp1 = L * (1 + S)
        else:
            temp1 = L + S - L*S
        temp2 = 2*L - temp1

        H = H/360

        temp_r = H + 0.333
        temp_g = H
        temp_b = H - 0.333

        if temp_r < 0:
            temp_r += 1
        elif temp_r > 1:
            temp_r -= 1

        if temp_g < 0:
            temp_g += 1
        elif temp_g > 1:
            temp_g -= 1

        if temp_b < 0:
            temp_b += 1
        elif temp_b > 1:
            temp_b -= 1

        if 6*temp_r < 1:
            r = temp2 + (temp1 - temp2) * 6 * temp_r
        elif 2 * temp_r < 1:
            r = temp1
        elif 3*temp_r < 2:
            r = temp2 + (temp1 - temp2) * (0.666 - temp_r) * 6
        else:
            r = temp2

        if 6*temp_g < 1:
            g = temp2 + (temp1 - temp2) * 6 * temp_g
        elif 2 * temp_g < 1:
            g = temp1
        elif 3*temp_g < 2:
            g = temp2 + (temp1 - temp2) * (0.666 - temp_g) * 6
        else:
            g = temp2

        if 6*temp_b < 1:
            b = temp2 + (temp1 - temp2) * 6 * temp_b
        elif 2 * temp_b < 1:
            b = temp1
        elif 3*temp_b < 2:
            b = temp2 + (temp1 - temp2) * (0.666 - temp_b) * 6
        else:
            b = temp2

        r, g, b = int(r*255), int(g*255), int(b*255)
        r, g, b = hex(r).replace("0x", ""), hex(g).replace("0x", ""), hex(b).replace("0x", "")
        r = "0" + r if len(r) == 1 else r
        g = "0" + g if len(g) == 1 else g
        b = "0" + b if len(b) == 1 else b
        return f"#{r}{g}{b}"


def a_difference_b(a, b):
    diff = []
    for element in a:
        if element not in b:
            diff.append(element)
    return diff


def reversed_language_mode(mode: str):
    lang1, lang2 = mode.split("_to_")[0], mode.split("_to_")[1]
    return f"{lang2}_to_{lang1}"


def point_dist(p1: tuple, p2: tuple):
    x1, y1 = p1
    x2, y2 = p2
    return sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


def num_in_range(num: float, r: tuple):
    return r[0] <= num <= r[1]


def ocr_language_map():
    map = {
        "العربية": "ara",
        "Български": "bul",
        "中文": "chs",
        "Hrvatski": "hrv",
        "Čeština": "cze",
        "Dansk": "dan",
        "Nederlands": "dut",
        "English": "eng",
        "Suomi": "fin",
        "Français": "fre",
        "Deutsch": "ger",
        "Ελληνικά": "gre",
        "Magyar": "hun",
        "한국어": "kor",
        "Italiano": "ita",
        "日本語": "jpn",
        "Polski": "pol",
        "Português": "por",
        "Русский": "rus",
        "Slovenščina": "slv",
        "Español": "spa",
        "Svenska": "swe",
        "Türkçe": "tur"
    }

    return map
