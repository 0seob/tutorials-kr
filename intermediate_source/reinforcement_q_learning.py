# -*- coding: utf-8 -*-
"""
��ȭ �н� (DQN) Ʃ�丮��
=====================================
**Author**: `Adam Paszke <https://github.com/apaszke>`_
  **����**: `Ȳ���� <https://github.com/adonisues>`_


�� Ʃ�丮�󿡼��� `OpenAI Gym <https://gym.openai.com/>`__ ��
CartPole-v0 �½�ũ���� DQN (Deep Q Learning) ������Ʈ�� �н��ϴµ�
PyTorch�� ����ϴ� ����� �����帳�ϴ�.

**�½�ũ**

������Ʈ�� ����� ���밡 �ȹٷ� �� �ֵ��� īƮ�� �����̳� ���������� 
�����̴� �� ���� ���� �� �ϳ��� �����ؾ� �մϴ�. 
�پ��� �˰���� �ð�ȭ ����� ���� ���� ����ǥ�� 
`Gym ������Ʈ <https://gym.openai.com/envs/CartPole-v0>`__ ���� ã�� �� �ֽ��ϴ�.

.. figure:: /_static/img/cartpole.gif
   :alt: cartpole

   cartpole

������Ʈ�� ���� ȯ�� ���¸� �����ϰ� �ൿ�� �����ϸ�,
ȯ���� ���ο� ���·� *��ȯ* �ǰ� �۾��� ����� ��Ÿ���� ���� ��ȯ�˴ϴ�. 
�� �½�ũ���� �� Ÿ�ӽ��� �������� ������ +1�� �ǰ�, ���� ���밡 �ʹ� �ָ�
�������ų� īƮ�� �߽ɿ��� 2.4 ���� �̻� �־����� ȯ���� �ߴܵ˴ϴ�.
�̰��� �� ���� �ó������� �� �������� �� ���� ������ �����ϴ� ���� �ǹ��մϴ�.

īƮ�� �½�ũ�� ������Ʈ�� ���� �Է��� ȯ�� ����(��ġ, �ӵ� ��)�� ��Ÿ���� 
4���� ���� ���� �ǵ��� ����Ǿ����ϴ�. �׷��� �Ű���� �����ϰ� �� ����� ����
�½�ũ�� �ذ��� �� �ֽ��ϴ� ���� īƮ �߽��� ȭ�� ��ġ�� �Է����� ����մϴ�.
�� ������ �츮�� ����� ���� ����ǥ�� ����� ���������� ���� �� �����ϴ�. 
�츮�� �½�ũ�� �ξ� �� ��ƽ��ϴ�.
�������� ��� �������� �������ؾߵǹǷ� �̰��� �н� �ӵ��� ���߰Ե˴ϴ�.

������ ���ϸ�, ���� ��ũ�� ��ġ�� ���� ��ũ�� ��ġ ������ ���̷� ���¸� ǥ���� ���Դϴ�.
�̷����ϸ� ������Ʈ�� ������ �ӵ��� �� �̹������� ����� �� �ֽ��ϴ�.

**��Ű��**

���� �ʿ��� ��Ű���� �����ɴϴ�. ù°, ȯ���� ���� 
`gym <https://gym.openai.com/docs>`__ �� �ʿ��մϴ�.
(`pip install gym` �� ����Ͽ� ��ġ�Ͻʽÿ�).
���� PyTorch���� ������ ����մϴ�:

-  �Ű�� (``torch.nn``)
-  ����ȭ (``torch.optim``)
-  �ڵ� �̺� (``torch.autograd``)
-  �ð� �½�ũ�� ���� ��ƿ��Ƽ�� (``torchvision`` - `a separate
   package <https://github.com/pytorch/vision>`__).

"""

import gym
import math
import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple
from itertools import count
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T


env = gym.make('CartPole-v0').unwrapped

# matplotlib ����
is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display

plt.ion()

# GPU�� ����� ���
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


######################################################################
# ���� �޸�(Replay Memory)
# -------------------------------
#
# �츮�� DQN �н��� ���� ���� ���� �޸𸮸� ����� ���Դϴ�.
# ������Ʈ�� ������ ��ȯ(transition)�� �����ϰ� ���߿� �� �����͸� 
# ������ �� �ֽ��ϴ�. �������� ���ø��ϸ� ��ġ�� �����ϴ� ��ȯ����
# ����(decorrelated)�ϰ� �˴ϴ�. �̰��� DQN �н� ������ ũ�� ������Ű��
# ����Ű�� ������ ��Ÿ�����ϴ�.
#
# �̸� ���ؼ� �ΰ��� Ŭ������ �ʿ��մϴ�:
#
# -  ``Transition`` - �츮 ȯ�濡�� ���� ��ȯ�� ��Ÿ������ ���� Ʃ��.
#    �װ��� ȭ���� ������ state�� (state, action) ���� (next_state, reward) ����� �����մϴ�.
# -  ``ReplayMemory`` - �ֱ� ������ ���̸� ���� �����ϴ� ���ѵ� ũ���� ��ȯ ����.
#    ���� �н��� ���� ��ȯ�� ������ ��ġ�� �����ϱ�����
#    ``.sample ()`` �޼ҵ带 �����մϴ�.

Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))


