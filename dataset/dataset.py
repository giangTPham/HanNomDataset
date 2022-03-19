from torch.utils.data import Dataset
from .imGen import FontStorage
from .ChineseDictionary import get_allCharacters
from .dataAugment import basic_transforms
from .cache import CacheImg
import random
import numpy as np

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

class SimSiamDataset(BaseDataset):
    '''
    Dataset used in Simsiam experiment.
    Return two different "views" of the same characters.
    Two views are essentially generated from different fonts, with augmentation.
    '''
    def __init__(self, cfg, transform=None, one_font_only=False):
        super().__init__(cfg, transform, one_font_only)

    def __getitem__(self, i):
        char_index = i % self.n_fonts
        other_indx = char_index*self.n_fonts +  random.randint(0, self.n_fonts-1)
        
        x1 = self.gen_char_img(i)
        x2 = self.gen_char_img(other_indx)
        
        return self.transform(x1), self.transform(x2)
        
class TripletDataset(BaseDataset):
    '''
    Dataset used in Triplet experiment.
    Return augmented images and their corresponding labels.
    '''	
    def __init__(self, cfg, transform=None, one_font_only=False):
        super().__init__(cfg, transform, one_font_only)
        import numpy as np
        self.label_list = np.tile(np.arange(self.n_chars), self.n_fonts)

    def getlabel(self, i):
        return self.allCharacters[i%self.n_chars]
        
    def __getitem__(self, i):
        char_index = i % self.n_chars
        
        x = self.gen_char_img(i)
        
        return self.transform(x), char_index
 
