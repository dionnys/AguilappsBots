
from googlesearch import search


class GoogleSearcher:
    def __init__(self, api_key, cx):
        self.api_key = api_key
        self.cx = cx
    @classmethod
    async def google_search(self, query):
        search_results = []
        try:
            for result in search(query, api_key=self.api_key, cx=self.cx):
                search_results.append(result)
            return search_results
        except Exception as e:
            print(f"Error performing Google search: {e}")
            return []
    @classmethod
    async def perform_search(self, query):
        if not query:
            return "Por favor, proporciona una consulta de búsqueda."

        search_results = await self.google_search(query)

        if not search_results:
            return "No se encontraron resultados para la búsqueda."
        else:
            response = "Resultados de la búsqueda:\n\n"
            for result in search_results:
                response += f"{result.title}\n{result.link}\n\n"
            return response