# SumUtilsRuntime

Portable adaptation helpers used by SUM-exported programs and by official host-language runtimes.

The runtime is deliberately independent of `sumCore`, `sumUI`, `sumPlot`, and every other SUM package. It can therefore travel with exported code without pulling the SUM ecosystem behind it.

## Angular convention

The conversion API exposes radians, degrees, gradians, and the surveying/geodesy alias `gon`:

```text
2*pi rad = 360 deg = 400 gra = 400 gon
```

Available conversions include `deg2rad`, `rad2deg`, `gra2rad`, `rad2gra`, `gra2deg`, `deg2gra`, plus the equivalent `gon*` aliases.

`ARAD = pi/180` and `AGRAD = 180/pi` preserve the historical SUM/BASIC conversion factors. In `AGRAD`, `GRAD` means "a grados"; it does not denote the gradian unit.

## SUMBLOCK

`serializeInBlocks()` and `unserializeInBlocks()` transport native in-memory objects through copy/paste-safe numbered text blocks. The SUMBLOCK envelope is portable text, but its serialized payload remains native to the host language. Use SUMTAB for cross-language data interchange.

Standalone files are provided under `standalone/`:

```text
standalone/python/sum_utils_runtime.py
standalone/python/sum_utils.py          # compatibility wrapper
standalone/R/sum_utils_runtime.R
standalone/R/sum_utils.R               # compatibility wrapper
```

<p align=center><b>- oOo -</b></p>
