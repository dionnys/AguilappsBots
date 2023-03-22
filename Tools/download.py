import re
import os
import aiohttp
import aiofiles
import instaloader
import pytube

class Downloader:
    def __init__(self):
        self.L = instaloader.Instaloader()

    def extract_shortcode(self, url):
        pattern = r"instagram.com/(?:p|reel)/([a-zA-Z0-9_-]+)(?:\?igshid=[a-zA-Z0-9_-]+)?"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid Instagram URL")

    @classmethod
    async def download_video_ig(self, post_url, target_folder):
        post = instaloader.Post.from_shortcode(self.L.context, post_url.split('/')[-2])
        if post.is_video:
            video_url = post.video_url
            video_id = post_url.split("/")[-2]
            video_file = os.path.join(target_folder, f"{video_id}.mp4")

            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as resp:
                    if resp.status == 200:
                        async with aiofiles.open(video_file, "wb") as f:
                            await f.write(await resp.read())
                        return video_file
                    else:
                        raise Exception("Error downloading video")
        else:
            raise ValueError("The provided URL is not a video.")
    
    @classmethod
    async  def download_video_yb(self, url, target_folder):
        """
        Función que descarga un video de YouTube y lo guarda en una ruta especificada.

        Args:
            url: str. URL del video de YouTube a descargar.
            target_folder: str. Ruta donde se guardará el video.

        Returns:
            str: La ruta y el nombre del archivo de video descargado.
        """
        # Crea una instancia de la clase YouTube a partir de la URL.
        video = pytube.YouTube(url)

        # Elige la primera corriente de video disponible (con la mayor resolución).
        stream = video.streams.first()

        # Descarga el video y lo guarda en la ruta especificada.
        video_file = os.path.join(target_folder, f"{video.title}.mp4")
        stream.download(output_path=target_folder, filename=video.title)

        print("¡Video descargado exitosamente!")
        return video_file
