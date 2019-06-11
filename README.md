# Deep-RL-Sim2Real

This project uses PPO as its main RL algorithm. [ikostrikov's implementation](https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail) was used as a starting point for this repository. ikostrikov_license.txt contains the license for this implementation.

## Requirements

* Python 3
* [PyTorch](http://pytorch.org/)
* [OpenAI baselines](https://github.com/openai/baselines)

In order to install requirements, follow:

```bash
# Pytorch and other requirements
pip install -r requirements.txt

# Baselines (with some personal edits)
git clone https://github.com/harry-uglow/baselines.git
cd baselines
pip install -e .
```
