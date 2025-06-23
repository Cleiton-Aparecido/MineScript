import re

tabela_de_token = [
    ('COMENTARIO',   r'//[^\n]*'),
    ('VARIAVEL',     r'\bbau\b'),
    ('ATRIBUICAO',   r'='),
    ('IF',           r'\bfunil\b'),
    ('ELSE',         r'\bejetor\b'),
    ('LOOP_WHILE',   r'\bredstone\b'),
    ('LOOP_FOR',     r'\btrilho\b'),
    ('FUNCAO',       r'\bcraftar\b'),
    ('RETORNO',      r'\bfornalha\b'),
    ('OP_ARIT',      r'\+|\-|\*'),  
    ('OP_REL',       r'==|!=|>=|<=|>|<'),
    ('OP_LOGICO',    r'\be\b|\bou\b|\bnao\b'),
    ('DELIM',        r'\(|\)|\{|\}|;'),
    ('NUM',          r'\d+(\.\d+)?'),
    ('ID',           r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('STRING',       r'"[^"\n]*"?'),
    ('CHAR',         r"'[^'\n]?'?"),
    ('SKIP',         r'[ \t]+'),
    ('PularLinha',   r'\n'),
    ('MISMATCH',     r'.'),
]

tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in tabela_de_token)

palavras_reservadas = {'bau', 'funil', 'ejetor', 'redstone', 'trilho', 'craftar', 'fornalha', 'e', 'ou', 'nao'}

def Analisador_lexico(code):
    line_num = 1
    line_start = 0
    pilha_chaves = []

    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start + 1

        if kind == 'PularLinha':
            line_num += 1
            line_start = mo.end()

        elif kind == 'SKIP':
            continue

        elif kind == 'COMENTARIO':
            continue  

        elif kind == 'DELIM':
            if value == '{':
                pilha_chaves.append((line_num, column))
            elif value == '}':
                if pilha_chaves:
                    pilha_chaves.pop()
                else:
                    print(f"Linha: {line_num} - Coluna: {column} - Erro: chave '}}' sem abertura correspondente")

        elif kind == 'MISMATCH':
            if value == '/':
                print(f"Linha: {line_num} - Coluna: {column} - Erro: uso incorreto de comentário ou símbolo inválido '{value}'")
            else:
                print(f"Linha: {line_num} - Coluna: {column} - Erro: símbolo inválido '{value}'")

        elif kind == 'ID':
            if value not in palavras_reservadas and any(value.startswith(p) for p in palavras_reservadas):
                print(f"Linha: {line_num} - Coluna: {column} - Erro: palavra reservada mal escrita '{value}'")
            elif re.match(r'\d', value):
                print(f"Linha: {line_num} - Coluna: {column} - Erro: identificador mal formado '{value}'")
            elif len(value) > 20:
                print(f"Linha: {line_num} - Coluna: {column} - Erro: identificador muito longo '{value}'")

        elif kind == 'NUM':
            if len(value.replace('.', '')) > 10:
                print(f"Linha: {line_num} - Coluna: {column} - Erro: número muito grande '{value}'")
            elif re.search(r'\d+\.\D|\.\d+', value):
                print(f"Linha: {line_num} - Coluna: {column} - Erro: número mal formado '{value}'")

        elif kind == 'STRING':
            if not value.endswith('"'):
                print(f"Linha: {line_num} - Coluna: {column} - Erro: string mal formada '{value}'")

        elif kind == 'CHAR':
            if not value.endswith("'"):
                print(f"Linha: {line_num} - Coluna: {column} - Erro: caractere mal formado '{value}'")

    
    for linha, coluna in pilha_chaves:
        print(f"Linha: {linha} - Coluna: {coluna} - Erro: chave '{{' aberta sem fechamento")


with open('./index.mine', 'r', encoding='utf-8') as arquivo:
    codigo_fonte = arquivo.read()
    Analisador_lexico(codigo_fonte)
