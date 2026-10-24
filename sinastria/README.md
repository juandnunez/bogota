# Sinastría Luna–Venus–Marte: verificación grado a grado

Verificación independiente de las dos cartas natales y de la sinastría del episodio
[`episodio.md`](episodio.md), recalculadas con la Efemérides Suiza (`pyswisseph` 2.10,
zodiaco tropical, casas Placidus). Bogotá 4.711 N, 74.072 W, UTC-5 (Colombia no tenía
horario de verano en enero de 1991 ni en enero de 1995).

Reproducir:

```bash
pip install pyswisseph
python sinastria.py
```

## Cartas natales

| Punto | Juan David · 10/01/1991 11:33 | Casa | Ella · 02/01/1995 13:45 | Casa |
|---|---|---|---|---|
| Sol | 19°55' Capricornio | 10 | 11°54' Capricornio | 9 |
| Luna | 22°18' Escorpio | 8 | 0°03' Acuario | 9 |
| Mercurio | 26°43' Sagitario | 9 | 23°18' Capricornio | 9 |
| Venus | 6°51' Acuario | 10 | 25°29' Escorpio | 7 |
| Marte | 28°16' Tauro | 2 | 2°40' Virgo | 4 |
| Júpiter | 10°56' Leo | 5 | 5°05' Sagitario | 7 |
| Saturno | 26°48' Capricornio | 10 | 8°08' Piscis | 11 |
| Urano | 10°18' Capricornio | 9 | 25°34' Capricornio | 9 |
| Neptuno | 14°29' Capricornio | 10 | 22°38' Capricornio | 9 |
| Plutón | 19°50' Escorpio | 8 | 29°34' Escorpio | 7 |
| Ascendente | 15°37' Aries | | 12°53' Tauro | |
| Medio Cielo | 12°46' Capricornio | | 6°43' Acuario | |

Sensibilidad de la Luna de ella: a las 13:37 estaría en 29°58' Capricornio. Cuatro
minutos antes de la hora declarada ya está en 0°01' Acuario. Es la pieza más frágil
de la lectura, como dice el episodio.

## Contactos de la sinastría citados en el episodio

| Contacto | Orbe calculado | Episodio | Estado |
|---|---|---|---|
| Luna JD conjunción Venus ella | 3.18° | "tres grados" | ✓ |
| Marte JD oposición Venus ella | 2.77° | "menos de tres grados" | ✓ |
| Marte JD oposición Plutón ella | 1.31° | "poco más de un grado" | ✓ |
| Venus JD conjunción Luna ella | 6.80° | "casi siete grados" | ✓ |
| Venus JD conjunción Medio Cielo ella | 0.14° = 8' de arco | "catorce minutos de arco" | corregido |
| Sol JD – Sol ella | 8.02° | "ocho grados" | ✓ |
| Medio Cielo JD conjunción Sol ella | 0.86° | "menos de un grado" | ✓ |
| Luna JD – Luna ella | 67.75° | "sesenta y ocho grados, cerca de un sextil" | ✓ |
| Luna JD sextil Mercurio ella | 1.00° | "un grado de orbe" | ✓ |
| Sol JD conjunción Mercurio ella | 3.39° | "junto a" | ✓ |
| Marte JD trígono Luna ella | 1.79° | "trígono" | ✓ |
| Saturno JD conjunción Luna ella | 3.26° | "tres grados" | ✓ |
| Marte JD cuadratura Marte ella | 4.40° | "cuadratura por grado, trígono por signo" | ✓ |

## Contactos cerrados que el episodio no menciona

| Contacto | Orbe |
|---|---|
| Medio Cielo JD trígono Ascendente ella | 0.12° |
| Luna JD sextil Neptuno ella | 0.32° |
| Saturno JD conjunción Urano ella | 1.22° |
| Saturno JD sextil Venus ella | 1.30° |
| Urano JD conjunción Sol ella | 1.60° |
| Venus JD sextil Júpiter ella | 1.78° |

## Cruce de casas

| Punto | De él en casas de ella | De ella en casas de él |
|---|---|---|
| Sol | 9 | 9 |
| Luna | 7 | 10 |
| Venus | 10 | 8 |
| Marte | 1 | 5 |
| Saturno | 9 | 11 |

## Tránsitos de Venus y Mercurio, octubre 2026 a enero 2027

| Fecha | Evento | Episodio |
|---|---|---|
| 03 oct 2026 | Venus retrógrado en 8°29' Escorpio | ✓ |
| 24 oct 2026 | Mercurio retrógrado en 20°58' Escorpio | ✓ |
| 13 nov 2026 | Mercurio directo | ✓ |
| 14 nov 2026 | Venus directo en 22°52' Libra | ✓ |
| 28 nov 2026 | Venus sextil Mercurio de JD | ✓ (ventana 17–30 nov) |
| 04 dic 2026 | Venus entra en Escorpio | corregido: el episodio decía 7–10 dic |
| 08 dic 2026 | Venus sextil Marte de ella | ✓ |
| 20 dic 2026 | Venus sextil Sol de ella | corregido: no es conjunción |
| 21 dic 2026 | Venus entra en casa 7 de ella | ✓ |
| 30 dic 2026 | Venus conjunción Luna de JD | ✓ |
| 03 ene 2027 | Venus conjunción Venus de ella | no mencionado |

## Correcciones aplicadas al texto del episodio

1. Venus de JD sobre el Medio Cielo de ella: 8 minutos de arco, no 14.
2. Urano de JD cae en casa 9 por Placidus, a 2.5° del Medio Cielo. Saturno y Neptuno sí están en casa 10.
3. Luna de ella: 0°03' Acuario, no 0°04'. A 13:37 habría estado en Capricornio. El margen de ocho minutos se sostiene.
4. Venus entra en Escorpio el 4 de diciembre, no entre el 7 y el 10.
5. En diciembre Venus hace sextil al Sol de ella, no conjunción. Venus está en Escorpio y su Sol en Capricornio.

Todo lo demás, incluidos los cuatro contactos centrales y la fecha del 30 de diciembre, resiste el recálculo.
