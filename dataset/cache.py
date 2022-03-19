import os
import numpy as np

class CacheImg:
	def __init__(self, save_to=None, limit=100000):
		self.save_to = save_to
		self.cache_hit = 0
		self.limit = limit
		if save_to is None:
			cur_dir = os.path.dirname(os.path.realpath(__file__))
			self.save_to = os.path.join(cur_dir, 'data')
		
		self.create_folder()
		
		self.indices = set(os.listdir(self.save_to))
		print('Found {} characters in cache folder'.format(len(self.indices)))
		
		
	def add(self, data, id):
		'''
		Add new data to cache file
		data must be a ndarray 
		'''
		# if self._getname(id) in self.indices:
			# return
		if len(self.indices) >= self.limit:
			return
		self.indices.add(self._getname(id))
		path = os.path.join(self.save_to, self._getname(id))
		with open(path, 'wb') as f:
			np.save(f, data)
		
	
	def exist(self, id):
		return self._getname(id) in self.indices
		
	def get(self, id):
		self.cache_hit += 1
		if (self.cache_hit + 1) % self.limit == 0:
			print('Cache hit rate reaches {} times'.format(self.cache_hit))
			
		im_path = os.path.join(self.save_to, self._getname(id))
		data = None
		with open(im_path, 'rb') as f:
			data = np.load(f)
		return data
		
	def _getname(self, id):
		return '{}.npy'.format(str(id))
		
	def create_folder(self):
		if not (os.path.exists(self.save_to)):
			print('Creating cache folder...')
			os.makedirs(self.save_to)
			print('Done')
			
	def reset(self):
		print('Resetting cache...')
		self.indices = set()
		os.remove(self.save_to)
		self.create_folder()