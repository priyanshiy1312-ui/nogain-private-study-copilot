# UNVERIFIED sandbox image: OpenShell may require its own base image (see openshell-community repo).
# If `openshell sandbox create --from ./sandbox` rejects this, check `openshell sandbox create --help`.
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/* && (id sandbox >/dev/null 2>&1 || useradd -m sandbox)
COPY seed /sandbox/NoGain
COPY sandbox_demo.py /opt/nogain/sandbox_demo.py
ENV NOGAIN_HOME=/sandbox/NoGain
