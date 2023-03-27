import instaloader
import concurrent.futures
import os
import threading


class ImageRepoBuilder:
    def __init__(self, dest_dir, instagram=None, twitter=None, mms=None, urls=None):
        if isinstance(instagram, str):
            instagram = [instagram]
        if isinstance(twitter, str):
            twitter = [twitter]
        if isinstance(mms, str):
            mms = [mms]
        self._instagram = instagram
        self._twitter = twitter
        self._urls = urls
        self._mms = mms

        if not dest_dir:
            dest_dir = os.path.join(os.path.dirname(__file__), "image_repo")

        self._dest_dir = dest_dir

    def update_repo(self):
        self.download_from_instagram()
        self.download_from_twitter()
        self.download_from_urls()

    def download_from_instagram(self, n=10):
        insta_loader = instaloader.Instaloader()
        count = 0
        lock = threading.Lock()

        def _download_from_instagram_profile(username):
            nonlocal count
            profile = instaloader.Profile.from_username(insta_loader.context, username)
            posts = profile.get_posts()

            for post in posts:
                if post.typename == 'GraphImage':
                    file_name = os.path.join(self._dest_dir, f"instagram_{post.owner_username}_{post.date_utc}.jpg")
                    if os.path.exists(file_name):
                        continue
                    with lock:
                        if count < n:
                            insta_loader.download_pic(file_name, post.url, post.date_utc)
                            count += 1
                        else:
                            break

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self._instagram)) as executor:
            for user in self._instagram:
                executor.submit(_download_from_instagram_profile, user)

    def download_from_twitter(self, n=10):
        pass

    def download_from_urls(self):
        pass

    def download_from_mms(self):
        pass

