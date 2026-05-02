#' @name render_word_report
#' @title Render a Biomatix consulting report as a Word document
#' @family popgen-report-render
#'
#' @description
#' Produces `jobs/<slug>/outputs/report_final.docx` from
#' `jobs/<slug>/outputs/report_draft.md`. The output combines a
#' job-specific Biomatix cover page (titlepage + page-2 citation block)
#' with the pandoc-rendered body. Used by Step 6 of the popgen-report
#' skill.
#'
#' @param slug The job slug (the directory name under `jobs/`).
#' @param assets_dir Path to the popgen-report assets directory holding
#'   `biomatix_cover_template.docx` and `biomatix_template.docx`. Default
#'   is the conventional location relative to project root.
#'
#' @details
#' The pipeline:
#'   1. Read `jobs/<slug>/brief.yaml` for metadata (title, client,
#'      date, photo, lead author).
#'   2. Build the per-job cover by unzipping
#'      `biomatix_cover_template.docx`, substituting the five
#'      placeholders ({{TITLE}}, {{RECIPIENT}}, {{DATE}},
#'      {{PHOTO_CREDIT}}, {{CITATION}}) in word/document.xml, swapping
#'      word/media/image2.jpeg with the per-job cover photo, and
#'      re-zipping into outputs/_cover.docx.
#'   3. Run pandoc on report_draft.md with --filter pandoc-crossref
#'      and --reference-doc=biomatix_template.docx, producing
#'      outputs/_body.docx.
#'   4. Concatenate cover + body via officer::body_add_docx into
#'      outputs/report_final.docx.
#'
#' Pandoc's docx writer renders inline images at the markdown position,
#' so the report_draft.md figure-after-first-reference convention
#' (popgen-report SKILL.md Step 3.1) carries over to Word naturally.
#' Cross-references via pandoc-crossref produce "Figure 1", "Table 1"
#' style labels in the Word output.
#'
#' Requires: pandoc and pandoc-crossref on PATH; R packages yaml, zip,
#' and officer.
#'
#' @author Arthur Georges, with the popgen-report harness.
#'
#' @return Invisible character: the absolute path of the rendered docx.
#' @export
render_word_report <- function(slug,
                               assets_dir = ".claude/skills/popgen-report/assets") {

  # PRELIMINARIES -- checking ----------------
  job_dir <- file.path("jobs", slug)
  outputs_dir <- file.path(job_dir, "outputs")
  brief_path <- file.path(job_dir, "brief.yaml")
  draft_path <- file.path(outputs_dir, "report_draft.md")

  stopifnot(
    "brief.yaml not found"       = file.exists(brief_path),
    "report_draft.md not found"  = file.exists(draft_path),
    "outputs/ not found"         = dir.exists(outputs_dir)
  )

  cover_template <- file.path(assets_dir, "biomatix_cover_template.docx")
  body_reference <- file.path(assets_dir, "biomatix_template.docx")
  stopifnot(
    "cover template missing"    = file.exists(cover_template),
    "body reference-doc missing" = file.exists(body_reference)
  )

  if (nchar(Sys.which("pandoc")) == 0) {
    stop("pandoc not on PATH")
  }
  if (nchar(Sys.which("pandoc-crossref")) == 0) {
    warning("pandoc-crossref not on PATH; cross-references will not resolve")
  }

  brief <- yaml::read_yaml(brief_path)

  # DO THE JOB --------------------------------
  cover_path <- file.path(outputs_dir, "_cover.docx")
  body_path  <- file.path(outputs_dir, "_body.docx")
  final_path <- file.path(outputs_dir, "report_final.docx")

  build_cover_(cover_template, cover_path, brief)
  cat("[render_word_report] cover written:", cover_path, "\n")

  draft_for_docx <- file.path(outputs_dir, "_report_draft_for_docx.md")
  prepare_body_markdown_(draft_path, draft_for_docx, outputs_dir)

  build_body_(draft_for_docx, body_reference, body_path, outputs_dir)
  cat("[render_word_report] body written:",  body_path,  "\n")

  concat_docx_(cover_path, body_path, final_path)
  cat("[render_word_report] final written:", final_path, "\n")

  invisible(normalizePath(final_path, winslash = "/"))
}

