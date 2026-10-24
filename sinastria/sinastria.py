"""Verificación grado a grado de dos cartas natales, su sinastría y los tránsitos de Venus.

Efemérides Suiza (pyswisseph, modo Moshier: no necesita archivos externos).
Zodiaco tropical, casas Placidus. Bogotá 4.711 N, 74.072 W.
Colombia estuvo en UTC-5 en enero de 1991 y enero de 1995 (sin horario de verano).

Uso:
    pip install pyswisseph
    python sinastria.py
"""
import datetime as dt

import swisseph as swe

LAT, LON = 4.711, -74.072
UTC_OFFSET = -5
SIGNOS = ['Aries', 'Tauro', 'Géminis', 'Cáncer', 'Leo', 'Virgo',
          'Libra', 'Escorpio', 'Sagitario', 'Capricornio', 'Acuario', 'Piscis']
CUERPOS = [('Sol', swe.SUN), ('Luna', swe.MOON), ('Mercurio', swe.MERCURY),
           ('Venus', swe.VENUS), ('Marte', swe.MARS), ('Júpiter', swe.JUPITER),
           ('Saturno', swe.SATURN), ('Urano', swe.URANUS), ('Neptuno', swe.NEPTUNE),
           ('Plutón', swe.PLUTO)]
ASPECTOS = [('conjunción', 0), ('sextil', 60), ('cuadratura', 90),
            ('trígono', 120), ('oposición', 180)]
ORBE = 8.0

JUAN_DAVID = ('Juan David', 1991, 1, 10, 11, 33)
ELLA = ('Ella', 1995, 1, 2, 13, 45)


def fmt(lon):
    lon %= 360
    signo = int(lon // 30)
    grados = lon - 30 * signo
    minutos = (grados - int(grados)) * 60
    return f"{int(grados):2d}°{int(minutos):02d}' {SIGNOS[signo]}"


def jd_local(y, m, d, hh, mm):
    """Día juliano UT a partir de hora civil de Bogotá."""
    return swe.julday(y, m, d, hh - UTC_OFFSET + mm / 60)


def carta(nombre, y, m, d, hh, mm):
    jd = jd_local(y, m, d, hh, mm)
    pos = {}
    for cuerpo, pid in CUERPOS:
        xx, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
        pos[cuerpo] = xx[0]
    cuspides, ascmc = swe.houses(jd, LAT, LON, b'P')
    pos['Ascendente'] = ascmc[0]
    pos['Medio Cielo'] = ascmc[1]

    def casa_de(lon):
        for i in range(12):
            a, b = cuspides[i], cuspides[(i + 1) % 12]
            if (lon - a) % 360 < (b - a) % 360:
                return i + 1

    print(f"\n=== {nombre}: {d:02d}/{m:02d}/{y} {hh:02d}:{mm:02d} Bogotá (UTC-5) ===")
    for k, v in pos.items():
        casa = casa_de(v) if k not in ('Ascendente', 'Medio Cielo') else ''
        print(f"  {k:12s} {fmt(v):22s} casa {casa}")
    return pos, cuspides, casa_de


def separacion(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def aspecto(d, orbe=ORBE):
    mejor = None
    for nombre, angulo in ASPECTOS:
        o = abs(d - angulo)
        if o <= orbe and (mejor is None or o < mejor[1]):
            mejor = (nombre, o)
    return mejor


def sinastria(a, pa, b, pb):
    print(f"\n=== Sinastría {a} / {b}, orbe ≤ {ORBE:.0f}°, ordenada por orbe ===")
    filas = []
    for ka, va in pa.items():
        for kb, vb in pb.items():
            asp = aspecto(separacion(va, vb))
            if asp:
                filas.append((asp[1], f"{a} {ka:11s} {fmt(va):20s} {asp[0]:11s} "
                                      f"{b} {kb:11s} {fmt(vb):20s} orbe {asp[1]:5.2f}°"))
    for _, fila in sorted(filas):
        print("  " + fila)


def cruce_de_casas(pa, casa_b, pb, casa_a):
    print("\n=== Cruce de casas ===")
    for k in ('Sol', 'Luna', 'Venus', 'Marte', 'Saturno'):
        print(f"  JD {k:8s} cae en casa {casa_b(pa[k]):2d} de ella | "
              f"Ella {k:8s} cae en casa {casa_a(pb[k]):2d} de él")


def transitos_venus(objetivos, desde, dias):
    """Fechas (mediodía Bogotá) en que Venus en tránsito cruza un aspecto exacto."""
    print(f"\n=== Tránsitos de Venus y Mercurio desde {desde} ({dias} días) ===")
    prev = {}
    for i in range(dias):
        dia = desde + dt.timedelta(days=i)
        jd = jd_local(dia.year, dia.month, dia.day, 12, 0)
        actual = {}
        for nombre, pid in (('Venus', swe.VENUS), ('Mercurio', swe.MERCURY)):
            xx, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
            actual[nombre] = (xx[0], xx[3])
            if nombre in prev and (prev[nombre][1] < 0) != (xx[3] < 0):
                estado = 'retrógrado' if xx[3] < 0 else 'directo'
                print(f"  {dia} {nombre} se pone {estado} en {fmt(xx[0])}")
            if nombre == 'Venus' and nombre in prev and int(prev[nombre][0] // 30) != int(xx[0] // 30):
                print(f"  {dia} Venus entra en {SIGNOS[int(xx[0] // 30)]}")
        if 'Venus' in prev:
            v_hoy, v_ayer = actual['Venus'][0], prev['Venus'][0]
            for etiqueta, objetivo in objetivos.items():
                for nombre, angulo in ASPECTOS:
                    for signo in ((1,) if angulo in (0, 180) else (1, -1)):
                        def f(lon):
                            return ((lon - objetivo - signo * angulo + 180) % 360) - 180
                        if f(v_ayer) * f(v_hoy) < 0 and abs(f(v_ayer)) < 3:
                            print(f"  {dia} Venus {nombre} {etiqueta} (Venus en {fmt(v_hoy)})")
        prev = actual


if __name__ == '__main__':
    pos_jd, cusp_jd, casa_jd = carta(*JUAN_DAVID)
    pos_ella, cusp_ella, casa_ella = carta(*ELLA)

    print("\n=== Sensibilidad de la Luna de ella a la hora de nacimiento ===")
    for off in (-8, -4, 0, 4):
        xx, _ = swe.calc_ut(jd_local(1995, 1, 2, 13, 45 + off), swe.MOON, swe.FLG_SWIEPH)
        print(f"  {off:+d} min -> Luna {fmt(xx[0])}")

    sinastria('JD', pos_jd, 'Ella', pos_ella)
    cruce_de_casas(pos_jd, casa_ella, pos_ella, casa_jd)

    objetivos = {
        'Luna de JD': pos_jd['Luna'],
        'Mercurio de JD': pos_jd['Mercurio'],
        'Sol de ella': pos_ella['Sol'],
        'Venus de ella': pos_ella['Venus'],
        'Marte de ella': pos_ella['Marte'],
        'Descendente de ella (cúspide 7)': cusp_ella[6],
    }
    transitos_venus(objetivos, dt.date(2026, 10, 1), 100)