class ReplayMemory(object):

    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *args):
        """transition ����"""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*args)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


######################################################################
# ���� ���� �����սô�. �׷��� ���� DQN�� �������� ������ ����� ���ڽ��ϴ�.
#
# DQN �˰���
# -------------
#
# �츮�� ȯ���� ���������̹Ƿ� ���⿡ ���õ� ��� �������� �ܼ�ȭ�� ����
# ������������ ����ȭ�˴ϴ�. ��ȭ �н� �ڷ��� ȯ�濡�� Ȯ������ ��ȯ�� 
# ���� ��밪(expectation)�� ������ ���Դϴ�.
#
# �츮�� ��ǥ�� ���ε� ���� ���� (discounted cumulative reward)�� 
# �ش�ȭ�Ϸ��� ��å(policy)�� �н��ϴ� ���Դϴ�.
# :math:`R_{t_0} = \sum_{t=t_0}^{\infty} \gamma^{t - t_0} r_t`, ���⼭
# :math:`R_{t_0}` �� *��ȯ(return)* �Դϴ�. ���� ���,
# :math:`\gamma`, �� :math:`0` �� :math:`1` �� ����̰� �հ谡 
# ���ŵǵ��� �����մϴ�. ������Ʈ���� ��Ȯ���� �� �̷��� ������
# ����� �̷��� �Ϳ� ���� �� �߿��ϰ� �����, �̰��� ����� �ո����Դϴ�.
#
# Q-learning�� �ֿ� ���̵��� ���� �Լ� :math:`Q^*: State \times Action \rightarrow \mathbb{R}` ��
# ������ �ִٸ� ��ȯ�� ��F�� ���� �˷��� �� �ְ�, 
# ���� �־��� ����(state)���� �ൿ(action)�� �Ѵٸ�, ������ �ִ�ȭ�ϴ� 
# ��å�� ���� ������ �� �ֽ��ϴ�:
#
# .. math:: \pi^*(s) = \arg\!\max_a \ Q^*(s, a)
#
# �׷��� ����(world)�� ���� ��� ���� ���� ���ϱ� ������, 
# :math:`Q^*` �� ������ �� �����ϴ�. �׷��� �Ű���� 
# ���� �Լ� �ٻ���(universal function approximator)�̱� ������
# �����ϰ� �����ϰ� :math:`Q^*` �� �൵�� �н��� �� �ֽ��ϴ�. 
#
# �н� ������Ʈ ��Ģ����, �Ϻ� ��å�� ���� ��� :math:`Q` �Լ��� 
# Bellman �������� �ؼ��Ѵٴ� ����� ����� ���Դϴ�:
#
# .. math:: Q^{\pi}(s, a) = r + \gamma Q^{\pi}(s', \pi(s'))
#
# ���(equality)�� �� ���� ������ ���̴� 
# �ð��� ����(temporal difference error), :math:`\delta` �Դϴ�.:
#
# .. math:: \delta = Q(s, a) - (r + \gamma \max_a Q(s', a))
#
# ������ �ּ�ȭ�ϱ� ���ؼ� `Huber
# loss <https://en.wikipedia.org/wiki/Huber_loss>`__ �� ����մϴ�.
# Huber loss �� ������ ������ ��� ���� ����( mean squared error)�� ����
# �����ϰ� ������ Ŭ ���� ��� ���� ������ �����մϴ�.
# - �̰��� :math:`Q` �� ������ �ſ� ȥ�������� �� �̻� ���� �� �����ϰ� �մϴ�.
# ���� �޸𸮿��� ���ø��� ��ȯ ��ġ :math:`B` ���� �̰��� ����մϴ�:
#
# .. math::
#
#    \mathcal{L} = \frac{1}{|B|}\sum_{(s, a, s', r) \ \in \ B} \mathcal{L}(\delta)
#
# .. math::
#
#    \text{where} \quad \mathcal{L}(\delta) = \begin{cases}
#      \frac{1}{2}{\delta^2}  & \text{for } |\delta| \le 1, \\
#      |\delta| - \frac{1}{2} & \text{otherwise.}
#    \end{cases}
#
# Q-��Ʈ��ũ
# ^^^^^^^^^^^
#
# �츮 ���� ����� ���� ��ũ�� ��ġ�� ���̸� ���ϴ� 
# CNN(convolutional neural network) �Դϴ�. �ΰ��� ��� :math:`Q(s, \mathrm{left})` ��
# :math:`Q(s, \mathrm{right})` �� �ֽ��ϴ�. (���⼭ :math:`s` �� ��Ʈ��ũ�� �Է��Դϴ�)
# ��������� ��Ʈ��ũ�� �־��� ���� �Է¿��� �� �ൿ�� *��밪* �� �����Ϸ��� �մϴ�.
#