# Internal helpers -------------------------------------------------------

build_cover_ <- function(template_path, out_path, brief) {
  tmp <- tempfile("biomatix_cover_")
  dir.create(tmp)
  on.exit(unlink(tmp, recursive = TRUE), add = TRUE)
  utils::unzip(template_path, exdir = tmp)

  doc_xml <- file.path(tmp, "word", "document.xml")
  xml <- readChar(doc_xml, file.info(doc_xml)$size, useBytes = TRUE)

  subs <- placeholder_values_(brief)
  for (token in names(subs)) {
    xml <- gsub(token, xml_escape_(subs[[token]]), xml,
                fixed = TRUE, useBytes = TRUE)
  }
  con <- file(doc_xml, open = "wb")
  writeBin(charToRaw(xml), con)
  close(con)

  # Swap image2.jpeg with the per-job cover photo (if present)
  photo_path <- brief$cover_photo$path %||% ""
  if (nzchar(photo_path) && file.exists(photo_path)) {
    media_dir <- file.path(tmp, "word", "media")
    dest <- file.path(media_dir, "image2.jpeg")
    if (file.exists(dest)) file.remove(dest)
    file.copy(photo_path, dest)
    cat("[render_word_report] cover photo swapped from:", photo_path, "\n")
  } else if (nzchar(photo_path)) {
    warning("cover_photo.path set but file not found: ", photo_path)
  }

  # Resolve out_path to an absolute path BEFORE setwd; zip into a sibling
  # of the project root, then move into place. Zipping the tmp dir into a
  # file inside that same tmp dir produces a recursive-input error.
  if (file.exists(out_path)) file.remove(out_path)
  out_abs   <- file.path(normalizePath(dirname(out_path), winslash = "/"),
                         basename(out_path))
  zip_stage <- tempfile(fileext = ".docx")
  # all.files = TRUE so dot-files like _rels/.rels (the OPC package
  # relationships file Word requires) are included.
  files <- list.files(tmp, recursive = TRUE, all.files = TRUE,
                      no.. = TRUE)
  old_wd <- setwd(tmp); on.exit(setwd(old_wd), add = TRUE)
  zip::zip(zipfile = zip_stage, files = files, compression_level = 9)
  setwd(old_wd)
  file.copy(zip_stage, out_abs, overwrite = TRUE)
  file.remove(zip_stage)
}

prepare_body_markdown_ <- function(draft_path, out_path, outputs_dir) {
  # Word's docx renderer cannot reliably display PDF-format inline images
  # (only the very latest builds do, and even then inconsistently). For
  # every `![...](xxx.pdf)` in the draft, convert xxx.pdf -> xxx.png with
  # pdftools::pdf_convert (300 dpi) and rewrite the include to point at
  # the PNG. Original .pdf figure files stay on disk for the LaTeX path
  # if anyone ever wants it back.
  if (!requireNamespace("pdftools", quietly = TRUE)) {
    stop("pdftools is required to convert PDF figures to PNG for the Word render")
  }
  txt <- readLines(draft_path, warn = FALSE, encoding = "UTF-8")
  pat <- "(!\\[[^]]*\\]\\()([^)]+\\.pdf)(\\))"
  matches <- regmatches(txt, regexec(pat, txt))
  pdf_refs <- unique(unlist(lapply(matches, function(m) if (length(m) >= 3) m[3] else NULL)))
  pdf_refs <- pdf_refs[nzchar(pdf_refs)]

  for (pdf_ref in pdf_refs) {
    pdf_local <- if (file.exists(pdf_ref)) pdf_ref else file.path(outputs_dir, basename(pdf_ref))
    if (!file.exists(pdf_local)) {
      warning("PDF figure not found, skipping: ", pdf_ref)
      next
    }
    png_local <- sub("\\.pdf$", ".png", pdf_local)
    if (!file.exists(png_local) ||
        file.info(png_local)$mtime < file.info(pdf_local)$mtime) {
      pdftools::pdf_convert(pdf_local, format = "png", dpi = 300,
                            filenames = png_local, verbose = FALSE)
      cat("[render_word_report] converted:", basename(pdf_local), "->",
          basename(png_local), "\n")
    }
  }

  # Rewrite the markdown: every .pdf figure include becomes its .png sibling.
  txt <- gsub(pat, "\\1\\2\\3", txt, perl = TRUE)  # no-op anchor for the rewrite below
  txt <- gsub("(!\\[[^]]*\\]\\()([^)]+)\\.pdf(\\))", "\\1\\2.png\\3",
              txt, perl = TRUE)
  writeLines(txt, out_path, useBytes = TRUE)
}

