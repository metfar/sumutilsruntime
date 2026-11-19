# sum_utils.R
# Common convenience helpers for local R/SUM examples.

# Preserve R's original print() before defining the SUM-style version.
printR = base::print;
print_r = base::print;

# SUM-style print(): simple human-readable output, similar to other languages.
# Use printR()/print_r() when native R print() semantics are required.
print = function(x, ..., sep = " ", end = "\n") {
  args = list(...);

  simple = is.atomic(x) &&
           !is.object(x) &&
           all(vapply(args, function(a) {
             is.atomic(a) && !is.object(a);
           }, logical(1)));

  if (simple) {
    cat(x, ..., sep = sep);
    cat(end);

    return(invisible(x));
  };

  base::print(x, ...);
};


load_package = function(
  pkg,
  repos = "https://cloud.r-project.org"
) {
  # Already installed: just try to load it.
  if (requireNamespace(pkg, quietly = TRUE)) {
    load_error = tryCatch(
      {
        suppressPackageStartupMessages(
          library(pkg, character.only = TRUE)
        );

        NULL;
      },
      error = function(e) {
        conditionMessage(e);
      }
    );

    if (is.null(load_error)) {
      return(list(
        package = pkg,
        ok = TRUE,
        reason = NULL
      ));
    };

    return(list(
      package = pkg,
      ok = FALSE,
      reason = sprintf(
        "Package '%s' is installed but could not be loaded: %s",
        pkg,
        load_error
      )
    ));
  };

  # Check whether the package is available from the configured CRAN repo.
  available = tryCatch(
    suppressWarnings(
      available.packages(repos = repos)
    ),
    error = function(e) NULL
  );

  if (is.null(available)) {
    return(list(
      package = pkg,
      ok = FALSE,
      reason = sprintf(
        "Could not access the configured CRAN repository while looking for package '%s'.",
        pkg
      )
    ));
  };

  if (!(pkg %in% rownames(available))) {
    return(list(
      package = pkg,
      ok = FALSE,
      reason = sprintf(
        "Package '%s' is not available from the configured CRAN repository for R %s.",
        pkg,
        getRversion()
      )
    ));
  };

  # Capture installation warnings so expected dependency failures can be
  # reported cleanly by include()/load_packages().
  install_warnings = character();

  install_error = tryCatch(
    {
      withCallingHandlers(
        suppressMessages(
          install.packages(
            pkg,
            repos = repos,
            quiet = TRUE
          )
        ),
        warning = function(w) {
          install_warnings <<- c(
            install_warnings,
            conditionMessage(w)
          );

          invokeRestart("muffleWarning");
        }
      );

      NULL;
    },
    error = function(e) {
      conditionMessage(e);
    }
  );

  if (!is.null(install_error)) {
    return(list(
      package = pkg,
      ok = FALSE,
      reason = sprintf(
        "Could not install package '%s': %s",
        pkg,
        install_error
      )
    ));
  };

  # install.packages() can finish with warnings rather than an error, so verify.
  if (!requireNamespace(pkg, quietly = TRUE)) {
    reason = if (length(install_warnings) > 0) {
      paste(unique(install_warnings), collapse = "\n");
    } else {
      "The package could not be loaded after installation.";
    };

    return(list(
      package = pkg,
      ok = FALSE,
      reason = sprintf(
        "Could not install/load package '%s': %s",
        pkg,
        reason
      )
    ));
  };

  # Installation succeeded; load the package.
  load_error = tryCatch(
    {
      suppressPackageStartupMessages(
        library(pkg, character.only = TRUE)
      );

      NULL;
    },
    error = function(e) {
      conditionMessage(e);
    }
  );

  if (!is.null(load_error)) {
    return(list(
      package = pkg,
      ok = FALSE,
      reason = sprintf(
        "Package '%s' was installed but could not be loaded: %s",
        pkg,
        load_error
      )
    ));
  };

  list(
    package = pkg,
    ok = TRUE,
    reason = NULL
  );
};


