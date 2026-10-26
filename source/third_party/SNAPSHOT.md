# ESP8266 runtime source/platform snapshot

Upstream: https://github.com/esp8266/Arduino/tree/3.0.2
Source: installed ESP8266 Arduino core 3.0.2 platform used for the tested build.
Included files are byte-identical to installed upstream files. Runtime library
source, headers, platform recipes, linker scripts, SDK archives and their
licenses are retained. External compiler toolchains are installed via CLI.

Excluded: local Python bytecode caches, unused upstream examples/tests/samples,
and demonstration key/certificate fixtures. They are not needed to compile or
relink this application and are not TinyLM source files. No runtime source code
was modified. Exclusions are recorded in SNAPSHOT_EXCLUSIONS.json; complete
upstream examples are available from the source URL above.

These exclusions prevent local cache paths and public example private-key
fixtures from entering the public package. Upstream copyright remains intact.
