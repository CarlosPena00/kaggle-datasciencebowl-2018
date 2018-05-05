import os

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils

import numpy as np
import random as rnd
from collections import namedtuple
from skimage import io, transform
from skimage import color
import cv2

import warnings
warnings.filterwarnings("ignore")

from deep.datasets import render as rnd
from deep.datasets import imageutl as imutl
from deep.datasets import weightmaps as wmap
from deep.datasets import utility

class SyntheticColorCheckerDataset(Dataset):
    '''
    Mnagement for Synthetic Color Checker dataset
    '''

    def __init__(self, 
        pathname,
        ext='jpg',
        transform=None,
        ):
        """           
        """            
        
        self.data = imutl.imageProvide(pathname, ext=ext);
        self.ren = rnd.Render();
        self.transform = transform      

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):   

        image = self.data[idx]
        image = utility.resize_image(image, 640, 1024, resize_mode='crop');
        image, mask = self.ren.generate_for_segmentation_mask( image, num=5 )   
        weight = wmap.getweightmap( mask )     

        #to rgb
        if len(image.shape)==2 or (image.shape==3 and image.shape[2]==1):
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        

        image_t = image        
        label_t = np.zeros( (mask.shape[0], mask.shape[1], 2 ) )
        label_t[:,:,0] = (mask <= 0).astype( np.uint8 )
        label_t[:,:,1] = (mask > 0).astype( np.uint8 )
        weight_t = weight

        #label_t = label_t[:,:,np.newaxis] 
        weight_t = weight[:,:,np.newaxis] 

        sample = {'image': image_t, 'label':label_t, 'weight':weight_t }
        if self.transform: 
            sample = self.transform(sample)
        return sample


class SynteticColorCheckerExDataset(Dataset):
    '''
    Mnagement for Synthetic Color Checker dataset
    '''

    def __init__(self, 
        pathname,
        ext='jpg',
        count=100,
        idx_base=0,
        transform=None,
        ):
        """           
        """            
        
        self.data = imutl.imageProvide(pathname, ext=ext);
        self.ren = rnd.Render();
        self.transform = transform 
        self.count = count
        self.idx_base = idx_base     

    def __len__(self):
        return self.count

    def __getitem__(self, idx):   

        image = self.data[ (self.idx_base + dx)%len(self.data)  ]
        image = utility.resize_image(image, 640, 1024, resize_mode='crop');

        #to rgb
        if len(image.shape)==2 or (image.shape==3 and image.shape[2]==1):
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        image, mask = self.ren.generate_for_segmentation_mask( image, num=5 )   
        weight = wmap.getweightmap( mask )     
        
        image_t = image        
        label_t = np.zeros( (mask.shape[0], mask.shape[1], 2) )
        label_t[:,:,0] = (mask <= 0).astype( np.uint8 )
        label_t[:,:,1] = (mask > 0).astype( np.uint8 )
        weight_t = weight

        #label_t = label_t[:,:,np.newaxis] 
        weight_t = weight[:,:,np.newaxis] 

        sample = {'image': image_t, 'label':label_t, 'weight':weight_t }
        if self.transform: 
            sample = self.transform(sample)
        return sample