load_packages = function(
  ...,
  strict = TRUE,
  repos = "https://cloud.r-project.org"
) {
  packages = c(...);

  if (length(packages) == 0) {
    return(invisible(logical()));
  };

  width = max(nchar(packages)) + 2;
  results = vector("list", length(packages));

  print("Loading dependencies:");

  for (i in seq_along(packages)) {
    result = load_package(
      packages[[i]],
      repos = repos
    );

    results[[i]] = result;

    status = if (result$ok) {
      "OK";
    } else {
      "FAILED";
    };

    print(
      sprintf(
        "  %-*s %s",
        width,
        result$package,
        status
      )
    );
  };

  failed = Filter(
    function(x) !x$ok,
    results
  );

  if (length(failed) > 0) {
    print("");

    for (result in failed) {
      print(
        sprintf(
          "Issue: %s",
          result$reason
        )
      );
    };

    if (strict) {
      quit(
        save = "no",
        status = 1,
        runLast = FALSE
      );
    };

    print("");
    print("Continuing without unavailable dependencies.");
  };

  status = vapply(
    results,
    function(x) x$ok,
    logical(1)
  );

  names(status) = packages;

  invisible(status);
};


# Division helpers
intdiv = function(a, b) {
    return(floor(a / b));
};

moddiv = function(a, b) {
    return(`%%`(a, b));
};

div = function(a, b) {
    return(list(
        result = a / b,
        quotient = intdiv(a, b),
        remainder = moddiv(a, b)
    ));
};



# Short, declarative alias for scripts.
include = load_packages;




# ---------------------------------------------------------------------------
# Angular units
# ---------------------------------------------------------------------------

PI_SUM = pi;
TAU = 2 * pi;

# Historical SUM/BASIC conversion factors: "a radianes" and "a grados".
# AGRAD means "to degrees" here; it is not the abbreviation for gradians.
ARAD = pi / 180;
AGRAD = 180 / pi;

deg2rad = function(value) {
  return(value * pi / 180);
};

rad2deg = function(value) {
  return(value * 180 / pi);
};

gra2rad = function(value) {
  return(value * pi / 200);
};

rad2gra = function(value) {
  return(value * 200 / pi);
};

gra2deg = function(value) {
  return(value * 0.9);
};

deg2gra = function(value) {
  return(value * 10 / 9);
};

# Surveying/geodesy aliases. A gon and a gradian are the same unit.
gon2rad = gra2rad;
rad2gon = rad2gra;
gon2deg = gra2deg;
deg2gon = deg2gra;

# ---------------------------------------------------------------------------
# Paths and files
# ---------------------------------------------------------------------------

.sum_utils_file = tryCatch(
  normalizePath(
    sys.frame(1)$ofile,
    winslash = "/",
    mustWork = FALSE
  ),
  error = function(e) NA_character_
);

.sum_utils_dir = if (
  length(.sum_utils_file) == 1 &&
  !is.na(.sum_utils_file) &&
  nzchar(.sum_utils_file)
) {
  dirname(.sum_utils_file);
} else {
  normalizePath(
    getwd(),
    winslash = "/",
    mustWork = FALSE
  );
};

project_dir = function() {
  return(.sum_utils_dir);
};

project_path = function(...) {
  return(
    file.path(
      project_dir(),
      ...
    )
  );
};

ensure_dir = function(path) {
  path = path.expand(path);

  if (!dir.exists(path)) {
    ok = dir.create(
      path,
      recursive = TRUE,
      showWarnings = FALSE
    );

    if (!ok && !dir.exists(path)) {
      stop(
        "Could not create directory: ",
        path
      );
    };
  };

  normalizePath(
    path,
    winslash = "/",
    mustWork = FALSE
  );
};

show_file = function(
  path,
  wait = FALSE
) {
  path = normalizePath(
    path.expand(path),
    winslash = "/",
    mustWork = TRUE
  );

  system_name = Sys.info()[["sysname"]];

  if (identical(system_name, "Linux")) {
    return(
      invisible(
        system2(
          "xdg-open",
          path,
          stdout = FALSE,
          stderr = FALSE,
          wait = wait
        )
      )
    );
  };

  if (identical(system_name, "Darwin")) {
    return(
      invisible(
        system2(
          "open",
          path,
          stdout = FALSE,
          stderr = FALSE,
          wait = wait
        )
      )
    );
  };

  if (identical(.Platform$OS.type, "windows")) {
    shell.exec(path);
    return(invisible(NULL));
  };

  stop(
    "Unsupported platform: ",
    system_name
  );
};

