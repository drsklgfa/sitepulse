from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'README.md', 'compose.yaml', '.env.example', 'Makefile',
    'backend/pyproject.toml', 'backend/Dockerfile', 'backend/app/main.py',
    'frontend/package.json', 'frontend/Dockerfile', 'frontend/src/App.tsx',
    'demo-target/Dockerfile', 'demo-target/app/main.py',
    '.github/workflows/ci.yml', '.github/workflows/pages.yml',
    'CHECKPOINT.md', 'RESTORE.md', 'VALIDATION_REPORT.md', 'CHANGELOG.md',
]


def fail(message: str) -> None:
    print(f'[ERRO] {message}')
    raise SystemExit(1)


def main() -> None:
    missing = [item for item in REQUIRED if not (ROOT / item).exists()]
    if missing:
        fail(f'Arquivos obrigatórios ausentes: {", ".join(missing)}')

    python_files = list((ROOT / 'backend').rglob('*.py')) + list((ROOT / 'demo-target').rglob('*.py'))
    for file in python_files:
        if any(part in {'.venv', '__pycache__'} for part in file.parts):
            continue
        try:
            ast.parse(file.read_text(encoding='utf-8'), filename=str(file))
        except SyntaxError as exc:
            fail(f'Sintaxe Python inválida em {file.relative_to(ROOT)}: {exc}')

    for file in [ROOT / 'frontend/package.json']:
        try:
            json.loads(file.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            fail(f'JSON inválido em {file.relative_to(ROOT)}: {exc}')

    forbidden = []
    for file in ROOT.rglob('*'):
        if file.is_file() and file.resolve() != Path(__file__).resolve() and file.name not in {'.env.example'} and '.git' not in file.parts:
            try:
                text = file.read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError):
                continue
            if 'sk_live_' in text or 'AKIA' in text or 'BEGIN PRIVATE KEY' in text:
                forbidden.append(str(file.relative_to(ROOT)))
    if forbidden:
        fail(f'Possíveis segredos encontrados: {", ".join(forbidden)}')

    print(f'[OK] {len(python_files)} arquivos Python com sintaxe válida.')
    print('[OK] Estrutura obrigatória presente.')
    print('[OK] JSON principal válido.')
    print('[OK] Nenhum padrão óbvio de segredo encontrado.')


if __name__ == '__main__':
    main()
