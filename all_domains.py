import numpy as np
import visualizer
import cv2
from random import choice
import itertools
import numpy as np
import torch
import copy

'''
    This code is initially provided by Chris
'''

# three representations
SCALAR = 0
VECTOR = 1
IMAGE = 2

# for image, the size of every block in grid world
BLOCK_SIZE = 4

# some of the domain has too many starts state, this will limit
# the evaluation to parts of the starts state, instead of evaluating
# them all
LIMIT_START_STATE_TO = 50

# for the background of the grid world, it is gray
FEATURE_DISCOUNT = 0.5

class Tireworld(object):

    def __init__(self, **args):

        '''general config'''
        self.config(**args)
        self.reset()
        self.build_domain_list()
        self.build_domain_related_list()

    def config(self):
        self.accept_gate=0.01
        
    def build_domain_list(self):
        '''domain specific'''
        self.descriptions_list = []
        for at_temp in range(self.description['at_len']):
            for flattire_temp in [0, 1]:
                self.description['at'], self.description['flattire'] = at_temp, flattire_temp
                self.descriptions_list += [copy.deepcopy(self.description)]

    def build_domain_related_list(self):
        self.state_list = []
        for description in self.descriptions_list:
            self.state_list  += [self.description_to_state(description)]
        
        self.string_list = []
        for description in self.descriptions_list:
            self.string_list += [self.description_to_string(description)]

    def get_description(self):
        return self.description

    def set_domain(self, description):
        '''set domain with description'''
        '''domain specific'''
        self.description = description

    def description_to_state(self, description):
        '''description to state'''
        '''domain specific'''
        at_state = np.zeros((self.description['at_len']), dtype=np.float)
        at_state[int(description['at'])] = 1.0
        flattire_state = np.zeros((1), dtype=np.float)
        flattire_state[0] = description['flattire']
        return np.concatenate((at_state, flattire_state), axis=0)

    def description_to_string(self, description):
        '''get current string'''
        return str(description)

    def get_state_size(self):
        return self.description['at_len']+1

    def get_state_list(self):
        return self.state_list
        # return [self.description_to_state([2, 0])]

    def get_string_list(self):
        return self.string_list

    def state_to_description(self, state, include_background=None):
        '''domain specific'''
        for i in range(len(self.state_list)):
            if np.mean(np.abs(state-self.state_list[i]))<self.accept_gate:
                return self.descriptions_list[i]
        return 'bad state'

    def get_transition_probs(self, description, is_tabular=False):
        '''string: prob'''
        '''domain specific'''

        prob_dict = {}
        self.set_domain(description=description)
        self.update()
        description_next=self.get_description()
        if description['flattire']==1:
            description_next['flattire']=1
            prob_dict[self.description_to_string(description_next)]=1.0
        else:
            description_next['flattire']=1
            prob_dict[self.description_to_string(description_next)]=self.description['p_flattire']
            description_next['flattire']=0
            prob_dict[self.description_to_string(description_next)]=1.0 - self.description['p_flattire']

        return prob_dict

    def reset(self):
        '''domain specific config'''
        self.accept_gate=0.01
        '''domain specific'''
        self.description = {}
        self.description['at_len'] = 17
        self.description['at'] = float(np.random.choice(range(self.description['at_len']), p=[1.0/self.description['at_len']]*self.description['at_len']))
        # self.description['at'] = 2
        self.description['road'] = []
        self.description['road'] += [[0, 12]]
        self.description['road'] += [[0, 16]]
        self.description['road'] += [[1, 2]]
        self.description['road'] += [[1, 3]]
        self.description['road'] += [[3, 4]]
        self.description['road'] += [[3, 13]]
        self.description['road'] += [[3, 14]]
        self.description['road'] += [[5, 8]]
        self.description['road'] += [[5, 10]]
        self.description['road'] += [[5, 16]]
        self.description['road'] += [[6, 14]]
        self.description['road'] += [[7, 9]]
        self.description['road'] += [[7, 13]]
        self.description['road'] += [[8, 9]]
        self.description['road'] += [[9, 12]]
        self.description['road'] += [[9, 16]]
        self.description['road'] += [[10, 12]]
        self.description['road'] += [[10, 13]]
        self.description['road'] += [[11, 16]]
        self.description['road'] += [[12, 16]]
        self.description['road'] += [[13, 15]]
        self.description['road'] += [[14, 16]]
        self.description['spare_in'] = []
        self.description['spare_in'] += [4]
        self.description['spare_in'] += [5]
        self.description['spare_in'] += [7]
        self.description['spare_in'] += [8]
        self.description['spare_in'] += [10]
        self.description['spare_in'] += [12]
        self.description['spare_in'] += [16]
        self.description['p_flattire'] = 3.0/5.0
        # self.description['flattire'] = 0
        self.description['flattire'] = np.random.choice([0, 1], p=[0.5, 0.5])

    def update_domain(self, action):
        '''domain specific'''
        self.description['at'] = action
        if self.description['flattire'] == 0:
            self.description['flattire'] = np.random.choice([0, 1], p=[(1.0-self.description['p_flattire']), self.description['p_flattire']])
        else:
            self.description['flattire'] = 1

    def update(self):
        '''domain specific'''
        action = 10
        self.update_domain(action)

