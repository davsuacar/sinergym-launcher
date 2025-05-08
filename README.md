# Sinergym Experiment Launcher

This project provides a basic setup for running experiments with Sinergym, a building energy simulation environment.

## Prerequisites

- Python 3.12 or higher
- EnergyPlus (required by Sinergym)

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd sinergym-launcher
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

To run a basic experiment:

```bash
python src/local_launcher/train_local_agent.py -conf src/local_launcher/local_launcher_config/train_agent_PPO.yml
```

The default configuration uses the `Eplus-datacenter-mixed-continuous-stochastic-v1` environment with random actions. You can modify the parameters in `run_experiment.py` to:

- Change the environment
- Adjust the number of episodes
- Modify the maximum steps per episode
- Implement your own control strategy

## Sinergym Info

For more information about available environments and their configurations, refer to the [Sinergym documentation](https://ugr-sail.github.io/sinergym/compilation/main/pages/environments.html).

## License

...