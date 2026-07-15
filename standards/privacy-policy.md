# Privacy policy

Real projects are private by default and live only below ignored `workspaces/` in directories ending
with `_private`. Git ignore rules are backed by an index-aware validator because force-add can bypass
ignore rules. Tracked examples require approved `public_synthetic` or `public_sanitized`
classification. Credentials, private keys, real customer documents, and unsanitized data are
prohibited. If private data is staged or committed, stop distribution, remove it from the index and
history as appropriate, rotate exposed credentials, notify repository security contacts privately,
and document the incident without reproducing the data.
