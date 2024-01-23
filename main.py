from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from PIL import Image
from io import BytesIO
import torch
import dnnlib
from networks.mat import Generator
from datasets.mask_generator_512 import RandomMask
import numpy as np
import legacy
import cv2
import pyspng
import base64
import json
from generate_image import copy_params_and_buffers
from ultralytics import YOLO

network_pkl = './pretrained/Places_512.pkl'
device = torch.device('cuda')
with dnnlib.util.open_url(network_pkl) as f:
    G_saved = legacy.load_network_pkl(f)['G_ema'].to(device).eval().requires_grad_(False)

net_res = 512
G = Generator(z_dim=512, c_dim=0, w_dim=512, img_resolution=net_res, img_channels=3).to(device).eval().requires_grad_(False)
copy_params_and_buffers(G_saved, G, require_all=True)

# no Labels.
label = torch.zeros([1, G.c_dim], device=device)

def read_image(upload_file):
    # Read image from UploadFile object
    contents = upload_file.file.read()

    # Use io.BytesIO to create a file-like object from the image contents
    image_stream = BytesIO(contents)

    if pyspng is not None and upload_file.filename.endswith('.png'):
        image = pyspng.load(image_stream.read())
    else:
        image = np.array(Image.open(image_stream))

    if image.ndim == 2:
        image = image[:, :, np.newaxis]  # HW => HWC
        image = np.repeat(image, 3, axis=2)

    image = image.transpose(2, 0, 1)  # HWC => CHW
    image = image[:3]

    return image

app = FastAPI()

# Sử dụng thư mục 'static' để chứa tệp tĩnh như CSS hoặc JavaScript
app.mount("/static", StaticFiles(directory="static"), name="static")

# Sử dụng Jinja2Templates để render trang HTML
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/editor", response_class=HTMLResponse)
async def read_editor(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/auto-detect", response_class=HTMLResponse)
async def read_auto_detect(request: Request):
    return templates.TemplateResponse("auto.html", {"request": request})


model = YOLO('yolov8n-seg.pt')
model.conf = 0.3
model.iou = 0.45
maxDet = 10

@app.post("/auto-detect")
def auto_detect(request: Request, fileInput: UploadFile = File(...)):
    image = Image.open(BytesIO(fileInput.file.read()))
    prediction = model.predict(image, max_det = 3)
    pred_string = prediction[0].tojson()

    data = json.loads(pred_string)

    dict_result = []

    '''if data and isinstance(data, list):
        first_prediction = data[0]
        if "name" in first_prediction and "confidence" in first_prediction and "segments" in first_prediction:
            name = first_prediction["name"]
            confidence = first_prediction["confidence"]
            segments = first_prediction["segments"]

        result = {
                "name": name,
                "confidence": confidence,
                "segments": segments
            }'''
    if data and isinstance(data, list):
        index = 1
        for i in data:
            first_prediction = i
            if "name" in first_prediction and "confidence" in first_prediction and "segments" in first_prediction:
                name = first_prediction["name"]
                confidence = first_prediction["confidence"]
                segments = first_prediction["segments"]

                result = {
                    "id": index,
                    "name": name,
                    "confidence": confidence,
                    "segments": segments
                }
                dict_result.append(result)
                index += 1
    return dict_result
    

@app.post("/generate-image")
async def generate_image(request: Request, fileInput: UploadFile = File(...), pointsInput: str = Form(None)):

    # Read the contents of the uploaded file
    image = read_image(fileInput)

    upload_path = f"static/images/uploads/{fileInput.filename}"
    saved_image = Image.fromarray(np.transpose(image, (1, 2, 0)))
    saved_image.save(upload_path)

    image = (torch.from_numpy(image).float().to(device) / 127.5 - 1).unsqueeze(0)

    if pointsInput is not None:
        mask = np.array(Image.open(BytesIO(base64.b64decode(pointsInput.split(',')[1]))))
        # mask = np.array(Image.open(BytesIO(maskContent)))
        mask = cv2.cvtColor(np.array(mask), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
        mask = torch.from_numpy(mask).float().to(device).unsqueeze(0).unsqueeze(0)
    else:
        mask = RandomMask(512) # adjust the masking ratio by using 'hole_range'
        mask = torch.from_numpy(mask).float().to(device).unsqueeze(0)

    z = torch.from_numpy(np.random.randn(1, G.z_dim)).to(device)
    output = G(image, mask, z, label, truncation_psi=1, noise_mode='random')
    output = (output.permute(0, 2, 3, 1) * 127.5 + 127.5).round().clamp(0, 255).to(torch.uint8)
    output = output[0].cpu().numpy()

    # Convert the NumPy array to a PIL Image
    pil_image = Image.fromarray(output)

    # Save the PIL Image to a BytesIO object in PNG format
    image_stream = BytesIO()
    pil_image.save(image_stream, format='PNG')

    # Seek to the beginning of the BytesIO buffer
    image_stream.seek(0)

    temp_result_path = f"static/images/results/{fileInput.filename}"
    pil_image.save(temp_result_path)


    # Return a StreamingResponse with the image content
    return StreamingResponse(image_stream, media_type="image/png")

    # return templates.TemplateResponse("results.html", {"request": request, "result_path": temp_result_path, "upload_path": upload_path})