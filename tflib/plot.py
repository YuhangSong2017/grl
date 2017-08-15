import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import collections
import time
import cPickle as pickle
import dill
import scipy.signal

import torch
import visdom
vis = visdom.Visdom()

MEAN_NUM = 50

class logger(object):
	"""docstring for logger"""
	def __init__(self,LOGDIR,DSP,params_str):
		super(logger, self).__init__()

		self.LOGDIR = LOGDIR
		self.DSP = DSP
		self.params_str = params_str

		self._iter = 0

		self._since_beginning = collections.defaultdict(lambda: {})
		self._since_last_flush = collections.defaultdict(lambda: {})

	def restore(self):

		print('Try load previous plot....')
		try:
			self._since_beginning = dill.load(open(self.LOGDIR+'log.pkl', "r"))
			self._iter = dill.load(open(self.LOGDIR+'iteration.pkl', "r"))
			print('Restore plot from iter: '+str(self._iter))
			return self._iter
		except Exception, e:
			print('Previous plot unfounded')
			return 0
		print('')

	def tick(self):
		self._iter += 1

	def plot(self, name, value):
		value = np.asarray(value)
		self._since_last_flush[name][self._iter] = value

	def flush(self):

		vis.text(
			self.params_str.replace('\n','<br>'),
			win='discribe'
		)

		for name, vals in self._since_last_flush.items():

			self._since_beginning[name].update(vals)

			x_vals = np.sort(self._since_beginning[name].keys())
			y_vals = np.squeeze(np.asarray([self._since_beginning[name][x] for x in x_vals]))


			plt.clf()
			plt.plot(x_vals, y_vals)
			print(y_vals)
			if np.shape(y_vals)[0] > 1:
				y_vals_meaned = scipy.signal.convolve(
					in1=y_vals,
					in2=np.asarray([1.0/MEAN_NUM]*MEAN_NUM),
					mode='same',
					method='auto'
				)
				plt.plot(x_vals, y_vals_meaned)
			plt.xlabel('iteration')
			plt.ylabel(name)
			plt.savefig(self.LOGDIR+name+'.jpg')

			x_vals = torch.from_numpy(np.asarray(x_vals))

			if np.shape(y_vals)[0] > 1:
				y_vals = torch.cat(
					[torch.FloatTensor(y_vals).unsqueeze(1),
					torch.FloatTensor(y_vals_meaned).unsqueeze(1)],
					1
				)

			if len(x_vals) > 1:
				vis.line(   X=x_vals,
							Y=y_vals,
		                    win=name,
		                    opts=dict(title=name))

		self._since_last_flush.clear()

		with open(self.LOGDIR+'log.pkl', 'wb') as f:
			dill.dump(self._since_beginning, f)
		with open(self.LOGDIR+'iteration.pkl', 'wb') as f:
			dill.dump(self._iter, f)