class DQN(nn.Module):

    def __init__(self, h, w, outputs):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=5, stride=2)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=5, stride=2)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 32, kernel_size=5, stride=2)
        self.bn3 = nn.BatchNorm2d(32)

        # Linear �Է��� ���� ���ڴ� conv2d ������ ��°� �Է� �̹����� ũ�⿡
        # ���� �����Ǳ� ������ ���� ����� �ؾ��մϴ�.
        def conv2d_size_out(size, kernel_size = 5, stride = 2):
            return (size - (kernel_size - 1) - 1) // stride  + 1
        convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(w)))
        convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(h)))
        linear_input_size = convw * convh * 32
        self.head = nn.Linear(linear_input_size, outputs)

    # ����ȭ �߿� ���� �ൿ�� �����ϱ� ���ؼ� �ϳ��� ��� �Ǵ� ��ġ�� �̿��� ȣ�͵˴ϴ�.
    # ([[left0exp,right0exp]...]) �� ��ȯ�մϴ�.
    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        return self.head(x.view(x.size(0), -1))


######################################################################
# �Է� ����
# ^^^^^^^^^^^^^^^^
#
# �Ʒ� �ڵ�� ȯ�濡�� ������ �� �̹����� �����ϰ� ó���ϴ� ��ƿ��Ƽ�Դϴ�.
# �̹��� ��ȯ�� ���� ������ �� �ִ� ``torchvision`` ��Ű���� ����մϴ�. 
# ��(cell)�� �����ϸ� ������ ���� ��ġ�� ǥ�õ˴ϴ�.
#

resize = T.Compose([T.ToPILImage(),
                    T.Resize(40, interpolation=Image.CUBIC),
                    T.ToTensor()])


def get_cart_location(screen_width):
    world_width = env.x_threshold * 2
    scale = screen_width / world_width
    return int(env.state[0] * scale + screen_width / 2.0)  # MIDDLE OF CART

