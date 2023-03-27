from image_repo_builder import ImageRepoBuilder
import os


class ImageServer:
    def __init__(self, repo_dir="image_repo"):
        self._repo_dir = repo_dir
        self._history = os.path.join(repo_dir, "history.pkl")

    def serve(self):
        pass


if __name__ == "__main__":
    server = ImageServer()
    server.serve()
