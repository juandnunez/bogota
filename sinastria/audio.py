"""Genera el audio del episodio (episodio.md -> episodio.mp3) con Piper TTS, sin servicios externos.

Requisitos:
    pip install piper-tts
    ffmpeg en el PATH
    Una voz Piper en español, por ejemplo vits-piper-es_MX-claude-high de
    https://github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models

Uso:
    python audio.py --model es_MX-claude-high.onnx --config es_MX-claude-high.onnx.json \
                    --out episodio.mp3
"""
import argparse
import pathlib
import re
import subprocess
import tempfile

PAUSA_PARRAFO = 0.9   # segundos entre párrafos
PAUSA_SECCION = 1.8   # segundos en cada cambio de sección

REEMPLAZOS = [
    (r'\b11:33\b', 'once y treinta y tres'),
    (r'\b1:45\b', 'una y cuarenta y cinco'),
    (r'\*\*(.+?)\*\*', r'\1'),
    (r'\*(.+?)\*', r'\1'),
    (r'\[(.+?)\]\(.+?\)', r'\1'),
    (r'`(.+?)`', r'\1'),
    (r'–', ', '),
]


def parrafos(md: str):
    """Devuelve [(texto, pausa_despues)] a partir del markdown del episodio."""
    out = []
    for bloque in re.split(r'\n\s*\n', md):
        b = bloque.strip()
        if not b or b == '---':
            continue
        if b.startswith('#'):
            if out:
                out[-1] = (out[-1][0], PAUSA_SECCION)
            continue
        if b.startswith('*Episodio de sinastría'):
            continue  # nota editorial, no se lee
        for patron, repl in REEMPLAZOS:
            b = re.sub(patron, repl, b)
        out.append((' '.join(b.split()), PAUSA_PARRAFO))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--config', required=True)
    ap.add_argument('--texto', default=pathlib.Path(__file__).with_name('episodio.md'))
    ap.add_argument('--out', default=pathlib.Path(__file__).with_name('episodio.mp3'))
    ap.add_argument('--length-scale', default='1.05', help='>1 habla más lento')
    ap.add_argument('--piper', default='piper', help='ejecutable de piper')
    ap.add_argument('--title', default='Lo que pasó antes de entender por qué')
    ap.add_argument('--album', default='Sinastría Luna–Venus–Marte')
    ap.add_argument('--language', default='spa')
    args = ap.parse_args()

    md = pathlib.Path(args.texto).read_text(encoding='utf-8')
    partes = parrafos(md)
    print(f'{len(partes)} párrafos')

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        lista = tmp / 'lista.txt'
        lineas = []
        for i, (texto, pausa) in enumerate(partes):
            wav = tmp / f'p{i:03d}.wav'
            subprocess.run([args.piper, '-m', args.model, '-c', args.config, '-f', str(wav),
                            '--length-scale', args.length_scale, '--sentence-silence', '0.45'],
                           input=texto, text=True, check=True, capture_output=True)
            sil = tmp / f's{i:03d}.wav'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi',
                            '-i', f'anullsrc=r=22050:cl=mono', '-t', str(pausa), str(sil)], check=True)
            lineas += [f"file '{wav}'", f"file '{sil}'"]
            print(f'  {i + 1}/{len(partes)}', end='\r')
        lista.write_text('\n'.join(lineas) + '\n')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lista),
                        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                        '-codec:a', 'libmp3lame', '-b:a', '96k', '-ac', '1',
                        '-metadata', f'title={args.title}',
                        '-metadata', f'album={args.album}',
                        '-metadata', f'language={args.language}', str(args.out)], check=True)
    print(f'\nlisto: {args.out}')


if __name__ == '__main__':
    main()
