---
language:
- en
tags:
- synthetic
pretty_name: SmolTalk
size_categories:
- 1M<n<10M
configs:
- config_name: all
  data_files:
  - split: train
    path: data/all/train-*
  - split: test
    path: data/all/test-*
- config_name: smol-magpie-ultra
  data_files:
  - split: train
    path: data/smol-magpie-ultra/train-*
  - split: test
    path: data/smol-magpie-ultra/test-*
- config_name: smol-constraints
  data_files:
  - split: train
    path: data/smol-constraints/train-*
  - split: test
    path: data/smol-constraints/test-*
- config_name: smol-rewrite
  data_files:
  - split: train
    path: data/smol-rewrite/train-*
  - split: test
    path: data/smol-rewrite/test-*
- config_name: smol-summarize
  data_files:
  - split: train
    path: data/smol-summarize/train-*
  - split: test
    path: data/smol-summarize/test-*
- config_name: apigen-80k
  data_files:
  - split: train
    path: data/apigen-80k/train-*
  - split: test
    path: data/apigen-80k/test-*
- config_name: everyday-conversations
  data_files:
  - split: train
    path: data/everyday-conversations/train-*
  - split: test
    path: data/everyday-conversations/test-*
- config_name: explore-instruct-rewriting
  data_files:
  - split: train
    path: data/explore-instruct-rewriting/train-*
  - split: test
    path: data/explore-instruct-rewriting/test-*
- config_name: longalign
  data_files:
  - split: train
    path: data/longalign/train-*
  - split: test
    path: data/longalign/test-*
- config_name: metamathqa-50k
  data_files:
  - split: train
    path: data/metamathqa-50k/train-*
  - split: test
    path: data/metamathqa-50k/test-*
- config_name: numina-cot-100k
  data_files:
  - split: train
    path: data/numina-cot-100k/train-*
  - split: test
    path: data/numina-cot-100k/test-*
- config_name: openhermes-100k
  data_files:
  - split: train
    path: data/openhermes-100k/train-*
  - split: test
    path: data/openhermes-100k/test-*
- config_name: self-oss-instruct
  data_files:
  - split: train
    path: data/self-oss-instruct/train-*
  - split: test
    path: data/self-oss-instruct/test-*
- config_name: systemchats-30k
  data_files:
  - split: train
    path: data/systemchats-30k/train-*
  - split: test
    path: data/systemchats-30k/test-*
---

# SmolTalk

![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/PlVz8O5yJ1FGGlJeLP4n-.png)

## Dataset description
This is a synthetic dataset designed for supervised finetuning (SFT) of LLMs. It was used to build [SmolLM2-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct) family of models and contains 1M samples. More details in our paper https://arxiv.org/abs/2502.02737

During the development of SmolLM2, we observed that models finetuned on public SFT datasets underperformed compared to other models with proprietary instruction datasets. To address this gap, we created new synthetic datasets that improve instruction following while covering diverse tasks including text editing, rewriting, summarization, and reasoning. 
Through a series of data ablations at 1.7B scale, we enhanced our SFT mix by incorporating public datasets to strengthen specific capabilities such as mathematics, coding, system prompt following and long-context understanding.

