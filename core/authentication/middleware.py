import threading

_thread_locals = threading.local()

def get_current_request():
    """
    Retorna o objeto HttpRequest atualmente em processamento,
    ou None se não houver nenhum.
    """
    return getattr(_thread_locals, 'request', None)

def get_current_user():
    """
    Retorna o usuário autenticado da requisição atual,
    ou None se não houver request ou usuário anônimo.
    """
    request = get_current_request()
    return getattr(request, 'user', None) if request else None

class ThreadLocalMiddleware:
    """
    Middleware que salva o objeto request em thread-local storage
    para permitir acesso global via get_current_request().
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # antes de processar a view, salva o request na thread
        _thread_locals.request = request
        response = self.get_response(request)
        # limpeza opcional (evita “vazamento” em alguns servidores)
        try:
            del _thread_locals.request
        except AttributeError:
            pass
        return response
