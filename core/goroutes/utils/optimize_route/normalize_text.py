import unicodedata

def normalizar_texto(texto: str) -> str:
    """
    Remove acentos e normaliza texto para busca
    """
    texto_sem_acentos = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto_sem_acentos = texto_sem_acentos.upper().strip()
 
    texto_sem_acentos = texto_sem_acentos.replace('RUA:', 'RUA')
    texto_sem_acentos = texto_sem_acentos.replace('SERVIDÃO', 'SERV')
    texto_sem_acentos = texto_sem_acentos.replace('AV.', 'AVENIDA')
    texto_sem_acentos = texto_sem_acentos.replace('AV ', 'AVENIDA ')
    return texto_sem_acentos

def normalizar_endereco_completo(endereco: str) -> str:
    """
    Normaliza endereço para comparação flexível
    """
    import re
    texto_sem_acentos = ''.join(
        c for c in unicodedata.normalize('NFD', endereco)
        if unicodedata.category(c) != 'Mn'
    )
    
    texto = texto_sem_acentos.upper()
    texto = re.sub(r'[^\w\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    texto = texto.replace('RUA ', '').replace('AVENIDA ', '').replace('AV ', '')
    texto = texto.replace(' - ', ' ').replace(',', '')
    
    return texto