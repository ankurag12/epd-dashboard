from image_repo_builder import ImageRepoBuilder
import os
import pickle
import glob
import logging
from collections import deque
import http.server
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageServer:
    def __init__(self, repo_dir="image_repo", image_sources=None):
        self._repo_dir = repo_dir
        # This keeps record of all the files that have been displayed
        self._history = os.path.join(repo_dir, "history.pkl")
        if not image_sources:
            image_sources = dict()
        self._repo_builder = ImageRepoBuilder(dest_dir=self._repo_dir, **image_sources)
        self._image_queue = deque()
        self._update_queue()
        self._next_image = self._update_next_image()

    def _get_history(self):
        try:
            with open(self._history, "rb") as fh:
                history = pickle.load(fh)
        except FileNotFoundError as e:
            history = set()
        return history

    def _update_history(self, history):
        with open(self._history, "wb") as fh:
            pickle.dump(history, fh)

    def update(self):
        history = self._get_history()
        history.add(self._next_image)
        self._update_history(history)
        self._update_next_image()

    def _update_queue(self, min_len=10, pull_from_sources=True):
        if len(self._image_queue) >= min_len:
            return

        history = self._get_history()
        repo = set(glob.glob(os.path.join(self._repo_dir, "*.jpg"))
                   + glob.glob(os.path.join(self._repo_dir, "*.jpeg")))

        self._image_queue.extend(repo - history)

        # If we're still short on images, pull from internet
        if pull_from_sources and len(self._image_queue) < min_len:
            logger.info(f"Pulling more images...")
            self._repo_builder.update_repo()
            self._update_queue(min_len=min_len, pull_from_sources=False)

    def _update_next_image(self):
        # Get the next image from the queue
        if len(self._image_queue) == 0:
            logger.error(f"No new images to serve, add more images!")
            return

        next_image = self._image_queue.popleft()
        self._next_image = next_image
        logger.info(f"Next image is: {next_image}")

        # Convert image to PGM
        img = Image.open(next_image).convert('L')

        # TODO: Resize keeping aspect ratio
        img = img.rotate(90, expand=1).resize((1280, 960), Image.Resampling.LANCZOS)
        img.save(os.path.join(self._repo_dir, "the_image.pgm"))

        self._update_queue(min_len=10)
        return next_image


class ImageRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=IMAGE_REPO_DIR, **kwargs)

    def do_GET(self) -> None:
        super().do_GET()
        if self.path.endswith("the_image.pgm"):
            image_server.update()


if __name__ == "__main__":
    SOURCES = {
        "instagram": ["dailystoic"],
        "twitter": [],
        "urls": []
    }
    IMAGE_REPO_DIR = os.path.join(os.path.dirname(__file__), "image_repo")

    image_server = ImageServer(repo_dir=IMAGE_REPO_DIR, image_sources=SOURCES)
    with http.server.HTTPServer(("", 8080), ImageRequestHandler) as httpd:
        httpd.serve_forever()