def get_screen():
    # gym�� ��û�� ȭ���� 400x600x3 ������, ���� 800x1200x3 ó�� ū ��찡 �ֽ��ϴ�.
    # �̰��� Torch order (CHW)�� ��ȯ�Ѵ�.
    screen = env.render(mode='rgb_array').transpose((2, 0, 1))
    # īƮ�� �Ʒ��ʿ� �����Ƿ� ȭ���� ��ܰ� �ϴ��� �����Ͻʽÿ�.
    _, screen_height, screen_width = screen.shape
    screen = screen[:, int(screen_height*0.4):int(screen_height * 0.8)]
    view_width = int(screen_width * 0.6)
    cart_location = get_cart_location(screen_width)
    if cart_location < view_width // 2:
        slice_range = slice(view_width)
    elif cart_location > (screen_width - view_width // 2):
        slice_range = slice(-view_width, None)
    else:
        slice_range = slice(cart_location - view_width // 2,
                            cart_location + view_width // 2)
    # īƮ�� �߽����� ���簢�� �̹����� �ǵ��� �����ڸ��� �����Ͻʽÿ�.
    screen = screen[:, :, slice_range]
    # float ���� ��ȯ�ϰ�,  rescale �ϰ�, torch tensor �� ��ȯ�Ͻʽÿ�.
    # (�̰��� ���縦 �ʿ������ �ʽ��ϴ�)
    screen = np.ascontiguousarray(screen, dtype=np.float32) / 255
    screen = torch.from_numpy(screen)
    # ũ�⸦ �����ϰ� ��ġ ����(BCHW)�� �߰��Ͻʽÿ�.
    return resize(screen).unsqueeze(0).to(device)


env.reset()
plt.figure()
plt.imshow(get_screen().cpu().squeeze(0).permute(1, 2, 0).numpy(),
           interpolation='none')
plt.title('Example extracted screen')
plt.show()


######################################################################
# �н�
# --------
#
# ������ �Ķ���Ϳ� ��ƿ��Ƽ
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# �� ���� �𵨰� ����ȭ�⸦ �ν��Ͻ�ȭ�ϰ� �Ϻ� ��ƿ��Ƽ�� �����մϴ�:
#
# -  ``select_action`` - Epsilon Greedy ��å�� ���� �ൿ�� �����մϴ�.
#    ������ ���ؼ�, ���� ���� ����Ͽ� �ൿ�� �����ϰ� ���δ� ���� �ϳ���
#    �����ϰ� ���ø��� ���Դϴ�. ������ �׼��� ������ Ȯ���� 
#    ``EPS_START`` ���� �����ؼ� ``EPS_END`` �� ���� ���������� ������ ���Դϴ�.
#    ``EPS_DECAY`` �� ���� �ӵ��� �����մϴ�.
# -  ``plot_durations`` - ���� 100�� ���Ǽҵ��� ���(���� �򰡿��� ��� �� ��ġ)�� ����
#    ���Ǽҵ��� ������ ��ǥ�� �׸��� ���� ����. ��ǥ�� �⺻ �Ʒ� ������ 
#    ���� �� �� �ؿ� ������, �� ���Ǽҵ帶�� ������Ʈ�˴ϴ�.
#

BATCH_SIZE = 128
GAMMA = 0.999
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 200
TARGET_UPDATE = 10

# AI gym���� ��ȯ�� ���¸� ������� ������ �ʱ�ȭ �ϵ��� ȭ���� ũ�⸦
# �����ɴϴ�. �� ������ �Ϲ������� 3x40x90 �� �������ϴ�. 
# �� ũ��� get_screen()���� ����, ��ҵ� ���� ������ ����Դϴ�. 
init_screen = get_screen()
_, _, screen_height, screen_width = init_screen.shape

# gym �ൿ �������� �ൿ�� ���ڸ� ����ϴ�.
n_actions = env.action_space.n

policy_net = DQN(screen_height, screen_width, n_actions).to(device)
target_net = DQN(screen_height, screen_width, n_actions).to(device)
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.RMSprop(policy_net.parameters())
memory = ReplayMemory(10000)


steps_done = 0


def select_action(state):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    if sample > eps_threshold:
        with torch.no_grad():
            # t.max (1)�� �� ���� ���� ū �� ���� ��ȯ�մϴ�.
            # �ִ� ����� �ι�° ���� �ִ� ����� �ּҰ��̹Ƿ�,
            # ��� ������ �� ū �ൿ�� ������ �� �ֽ��ϴ�. 
            return policy_net(state).max(1)[1].view(1, 1)
    else:
        return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long)


episode_durations = []


def plot_durations():
    plt.figure(2)
    plt.clf()
    durations_t = torch.tensor(episode_durations, dtype=torch.float)
    plt.title('Training...')
    plt.xlabel('Episode')
    plt.ylabel('Duration')
    plt.plot(durations_t.numpy())
    # 100���� ���Ǽҵ� ����� ���� �ͼ� ��ǥ �׸���
    if len(durations_t) >= 100:
        means = durations_t.unfold(0, 100, 1).mean(1).view(-1)
        means = torch.cat((torch.zeros(99), means))
        plt.plot(means.numpy())

    plt.pause(0.001)  # ��ǥ�� ������Ʈ�ǵ��� ��� ���� 
    if is_ipython:
        display.clear_output(wait=True)
        display.display(plt.gcf())


######################################################################
# �н� ����
# ^^^^^^^^^^^^^
#
# ���������� �� �н��� ���� �ڵ�.
#
# ���⼭, ����ȭ�� �� �ܰ踦 �����ϴ� ``optimize_model`` �Լ��� ã�� �� �ֽ��ϴ�.
# ���� ��ġ �ϳ��� ���ø��ϰ� ��� Tensor�� �ϳ��� �����ϰ� 
# :math:`Q(s_t, a_t)` ��  :math:`V(s_{t+1}) = \max_a Q(s_{t+1}, a)` �� ����ϰ�
# �װ͵��� �սǷ� ��Ĩ�ϴ�. �츮�� ������ ���ǿ� ������ ���� :math:`s` ��
# ������ ���¶�� :math:`V(s) = 0` �Դϴ�.
# ���� ������ �߰� ���� :math:`V(s_{t+1})` ����� ���� ��ǥ ��Ʈ��ũ�� ����մϴ�. 
# ��ǥ ��Ʈ��ũ�� ��κ��� �ð� ���� ���·� ����������, ���� ��å 
# ��Ʈ��ũ�� ����ġ�� ������Ʈ�˴ϴ�.
# �̰��� �밳 ������ ���� ���������� �ܼ�ȭ�� ���� ���Ǽҵ带 ����մϴ�.
#

def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)
    # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
    # detailed explanation). �̰��� batch-array�� Transitions�� Transition�� batch-arrays��
    # ��ȯ�մϴ�.
    batch = Transition(*zip(*transitions))

    # ������ �ƴ� ������ ����ũ�� ����ϰ� ��ġ ��Ҹ� �����մϴ�
    # (���� ���´� �ùķ��̼��� ���� �� ������ ����)
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                          batch.next_state)), device=device, dtype=torch.uint8)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                                if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    # Q(s_t, a) ��� - ���� Q(s_t)�� ����ϰ�, ���� �ൿ�� ���� �����մϴ�.
    # �̵��� policy_net�� ���� �� ��ġ ���¿� ���� ���õ� �ൿ�Դϴ�.
    state_action_values = policy_net(state_batch).gather(1, action_batch)

    # ��� ���� ���¸� ���� V(s_{t+1}) ���
    # non_final_next_states�� �ൿ�鿡 ���� ��밪�� "����" target_net�� ������� ���˴ϴ�.
    # max(1)[0]���� �ְ��� ������ �����Ͻʽÿ�.
    # �̰��� ����ũ�� ������� ���յǾ� ��� ���� ���� ���ų� ���°� ������ ��� 0�� �����ϴ�.
    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()
    # ��� Q �� ���
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    # Huber �ս� ���
    loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))

    # �� ����ȭ
    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()


