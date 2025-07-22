import torch
import cv2
import yaml
import numpy as np
import time
from pathlib import Path
from ultralytics import YOLO
from typing import List, Tuple, Optional
from tqdm import tqdm


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_device(config: dict) -> torch.device:
    device_str = config.get('device', 'auto')
    if device_str == 'auto' or (device_str.startswith('cuda') and not torch.cuda.is_available()):
        return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    return torch.device(device_str if device_str.startswith(('cuda', 'cpu')) else 'cpu')


def load_frames_to_memory(video_path: Path, max_frames: int) -> Optional[np.ndarray]:
    if max_frames <= 0:
        return None
    
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


def letterbox_preprocess(frames: np.ndarray, imgsz: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    batch_tensor = torch.from_numpy(frames).to(device)
    B, H, W = batch_tensor.shape[:3]
    
    # BGR to RGB and normalize
    batch_tensor = batch_tensor[..., [2, 1, 0]].permute(0, 3, 1, 2).float() / 255.0
    
    # Calculate letterbox parameters
    scale = imgsz / max(H, W)
    new_h, new_w = int(H * scale), int(W * scale)
    pad_h, pad_w = (imgsz - new_h) // 2, (imgsz - new_w) // 2
    
    # Resize and pad
    batch_tensor = torch.nn.functional.interpolate(batch_tensor, size=(new_h, new_w), mode='bilinear', align_corners=False)
    batch_tensor = torch.nn.functional.pad(batch_tensor, (pad_w, imgsz - new_w - pad_w, pad_h, imgsz - new_h - pad_h), value=114/255.0)
    
    ratios = torch.full((B,), scale, device=device, dtype=torch.float32)
    pads = torch.tensor([pad_w, pad_h], device=device, dtype=torch.float32).expand(B, 2)
    
    return batch_tensor, ratios, pads


def postprocess_batch(frames: List[np.ndarray], results, ratios: torch.Tensor, pads: torch.Tensor, device: torch.device) -> List[np.ndarray]:
    if not results or not any(r.boxes is not None and len(r.boxes) > 0 for r in results):
        return frames
    
    # Collect all detections
    all_boxes = []
    for i, result in enumerate(results):
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes.data.clone()
            batch_idx = torch.full((boxes.shape[0], 1), i, device=device, dtype=boxes.dtype)
            all_boxes.append(torch.cat([batch_idx, boxes], dim=1))
    
    if not all_boxes:
        return frames
    
    all_boxes = torch.cat(all_boxes, dim=0)
    batch_indices = all_boxes[:, 0].long()
    
    # Vectorized coordinate unscaling
    all_boxes[:, [1, 3]] = (all_boxes[:, [1, 3]] - pads[batch_indices, 0:1]) / ratios[batch_indices].unsqueeze(1)  # x1, x2
    all_boxes[:, [2, 4]] = (all_boxes[:, [2, 4]] - pads[batch_indices, 1:2]) / ratios[batch_indices].unsqueeze(1)  # y1, y2
    
    # Clamp to frame bounds
    frame_shapes = torch.tensor([[f.shape[0], f.shape[1]] for f in frames], device=device, dtype=torch.float32)
    zero = torch.tensor(0.0, device=device)
    all_boxes[:, [1, 3]] = torch.clamp(all_boxes[:, [1, 3]], zero, frame_shapes[batch_indices, 1:2])  # x bounds
    all_boxes[:, [2, 4]] = torch.clamp(all_boxes[:, [2, 4]], zero, frame_shapes[batch_indices, 0:1])  # y bounds
    
    # Draw detections
    boxes_cpu = all_boxes.cpu().numpy()
    output_frames = []
    
    for i, frame in enumerate(frames):
        frame_copy = frame.copy()
        frame_boxes = boxes_cpu[boxes_cpu[:, 0] == i]
        
        for box in frame_boxes:
            x1, y1, x2, y2 = map(int, box[1:5])
            conf, cls = box[5], int(box[6])
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame_copy, f"{results[i].names[cls]}: {conf:.2f}", (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        output_frames.append(frame_copy)
    
    return output_frames


def process_video(video_path: Path, output_path: Path, model: YOLO, config: dict, device: torch.device) -> None:
    # Setup video I/O
    memory_frames = load_frames_to_memory(video_path, config.get('max_memory_frames', 2000))
    
    if memory_frames is not None:
        total_frames, fps, width, height = len(memory_frames), 30.0, memory_frames[0].shape[1], memory_frames[0].shape[0]
        print(f"📋 Loaded {total_frames} frames to memory")
        cap = None
    else:
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Video info
    fourcc = int(cv2.VideoCapture(str(video_path)).get(cv2.CAP_PROP_FOURCC))
    codec = "".join(chr(fourcc >> 8 * i & 0xFF) for i in range(4))
    print(f"📹 {video_path.name} | {codec} | {width}x{height} | {fps:.1f}fps | {'Memory' if memory_frames is not None else 'Stream'}")
    
    # Setup output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    
    imgsz, batch_size = config.get('imgsz', 1280), config.get('batch', 16)
    
    # Process batches
    pbar = tqdm(total=total_frames, desc="Processing", unit="frames")
    processed_frames, start_time, frame_idx = 0, time.time(), 0
    
    while frame_idx < total_frames:
        # Collect batch
        frames = []
        for _ in range(min(batch_size, total_frames - frame_idx)):
            if memory_frames is not None:
                frames.append(memory_frames[frame_idx])
            else:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            frame_idx += 1
        
        if not frames:
            break
        
        # Inference pipeline
        batch_start = time.time()
        batch_tensor, ratios, pads = letterbox_preprocess(np.stack(frames), imgsz, device)
        results = model(batch_tensor, verbose=False)
        output_frames = postprocess_batch(frames, results, ratios, pads, device)
        
        # Write output
        for frame in output_frames:
            writer.write(frame)
        
        # Update progress
        processed_frames += len(frames)
        pbar.set_postfix_str(f"{len(frames) / (time.time() - batch_start):.1f}")
        pbar.update(len(frames))
    
    # Cleanup
    if cap:
        cap.release()
    writer.release()
    pbar.close()
    
    total_time = time.time() - start_time
    print(f"✓ {output_path.name} | {processed_frames} frames | {total_time:.1f}s | {processed_frames/total_time:.1f} avg fps")


def main(config_path: str = "config.yaml") -> None:
    print("🚀 Starting YOLO video inference...")
    
    config = load_config(config_path)
    device = get_device(config)
    
    # Setup model
    model = YOLO(config['path_weight'])
    model.conf, model.iou = config.get('conf', 0.25), config.get('iou', 0.45)
    
    if config.get('fp16', False) and device.type == 'cuda':
        model.model.half()
    
    model.to(device)
    
    # Display info
    device_name = f"{device.type}:{device.index}" if device.index is not None else str(device)
    print(f"✓ {Path(config['path_weight']).name} on {device_name}")
    
    if device.type == 'cuda':
        print(f"  {torch.cuda.get_device_name(device)}")
    
    # Process videos
    src_path, dst_path = Path(config['src_video']), Path(config['dst_video'])
    
    if src_path.is_file():
        assert dst_path.suffix, "Output must be file when input is file"
        video_paths = [src_path]
    elif src_path.is_dir():
        assert not dst_path.suffix, "Output must be directory when input is directory"
        video_paths = [p for p in src_path.rglob('*') if p.suffix.lower() in {'.mp4', '.avi', '.mov', '.mkv', '.webm'}]
    else:
        raise FileNotFoundError(f"Source path not found: {src_path}")
    
    print(f"✓ Processing {len(video_paths)} video(s)")
    
    # Process each video
    for video_path in video_paths:
        output_path = dst_path if dst_path.suffix else dst_path / f"{video_path.stem}_detected{video_path.suffix}"
        process_video(video_path, output_path, model, config, device)


if __name__ == "__main__":
    main()