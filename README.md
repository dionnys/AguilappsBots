Bot de Twitter para búsqueda y publicación de noticias

Este es un script en Python que utiliza la API de Twitter, la API de NewsAPI, la API de Cuttly y Spacy para buscar noticias relevantes según una pregunta específica y publicarlas en una cuenta de Twitter. También tiene otras funcionalidades, como obtener una lista de seguidores o verificar si un usuario sigue a otro en Twitter.

Requerimientos

Python 3.x
pip
Claves de API para Twitter, NewsAPI y Cuttly
Cuenta de Twitter para publicación
Instalación

Clone o descargue el repositorio.
Instale las dependencias necesarias: pip install -r requirements.txt.
Configure las variables de entorno en un archivo .env siguiendo el formato del archivo .env.example.
Ejecute el script: python bot.py.
Uso

### See PIN-based authorization for details at
https://dev.twitter.com/docs/auth/pin-based-authorization

#https://github.com/mattlisiv/newsapi-python
#https://pypi.org/project/cuttpy/

El script se ejecuta desde la línea de comandos y acepta varios argumentos:

css
Copy code
-a, --authorization    Obtiene los token autorización del usuario.
-q, --question         Especifica la pregunta para la búsqueda de noticias (por defecto: 'python').
-l, --language         Especifica el idioma para la búsqueda 'en' (English) o 'es' (Español) (por defecto: 'es').
-g, --getuser          Obtiene la lista de seguidores.
-f, --friends          Verifica si un usuario sigue a otro.
Por ejemplo, para buscar noticias relacionadas con "tecnología" en inglés, ejecute python bot.py -q technology -l en. Para obtener la lista de seguidores, ejecute python bot.py -g. Para verificar si un usuario específico sigue a otro, ejecute python bot.py -f.

Contribuciones

Las contribuciones son bienvenidas. Si encuentra un error o desea agregar una nueva característica, cree un pull request o abra un issue.

Licencia

Este proyecto está bajo la Licencia MIT. Consulte el archivo LICENSE para obtener más detalles.
