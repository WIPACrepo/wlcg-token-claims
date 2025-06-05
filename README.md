# wlcg-token-claims
Service application to fill out WLCG storage token claims for IceCube storage

## Running Locally

Set up a virtualenv, load it, and run the server:

```
./setupenv.sh
. env/bin/activate
mkdir datadir
export BASE_PATH=$PWD/datadir
export AUTH_SECRET=secret
export PORT=8888
python -m wlcg_token_claims
```

Now send requests to localhost:8888, with the auth secret in
the http Authorization header, like:

```
curl -XPOST -H 'Authorization: bearer secret' -d '{"username": "foo", "scopes": "storage.modify:/foo"}' http://localhost:8888/auth
```

## Running in Production

There is a Docker container built on every release that contains the server.

Run it like:

```
docker run --name token-claims -p 8888:8888 -e PORT=8888 \
    -v $PWD/datadir:/datadir -e BASE_PATH=/datadir \
    -e AUTH_SECRET=secret \
    ghcr.io/wipacrepo/wlcg-token-claims:latest
```

Or run with Kubernetes or other tools.


## Using LDAP

If local accounts or PAM isn't enough, you can connect directly to LDAP
for user and group translation (username -> uid,gids).

These environment variables are available:

```
export USE_LDAP=true
export LDAP_URL=ldaps://foo.bar
export LDAP_USER_BASE='ou=People,dc=icecube,dc=wisc,dc=edu'
export LDAP_GROUP_BASE='ou=Group,dc=icecube,dc=wisc,dc=edu'
```

### Code Structure

Tests are in tests/
Code is in src/wlcg_token_claims/

* config.py - configuration variables from the environment
* server.py - main server code
* group_validation.py - validating scopes against a POSIX filesystem
