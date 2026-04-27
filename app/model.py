from dataclasses import dataclass
from typing import Optional
from PIL.Image import Image as PILImage


@dataclass
class Record:
  title: str
  artists: str
  section: str
  code: str
  cover_path: Optional[str] = None
  cover_img: Optional[PILImage] = None
