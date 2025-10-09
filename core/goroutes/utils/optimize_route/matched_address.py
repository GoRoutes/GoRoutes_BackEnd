from .normalize_text import normalizar_endereco_completo

def enderecos_coincidem(endereco1: str, endereco2: str) -> bool:
    """
    Compara dois endereços de forma flexível para encontrar correspondência
    """
    endereco1_normalizado = normalizar_endereco_completo(endereco1)
    endereco2_normalizado = normalizar_endereco_completo(endereco2)
    
    return (endereco1_normalizado in endereco2_normalizado or 
            endereco2_normalizado in endereco1_normalizado or
            endereco1_normalizado == endereco2_normalizado)