import numpy as np
from torch.utils.data import DataLoader, Subset

from datasets.utils import CombinedDataSet
from datasets.visda import CustomVisdaTarget, CustomVisdaSource

DATA_SETS = {
    CustomVisdaTarget.code(): CustomVisdaTarget,
    CustomVisdaSource.code(): CustomVisdaSource,
}


def _get_eval_transform_type(target_dataset_code):
    if target_dataset_code == CustomVisdaTarget.code():
        return 'visda_standard'
    else:
        return 'none'


def dataset_factory(dataset_code, transform_type, is_train=True, **kwargs):
    cls = DATA_SETS[dataset_code]
    transform = cls.train_transform_config(transform_type) if is_train else cls.eval_transform_config(transform_type)

    print("{} has been created.".format(cls.code()))
    return cls(transform=transform, is_train=is_train, **kwargs)


def dataloaders_factory(args):
    source_dataset_code = args.source_dataset_code
    target_dataset_code = args.target_dataset_code
    transform_type = args.transform_type

    if source_dataset_code == CustomVisdaSource.code() and target_dataset_code == CustomVisdaTarget.code():
        source_train_dataset = dataset_factory(source_dataset_code, transform_type + '_source', is_train=True)
        target_train_dataset = dataset_factory(target_dataset_code, transform_type + '_target', is_train=True)
    else:
        source_train_dataset = dataset_factory(source_dataset_code, transform_type, is_train=True)
        target_train_dataset = dataset_factory(target_dataset_code, transform_type, is_train=True)

    train_dataset = CombinedDataSet(source_train_dataset, target_train_dataset)

    target_transform_type = _get_eval_transform_type(target_dataset_code)
    target_val_dataset = dataset_factory(target_dataset_code, target_transform_type, is_train=False)

    if args.test:
        train_dataset = Subset(train_dataset, np.random.randint(0, len(train_dataset), args.batch_size * 5))
        target_val_dataset = Subset(target_val_dataset,
                                    np.random.randint(0, len(target_val_dataset), args.batch_size * 5))

    train_dataloader = DataLoader(train_dataset, batch_size=args.batch_size, num_workers=32, shuffle=True,
                                  pin_memory=True)

    target_val_dataloader = DataLoader(target_val_dataset,
                                       batch_size=args.batch_size, num_workers=16, shuffle=False, pin_memory=True)
    return {
        'train': train_dataloader,
        'val': target_val_dataloader
    }
