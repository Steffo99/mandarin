# mandarin

A cloud music library

## `config.toml`

```toml
[auth]
authorization = "https://ryg.eu.auth0.com/authorize"
device = "https://ryg.eu.auth0.com/oauth/device/code"
token = "https://ryg.eu.auth0.com/oauth/token"
userinfo = "https://ryg.eu.auth0.com/userinfo"
openidcfg = "https://ryg.eu.auth0.com/.well-known/openid-configuration"
jwks = "https://ryg.eu.auth0.com/.well-known/jwks.json"

[database]
uri = "postgres://steffo@/mandarin_dev"

[storage]
[storage.music]
dir = "./data/music"

[apps]
[apps.files]
port = 30009

[apps.files.roles]
albumartist = "Artist"
artist = "Artist"
composer = "Composer"
performer = "Performer"
```
