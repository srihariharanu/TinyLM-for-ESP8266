# Model card — TinyLM ESP8266 experimental

Version: 0.1.0-experimental. Creator: Sri Hariharan U.
Purpose: demonstrate fully local neural generation on constrained ESP8266 hardware
with an offline mobile UI, for research and education.

## Model and data

284,551 parameters; word-attention encoder and character GRU decoder. Lowercase
English ASCII. 1,841 word tokens, 192 hidden units, 307,440-byte weight arrays.
Public SmolTalk everyday-conversations plus original focused electronics/model
examples. Checkpoint, exported arrays and hashes are supplied. See TRAINING.md.

## Intended use and limitations

Short domain questions, education and embedded experiments. No conversational
memory, broad knowledge guarantee, hardware control, web search or online learning.
Input order is ignored; unknown words share a token. Unfamiliar prompts can yield
confident, repeated or nonsensical text. Dataset biases and synthetic phrasing
can appear. Not suitable for medical, legal, financial, safety-critical or
autonomous-control applications.

## Evidence

Final diagnostic: 9/12 keyword matches. Earlier seven-prompt hardware test: six
relevant answers, seven exact matches to host quantized inference, one irrelevant
answer. Portal checks covered a real neural reply and offline sessions. These
engineering checks do not establish general conversational quality or safety.

## Privacy and ownership

No cloud API, analytics or telemetry. Runtime sessions and job state live in RAM;
visible turns live in the browser. HTTP and public demo Wi-Fi credentials provide
limited confidentiality. Use non-sensitive inputs. Original contributions are
Apache-2.0 licensed to the extent rights are held; source data and runtime keep their
own terms. Rights contact: srihariharanu@gmail.com.