All the new datasets were generated with [distilabel](https://github.com/argilla-io/distilabel) and you can find the generation code here https://github.com/huggingface/smollm/tree/main/text/data/smoltalk.

You can load a dataset using
```python
from datasets import load_dataset

ds = load_dataset("HuggingFaceTB/smoltalk", "all", split="train")
# to load the train split of a specific subset such as smol-magpie-ultra, you can do
ds = load_dataset("HuggingFaceTB/smoltalk", "smol-magpie-ultra", split="train")
```

## Dataset composition
The mix consists of:

**New datasets**
- *Smol-Magpie-Ultra*: the core component of our mix, consisting of 400K samples generated using the Magpie pipeline with /Llama-3.1-405B-Instruct. We also heavily curate and filter this dataset compared to the original Magpie-Pro pipeline. SmolLM models trained on this dataset alone outperform those trained on popular public datasets like OpenHermes and Magpie Pro across key benchmarks including IFEval and MT-Bench.
- Smol-contraints: a 36K-sample dataset that trains models to follow specific constraints, such as generating responses with a fixed number of sentences or words, or incorporating specified words in the output. The dataset has been decontaminated against IFEval to prevent overlap.
- Smol-rewrite: an 50k-sample collection focused on text rewriting tasks, such as adjusting tone to be more friendly or professional. Note that Smol-Magpie-Ultra also includes some rewriting, editing, and summarization examples.
- Smol-summarize: an 100k-sample dataset specialized in email and news summarization.

**Existing public datasets**
To enhance capabilities in mathematics, coding, system prompts, and long-context understanding, we fine-tuned SmolLM2-1.7B on various public SFT datasets and included subsets of the best performing ones using tuned ratios. These include:

- OpenHermes2.5: we added 100k samples from [OpenHermes2.5](https://huggingface.co/datasets/teknium/OpenHermes-2.5), since we found that it helps preserve and boost benchmarks such as MMLU and WinoGrande, and BBH.
- MetaMathQA: we add this [dataset](https://huggingface.co/datasets/meta-math/MetaMathQA?) to improve the model on mathematics and reasoning, we include 50k random samples.
- NuminaMath-CoT: we find that this [dataset](https://huggingface.co/datasets/AI-MO/NuminaMath-CoT) helps on mathematics, especially hard problems found in benchmarks such as MATH.
- Self-Oss-Starcoder2-Instruct: we use this [dataset](https://huggingface.co/datasets/bigcode/self-oss-instruct-sc2-exec-filter-50k) to improve coding capabilities.
- SystemChats2.0: to make the model support a variety of system prompt formats we add 30k samples from the [SystemChat-2.0](https://huggingface.co/datasets/cognitivecomputations/SystemChat-2.0) dataset. Note that Smol-rewrite and and Smol-summarize datasets also include system prompts.
- LongAlign: we find that finetuning the model on only short samples makes it loose long context abilities beyond 2048 tokens, so we add english samples (with less than 16k tokens) from the [LongAlign-10k](https://huggingface.co/datasets/THUDM/LongAlign-10k) dataset and train with a 8192 sequence.
- Everyday-conversations: this [dataset](https://huggingface.co/datasets/HuggingFaceTB/everyday-conversations-llama3.1-2k) includes multi-turn everyday conversations such as greeting and was used in SmolLM v1 post-training.
- APIGen-Function-Calling: we use 80k samples from [apigen-function-calling](https://huggingface.co/datasets/argilla/apigen-function-calling) which is a mix of [Synth-APIGen-v0.1](https://huggingface.co/datasets/argilla/Synth-APIGen-v0.1) and [xlam-function-calling-60k](https://huggingface.co/datasets/Salesforce/xlam-function-calling-60k) datasets.
- Explore-Instruct-Rewriting: 30k samples from this rewriting [dataset](https://huggingface.co/datasets/Wanfq/Explore_Instruct_Rewriting_32k).


You can find the code for generating the new datasets with [distilabel](https://github.com/argilla-io/distilabel) here: https://github.com/huggingface/smollm. The ablation details will be included in an upcoming blog post. 

## License

All the new datasets (Smol-Magpie-Ultra, Smol-contraints, Smol-rewrite, Smol-summarize) are licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). For the existing public datasets, please refer to the original dataset for the license [Dataset composition](#dataset-composition)

## Evaluation

We compare SmolTalk to the recent [Orca AgentInstruct 1M](https://huggingface.co/datasets/microsoft/orca-agentinstruct-1M-v1) dataset by finetuning SmolLM2 on both datasets using the same training setup (we train for 2 epochs, using a learning rate of 3e-04, a sequence length of 8192 and a global batch size of 16).

![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/W7TOuHqb5rILneQ-QkIDU.png)

We also observe significant improvements at 7B scale when fine-tuning [Mistral-7B](https://huggingface.co/mistralai/Mistral-7B-v0.3) on SmolTalk, notably on IFEval, BBH, GS8Mk and MATH.

![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/M5EzF6PFZij7hLI8fTxEV.png)

## Smol-SmolTalk
For SmolLM2-135M-Instruct and SmolLM2-360M-Instruct, we use a subset of the dataset that is more suitable for these smaller models. For instance, we only include samples from Smol-Magpie-Ultra with more concise conversations and exclude advanced math datasets. You can find the dataset here: https://huggingface.co/datasets/HuggingFaceTB/smol-smoltalk

The training code is available here https://github.com/huggingface/alignment-handbook/tree/main/recipes/smollm2

## Citation
```bash
@misc{allal2025smollm2smolgoesbig,
      title={SmolLM2: When Smol Goes Big -- Data-Centric Training of a Small Language Model}, 
      author={Loubna Ben Allal and Anton Lozhkov and Elie Bakouch and Gabriel Martín Blázquez and Guilherme Penedo and Lewis Tunstall and Andrés Marafioti and Hynek Kydlíček and Agustín Piqueres Lajarín and Vaibhav Srivastav and Joshua Lochner and Caleb Fahlgren and Xuan-Son Nguyen and Clémentine Fourrier and Ben Burtenshaw and Hugo Larcher and Haojun Zhao and Cyril Zakka and Mathieu Morlon and Colin Raffel and Leandro von Werra and Thomas Wolf},
      year={2025},
      eprint={2502.02737},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2502.02737}, 
}
```