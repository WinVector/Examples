
import tempfile
import os
from typing import Optional
import numpy as np
import pandas as pd
import dataframe_image as dfi
import PIL
from PIL import ImageDraw, ImageFont
import IPython.display



def convert_styled_table_to_image(
        st, file_path: Optional[str] = None, 
        *, 
        add_note: bool = True,
        max_width: int = 800, max_height: int = 800,
        ) -> str:
    """Convert st to an image on disk and return file_path (temp file if None)."""
    if file_path is None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
            file_path = f.name
    # convert to PNG
    dfi.export(st, file_path, dpi=600)
    # possibly resize and annotate
    image = PIL.Image.open(file_path)
    if add_note:
        # annotate
        try:
            note = st.data.attrs['note']
            if note is not None:
                # add annotation notes
                font = ImageFont.load_default(size=50)
                text_position = (50, 10)  # x, y coordinates for the text
                text_color = (0, 0, 0)
                # add in text
                draw = ImageDraw.Draw(image)
                draw.text(text_position, note, fill=text_color, font=font)
        except KeyError:
            pass
    if (image.width > max_width) or (image.height > max_height):
        scale = np.min([max_width / image.width, max_height / image.height])
        image = image.resize(
            (int(image.width * scale), int(image.height * scale)),
            PIL.Image.Resampling.LANCZOS)
    image.save(file_path)
    return file_path


def display_styled_table(
        st, 
        *, 
        add_note: bool = True,
        max_width: int = 800, max_height: int = 800,
        ) -> None:
    file_path = convert_styled_table_to_image(
        st, add_note=add_note, max_width=max_width, max_height=max_height)
    image = IPython.display.Image(filename=file_path)
    IPython.display.display(image)
    os.remove(file_path)
