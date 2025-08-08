__all__ = [
    # Optional cloud provider
    "azure_face",
    # Local duplicate detection
    "local_hash",
    # Local providers (choose one):
    "local_insightface",  # requires onnxruntime; skip on Windows without build tools
    "local_deepface",     # pure Python wheels available on Windows (requires tensorflow)
    "local_onnx_arcface", # lightweight ONNXRuntime + OpenCV (requires downloading ONNX model)
]