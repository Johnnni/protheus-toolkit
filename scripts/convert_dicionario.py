"""
Converte arquivos .md do dicionário Protheus para JSON compacto.

Lê:  cache/.../dicionario/{PREFIXO}/{TABELA}.md
Gera: output/tabelas/{PREFIXO}/{CODE}.json  +  output/index.json

Stdlib only: re, json, pathlib
"""

import re
import json
from pathlib import Path


def parse_properties(text):
    """Extrai tabela de propriedades (x2_chave, x2_nome, etc.)."""
    props = {}
    for m in re.finditer(r'\| `(\w+)` \| (.+?) \|', text):
        key = m.group(1).strip()
        val = m.group(2).strip()
        props[key] = val
    return props


def parse_campos(text):
    """Extrai tabela de campos e detalhes adicionais."""
    # Find the campos section
    campos_match = re.search(r'## Campos \((\d+)\)\s*\n\n\|[^\n]+\n\|[-| ]+\n((?:\|[^\n]+\n)*)', text)
    if not campos_match:
        return []

    campos = []
    header_line = text[text.find('## Campos'):].split('\n')[2]  # header row
    rows_text = campos_match.group(2)

    for line in rows_text.strip().split('\n'):
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if len(cols) < 10:
            continue
        campo = {
            'campo': cols[0].strip('` '),
            'titulo': cols[1],
            'tipo': cols[2],
        }
        # Parse tam and dec as numbers
        try:
            tam_val = cols[3]
            campo['tam'] = int(float(tam_val)) if tam_val else 0
        except (ValueError, TypeError):
            campo['tam'] = 0
        try:
            dec_val = cols[4]
            campo['dec'] = int(float(dec_val)) if dec_val else 0
        except (ValueError, TypeError):
            campo['dec'] = 0

        if cols[6].strip():
            campo['obrig'] = True

        campos.append(campo)

    # Parse field details (validacao, ini_padrao, combo, etc.)
    details_section = re.search(r'### Detalhes dos Campos\s*\n(.*?)(?=\n## |\Z)', text, re.DOTALL)
    if details_section:
        detail_text = details_section.group(1)
        # Parse each field's details
        field_blocks = re.split(r'\n\*\*(\w+)\*\*\s*\n', detail_text)
        # field_blocks: ['', 'FIELD1', '  - detail\n  - detail\n', 'FIELD2', ...]
        for i in range(1, len(field_blocks) - 1, 2):
            field_name = field_blocks[i]
            field_details = field_blocks[i + 1]

            # Find corresponding campo
            for c in campos:
                if c['campo'] == field_name:
                    validacao = re.search(r'Validacao: `(.+?)`', field_details)
                    if validacao:
                        c['validacao'] = validacao.group(1)
                    ini_padrao = re.search(r'Ini Padrao: `(.+?)`', field_details)
                    if ini_padrao:
                        c['ini_padrao'] = ini_padrao.group(1)
                    combo = re.search(r'Combo: `(.+?)`', field_details)
                    if combo:
                        c['combo'] = combo.group(1)
                    break

    return campos


def parse_indices(text):
    """Extrai tabela de índices."""
    idx_match = re.search(r'## Indices \((\d+)\)\s*\n\n\|[^\n]+\n\|[-| ]+\n((?:\|[^\n]+\n)*)', text)
    if not idx_match:
        return []

    indices = []
    for line in idx_match.group(2).strip().split('\n'):
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if len(cols) < 3:
            continue
        idx = {
            'ordem': cols[0].strip(),
            'chave': cols[1].strip('` '),
            'descricao': cols[2].strip(),
        }
        if len(cols) > 3 and cols[3].strip():
            idx['nickname'] = cols[3].strip()
        indices.append(idx)

    return indices


def parse_gatilhos(text):
    """Extrai tabela de gatilhos (triggers)."""
    gat_match = re.search(r'## Gatilhos \((\d+)\)\s*\n\n\|[^\n]+\n\|[-| ]+\n((?:\|[^\n]+\n)*)', text)
    if not gat_match:
        return []

    gatilhos = []
    for line in gat_match.group(2).strip().split('\n'):
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if len(cols) < 5:
            continue
        gat = {
            'origem': cols[0].strip('` '),
            'tipo': cols[1].strip(),
            'seq': cols[2].strip(),
            'destino': cols[3].strip('` '),
            'regra': cols[4].strip('` '),
        }
        gatilhos.append(gat)

    return gatilhos


