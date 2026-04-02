## Energy Efficient Programming AI
This tool has been developed to help solve coding problems in a more sustainable way, without sacrificing performance. A user is tempted to use the largest model available to solve the problem at hand, but is this necessary? The larger the model, generally the more energy is used for generating the answer to the prompt. By using a larger model to decompose the problem, feeding the small tasks to smaller LLMs and then combining the answer, this tool generates the answer in a more energy efficient way. This tool makes use of two basic models, which will be installed in the installation script. Users will be able to specify which models they want to use with this tool.

## Prerequisites

Before you are able to use the tool, be sure to have the following prerequisites installed:

- python3
- EnergiBridge
- Linux

## Installation

Clone the git repository and run the installation script:

```console
git clone https://github.com/Fedor-Baryshnikov/SustSE-P2.git
bash ./setup/setup.sh -install
```

To add your own models, add them to the ./setup/models.txt file and run:

```console
bash ./setup/setup.sh -add
```

## Running the script

The script can be run with the basic models that have been installed during installation:

```console
bash ./efficientLLM
```

Alternatively, you can specify the models you want to use. Make sure you add them to setup/models.txt first and run the following:

```console
bash ./efficientLLM -l <my-large-model> -s <my-small-model>
```

## Example usage

```console
bash ./efficientLLM -l gemma3:12b -s gemma3:4b
```
