import os
from glob import glob
from pathlib import PurePath
PATH = "data/lyrics/"
EXT = "*.txt"
lyric_txts = [file
              for path, subdir, files in os.walk(PATH)
              for file in glob(os.path.join(path, EXT))]

lyrics_dict = {}

for fname in lyric_txts:
    song = PurePath(fname).parts[2].split('.txt')[0]
    print(song)