class Climber(Tireworld):

    def __init__(self, **args):
        super(Climber, self).__init__(**args)

    def build_domain_list(self):
        '''domain specific'''
        self.descriptions_list = []
        for on_roof_temp in [0, 1]:
            for alive_temp in [0, 1]:
                for ladder_on_ground_temp in [0, 1]:
                    self.description['on_roof'], self.description['alive'], self.description['ladder_on_ground'] = on_roof_temp, alive_temp, ladder_on_ground_temp
                    self.descriptions_list += [copy.deepcopy(self.description)]

    def description_to_state(self, description):
        '''description to state'''
        '''domain specific'''
        state = np.zeros((3), dtype=np.float)
        state[0]=description['on_roof']
        state[1]=description['alive']
        state[2]=description['ladder_on_ground']
        return state

    def get_state_size(self):
        return 3

    def get_transition_probs(self, description, is_tabular=False):
        '''string: prob'''
        '''domain specific'''

        prob_dict = {}
        self.set_domain(description=description)
        self.update()
        description_next=self.get_description()
        if (description['on_roof']==1) and (description['alive']==1):
            description_next['alive']=0
            prob_dict[self.description_to_string(description_next)]=0.4
            description_next['alive']=1
            prob_dict[self.description_to_string(description_next)]=0.6
        else:
            prob_dict[self.description_to_string(description_next)]=1.0

        return prob_dict

    def reset(self):
        '''domain specific config'''
        self.accept_gate=0.01
        '''domain specific'''
        self.description = {}
        self.description['on_roof'] = float(np.random.choice([1, 0], p=[0.5]*2))
        self.description['alive'] = float(np.random.choice([1, 0], p=[0.5]*2))
        self.description['ladder_on_ground'] = float(np.random.choice([1, 0], p=[0.5]*2))

    def update_domain(self, action):
        '''domain specific'''
        if action == 'climb-without-ladder':
            if (self.description['on_roof']==1) and (self.description['alive']==1):
                self.description['on_roof']=0
                self.description['alive']=np.random.choice([0, 1], p=[0.4, 0.6])

    def update(self):
        '''domain specific'''
        action = 'climb-without-ladder'
        self.update_domain(action)

