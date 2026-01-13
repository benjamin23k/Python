# imagenes.py
try:
    from diffusers import StableDiffusionPipeline
    import torch
    pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")
    else:
        pipe = pipe.to("cpu")
except Exception as e:
    pipe = None
    print("Stable Diffusion no inicializado:", e)

def generar_imagen(prompt, out="ben_imagen.png"):
    if pipe is None:
        return False, "Generación no disponible (pipe es None)."
    image = pipe(prompt).images[0]
    image.save(out)
    return True, out