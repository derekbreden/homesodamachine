# THE ENVIRONMENT A RUNNER CANNOT BE ASKED TO ASSEMBLE, assembled once.
#
# Six things broke the first six CI runs and every one of them was state one laptop had and
# no clean machine does — the CadQuery pin, the renderer lockfile, the sandbox mount pairs,
# the reference solids, puppeteer's Chromium, express. This image is where the ones that are
# INSTALLS rather than fetches now live: they are paid at image-build time, keyed on the
# files that name them, and a derive run pulls the answer instead of computing it.
#
# IT IS ALSO THE ONLY WAY THE FULL GRAPH BUILDS AT ALL. `//:appliance-model` shells out to
# blender for the line-art SVGs and `freestyle-sieve` shells out to rsvg-convert; a stock
# `ubuntu-latest` has neither, so those targets fail on a runner however long you give them.
# The image is a correctness fix that happens to also be a speed fix.
#
# manylinux_2_31 IS THE FLOOR THE WHEELS SET. `cadquery-ocp 7.8.1.1.post1` publishes cp313
# for macosx arm64, macosx x86_64, manylinux_2_31_x86_64 and win_amd64 — no linux aarch64 —
# so this image is x86_64 and its base needs glibc >= 2.31. Noble is 2.39.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# NOTHING HERE IS THE BUILD'S CHOICE — it is what the build already reaches for by name.
# `_blender_render.py` resolves `blender` off PATH, `sieve.py` and `appliance_quickstart.py`
# call `rsvg-convert`, and `actions/cache` needs tar and zstd to unpack into a container.
# python3.13 is not in noble, so deadsnakes carries it; the venv's own pin does the rest.
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl gnupg git tar zstd unzip xz-utils sudo \
      build-essential \
      software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
      python3.13 python3.13-venv python3.13-dev \
      librsvg2-bin \
      libglu1-mesa libgl1 libegl1 libxi6 libxxf86vm1 libxfixes3 libxrender1 \
      libxkbcommon0 libsm6 libice6 libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# BLENDER IS A PIN, NOT A PACKAGE, for the same reason `cadquery-ocp` is. noble ships 4.0.2,
# and `_blender_scene.py` enables the Freestyle SVG exporter through the extension namespace
# 4.2 introduced — on 4.0.2 that is `ModuleNotFoundError: No module named 'bl_ext.blender_org'`
# and a line-art target that cannot run whatever else is on the disk. The version here is the
# one the Mac that draws these cuts them with, because a different Blender is different pixels
# in files this repo commits.
ARG BLENDER_VERSION=5.1.2
RUN curl -fsSL "https://download.blender.org/release/Blender${BLENDER_VERSION%.*}/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
      | tar -xJ -C /opt \
    && mv "/opt/blender-${BLENDER_VERSION}-linux-x64" /opt/blender \
    && ln -s /opt/blender/blender /usr/local/bin/blender

# NODE 22, WHICH IS WHAT THE LOCKFILES ACTUALLY ASK FOR. `tools/render/package.json` says
# `>=20`, but its own lock pins puppeteer, puppeteer-core and @puppeteer/browsers at
# `>=22.12.0`, and `web/package.json` is `>=22` outright — so 20 installs with EBADENGINE
# across both trees. The Mac that cuts these runs 22.16.0.
#
# AND THE VERSION HERE IS THE ONE THE BUILD ACTUALLY USES, which was not true before. Every
# genrule's PATH is `.bazelrc`'s `--action_env`, so a bazel action reaches /usr/bin/node and
# never the one `actions/setup-node` puts in the tool cache — the hosted runner's own node 22
# is what every CI build has run on, whatever the workflow asked for.
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# THE PUPPETEER LIBS ARE A LIST NOBODY CAN DERIVE, so let puppeteer name them. Its own
# `--no-install-recommends` set is what a headless Chromium links against; the deck drives a
# real Chrome and dies on a missing one of these with an error that names none of them.
RUN apt-get update && apt-get install -y --no-install-recommends \
      libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 libatspi2.0-0t64 libcairo2 \
      libcups2t64 libdbus-1-3 libdrm2 libgbm1 libglib2.0-0t64 libnspr4 libnss3 \
      libpango-1.0-0 libpangocairo-1.0-0 libx11-6 libxcb1 libxcomposite1 libxdamage1 \
      libxext6 libxfixes3 libxrandr2 libxss1 libxtst6 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# `.bazelrc` NAMES TWO MOUNT PAIRS AND BAZEL REFUSES ONE WHOSE SOURCE IS ABSENT. The tools
# those paths exist for resolve from /usr/bin here, which the same `--action_env=PATH`
# already carries; the directories only have to exist.
RUN mkdir -p /opt/homebrew/bin /usr/local/bin

# Bazel at the tree's own pin, downloaded now rather than on the first build.
COPY .bazelversion /tmp/.bazelversion
RUN curl -fsSL -o /usr/local/bin/bazel \
      https://github.com/bazelbuild/bazelisk/releases/download/v1.25.0/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel \
    && cd /tmp && USE_BAZEL_VERSION="$(cat /tmp/.bazelversion)" bazel version

# THE 840 MB. Built at /opt/hsm so it survives `actions/checkout` writing the workspace, and
# symlinked into `tools/cad-venv` by the job — a venv follows a symlink to itself fine, and
# `.gitignore` already holds that path out of the tree, so the link dirties nothing.
COPY tools/cad-requirements.txt /tmp/cad-requirements.txt
RUN python3.13 -m venv /opt/hsm/cad-venv \
    && /opt/hsm/cad-venv/bin/pip install --quiet --upgrade pip \
    && /opt/hsm/cad-venv/bin/pip install --quiet -r /tmp/cad-requirements.txt \
    && /opt/hsm/cad-venv/bin/python -c "import cadquery, OCP; print('cadquery', cadquery.__version__)"

# The renderers, and the Chromium they download on install. `PUPPETEER_CACHE_DIR` is set for
# every later shell so the browser the job launches is the one baked here.
ENV PUPPETEER_CACHE_DIR=/opt/hsm/puppeteer
COPY tools/render/package.json tools/render/package-lock.json /opt/hsm/render/
RUN cd /opt/hsm/render && npm ci --no-audit --no-fund

# `//:render-scenes` BOOTS `web/server.js` TO DRAW AGAINST, and that imports express.
# `--omit=dev` is what render.yaml installs for the deploy and it is enough for the same
# reason: nothing in the scene render reaches a dev dependency.
COPY web/package.json web/package-lock.json /opt/hsm/web/
RUN cd /opt/hsm/web && npm ci --omit=dev --no-audit --no-fund

# What the job needs to know to wire the three baked trees into a fresh checkout.
ENV HSM_CAD_VENV=/opt/hsm/cad-venv \
    HSM_RENDER_MODULES=/opt/hsm/render/node_modules \
    HSM_WEB_MODULES=/opt/hsm/web/node_modules

RUN blender --version | head -1 && rsvg-convert --version && node --version \
    && /opt/hsm/cad-venv/bin/python --version

# THE DIGEST OF THE FILES THIS IMAGE WAS MADE OF, carried in the image. `derive` recomputes
# it from its own checkout and compares — an image lagging the tree that pulled it is a run
# whose environment is not the one the tree names, and it says so rather than guessing.
ARG HSM_REQ_SHA=unknown
ENV HSM_REQ_SHA=${HSM_REQ_SHA}