save_plot = function(
  figure,
  filename,
  width = 12,
  height = 7,
  dpi = 150,
  show = TRUE
) {
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    stop(
      "save_plot() requires ggplot2. ",
      "Use include(\"ggplot2\") first."
    );
  };

  output_path = normalizePath(
    path.expand(filename),
    winslash = "/",
    mustWork = FALSE
  );

  parent = dirname(output_path);

  if (!dir.exists(parent)) {
    dir.create(
      parent,
      recursive = TRUE,
      showWarnings = FALSE
    );
  };

  ggplot2::ggsave(
    filename = output_path,
    plot = figure,
    width = width,
    height = height,
    dpi = dpi
  );

  print(
    "Plot saved to:",
    output_path
  );

  if (show) {
    show_file(output_path);
  };

  return(invisible(output_path));
};



# ---------------------------------------------------------------------------
# Copy/paste serialization blocks
# ---------------------------------------------------------------------------

.SUMBLOCK_FORMAT = "SUMBLOCK/1";
.SUMBLOCK_LANGUAGE = "R";
.SUMBLOCK_ENCODING = "hex";
.SUMBLOCK_COMPRESSION = "zlib";

.sumblock_lines = function(blocks) {
  chunks = as.character(blocks$chunks);
  total = length(chunks);

  lines = c(
    sprintf("===== %s =====", blocks$format),
    sprintf("language=%s", blocks$language),
    sprintf("serialization=%s", blocks$serialization),
    sprintf("compression=%s", blocks$compression),
    sprintf("encoding=%s", blocks$encoding),
    sprintf("chunk_size=%d", blocks$chunk_size),
    sprintf("chunks=%d", total),
    sprintf("payload_bytes=%d", blocks$payload_bytes),
    sprintf("object_bytes=%d", blocks$object_bytes)
  );

  for (i in seq_along(chunks)) {
    lines = c(
      lines,
      sprintf("===== CHUNK %d/%d =====", i, total),
      chunks[[i]],
      sprintf("===== END CHUNK %d/%d =====", i, total)
    );
  };

  c(
    lines,
    sprintf("===== END %s =====", blocks$format)
  );
};

serializeInBlocks = function(
  object,
  chunk_size = 12000,
  emit = FALSE
) {
  if (!is.numeric(chunk_size) || length(chunk_size) != 1 ||
      is.na(chunk_size) || chunk_size <= 0) {
    stop("chunk_size must be greater than zero.");
  };

  chunk_size = as.integer(chunk_size);

  raw_data = serialize(
    object,
    NULL,
    version = 3
  );

  # R calls this compression type "gzip", but memCompress()/memDecompress()
  # use the zlib stream format for in-memory payloads. The envelope records the
  # actual wire representation as "zlib".
  compressed = memCompress(
    raw_data,
    type = "gzip"
  );

  encoded = paste(
    sprintf(
      "%02x",
      as.integer(compressed)
    ),
    collapse = ""
  );

  starts = seq.int(
    1L,
    nchar(encoded),
    by = chunk_size
  );

  chunks = vapply(
    starts,
    function(start) {
      substr(
        encoded,
        start,
        min(start + chunk_size - 1L, nchar(encoded))
      );
    },
    character(1)
  );

  result = list(
    format = .SUMBLOCK_FORMAT,
    language = .SUMBLOCK_LANGUAGE,
    serialization = "r-native-v3",
    compression = .SUMBLOCK_COMPRESSION,
    encoding = .SUMBLOCK_ENCODING,
    chunk_size = chunk_size,
    payload_bytes = length(compressed),
    object_bytes = length(raw_data),
    chunks = chunks
  );

  class(result) = c(
    "sumblocks",
    "list"
  );

  if (isTRUE(emit)) {
    printBlocks(result);
  };

  return(result);
};

