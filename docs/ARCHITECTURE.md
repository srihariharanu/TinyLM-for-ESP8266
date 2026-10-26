# Architecture

Target: ESP8266EX, 4 MB flash, 160 MHz. Experimental.

```text
TRAINING COMPUTER
public parquet + focused examples -> preparation -> PyTorch training
 -> checkpoint -> int8 export -> weights.h + verification arrays
web/index.html -> deterministic gzip -> web_ui.h
Arduino compiler -> combined firmware -> USB flash at 0x0

OFFLINE DEVICE
phone -> ESP hotspot -> DNS / HTTP -> local display-name session
 -> message API -> attention encoder -> GRU character loop -> reply polling
 -> phone renders the result
```

Normalized input words map to learned embeddings, attention pools a vector,
and the decoder state is initialized. Input word order is discarded. The GRU
produces characters greedily until end token or 160-character limit. Flash-resident
int8 rows use integer dot products, float32 scales and biases. Recurrent
activations use int16 in dot products. Unknown words share a token.

No retrieval, answer table, cloud service or earlier-message context is used.
Incremental generation and yield calls keep network requests responsive. Four
sessions expire after 30 minutes; only one generation job runs at once. The UI
polls job state and uses DOM text operations for displayed messages.

UI and weights are compiled into flash. No remote fonts/scripts, CDN, filesystem
upload or internet is needed in use. Wi-Fi, web/DNS servers and vendor runtime
are third-party components under their own terms.

Project maintainer and original-work rights holder: **Sri Hariharan U**.
Rights contact: **srihariharanu@gmail.com**.
