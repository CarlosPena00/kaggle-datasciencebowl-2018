from __future__ import print_function
import os
import shutil
import math

import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import warnings

warnings.filterwarnings("ignore")


class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()        

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0
        
    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def to_np(x):
    return x.data.cpu().numpy()

def to_var(x, cuda, requires_grad=False, volatile=False):
    if cuda: x = x.cuda()
    return Variable(x, requires_grad=requires_grad, volatile=volatile)

def argmax(x): return torch.max(x, 1)[1]

def fit(net, ngpu, inputs):
    if ngpu > 1: outputs = nn.parallel.data_parallel(net, inputs, range(ngpu))
    else: outputs = net(inputs)
    return outputs

def adjust_learning_rate(optimizer, epoch, lr):
    """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
    lr = lr * (0.1 ** (epoch // 30))    
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr
    return lr


def save_checkpoint(state, is_best, path, filename='checkpoint.pth.tar'):
    """Saves checkpoint to disk"""
    filename = os.path.join(path, filename)
    torch.save(state, filename)
    if is_best:
        shutil.copyfile(filename, os.path.join(path, 'model_best.pth.tar'))

def resumecheckpoint(resume, net, optimizer):
    """Optionally resume from a checkpoint"""
    start_epoch = 0
    prec = 0
    if resume:
        if os.path.isfile(resume):
            print("=> loading checkpoint '{}'".format(resume))
            checkpoint = torch.load(resume)
            start_epoch = checkpoint['epoch']
            prec = checkpoint['prec']
            net.load_state_dict(checkpoint['state_dict'])
            optimizer.load_state_dict(checkpoint['optimizer'])
            print("=> loaded checkpoint '{}' (epoch {})"
                  .format(resume, checkpoint['epoch']))
        else:
            print("=> no checkpoint found at '{}'".format(resume))

    return start_epoch, prec