class Walk1D(Tireworld):
        
    def __init__(self, **args):
        super(Walk1D, self).__init__(**args)

    def config(self, length, prob_left, mode, fix_state=False):
        self.accept_gate = 0.1
        self.mode = mode
        self.n = length
        self.prob_dis = [prob_left, (1-prob_left)]
        self.visualizer = visualizer.Visualizer(BLOCK_SIZE, 1, self.n,
                                                {0: visualizer.WHITE,
                                                 1: visualizer.BLUE})

    def reset(self):
        '''domain specific'''
        self.description = {}
        self.description['at'] = np.random.randint(0, self.n)

    def build_domain_list(self):
        '''domain specific'''
        self.descriptions_list = []
        for at_temp in range(self.n):
            self.description['at'] = at_temp
            self.descriptions_list += [copy.deepcopy(self.description)]

    def description_to_state(self, description):
        '''description to state'''
        '''domain specific'''
        onehot = [0] * self.n
        onehot[description['at']] = 1
        if self.mode == IMAGE:
            image = self.visualizer.make_screen([onehot])
            image = image[:,:,1:2]
            image = image / 255.0
            image = 1.0 - image
            return image
        else:
            return np.array(onehot)
        return state

    def get_state_size(self):
        return self.n

    def get_transition_probs(self, description, is_tabular=False):
        '''string: prob'''
        '''domain specific'''

        prob_dict = {}

        self.set_domain(description=description)
        action = 0
        self.update_domain(action)
        description_next=self.get_description()
        try:
            prob_dict[self.description_to_string(description_next)]+=self.prob_dis[0]
        except Exception as e:
            prob_dict[self.description_to_string(description_next)]=self.prob_dis[0]

        self.set_domain(description=description)
        action = 1
        self.update_domain(action)
        description_next=self.get_description()
        try:
            prob_dict[self.description_to_string(description_next)]+=self.prob_dis[1]
        except Exception as e:
            prob_dict[self.description_to_string(description_next)]=self.prob_dis[1]

        return prob_dict

    def update_domain(self, action):
        '''domain specific'''
        if action == 0:
            self.description['at'] -= 1
        elif action == 1:
            self.description['at'] += 1
        self.description['at'] = np.clip(self.description['at'], 0, self.n-1)

    def update(self):
        '''domain specific'''
        action = np.random.choice([0,1], p=self.prob_dis)
        self.update_domain(action)

