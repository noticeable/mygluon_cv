'''
    ModelNet dataset. Support ModelNet40, ModelNet10, XYZ and normal channels. Up to 10000 points.
'''

import os
import os.path
import numpy as np
from . import pc_tranforms
from mxnet.gluon.data import Dataset
from mxnet.gluon.data import DataLoader
from mxnet import nd
from mxnet.gluon.data.vision import transforms

__all__ = ['ModelNetDataset']


class ModelNetDataset(Dataset):
    def __init__(self, root='/mnt/mdisk/xcq/ModelNet', train=True, modelnet='ModelNet10', npoint=300, transform=None):
        super(ModelNetDataset, self).__init__()
        self.root = os.path.join(root,modelnet)
        self.train = train
        self.transform = transform
        self.npoint = npoint
        self.mode = modelnet
        self.files, classes = self.files_name()
        self.labels = {}
        for i, name in enumerate(classes):
            self.labels.update({name: i})

    def files_name(self):
        if self.mode == 'ModelNet10':
            CLASS = ['bathtub', 'bed', 'chair', 'desk', 'dresser', 'monitor', 'night_stand', 'sofa', 'table', 'toilet']
        elif self.mode == 'ModelNet40':
            CLASS = ['sink', 'stairs', 'laptop', 'night_stand', 'bed', 'mantel', 'curtain', 'vase', 'toilet', 'person',
                     'stool', 'cup', 'glass_box', 'desk', 'door', 'tent', 'range_hood', 'table', 'radio', 'car',
                     'lamp', 'tv_stand', 'xbox', 'piano', 'plant', 'monitor', 'dresser', 'chair', 'flower_pot', 'bathtub',
                     'guitar', 'airplane', 'bench', 'keyboard', 'bottle', 'bookshelf', 'sofa', 'cone', 'wardrobe', 'bowl']
        else:
            raise NameError
        files = {'files': [], 'labels': []}
        for i, cls in enumerate(CLASS):
            if self.train:
                for file in os.listdir(os.path.join(self.root, cls, 'train')):
                    if file.endswith('.off'):
                        files['files'].append(os.path.join(self.root, cls, 'train', file))
                        files['labels'].append(i)
            else:
                for file in os.listdir(os.path.join(self.root, cls, 'test')):
                    if file.endswith('.off'):
                        files['files'].append(os.path.join(self.root, cls, 'test', file))
                        files['labels'].append(i)
        return files, CLASS

    def __getitem__(self, idx):
        with open(self.files['files'][idx]) as off:
            point_matrix = []
            for i, data in enumerate(off.readlines()):
                if i == 0:
                    continue
                elif i == 1:
                    data = data.strip('\n')
                    nums = data.split(' ')
                    nums = [int(x) for x in nums]
                    npoint = nums[0]
                    if self.npoint > npoint-2:
                        print(self.files['files'][idx], npoint)
                        # raise ValueError("npoint beyong the range.")
                else:
                    data = data.strip('\n')
                    nums = data.split(' ')
                    nums = [float(x) for x in nums]
                    point_matrix.append(nums)
                if i > npoint - 2:
                    if self.npoint>npoint-2:
                        [point_matrix.append(nums) for _ in range(0, self.npoint-npoint+2)]
                    point_matrix = np.stack(point_matrix)
                    break
        choice = np.random.choice(point_matrix.shape[0], self.npoint, replace=True)
        data = point_matrix[choice, :]
        label = self.files['labels'][idx]
        if self.transform is not None:
            for trans in self.transform:
                data = trans(data)
        return nd.array(data), nd.array([label])

    def __len__(self):
        return len(self.files['labels'])


if __name__ == '__main__':

    dataset = ModelNetDataset()
    dataloader = DataLoader(dataset, batch_size=128, shuffle=True, num_workers=8)
    for i,batch in enumerate(dataloader):
        print(i)
