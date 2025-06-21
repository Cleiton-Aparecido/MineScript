import re


token_specification = [
    ('VARIAVEL',     r'\bbau\b'),
    ('ATRIBUICAO',   r'='),
    ('IF',           r'\bfunil\b'),
    ('ELSE',         r'\bejetor\b'),
    ('LOOP_WHILE',   r'\bredstone\b'),
    ('LOOP_FOR',     r'\btrilho\b'),
    ('FUNCAO',       r'\bcraftar\b'),
    ('RETORNO',      r'\bfornalha\b'),
    ('OP_ARIT',      r'\+|\-|\*|\/'),
    ('OP_REL',       r'==|!=|>=|<=|>|<'),
    ('OP_LOGICO',    r'\be\b|\bou\b|\bnao\b'),
    ('DELIM',        r'\(|\)|\{|\}|;'),
    ('NUM',          r'\d+(\.\d+)?'),
    ('ID',           r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('STRING',       r'"[^"\n]*"?'), 
    ('CHAR',         r"'[^'\n]?'?"), 
    ('SKIP',         r'[ \t]+'),
    ('NEWLINE',      r'\n'),
    ('MISMATCH',     r'.'),
]

tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)

def Analisador_lexico(code):
    line_num = 1
    line_start = 0
    tokens = []

    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start + 1

        if kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()

        elif kind == 'SKIP':
            continue

        elif kind == 'MISMATCH':
            print(f"Linha: {line_num} - Coluna: {column} - Erro: símbolo inválido '{value}'")

        elif kind == 'ID':
            if re.match(r'\d', value):  
                print(f"Linha: {line_num} - Coluna: {column} - Erro: identificador mal formado '{value}'")
            elif len(value) > 20:
                print(f"Linha: {line_num} - Coluna: {column} - Erro: identificador muito longo '{value}'")
            else:
                print(f"Linha: {line_num} - Coluna: {column} - Token:<{kind}, {value}>")

        elif kind == 'NUM':
            if len(value.replace('.', '')) > 10:
                print(f"Linha: {line_num} - Coluna: {column} - Erro: número muito grande '{value}'")
            elif re.search(r'\d+\.\D|\.\d+', value):  
                print(f"Linha: {line_num} - Coluna: {column} - Erro: número mal formado '{value}'")
            else:
                print(f"Linha: {line_num} - Coluna: {column} - Token:<{kind}, {value}>")

        elif kind == 'STRING':
            if not value.endswith('"'):
                print(f"Linha: {line_num} - Coluna: {column} - Erro: string mal formada '{value}'")
            else:
                print(f"Linha: {line_num} - Coluna: {column} - Token:<{kind}, {value}>")

        elif kind == 'CHAR':
            if not value.endswith("'"):
                print(f"Linha: {line_num} - Coluna: {column} - Erro: caractere mal formado '{value}'")
            else:
                print(f"Linha: {line_num} - Coluna: {column} - Token:<{kind}, {value}>")

        else:
            print(f"Linha: {line_num} - Coluna: {column} - Token:<{kind}, {value}>")


with open('./index.mine', 'r', encoding='utf-8') as arquivo:
    codigo_fonte = arquivo.read()
    Analisador_lexico(codigo_fonte)