build_body_ <- function(draft_path, body_reference, body_path, outputs_dir) {
  args <- c(
    normalizePath(draft_path, winslash = "/"),
    "--filter", "pandoc-crossref",
    "--reference-doc", normalizePath(body_reference, winslash = "/"),
    "--from", "markdown",
    "--to",   "docx",
    "-o",     normalizePath(body_path, winslash = "/", mustWork = FALSE),
    "--resource-path", normalizePath(outputs_dir, winslash = "/")
  )
  ret <- system2("pandoc", args = args, stdout = TRUE, stderr = TRUE)
  status <- attr(ret, "status")
  if (!is.null(status) && status != 0) {
    stop("pandoc failed (exit ", status, "):\n",
         paste(ret, collapse = "\n"))
  }
}

concat_docx_ <- function(cover_path, body_path, final_path) {
  doc <- officer::read_docx(path = cover_path)
  doc <- officer::body_add_docx(doc, src = body_path)
  print(doc, target = final_path)
}

placeholder_values_ <- function(brief) {
  date_iso <- brief$deliverables[[1]]$deadline
  date_obj <- as.Date(date_iso)
  date_str <- format(date_obj, "%d-%b-%Y")
  year     <- format(date_obj, "%Y")

  client_name <- brief$client$name %||% ""
  client_addr <- brief$client$address %||% ""
  recipient   <- if (nzchar(client_addr)) {
    sprintf("Report to %s, %s.", client_name, client_addr)
  } else {
    sprintf("Report to %s.", client_name)
  }

  photographer <- brief$cover_photo$photographer %||% ""
  photo_credit <- if (nzchar(photographer)) {
    paste0("Photo: ", photographer)
  } else {
    ""
  }

  lead_author <- brief$lead_author %||% ""
  citation    <- build_citation_(lead_author, year, brief$project$title,
                                 client_name, date_str)

  list(
    "{{TITLE}}"        = brief$project$title %||% "",
    "{{RECIPIENT}}"    = recipient,
    "{{DATE}}"         = date_str,
    "{{PHOTO_CREDIT}}" = photo_credit,
    "{{CITATION}}"     = citation
  )
}

build_citation_ <- function(lead_author, year, title, client, date_str) {
  # Strip trailing punctuation from title so we don't double-up periods.
  title <- sub("[.!?\\s]+$", "", trimws(title))
  if (!nzchar(lead_author)) {
    return(sprintf("(%s). %s. Report to %s. %s.", year, title, client, date_str))
  }
  parts   <- strsplit(trimws(lead_author), "\\s+")[[1]]
  surname <- parts[length(parts)]
  given   <- parts[-length(parts)]
  inits   <- if (length(given) > 0) {
    paste0(substr(given, 1, 1), ".", collapse = " ")
  } else { "" }
  byline  <- if (nzchar(inits)) sprintf("%s, %s", surname, inits) else surname
  sprintf("%s (%s). %s. Report to %s. %s.",
          byline, year, title, client, date_str)
}

xml_escape_ <- function(s) {
  if (is.null(s)) return("")
  s <- gsub("&", "&amp;",  s, fixed = TRUE)
  s <- gsub("<", "&lt;",   s, fixed = TRUE)
  s <- gsub(">", "&gt;",   s, fixed = TRUE)
  s
}

`%||%` <- function(a, b) if (is.null(a) || (is.character(a) && !nzchar(a))) b else a
