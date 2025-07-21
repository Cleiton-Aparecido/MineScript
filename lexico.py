# lexico.py
import re
from typing import List, Tuple

# Token: (tipo, valor, linha, coluna)
Token = Tuple[str,str,int,int]

def lex(codigo: str) -> List[Token]:
    tabela_de_token = [
        ('COMENTARIO',   r'//[^\n]*|#[^\n]*'),
        ('VARIAVEL',     r'\bbau\b'),
        ('QUADRO',       r'\bquadro\b'),
        ('FUNCAO',       r'\bcraftar\b'),
        ('IF',           r'\bfunil\b'),
        ('ELSE',         r'\bejetor\b'),
        ('LOOP_WHILE',   r'\bredstone\b'),
        ('LOOP_FOR',     r'\btrilho\b'),
        ('RETORNO',      r'\bfornalha\b'),
        ('ATRIBUICAO',   r'='),
        ('OP_ARIT',      r'[+\-*/]'),
        ('OP_REL',       r'==|!=|>=|<=|>|<'),
        ('OP_LOGICO',    r'\b(e|ou|nao)\b'),
        ('DELIM',        r'[(){}\[\];,]'),
        ('NUM',          r'\d+(\.\d+)?'),
        ('STRING',       r'"[^"\n]*"'),
        ('CHAR',         r"'[^'\n]'"),
        ('ID',           r'[A-Za-z_][A-Za-z0-9_]*'),
        ('SKIP',         r'[ \t]+'),
        ('PULARLINHA',   r'\n+'),
        ('MISMATCH',     r'.'),
    ]
    tok_regex = '|'.join(f'(?P<{n}>{p})' for n,p in tabela_de_token)
    line_num = 1
    line_start = 0
    tokens: List[Token] = []
    for mo in re.finditer(tok_regex, codigo):
        kind = mo.lastgroup
        val = mo.group()
        start = mo.start()
        if kind == 'PULARLINHA':
            line_num += val.count('\n')
            line_start = mo.end()
            continue
        if kind in ('SKIP','COMENTARIO','MISMATCH'):
            continue
        col = start - line_start + 1
        tokens.append((kind, val, line_num, col))
    tokens.append(('EOF','', line_num, 1))
    return tokens