.parse_sumblock_text = function(text_value) {
  if (length(text_value) == 0) {
    stop("No SUMBLOCK text was supplied.");
  };

  text_blob = paste(
    text_value,
    collapse = "\n"
  );

  lines = trimws(
    unlist(
      strsplit(
        text_blob,
        "\n",
        fixed = TRUE
      )
    )
  );

  lines = lines[nzchar(lines)];

  if (length(lines) == 0 ||
      !grepl("^===== SUMBLOCK/[0-9]+ =====$", lines[[1]])) {
    stop("Input does not start with a valid SUMBLOCK header.");
  };

  format = sub(
    "^===== (SUMBLOCK/[0-9]+) =====$",
    "\\1",
    lines[[1]]
  );

  metadata = list(
    format = format
  );

  chunks = list();
  declared_chunks = NULL;
  i = 2L;

  while (i <= length(lines)) {
    line = lines[[i]];

    if (identical(
      line,
      sprintf("===== END %s =====", format)
    )) {
      break;
    };

    chunk_match = regexec(
      "^===== CHUNK ([0-9]+)/([0-9]+) =====$",
      line
    );

    matched = regmatches(
      line,
      chunk_match
    )[[1]];

    if (length(matched) == 3) {
      chunk_number = as.integer(matched[[2]]);
      total = as.integer(matched[[3]]);
      declared_chunks = total;
      i = i + 1L;
      payload_lines = character();
      end_marker = sprintf(
        "===== END CHUNK %d/%d =====",
        chunk_number,
        total
      );

      while (i <= length(lines) && !identical(lines[[i]], end_marker)) {
        payload_lines = c(
          payload_lines,
          lines[[i]]
        );
        i = i + 1L;
      };

      if (i > length(lines)) {
        stop(
          sprintf(
            "Missing end marker for chunk %d.",
            chunk_number
          )
        );
      };

      key = as.character(chunk_number);

      if (!is.null(chunks[[key]])) {
        stop(
          sprintf(
            "Duplicate chunk %d.",
            chunk_number
          )
        );
      };

      chunks[[key]] = paste(
        payload_lines,
        collapse = ""
      );
    } else if (grepl("=", line, fixed = TRUE)) {
      parts = strsplit(
        line,
        "=",
        fixed = TRUE
      )[[1]];

      key = parts[[1]];
      value = paste(
        parts[-1],
        collapse = "="
      );

      metadata[[key]] = value;
    };

    i = i + 1L;
  };

  total = if (!is.null(metadata$chunks)) {
    as.integer(metadata$chunks);
  } else if (!is.null(declared_chunks)) {
    declared_chunks;
  } else {
    0L;
  };

  if (is.na(total) || total <= 0L) {
    stop("SUMBLOCK metadata does not declare a positive chunk count.");
  };

  missing = integer();
  ordered_chunks = character(total);

  for (number in seq_len(total)) {
    key = as.character(number);

    if (is.null(chunks[[key]])) {
      missing = c(
        missing,
        number
      );
    } else {
      ordered_chunks[[number]] = chunks[[key]];
    };
  };

  if (length(missing) > 0) {
    stop(
      sprintf(
        "Missing SUMBLOCK chunks: %s",
        paste(missing, collapse = ", ")
      )
    );
  };

  metadata$chunks = ordered_chunks;

  for (key in c(
    "chunk_size",
    "payload_bytes",
    "object_bytes"
  )) {
    if (!is.null(metadata[[key]])) {
      metadata[[key]] = as.integer(metadata[[key]]);
    };
  };

  return(metadata);
};

.hex_to_raw = function(encoded) {
  encoded = paste(
    encoded,
    collapse = ""
  );

  if ((nchar(encoded) %% 2L) != 0L ||
      !grepl("^[0-9a-fA-F]*$", encoded)) {
    stop("SUMBLOCK hex payload is malformed.");
  };

  if (nchar(encoded) == 0L) {
    return(raw());
  };

  starts = seq.int(
    1L,
    nchar(encoded),
    by = 2L
  );

  values = vapply(
    starts,
    function(start) {
      strtoi(
        substr(
          encoded,
          start,
          start + 1L
        ),
        base = 16L
      );
    },
    integer(1)
  );

  as.raw(values);
};

inspectBlocks = function(blocks) {
  parsed = if (is.list(blocks) && !is.character(blocks)) {
    blocks;
  } else {
    .parse_sumblock_text(blocks);
  };

  if (!identical(
    as.character(parsed$format),
    .SUMBLOCK_FORMAT
  )) {
    stop(
      "Unsupported SUMBLOCK format: ",
      parsed$format
    );
  };

  if (!identical(
    as.character(parsed$encoding),
    .SUMBLOCK_ENCODING
  )) {
    stop(
      "Unsupported encoding: ",
      parsed$encoding
    );
  };

  payload = .hex_to_raw(parsed$chunks);

  expected_payload = if (!is.null(parsed$payload_bytes)) {
    as.integer(parsed$payload_bytes);
  } else {
    length(payload);
  };

  if (length(payload) != expected_payload) {
    stop(
      sprintf(
        "Payload size mismatch: expected %d, got %d.",
        expected_payload,
        length(payload)
      )
    );
  };

  list(
    format = parsed$format,
    language = parsed$language,
    serialization = parsed$serialization,
    compression = parsed$compression,
    encoding = parsed$encoding,
    chunks = length(parsed$chunks),
    payload_bytes = length(payload),
    object_bytes = as.integer(parsed$object_bytes),
    status = "COMPLETE"
  );
};