class Walk2D(object):

    def __init__(self, width, height, prob_dirs, obstacle_pos_list, mode, should_wrap, fix_state=False, random_background=False):
        self.UP, self.DOWN, self.LEFT, self.RIGHT = 0, 1, 2, 3
        self.action_dic = [self.UP, self.DOWN, self.LEFT, self.RIGHT]
        assert sum(prob_dirs) == 1
        self.h = height
        self.w = width
        self.prob_dirs = prob_dirs
        self.action_delta_mapping = {
            self.UP: (0, -1),
            self.DOWN: (0, 1),
            self.LEFT: (-1, 0),
            self.RIGHT: (1, 0)
        }
        self.obstacle_pos_list = obstacle_pos_list
        self.non_obstacle_squares = [(x, y) for x in range(self.w) for y in range(self.h)
                                     if (x, y) not in self.obstacle_pos_list]
        self.should_wrap = should_wrap
        self.mode = mode
        self.x_pos, self.y_pos = choice(self.non_obstacle_squares)
        self.visualizer = visualizer.Visualizer(BLOCK_SIZE, height, width,
                                                {0: visualizer.WHITE,
                                                 1: visualizer.BLUE,
                                                 2: visualizer.BLACK})
        self.cleaner_function = clean_entry_012_vec
        self.fix_state = fix_state
        self.fix_state_to = (self.w/2, self.h/2)
        self.random_background = random_background

        self.reset_background()
        self.build_background_feature_mask()

    def reset_background(self):
        self.background_array = np.random.randint(
            2, 
            size=(self.h, self.w),
            dtype=np.uint8,
        )
        if not self.random_background:
            self.background_array = self.background_array*0.0
    
    def build_background_feature_mask(self):
        self.background_feature_mask = (1.0-self.visualizer.make_screen(self.background_array)[:,:,1:2]/255.0)
        for y in range(np.shape(self.background_feature_mask)[0]):
            self.background_feature_mask[y,:,:] = y%2

        self.background_feature_block = np.copy(self.background_feature_mask[0:BLOCK_SIZE,0:BLOCK_SIZE,:])
        for y in range(np.shape(self.background_feature_block)[0]):
            self.background_feature_block[y,:,:] = y%2
        self.background_feature_block = self.background_feature_block * FEATURE_DISCOUNT

        self.background_unfeature_block = np.copy(self.background_feature_block)
        self.background_unfeature_block = self.background_unfeature_block*0.0

        self.agent_block = np.copy(self.background_unfeature_block)
        self.agent_block = 1.0 - self.agent_block

    def set_fix_state(self,fix_state):
        self.fix_state = fix_state

    def get_state_size(self):
        return self.h * self.w

    def get_state_list(self):

        if self.fix_state:
            return [self.get_state(self.fix_state_to)]

        else:
            return [self.get_state((x, y)) for (x, y) in self.non_obstacle_squares]

    def state_to_description(self, state, include_background=False):

        if self.mode==SCALAR:

            agent_count = 0
            for x in range(self.w):
                for y in range(self.h):
                    if np.abs(float(x)/self.w-state[0])<(1.0/self.w*self.accept_gate) and np.abs(float(y)/self.h-state[1])<(1.0/self.h*self.accept_gate):
                        pos = (x,y)
                        agent_count += 1

            if agent_count==1:
                return pos

            else:
                return 'bad state'

        elif self.mode==VECTOR:
            raise Exception('error')

        elif self.mode==IMAGE:

            '''detect agent opsition from image'''
            agent_count = 0
            for x in range(self.w):
                for y in range(self.h):
                    block = state[y*BLOCK_SIZE:(y+1)*BLOCK_SIZE,x*BLOCK_SIZE:(x+1)*BLOCK_SIZE,:]
                    close_to_agent = np.mean(np.abs(block-self.agent_block))
                    if close_to_agent <= self.accept_gate:
                        '''if agent is here'''
                        pos = (x,y)
                        agent_count += 1
                        self.background_array[y,x] = 255
                    else:
                        '''if agent is not here'''
                        if self.random_background:
                            close_to_feature_background = np.mean(np.abs(block-self.background_feature_block))
                            close_to_unfeature_background = np.mean(np.abs(block-self.background_unfeature_block))
                            if include_background:
                                '''if start state, set the self.background_array'''        
                                if close_to_feature_background <= self.accept_gate:
                                    self.background_array[y,x] = 1
                                elif close_to_unfeature_background <= self.accept_gate:
                                    self.background_array[y,x] = 0
                                else:
                                    return 'bad state'
                            else:
                                '''see if generate background right'''
                                if self.background_array[y,x]==1:
                                    if not (close_to_feature_background <= self.accept_gate):
                                        return 'bad state'
                                elif self.background_array[y,x]==0:
                                    if not (close_to_unfeature_background <= self.accept_gate):
                                        return 'bad state'
                                elif self.background_array[y,x]==255:
                                    pass
                                else:
                                    print(self.background_array[y,x])
                                    raise Exception('s')


            if agent_count==1:
                return pos

            else:
                return 'bad state'

        else:
            raise Exception('Not a valid mode')

    def state_to_string(self, state):
        return str((state/FEATURE_DISCOUNT).astype(int)[:,:,0])

    def get_transition_probs(self, state=None, description=None, is_tabular=False):

        prob_dict = {}

        for action_i in range(len(self.action_dic)):

            if is_tabular:
                key = self.state_to_string(self.get_state(self.update_state(description, self.action_dic[action_i])))
            else:
                key = str(self.update_state(description, self.action_dic[action_i]))

            if prob_dict.has_key(key):
                prob_dict[key] += self.prob_dirs[action_i]
            else:
                prob_dict[key] = self.prob_dirs[action_i]

        return prob_dict

    def reset(self):
        if not self.fix_state:
            self.x_pos, self.y_pos = choice(self.non_obstacle_squares)

        else:
            self.x_pos, self.y_pos = self.fix_state_to

        self.reset_background()

    def set_domain(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        assert (x_pos, y_pos) not in self.obstacle_pos_list

    def get_screen(self,x):
        return (1.0-self.visualizer.make_screen(x)[:,:,1:2]/255.0)

    def get_state(self, state=None):
        if state is None:
            state = self.x_pos, self.y_pos
        x_pos, y_pos = state
        array = np.zeros((self.h, self.w), dtype=np.uint8)
        array[y_pos, x_pos] = 1
        for obs_x, obs_y in self.obstacle_pos_list:
            array[obs_y, obs_x] = 2

        if self.mode == SCALAR:
            return np.array([float(x_pos)/float(self.w),float(y_pos)/float(self.h)])

        elif self.mode == VECTOR:
            return np.reshape(array, [-1])

        elif self.mode == IMAGE:
            if self.obstacle_pos_list==[]:
                image_agent = self.get_screen(array)
                if self.random_background:
                    image_background = self.get_screen(self.background_array)
                    image_background = image_background*self.background_feature_mask*FEATURE_DISCOUNT
                    image_background_no_agent = image_background*(1.0-image_agent)
                    image = image_agent + image_background_no_agent
                else:
                    image = image_agent
            else:
                if self.random_background:
                    raise Exception('s')
                image = self.visualizer.make_screen(array)
                image = image / 255.0
                image = 1.0 - image
                image_obst = image[:,:,0:1]
                image_agent = image[:,:,1:2] - image_obst
                image = image_agent + image_obst * 0.5
            return image
        
        else:
            print(sss)

    def update_state(self, x, y, action):
        (delta_x, delta_y) = self.action_delta_mapping[action]
        if self.should_wrap:
            new_x_pos = (x+delta_x) % self.w
            new_y_pos = (y+delta_y) % self.h
        else:
            new_x_pos = np.clip(x+delta_x, 0, self.w-1)
            new_y_pos = np.clip(y+delta_y, 0, self.h-1)
        if (new_x_pos, new_y_pos) not in self.obstacle_pos_list:
            return (new_x_pos, new_y_pos)
        else:
            return (x, y)

    def update(self):
        action = np.random.choice([self.UP, self.DOWN, self.LEFT, self.RIGHT], p=self.prob_dirs)
        self.x_pos, self.y_pos = self.update_state(self.x_pos, self.y_pos, action)
        return self.get_state((self.x_pos, self.y_pos))

def clean_entry_01(entry):
    if np.abs(entry - 0) <= self.accept_gate:
        return 0
    elif np.abs(entry - 1) <= self.accept_gate:
        return 1
    else:
        return -1

def clean_entry_012(entry):
    if np.abs(entry - 0) <= self.accept_gate:
        return 0
    elif np.abs(entry - 1) <= self.accept_gate:
        return 1
    elif np.abs(entry - 2) <= self.accept_gate:
        return 2
    else:
        return -1

clean_entry_01_vec = np.vectorize(clean_entry_01, [np.int32])
clean_entry_012_vec = np.vectorize(clean_entry_012, [np.int32])

def determine_transition(domain, sample):
    cleaned_sample = domain.cleaner_function(sample)
    if np.min(cleaned_sample) == -1:
        return 'bad state'
    else:
        return cleaned_sample

def l1_distance(dist1, dist2):
    l1 = 0.0
    combined_keyset = set(dist1.keys()).union(set(dist2.keys()))
    for key in combined_keyset:
        l1 += np.abs(dist1.get(key, 0) - dist2.get(key, 0))
    return l1

def evaluate_domain(domain, s1_state, s2_samples, is_tabular=False):

    description = domain.state_to_description(
        s1_state,
        include_background = True,
    )
    # print(description)
    # print(s)

    true_distribution = domain.get_transition_probs(
        description=description,
        is_tabular=is_tabular,
    )
    # print(true_distribution)
    # print(s)
    bad_count = 0
    good_count = 0
    sample_distribution = {}

    if is_tabular:

        for s2_sample in s2_samples.next_dic.keys():
            good_count += s2_samples.next_dic[s2_sample]
            try:
                sample_distribution[s2_sample] = sample_distribution[str(s2_sample_pos)] + s2_samples.next_dic[s2_sample]
            except Exception as e:
                sample_distribution[s2_sample] = s2_samples.next_dic[s2_sample]

    else:
        for b in range(np.shape(s2_samples)[0]):
            # print(np.shape(s2_samples[b]))
            s2_sample_pos = domain.description_to_string(domain.state_to_description(s2_samples[b]))
            # print(s2_sample_pos)
            # print(s)
            if s2_sample_pos=='bad state':
                bad_count += 1
            else:
                good_count += 1
                try:
                    sample_distribution[s2_sample_pos] = sample_distribution[s2_sample_pos] + 1.0
                except Exception as e:
                    sample_distribution[s2_sample_pos] = 1

    if good_count>0.0:

        for key in sample_distribution.keys():
            sample_distribution[key] = sample_distribution[key] / float(good_count)
        print('----------------------------------------------')
        print('Start: '+str(description))
        print('True: '+str(true_distribution))
        print('Sample: '+str(sample_distribution))
        L1 = l1_distance(true_distribution, sample_distribution)
        AC = good_count / float(good_count + bad_count)
        return L1, AC
    else:

        return 2.0, 0.0

            