######################################################################
#
# �Ʒ����� �ֿ� �н� ������ ã�� �� �ֽ��ϴ�. ó������ ȯ���� 
# �缳���ϰ� ``����`` Tensor�� �ʱ�ȭ�մϴ�. �׷� ���� �ൿ��
# ���ø��ϰ�, �װ��� �����ϰ�, ���� ȭ��� ����(�׻� 1)�� �����ϰ�,
# ���� �� �� ����ȭ�մϴ�. ���Ǽҵ尡 ������ (���� ����) 
# ������ �ٽ� �����մϴ�.
#
# �Ʒ����� `num_episodes` �� �۰� �����˴ϴ�. ��Ʈ���� �ٿ�ް�
# �ǹ��ִ� ������ ���ؼ� 300 �̻��� �� ���� ���Ǽҵ带 ������ ���ʽÿ�.  
#

num_episodes = 50
for i_episode in range(num_episodes):
    # ȯ��� ���� �ʱ�ȭ
    env.reset()
    last_screen = get_screen()
    current_screen = get_screen()
    state = current_screen - last_screen
    for t in count():
        # �ൿ ���ð� ����
        action = select_action(state)
        _, reward, done, _ = env.step(action.item())
        reward = torch.tensor([reward], device=device)

        # ���ο� ���� ����
        last_screen = current_screen
        current_screen = get_screen()
        if not done:
            next_state = current_screen - last_screen
        else:
            next_state = None

        # �޸𸮿� ���� ����
        memory.push(state, action, next_state, reward)

        # ���� ���·� �̵�
        state = next_state

        # ����ȭ �Ѵܰ� ����(��ǥ ��Ʈ��ũ����)
        optimize_model()
        if done:
            episode_durations.append(t + 1)
            plot_durations()
            break
    #��ǥ ��Ʈ��ũ ������Ʈ, ��� ����Ʈ�� ���̾ ����
    if i_episode % TARGET_UPDATE == 0:
        target_net.load_state_dict(policy_net.state_dict())

print('Complete')
env.render()
env.close()
plt.ioff()
plt.show()

######################################################################
# ������ ��ü ��� ������ �帧�� �����ִ� ���̾�׷��Դϴ�.
#
# .. figure:: /_static/img/reinforcement_learning_diagram.jpg
#
# �ൿ�� ������ �Ǵ� ��å�� ���� ���õǾ�, gym ȯ�濡�� ���� �ܰ� ������ �����ɴϴ�.
# ����� ���� �޸𸮿� �����ϰ� ��� �ݺ����� ����ȭ �ܰ踦 �����մϴ�.
# ����ȭ�� ���� �޸𸮿��� ������ ��ġ�� �����Ͽ� �� ��å�� �н��մϴ�.
# "����" target_net�� ����ȭ���� ��� Q ���� ����ϴ� ������ ���ǰ�,
# �ֽ� ���¸� �����ϱ� ���� ���� ������Ʈ�˴ϴ�.
#