printBlocks = function(blocks) {
  lines = .sumblock_lines(blocks);

  base::cat(
    paste(
      lines,
      collapse = "\n"
    ),
    "\n",
    sep = ""
  );

  invisible(blocks);
};

unserializeInBlocks = function(blocks) {
  parsed = if (is.list(blocks) && !is.character(blocks)) {
    blocks;
  } else {
    .parse_sumblock_text(blocks);
  };

  inspectBlocks(parsed);

  if (!identical(
    as.character(parsed$language),
    .SUMBLOCK_LANGUAGE
  )) {
    stop(
      sprintf(
        "This payload is native to %s; R was expected.",
        parsed$language
      )
    );
  };

  if (!identical(
    as.character(parsed$compression),
    .SUMBLOCK_COMPRESSION
  )) {
    stop(
      "Unsupported compression: ",
      parsed$compression
    );
  };

  compressed = .hex_to_raw(parsed$chunks);
  raw_data = memDecompress(
    compressed,
    type = "gzip"
  );

  expected_object = if (!is.null(parsed$object_bytes)) {
    as.integer(parsed$object_bytes);
  } else {
    length(raw_data);
  };

  if (length(raw_data) != expected_object) {
    stop(
      sprintf(
        "Object size mismatch: expected %d, got %d.",
        expected_object,
        length(raw_data)
      )
    );
  };

  unserialize(raw_data);
};

serialize_in_blocks = serializeInBlocks;
unserialize_in_blocks = unserializeInBlocks;
print_blocks = printBlocks;
inspect_blocks = inspectBlocks;

# ---------------------------------------------------------------------------
# Didactic console output
# ---------------------------------------------------------------------------

section = function(
  title,
  width = 72
) {
  rule = paste(
    rep("=", width),
    collapse = ""
  );

  print("");
  print(rule);
  print(title);
  print(rule);

  invisible(NULL);
};

subsection = function(
  title,
  width = 72
) {
  rule_width = min(
    width,
    max(nchar(title), 12)
  );

  rule = paste(
    rep("-", rule_width),
    collapse = ""
  );

  print("");
  print(title);
  print(rule);

  invisible(NULL);
};

show_values = function(values) {
  if (is.null(values) || length(values) == 0) {
    return(invisible(NULL));
  };

  if (is.null(names(values))) {
    stop(
      "show_values() expects a named list or named vector."
    );
  };

  labels = names(values);
  label_width = max(nchar(labels));

  for (i in seq_along(values)) {
    print(
      sprintf(
        "%-*s : %s",
        label_width,
        labels[[i]],
        as.character(values[[i]])
      )
    );
  };

  invisible(NULL);
};

format_p_value = function(p_value) {
  if (p_value < 0.0001) {
    return(
      sprintf(
        "%.6e",
        p_value
      )
    );
  };

  sprintf(
    "%.6f",
    p_value
  );
};

hypothesis_decision = function(
  p_value,
  alpha = 0.05,
  null_name = "H0"
) {
  reject = p_value <= alpha;

  show_values(
    list(
      "p-value" = format_p_value(p_value),
      "alpha" = alpha
    )
  );

  if (reject) {
    print(
      "Decision : REJECT",
      null_name
    );

    print(
      paste(
        "Reason   : p-value <= alpha, so the observed result is",
        "sufficiently incompatible with the null hypothesis."
      )
    );
  } else {
    print(
      "Decision : FAIL TO REJECT",
      null_name
    );

    print(
      paste(
        "Reason   : p-value > alpha, so the sample does not provide",
        "enough evidence to reject the null hypothesis."
      )
    );
  };

  return(invisible(reject));
};

explain = function(text) {
  print("");
  print(
    "Explanation:",
    text
  );

  invisible(NULL);
};
