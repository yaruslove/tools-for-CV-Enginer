import os
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

class YOLOResultsProcessor:
    def __init__(self, config_path: str):
        """Initialize processor with config file path."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.src_dir = Path(config['src'])
        self.dst_dir = Path(config['dst'])
        self.dst_dir.mkdir(parents=True, exist_ok=True)

    def _read_yaml(self, file_path: Path) -> Dict:
        """Read YAML file and return dictionary."""
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)

    def _get_train_dirs(self) -> List[Path]:
        """Get all train directories sorted by number."""
        train_dirs = []
        for d in self.src_dir.iterdir():
            if d.is_dir() and d.name.startswith('train'):
                train_dirs.append(d)
        return sorted(train_dirs, key=lambda x: int(x.name.replace('train', '')) if x.name != 'train' else 0)

    def _get_best_metrics(self, results_csv: Path) -> pd.Series:
        """Get metrics for epoch with best mAP50-95(B)."""
        df = pd.read_csv(results_csv)
        return df.loc[df['metrics/mAP50-95(B)'].idxmax()]

    def create_summary_table(self) -> pd.DataFrame:
        """Create summary table from all train directories."""
        rows = []
        for train_dir in self._get_train_dirs():
            args_path = train_dir / 'args.yaml'
            results_path = train_dir / 'results.csv'
            
            if not (args_path.exists() and results_path.exists()):
                continue

            args = self._read_yaml(args_path)
            best_metrics = self._get_best_metrics(results_path)

            row = {
                'experiment': train_dir.name,
                'model': args['model'],
                'imgsz': args['imgsz'],
                'epochs': args['epochs'],
                'batch': args['batch'],
                'best_epoch': best_metrics['epoch'],
                'train/box_loss': best_metrics['train/box_loss'],
                'train/cls_loss': best_metrics['train/cls_loss'],
                'train/dfl_loss': best_metrics['train/dfl_loss'],
                'metrics/precision(B)': best_metrics['metrics/precision(B)'],
                'metrics/recall(B)': best_metrics['metrics/recall(B)'],
                'metrics/mAP50(B)': best_metrics['metrics/mAP50(B)'],
                'metrics/mAP50-95(B)': best_metrics['metrics/mAP50-95(B)'],
                'val/box_loss': best_metrics['val/box_loss'],
                'val/cls_loss': best_metrics['val/cls_loss'],
                'val/dfl_loss': best_metrics['val/dfl_loss']
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(self.dst_dir / 'table_01.csv', index=False)
        return df

    def get_training_data(self) -> Dict[str, pd.DataFrame]:
        """Get training data from all experiments."""
        data = {}
        for train_dir in self._get_train_dirs():
            results_path = train_dir / 'results.csv'
            if results_path.exists():
                data[train_dir.name] = pd.read_csv(results_path)
        return data

if __name__ == '__main__':
    processor = YOLOResultsProcessor('config.yaml')
    processor.create_summary_table()