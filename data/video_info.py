class VideoInfo:
    def __init__(self, title: str, link: str, status: int):
        self.title = title
        self.link = link
        self.status = status

    def __repr__(self):
        return f"VideoInfo(title={self.title!r}, link={self.link!r}, status={self.status!r})"