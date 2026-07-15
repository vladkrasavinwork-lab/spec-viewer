# Private SpecViewer workspace

This directory contains private project data and must never be tracked by Git. `source/` holds
immutable originals, `normalized/` holds future canonical documents and media, `context/` holds
confirmed project context, and `artifacts/` contains immutable skill runs. Current artifacts are
referenced by relative paths in `project.yaml`. Never edit a completed run.
