# Security

Hermes can execute tools and terminal commands. Keep the API on loopback and use
Tailscale Serve with access limited to intended devices. Do not enable Funnel,
public port forwarding, wildcard CORS, or disable TLS verification for this setup.

Never attach credentials, full configuration, conversations, screenshots of keys,
or private hostnames to public issues. Rotate any accidentally disclosed key.
Use the repository's private vulnerability reporting feature if enabled; otherwise
request a private contact route without publishing exploit details or secrets.

The config generator uses mode 0600 on POSIX. On Windows, file modes do not replace
NTFS ACLs: store keys in your user-private directory and inspect access permissions.
Generated files are ignored by Git, but ignore rules are not encryption.

The doctor refuses redirects and non-loopback HTTP to prevent accidentally sending
a key over plaintext or forwarding it to another origin. It prints only sanitized
status information. It is a diagnostic utility, not a security audit.
