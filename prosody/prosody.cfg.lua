admins = { }

modules_enabled = {
  "roster";
  "saslauth";
  "tls";
  "disco";
  "ping";
  "auth_anonymous";
}

authentication = "anonymous"
c2s_require_encryption = false

VirtualHost "localhost"