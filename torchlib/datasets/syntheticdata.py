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

from .render import ColorCheckerRender, CircleRender, EllipseRender
from .aumentation import ObjectImageMaskAndWeightTransform

from . import imageutl as imutl
from . import weightmaps as wmap
from . import utility



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
        self.ren = ColorCheckerRender();
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
        self.ren = ColorCheckerRender();
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

class SynteticCircleDataset(Dataset):
    '''
    Mnagement for Synthetic Circle dataset
    '''

    def __init__(self, 
        count=100,
        cnt=5,
        imsize=(512, 512),
        rmin=5, rmax=50,
        border=90,
        sigma=0.2,
        btouch=True,
        bdraw_grid=False,
        transform=None,
        ):
        """           
        """            
        
        self.ren = CircleRender();
        self.count = count
        self.imsize= imsize
        self.cnt = cnt
        self.rmin = rmin
        self.rmax = rmax
        self.border = border
        self.sigma = sigma
        self.btouch = btouch
        self.transform = transform 
        self.bdraw_grid = bdraw_grid
    

    def __len__(self):
        return self.count

    def __getitem__(self, idx):   
        
        image, masks, meta = self.ren.generate( 
            self.imsize[0], self.imsize[1], self.cnt, self.rmin, 
            self.rmax, self.border, self.sigma, 
            self.btouch
            )

        mask = masks.max(0)
        #weight = wmap.getweightmap( mask )     
        weight = wmap.getunetweightmap(mask, masks )
        
        image_t = image
        label_t = np.zeros( (mask.shape[0], mask.shape[1], 2) )
        label_t[:,:,0] = (mask <= 0).astype( np.uint8 )
        label_t[:,:,1] = (mask > 0).astype( np.uint8 )
        weight_t = weight

        #label_t = label_t[:,:,np.newaxis] 
        weight_t = weight[:,:,np.newaxis] 

        obj = ObjectImageMaskAndWeightTransform( image_t, label_t, weight_t  )

        if self.bdraw_grid:
            obj._draw_grid( grid_size=50 )

        if self.transform: 
            sample = self.transform( obj )

        return obj.to_output()

