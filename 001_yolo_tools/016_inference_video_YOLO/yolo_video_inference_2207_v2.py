import torch
import cv2
import yaml
import numpy as np
import time
from pathlib import Path
from ultralytics import YOLO
from typing import List, Tuple, Optional
from tqdm import tqdm
import torchvision.transforms as T


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


def get_device(config: dict) -> torch.device:
    """Get device from config with validation."""
    device_str = config.get('device', 'auto')
    
    if device_str == 'auto':
        return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    elif device_str == 'cpu':
        return torch.device('cpu')
    elif device_str.startswith('cuda'):
        if not torch.cuda.is_available():
            print(f"⚠️ CUDA not available, falling back to CPU")
            return torch.device('cpu')
        
        if ':' in device_str:
            gpu_id = int(device_str.split(':')[1])
            if gpu_id >= torch.cuda.device_count():
                print(f"⚠️ GPU {gpu_id} not available (only {torch.cuda.device_count()} GPUs), using GPU 0")
                return torch.device('cuda:0')
        
        return torch.device(device_str)
    else:
        print(f"⚠️ Unknown device '{device_str}', using auto")
        return torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def letterbox_resize_torch(frames: torch.Tensor, imgsz: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Optimized letterbox resize using torch operations on specified device."""
    B, H, W, C = frames.shape
    
    # Ensure frames are on correct device
    frames = frames.to(device)
    
    # Calculate scale factor
    scale = imgsz / max(H, W)
    new_h, new_w = int(H * scale), int(W * scale)
    
    # Resize using torch interpolate
    frames = frames.permute(0, 3, 1, 2).float() / 255.0  # BHWC -> BCHW and normalize
    frames = torch.nn.functional.interpolate(frames, size=(new_h, new_w), mode='bilinear', align_corners=False)
    
    # Calculate padding
    pad_h = (imgsz - new_h) // 2
    pad_w = (imgsz - new_w) // 2
    
    # Apply padding
    frames = torch.nn.functional.pad(frames, (pad_w, imgsz - new_w - pad_w, pad_h, imgsz - new_h - pad_h), 
                                   value=114/255.0)
    
    # Return scale info as tensors on the same device
    ratios = torch.full((B,), scale, device=device, dtype=torch.float32)
    pads = torch.tensor([[pad_w, pad_h]], device=device, dtype=torch.float32).repeat(B, 1)
    
    return frames, ratios, pads


def preprocess_batch_optimized(frames: List[np.ndarray], imgsz: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Optimized preprocessing with torch operations on specified device."""
    # Convert to tensor batch on specified device
    batch = torch.from_numpy(np.stack(frames)).to(device)
    
    # RGB conversion and letterbox resize in one go
    batch = batch[..., [2, 1, 0]]  # BGR to RGB
    batch, ratios, pads = letterbox_resize_torch(batch, imgsz, device)
    
    return batch, ratios, pads


def unscale_boxes_vectorized(boxes: torch.Tensor, ratios: torch.Tensor, pads: torch.Tensor, 
                           orig_shapes: torch.Tensor) -> torch.Tensor:
    """Vectorized box unscaling on specified GPU device."""
    if boxes.numel() == 0:
        return boxes
    
    # Ensure all tensors are on the same device
    device = boxes.device
    ratios = ratios.to(device)
    pads = pads.to(device)
    orig_shapes = orig_shapes.to(device)
    
    # Get batch indices for each box
    batch_indices = boxes[:, 0].long()
    
    # Unscale coordinates
    boxes[:, 1] = (boxes[:, 1] - pads[batch_indices, 0]) / ratios[batch_indices]  # x1
    boxes[:, 2] = (boxes[:, 2] - pads[batch_indices, 1]) / ratios[batch_indices]  # y1
    boxes[:, 3] = (boxes[:, 3] - pads[batch_indices, 0]) / ratios[batch_indices]  # x2
    boxes[:, 4] = (boxes[:, 4] - pads[batch_indices, 1]) / ratios[batch_indices]  # y2
    
    # Clip to image bounds using proper tensor operations
    zero = torch.zeros_like(boxes[:, 1])
    max_w = orig_shapes[batch_indices, 1].float()
    max_h = orig_shapes[batch_indices, 0].float()
    
    boxes[:, 1] = torch.clamp(boxes[:, 1], zero, max_w)  # x1
    boxes[:, 3] = torch.clamp(boxes[:, 3], zero, max_w)  # x2
    boxes[:, 2] = torch.clamp(boxes[:, 2], zero, max_h)  # y1
    boxes[:, 4] = torch.clamp(boxes[:, 4], zero, max_h)  # y2
    
    return boxes


def draw_results_optimized(frames: List[np.ndarray], results, ratios: torch.Tensor, 
                         pads: torch.Tensor, device: torch.device) -> List[np.ndarray]:
    """Optimized drawing with vectorized operations."""
    if not results or not any(r.boxes is not None for r in results):
        return frames
    
    # Collect all boxes from batch
    all_boxes = []
    
    for i, result in enumerate(results):
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes.data.clone()  # [N, 6] format: x1,y1,x2,y2,conf,cls
            # Add batch index as first column
            batch_idx = torch.full((boxes.shape[0], 1), i, device=device, dtype=boxes.dtype)
            boxes_with_idx = torch.cat([batch_idx, boxes], dim=1)  # [N, 7]
            all_boxes.append(boxes_with_idx)
    
    if not all_boxes:
        return frames
    
    # Concatenate all boxes
    all_boxes = torch.cat(all_boxes, dim=0)
    
    # Prepare original shapes tensor
    orig_shapes = torch.tensor([[f.shape[0], f.shape[1]] for f in frames], 
                              device=device, dtype=torch.float32)
    
    # Vectorized unscaling
    all_boxes = unscale_boxes_vectorized(all_boxes, ratios, pads, orig_shapes)
    
    # Convert back to CPU for drawing
    all_boxes_cpu = all_boxes.cpu().numpy()
    
    # Draw on frames
    output_frames = []
    for i, frame in enumerate(frames):
        frame_copy = frame.copy()
        frame_boxes = all_boxes_cpu[all_boxes_cpu[:, 0] == i]
        
        if len(frame_boxes) > 0:
            # Vectorized drawing preparation
            coords = frame_boxes[:, 1:5].astype(int)  # x1,y1,x2,y2
            confs = frame_boxes[:, 5]
            classes = frame_boxes[:, 6].astype(int)
            
            # Draw all boxes for this frame
            for j, (x1, y1, x2, y2) in enumerate(coords):
                conf = confs[j]
                cls = classes[j]
                
                cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{results[i].names[cls]}: {conf:.2f}"
                cv2.putText(frame_copy, label, (x1, y1 - 10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        output_frames.append(frame_copy)
    
    return output_frames


def load_video_to_memory(video_path: Path, max_frames: int = 2000) -> Optional[np.ndarray]:
    """Load entire video to memory for faster processing."""
    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames > max_frames:
        cap.release()
        return None
    
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    
    cap.release()
    return np.array(frames) if frames else None


def get_codec_info(video_path: Path) -> str:
    """Get video codec information."""
    cap = cv2.VideoCapture(str(video_path))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
    cap.release()
    return codec


def process_video_optimized(video_path: Path, output_path: Path, model: YOLO, config: dict, device: torch.device) -> None:
    """Optimized video processing with GPU acceleration."""
    
    # Try to load video to memory first
    video_frames = load_video_to_memory(video_path, config.get('max_memory_frames', 2000))
    use_memory = video_frames is not None
    
    if use_memory:
        total_frames = len(video_frames)
        fps = 30  # Default, we'll get real fps from original video
        width, height = video_frames[0].shape[1], video_frames[0].shape[0]
        print(f"📋 Loaded {total_frames} frames to memory")
    else:
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Display video info
    codec = get_codec_info(video_path)
    print(f"\n📹 Video: {video_path.name}")
    print(f"   Codec: {codec} | Resolution: {width}x{height} | FPS: {fps:.1f}")
    print(f"   Processing: {'Memory' if use_memory else 'Streaming'}")
    
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
    frame_idx = 0
    
    while frame_idx < total_frames:
        frames = []
        
        # Collect batch of frames
        for _ in range(batch_size):
            if frame_idx >= total_frames:
                break
                
            if use_memory:
                frame = video_frames[frame_idx]
            else:
                ret, frame = cap.read()
                if not ret:
                    break
                
            frames.append(frame)
            frame_idx += 1
        
        if not frames:
            break
        
        batch_start = time.time()
        
        # Optimized preprocessing
        batch_tensor, ratios, pads = preprocess_batch_optimized(frames, imgsz, device)
        
        # Inference
        results = model(batch_tensor, verbose=False)
        
        # Optimized postprocessing
        output_frames = draw_results_optimized(frames, results, ratios, pads, device)
        
        # Write frames
        for output_frame in output_frames:
            writer.write(output_frame)
        
        inference_fps = len(frames) / (time.time() - batch_start)
        processed_frames += len(frames)
        pbar.set_postfix_str(f"{inference_fps:.1f}")
        pbar.update(len(frames))
    
    if not use_memory:
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
    
    # Get device from config
    device = get_device(config)
    
    # Initialize model
    model = YOLO(config['path_weight'])
    model.conf = config.get('conf', 0.25)
    model.iou = config.get('iou', 0.45)
    
    # Enable optimizations
    if config.get('fp16', False) and device.type == 'cuda':
        model.model.half()
    
    # Move model to specified device
    model.to(device)
    
    # Display startup info
    weight_name = Path(config['path_weight']).name
    imgsz = config.get('imgsz', 1280)
    batch = config.get('batch', 16)
    device_name = f"{device.type}:{device.index}" if device.index is not None else str(device)
    
    print(f"✓ Model loaded: {weight_name} on {device_name}")
    if device.type == 'cuda':
        gpu_name = torch.cuda.get_device_name(device)
        print(f"  GPU: {gpu_name}")
    print(f"✓ Config: imgsz={imgsz}, batch={batch}")
    print(f"✓ Memory loading: {'enabled' if config.get('max_memory_frames', 2000) > 0 else 'disabled'}")
    
    video_paths = get_video_paths(config['src_video'])
    print(f"✓ Found {len(video_paths)} video(s) to process")
    
    dst_path = Path(config['dst_video'])
    
    if len(video_paths) == 1 and dst_path.suffix:
        process_video_optimized(video_paths[0], dst_path, model, config, device)
    else:
        for video_path in video_paths:
            output_path = dst_path / f"{video_path.stem}_detected{video_path.suffix}"
            process_video_optimized(video_path, output_path, model, config, device)


if __name__ == "__main__":
    inference_video()