import torch
import cv2
import yaml
import numpy as np
import time
from pathlib import Path
from ultralytics import YOLO
from typing import List, Tuple
from tqdm import tqdm


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_video_paths(src_video: str) -> List[Path]:
    """Get list of video file paths from source."""
    src_path = Path(src_video)
    if src_path.is_file():
        return [src_path]
    if src_path.is_dir():
        extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        return [p for p in src_path.rglob('*') if p.suffix.lower() in extensions]
    raise AssertionError(f"Source path does not exist: {src_video}")


def validate_paths(src_video: str, dst_video: str) -> None:
    """Validate that src and dst paths are compatible."""
    src_path = Path(src_video)
    dst_path = Path(dst_video)
    
    if src_path.is_file():
        assert dst_path.suffix, "If src_video is file, dst_video must be file too"
    elif src_path.is_dir():
        assert not dst_path.suffix, "If src_video is directory, dst_video must be directory too"
    else:
        raise AssertionError(f"Invalid src_video path: {src_video}")


def letterbox_resize(image: np.ndarray, imgsz: int) -> Tuple[np.ndarray, float, Tuple[int, int]]:
    """Resize image with padding to maintain aspect ratio."""
    h, w = image.shape[:2]
    r = imgsz / max(h, w)
    
    if r != 1:
        new_w, new_h = int(w * r), int(h * r)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    dw, dh = (imgsz - new_w) / 2, (imgsz - new_h) / 2
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    
    image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))
    return image, r, (left, top)


def preprocess_batch(frames: List[np.ndarray], imgsz: int) -> Tuple[torch.Tensor, List[Tuple[float, Tuple[int, int]]]]:
    """Preprocess batch with letterbox resize."""
    processed_frames = []
    scale_info = []
    
    for frame in frames:
        img, ratio, pad = letterbox_resize(frame, imgsz)
        processed_frames.append(img)
        scale_info.append((ratio, pad))
    
    batch = np.stack(processed_frames)
    batch = batch[..., ::-1].copy()  # BGR to RGB
    batch = np.transpose(batch, (0, 3, 1, 2))  # BHWC to BCHW
    
    return torch.from_numpy(batch).float() / 255.0, scale_info


def unscale_boxes(boxes: np.ndarray, ratio: float, pad: Tuple[int, int], orig_shape: Tuple[int, int]) -> np.ndarray:
    """Unscale boxes from letterbox format to original image."""
    pad_w, pad_h = pad
    boxes[:, [0, 2]] -= pad_w
    boxes[:, [1, 3]] -= pad_h
    boxes[:, :4] /= ratio
    
    boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, orig_shape[1])
    boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, orig_shape[0])
    return boxes


def draw_results(frame: np.ndarray, result, ratio: float, pad: Tuple[int, int]) -> np.ndarray:
    """Draw detection results on frame."""
    if result.boxes is None:
        return frame
    
    boxes = result.boxes.cpu().numpy()
    orig_shape = frame.shape[:2]
    
    for box in boxes:
        coords = unscale_boxes(box.xyxy, ratio, pad, orig_shape)
        x1, y1, x2, y2 = coords[0].astype(int)
        conf = box.conf[0]
        cls = int(box.cls[0])
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{result.names[cls]}: {conf:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return frame


def get_codec_info(video_path: Path) -> str:
    """Get video codec information."""
    cap = cv2.VideoCapture(str(video_path))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
    cap.release()
    return codec


def process_video(video_path: Path, output_path: Path, model: YOLO, config: dict) -> None:
    """Process single video with YOLO inference."""
    cap = cv2.VideoCapture(str(video_path))
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Display video info
    codec = get_codec_info(video_path)
    print(f"\n📹 Video: {video_path.name}")
    print(f"   Codec: {codec} | Resolution: {width}x{height} | FPS: {fps:.1f}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    
    imgsz = config.get('imgsz', 1280)
    batch_size = config.get('batch', 16)
    
    pbar = tqdm(
        total=total_frames,
        desc="Processing",
        unit="frames",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}, FPS: {postfix}]"
    )
    
    processed_frames = 0
    start_time = time.time()
    
    while True:
        frames = []
        for _ in range(batch_size):
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        if not frames:
            break
        
        batch_start = time.time()
        batch_tensor, scale_info = preprocess_batch(frames, imgsz)
        results = model(batch_tensor, verbose=False)  # Disable YOLO output
        inference_fps = len(frames) / (time.time() - batch_start)
        
        for frame, result, (ratio, pad) in zip(frames, results, scale_info):
            output_frame = draw_results(frame, result, ratio, pad)
            writer.write(output_frame)
        
        processed_frames += len(frames)
        pbar.set_postfix_str(f"{inference_fps:.1f}")
        pbar.update(len(frames))
    
    cap.release()
    writer.release()
    pbar.close()
    
    total_time = time.time() - start_time
    avg_fps = processed_frames / total_time
    print(f"✓ Saved: {output_path.name}")
    print(f"  {processed_frames} frames in {total_time:.1f}s (avg {avg_fps:.1f} FPS)")


def inference_video(config_path: str = "config.yaml") -> None:
    """Main inference function."""
    print("🚀 Starting YOLO video inference...")
    
    config = load_config(config_path)
    validate_paths(config['src_video'], config['dst_video'])
    
    model = YOLO(config['path_weight'])
    model.conf = config.get('conf', 0.25)
    model.iou = config.get('iou', 0.45)
    
    if config.get('fp16', False) and torch.cuda.is_available():
        model.model.half()
    
    # Display startup info
    weight_name = Path(config['path_weight']).name
    imgsz = config.get('imgsz', 1280)
    batch = config.get('batch', 16)
    
    print(f"✓ Model loaded: {weight_name}")
    print(f"✓ Config: imgsz={imgsz}, batch={batch}")
    
    video_paths = get_video_paths(config['src_video'])
    print(f"✓ Found {len(video_paths)} video(s) to process")
    
    dst_path = Path(config['dst_video'])
    
    if len(video_paths) == 1 and dst_path.suffix:
        process_video(video_paths[0], dst_path, model, config)
    else:
        for video_path in video_paths:
            output_path = dst_path / f"{video_path.stem}_detected{video_path.suffix}"
            process_video(video_path, output_path, model, config)


if __name__ == "__main__":
    inference_video()