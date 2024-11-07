
import tempfile
from typing import Optional
import pandas as pd
import dataframe_image as dfi
from PIL import Image, ImageDraw, ImageFont



def convert_styled_table_to_image(st, file_path: Optional[str] = None) -> str:
    """Convert st to an image on disk and return file_path (temp file if None)."""
    if file_path is None:
        with tempfile.NamedTemporaryFile(delete=False) as f:
            file_path = f.name
    # convert to PNG
    dfi.export(st, file_path, dpi=600)
    # annotate
    try:
        note = st.data.attrs['note']
        if note is not None:
            # add annotation notes
            font = ImageFont.load_default(size=50)
            text_position = (50, 10)  # x, y coordinates for the text
            text_color = (0, 0, 0)
            # add in text or copy image  
            image = Image.open(file_path)
            draw = ImageDraw.Draw(image)
            draw.text(text_position, note, fill=text_color, font=font)
            image.save(file_path)   
    except KeyError:
        pass
    return file_path
