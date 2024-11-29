import base64
from promptflow import tool
from promptflow.contracts.multimedia import Image as PFImage
from PIL import Image
import io

def pil_to_base64(input_img):
    #convert the input image data to a BytesIO object
    data_byteIO = io.BytesIO(input_img)

    # buffer = BytesIO()

    # img.save(buffer, format)
    img_str = base64.b64encode(data_byteIO.getvalue()).decode("utf-8")

    return img_str


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def process_image(input_image: PFImage) -> str:
    base64_image = pil_to_base64(input_image)
    return base64_image