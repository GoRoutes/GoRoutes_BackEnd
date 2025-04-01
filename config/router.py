from rest_framework.routers import DefaultRouter


class SharedAPIRootRouter(DefaultRouter):
    """
    Extende o DefaultRouter para permitir a inclusão de rotas de outros roteadores.
    """

    def extend(self, router):
        """
        Adiciona as rotas do roteador passado como argumento ao roteador compartilhado.
        """
        self.registry.extend(router.registry)


shared_router = SharedAPIRootRouter()
