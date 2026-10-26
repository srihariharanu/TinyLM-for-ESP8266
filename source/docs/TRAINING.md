# Training, datasets and reproducibility

All original inputs, prepared pairs, checkpoint and quantized arrays are included.
See data/ATTRIBUTION.md, source cards and LICENSE-Apache-2.0.txt for provenance.

## Pipeline

1. `prepare_focused.py` creates focused examples and held-out prompts.
2. `train_gru.py` extracts adjacent user/assistant turns from public parquet and
   reads focused examples. It normalizes lowercase ASCII, limits length, shortens
   replies, removes duplicate pairs and excludes exact held-out prompts. It saves
   prepared-training.json and word-vocabulary.json.
3. PyTorch learns the attention encoder and character GRU, weighting the first
   12 reply characters 12x with surface-form augmentation. The reference run
   used 6,000 focused steps and selected the checkpoint by validation loss.
4. `export_gru.py` quantizes rows to int8 and creates weights.h, gru-int8.npz,
   reference replies and evaluation outputs.
5. `build_web.py` embeds the offline UI; Arduino compilation produces the image.

Run `train-and-build.ps1` on Windows after developer setup, or execute these
Python scripts in order and compile using DEVELOPMENT.md. Generated outputs are
overwritten in your checkout. Firmware can also be built without retraining.

## Reference run and limits

6,084 general pairs; 761 focused train pairs; 85 focused validation pairs.
Architecture and recorded settings: model/gru-info.json. One RTX 4050 training
run took about 74.6 seconds; this is not a performance guarantee. Seeds are set,
but dependency/hardware differences can change floating-point results and model
bytes. Retraining and recompilation are not claimed bit-for-bit reproducible.

## Data inventory and license

- train-00000-of-00001.parquet: public SmolTalk everyday-conversations subset.
- SOURCE-*.md: upstream cards and provenance.
- focused-dialogues.json: original focused example pairs.
- prepared-training.json: exact normalized paired data from the run.
- word-vocabulary.json: input token inventory.
- heldout-prompts.json / final-test-prompts.json: diagnostic inputs.

Prepared data mixes original and Apache-2.0 content. Retain Apache attribution;
do not treat the whole dataset as exclusively Apache-2.0. No private user conversations
were collected. Upstream public dataset content may itself contain names.

Final diagnostic: 9/12 topic-keyword matches on exact unseen prompts. This small,
narrow-domain diagnostic is not a general chatbot accuracy measure. Review all
model/evaluation-final.json outputs, including failures. Near paraphrases and
limited domain coverage constrain what this result establishes.

Project maintainer and original-work rights holder: **Sri Hariharan U**.
Rights contact: **srihariharanu@gmail.com**.