def parse_relacionamentos(text):
    """Extrai tabela de relacionamentos."""
    rel_match = re.search(r'## Relacionamentos \((\d+)\)\s*\n\n\|[^\n]+\n\|[-| ]+\n((?:\|[^\n]+\n)*)', text)
    if not rel_match:
        return []

    rels = []
    for line in rel_match.group(2).strip().split('\n'):
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if len(cols) < 4:
            continue
        rel = {
            'dominio': cols[0].strip(),
            'expressao_dom': cols[1].strip('` '),
            'identificador': cols[2].strip(),
            'expressao_ident': cols[3].strip('` '),
        }
        rels.append(rel)

    return rels


def parse_md_file(filepath):
    """Parseia um arquivo .md completo do dicionário e retorna dict."""
    text = filepath.read_text(encoding='utf-8')

    # Header: # CODE - NAME
    header_match = re.match(r'^# (\w+) - (.+)', text)
    if not header_match:
        return None

    codigo = header_match.group(1)
    nome = header_match.group(2).strip()

    # Properties
    props = parse_properties(text)

    result = {
        'tabela': codigo,
        'nome': nome,
    }

    if props.get('x2_nomeeng'):
        result['nome_eng'] = props['x2_nomeeng']
    if props.get('x2_modo'):
        result['modo'] = props['x2_modo']
    if props.get('x2_arquivo'):
        result['arquivo'] = props['x2_arquivo']

    # Campos
    campos = parse_campos(text)
    if campos:
        result['campos'] = campos

    # Indices
    indices = parse_indices(text)
    if indices:
        result['indices'] = indices

    # Gatilhos
    gatilhos = parse_gatilhos(text)
    if gatilhos:
        result['gatilhos'] = gatilhos

    # Relacionamentos
    rels = parse_relacionamentos(text)
    if rels:
        result['relacionamentos'] = rels

    return result


def main():
    import sys

    # Default source path
    default_source = Path(r"C:\Users\Johnni\.claude\plugins\cache\claude-tdn\protheus-toolkit\2.0.0\skills\protheus-data-model\references\dicionario")

    source = Path(sys.argv[1]) if len(sys.argv) > 1 else default_source
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent.parent / "output"

    if not source.exists():
        print(f"Source directory not found: {source}")
        sys.exit(1)

    tabelas_dir = output / "tabelas"
    tabelas_dir.mkdir(parents=True, exist_ok=True)

    index = []
    converted = 0
    errors = 0

    # Iterate all prefix directories (A, B, C, ..., V)
    for prefix_dir in sorted(source.iterdir()):
        if not prefix_dir.is_dir() or prefix_dir.name.startswith('_'):
            continue

        prefix = prefix_dir.name
        out_prefix_dir = tabelas_dir / prefix
        out_prefix_dir.mkdir(parents=True, exist_ok=True)

        for md_file in sorted(prefix_dir.glob("*.md")):
            try:
                data = parse_md_file(md_file)
                if data is None:
                    errors += 1
                    print(f"  SKIP (no header): {md_file.name}")
                    continue

                # Write JSON
                out_file = out_prefix_dir / f"{data['tabela']}.json"
                out_file.write_text(
                    json.dumps(data, ensure_ascii=False, separators=(',', ':')),
                    encoding='utf-8'
                )

                # Add to index
                index.append({
                    'codigo': data['tabela'],
                    'nome': data['nome'],
                    'prefixo': prefix,
                })

                converted += 1
            except Exception as e:
                errors += 1
                print(f"  ERROR {md_file.name}: {e}")

    # Write index
    index_file = output / "index.json"
    index_file.write_text(
        json.dumps(index, ensure_ascii=False, separators=(',', ':')),
        encoding='utf-8'
    )

    print(f"\nDone! {converted} tables converted, {errors} errors")
    print(f"Output: {output}")
    print(f"Index: {index_file} ({len(index)} entries)")


if __name__ == "__main__":
    main()
