import glob
import os.path as osp
from typing import Optional, Tuple

from pytorch_lightning import LightningDataModule
from torch.utils.data import DataLoader, Dataset

from semantic_val.datamodules.datasets.lidar_dataset import (
    LidarToyTestDataset,
    LidarTrainDataset,
    LidarValDataset,
)
from semantic_val.datamodules.datasets.lidar_transforms import (
    transform_labels_for_building_segmentation,
)


class LidarDataModule(LightningDataModule):
    """
    A DataModule implements 5 key methods:
        - prepare_data (things to do on 1 GPU/TPU, not on every GPU/TPU in distributed mode)
        - setup (things to do on every accelerator in distributed mode)
        - train_dataloader (the training dataloader)
        - val_dataloader (the validation dataloader(s))
        - test_dataloader (the test dataloader(s))

    Read the docs:
        https://pytorch-lightning.readthedocs.io/en/latest/extensions/datamodules.html
    """

    def __init__(
        self,
        data_dir: str = "./data/lidar_toy/",
        batch_size: int = 8,
        num_workers: int = 0,
        subtile_width_meters: float = 100.0,
        subtile_overlap: float = 0.0,
        input_cloud_size: int = 200000,
        train_subtiles_by_tile: int = 4,
    ):
        super().__init__()

        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.input_cloud_size = input_cloud_size
        self.subtile_width_meters = subtile_width_meters
        self.train_subtiles_by_tile = train_subtiles_by_tile

        self.subtile_overlap = subtile_overlap
        self.data_train: Optional[Dataset] = None
        self.data_val: Optional[Dataset] = None
        self.data_test: Optional[Dataset] = None

    @property
    def num_classes(self) -> int:
        return 2

    def prepare_data(self):
        """Download data if needed. This method is called only from a single GPU.
        Do not use it to assign state (self.x = y)."""
        # TODO: implement train-val-test split that add a split column used as reference for later datasets
        pass

    def setup(self, stage: Optional[str] = None):
        """Load data. Set variables: self.data_train, self.data_val, self.data_test."""

        train_files = glob.glob(osp.join(self.data_dir, "train/*.las"))
        train_files = sorted(train_files * self.train_subtiles_by_tile)
        val_files = glob.glob(osp.join(self.data_dir, "val/*.las"))
        test_files = glob.glob(osp.join(self.data_dir, "test/*.las"))

        # TODO : add data augmentation using PytorchGeometric
        self.data_train = LidarTrainDataset(
            train_files,
            transform=None,
            target_transform=transform_labels_for_building_segmentation,
            input_cloud_size=self.input_cloud_size,
            subtile_width_meters=self.subtile_width_meters,
        )
        # self.dims is returned when you call datamodule.size()
        self.dims = tuple(self.data_train[0][0].shape)

        self.data_val = LidarValDataset(
            val_files,
            transform=None,
            target_transform=transform_labels_for_building_segmentation,
            input_cloud_size=self.input_cloud_size,
            subtile_width_meters=self.subtile_width_meters,
            subtile_overlap=self.subtile_overlap,
        )
        self.data_test = LidarToyTestDataset(
            test_files,
            transform=None,
            target_transform=transform_labels_for_building_segmentation,
            input_cloud_size=self.input_cloud_size,
            subtile_width_meters=self.subtile_width_meters,
            subtile_overlap=self.subtile_overlap,
        )

    def train_dataloader(self):
        return DataLoader(
            dataset=self.data_train,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            shuffle=True,
        )

    def val_dataloader(self):
        return DataLoader(
            dataset=self.data_val,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            shuffle=False,
        )

    def test_dataloader(self):
        return DataLoader(
            dataset=self.data_test,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            shuffle=False,
        )
