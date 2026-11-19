# Compatibility wrapper for the renamed SUM portable runtime.

.sum_utils_wrapper_file = tryCatch(
  normalizePath(sys.frame(1)$ofile, winslash = "/", mustWork = FALSE),
  error = function(e) NA_character_
);

if (length(.sum_utils_wrapper_file) != 1 ||
    is.na(.sum_utils_wrapper_file) ||
    !nzchar(.sum_utils_wrapper_file)) {
  stop("sum_utils.R must be loaded with source() so the runtime file can be located.");
};

source(
  file.path(dirname(.sum_utils_wrapper_file), "sum_utils_runtime.R"),
  local = parent.frame()
);

rm(.sum_utils_wrapper_file);
