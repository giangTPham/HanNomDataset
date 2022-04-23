from torch.utils.data import Dataset
from .imGen import FontStorage
from .ChineseDictionary import get_allCharacters
from .dataAugment import basic_transforms
from .cache import CacheImg
import random
import numpy as np

TRAIN_SIZE = 6000
TEST_SIZE = 200

class BaseDataset(Dataset):
    '''
    Base class for creating dataset.
    Support generating synthetic images online.
    '''
    def __init__(self, cfg, transform=None, one_font_only=False, *args, **kwargs):
        self.fonts = FontStorage(n_fonts=cfg.data.n_fonts if not one_font_only else 1, 
            img_size=cfg.data.input_shape, *args, **kwargs)
        self.n_fonts = len(self.fonts)
        self.allCharacters = get_allCharacters()
        self.n_chars = len(self.allCharacters)
        self.len = self.n_fonts * self.n_chars
        self.transform = transform
        self.img_size = cfg.data.input_shape
        self.cache = CacheImg()
        
        if self.transform is None:
            self.transform = basic_transforms(cfg)

            
    def __len__(self):
        return self.len
        
    def _gen_char_img(self, i):
        char_index = i % len(self.allCharacters)
        font_index = i // len(self.allCharacters)
        char = self.allCharacters[char_index]
        
        data = self.fonts.gen_char_img(char, font_index)
        self.cache.add(data, i)
        return data
    
    def gen_char_img(self, i):
        if self.cache.exist(i):
            try:
                return self.cache.get(i)
            except:
                return self._gen_char_img(i)
        else:
            return self._gen_char_img(i)
        
    def __getitem__(self, i):
        raise NotImplementedError

class HanNomDataset(BaseDataset):
    '''
    Dataset used in Triplet experiment.
    Return augmented images and their corresponding labels.
    '''	
    def __init__(self, cfg, transform=None, one_font_only=False,train=True):
        super().__init__(cfg, transform, one_font_only)
        import numpy as np
        if train:
            self.allCharacters = self.allCharacters[:TRAIN_SIZE]
            self.n_chars = len(self.allCharacters)
            self.len = self.n_fonts * self.n_chars
        else:
            self.allCharacters = self.allCharacters[TRAIN_SIZE:TRAIN_SIZE+TEST_SIZE]
            self.n_chars = len(self.allCharacters)
            self.len = self.n_fonts * self.n_chars
        self.label_list = np.tile(np.arange(self.n_chars), self.n_fonts)

    def getlabel(self, i):
        return self.allCharacters[i%self.n_chars]
        
    def __getitem__(self, i):
        char_index = i % self.n_chars
        
        x = self.gen_char_img(i)
        
        return self.transform(x), char_index
