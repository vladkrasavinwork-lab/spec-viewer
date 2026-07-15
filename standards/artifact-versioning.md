# Artifact versioning

Runs are immutable directories named by UTC timestamp and skill type. Every run records schema,
skill, and methodology versions; input hashes; status; project ID; and generation time. A completed
run is never overwritten. `project.yaml` uses relative current-run and current-artifact pointers and
may point only to validated completed runs. Breaking artifact changes require a schema-version bump.
