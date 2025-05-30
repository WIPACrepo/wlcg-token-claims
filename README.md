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


### Code Structure

Tests are in tests/
Code is in src/wlcg_token_claims/

* config.py - configuration variables from the environment
* server.py - main server code
* group_validation.py - validating scopes against a POSIX filesystem
