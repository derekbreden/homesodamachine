# Shared CAD, image and browser environment for repository tools.
#
# The image carries the pinned CAD toolchain, renderer dependencies, Chromium, scene-server
# runtime and sandbox tools. Blender supports the manual kitchen illustrations and studio film.
#
# manylinux_2_31 IS THE FLOOR THE WHEELS SET. `cadquery-ocp 7.8.1.1.post1` publishes cp313
# for macosx arm64, macosx x86_64, manylinux_2_31_x86_64 and win_amd64 — no linux aarch64 —
# so this image is x86_64 and its base needs glibc >= 2.31. Noble is 2.39.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Image tools and shared libraries for the browser, Blender and runner archive handling.
# python3.13 is not in noble, so deadsnakes carries it; the venv's own pin does the rest.
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl gnupg git tar zstd unzip xz-utils sudo \
      build-essential \
      software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
      python3.13 python3.13-venv python3.13-dev \
      imagemagick librsvg2-bin \
      libglu1-mesa libgl1 libegl1 libxi6 libxxf86vm1 libxfixes3 libxrender1 \
      libxkbcommon0 libsm6 libice6 libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# The manual kitchen illustrations and studio film use this pinned Blender runtime.
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

# `gh`, BECAUSE `pack.py` UPLOADS WITH IT. `upload()` shells out to `gh release view` and
# `gh release upload`, and a hosted runner has the CLI preinstalled while a container has
# whatever it was given. Same family as blender and rsvg-convert: a tool the build reaches
# for by name, present on one machine by accident of its image.
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# A SANE SANS AND MONO, FOR WHATEVER RENDERS TEXT WITHOUT CARRYING ITS OWN FACE. The card deck
# no longer needs this: `cards/style.css` vendors IBM Plex under `cards/fonts/` and declares it
# with `@font-face`, so the deck resolves nothing from the system and lays out identically on
# any machine — which is the right shape, and the same argument as the OCC and Blender pins.
# What is left here is the fallback the scene renders and anything else HTML get, and the two
# packages are metric matches rather than lookalikes: Liberation Sans for Arial and so for
# Helvetica, DejaVu Sans Mono for Menlo — both derive from Bitstream Vera Sans Mono, where
# Liberation Mono is Courier New's match and a different width entirely.
#
# THE PUPPETEER LIBS ARE A LIST NOBODY CAN DERIVE, so let puppeteer name them. Its own
# `--no-install-recommends` set is what a headless Chromium links against; the deck drives a
# real Chrome and dies on a missing one of these with an error that names none of them.
RUN apt-get update && apt-get install -y --no-install-recommends \
      libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 libatspi2.0-0t64 libcairo2 \
      libcups2t64 libdbus-1-3 libdrm2 libgbm1 libglib2.0-0t64 libnspr4 libnss3 \
      libpango-1.0-0 libpangocairo-1.0-0 libx11-6 libxcb1 libxcomposite1 libxdamage1 \
      libxext6 libxfixes3 libxrandr2 libxss1 libxtst6 \
      fonts-liberation fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# `.bazelrc` NAMES TWO MOUNT PAIRS AND BAZEL REFUSES ONE WHOSE SOURCE IS ABSENT. The tools
# those paths exist for resolve from /usr/bin here, which the same `--action_env=PATH`
# already carries; the directories only have to exist.
RUN mkdir -p /opt/homebrew/bin /usr/local/bin

# Bazel at the tree's own pin, downloaded now rather than on the first build.
# `BAZELISK_HOME` IS NAMED BECAUSE THE TWO HOMES DIFFER. bazelisk caches the real bazel under
# $HOME, which is /root while this image is built and /github/home when Actions runs it — so a
# prefetch into the default location is one the job never finds, and every run re-downloaded
# and re-extracted a 9.2.0 release before it could start. Fixed path, baked and then filled.
ENV BAZELISK_HOME=/opt/hsm/bazelisk
COPY .bazelversion /tmp/.bazelversion
RUN curl -fsSL -o /usr/local/bin/bazel \
      https://github.com/bazelbuild/bazelisk/releases/download/v1.25.0/bazelisk-linux-amd64 \
    && chmod +x /usr/local/bin/bazel \
    && cd /tmp && USE_BAZEL_VERSION="$(cat /tmp/.bazelversion)" bazel version \
    && test -d "$BAZELISK_HOME"

# THE 840 MB. Built at /opt/hsm so it survives `actions/checkout` writing the workspace, and
# symlinked into `tools/cad-venv` by the job — a venv follows a symlink to itself fine, and
# `.gitignore` already holds that path out of the tree, so the link dirties nothing.
COPY tools/cad-requirements.txt /tmp/cad-requirements.txt
COPY tools/cad-venv-site /opt/hsm/cad-venv-site/
RUN python3.13 -m venv /opt/hsm/cad-venv \
    && /opt/hsm/cad-venv/bin/pip install --quiet --upgrade pip \
    && /opt/hsm/cad-venv/bin/pip install --quiet -r /tmp/cad-requirements.txt \
    && /opt/hsm/cad-venv/bin/python /opt/hsm/cad-venv-site/install.py \
    && /opt/hsm/cad-venv/bin/python /opt/hsm/cad-venv-site/install.py --check \
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

# RUST AND CMAKE, FOR THE PARTS THE KERNEL CUTS. `_rust_part.py` builds a part's program with the
# `cargo` it finds on the action's PATH, and the kernel's booleans are Manifold, which
# `manifold-csg-sys` clones and builds with CMake the first time. The toolchain is the standalone
# release, at the version the Mac that cuts these runs, installed under /usr/local so `cargo` and
# `rustc` are on `.bazelrc`'s PATH with no rustup home for an action to be told about.
ARG RUST_VERSION=1.99.1
RUN apt-get update && apt-get install -y --no-install-recommends cmake \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL "https://static.rust-lang.org/dist/rust-${RUST_VERSION}-x86_64-unknown-linux-gnu.tar.xz" \
      | tar -xJ -C /tmp \
    && "/tmp/rust-${RUST_VERSION}-x86_64-unknown-linux-gnu/install.sh" --prefix=/usr/local \
      --components=rustc,cargo,rust-std-x86_64-unknown-linux-gnu \
    && rm -rf "/tmp/rust-${RUST_VERSION}-x86_64-unknown-linux-gnu"

# VULKAN WITH NO GPU, FOR THE PICTURES `hsm-render` DRAWS. The renderer is wgpu, which draws
# through Vulkan on Linux, and a hosted runner has no GPU to answer it. Mesa's lavapipe is a
# Vulkan device on the CPU: `mesa-vulkan-drivers` carries it and `libvulkan1` is the loader that
# finds it. `fonts-dejavu-core` is the face a look's annotations are set in off a Mac. A picture
# is the same bytes on every runner this image runs on, whatever its CPU or thread count; a
# rebuild of this layer can bring a newer Mesa, which can move them. Its own layer, after the
# 840 MB, so a change here rebuilds nothing above it.
RUN apt-get update && apt-get install -y --no-install-recommends mesa-vulkan-drivers libvulkan1 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# What the job needs to know to wire the three baked trees into a fresh checkout.
ENV HSM_CAD_VENV=/opt/hsm/cad-venv \
    HSM_RENDER_MODULES=/opt/hsm/render/node_modules \
    HSM_WEB_MODULES=/opt/hsm/web/node_modules

# Report the installed tools, preserving each command's exit status.
RUN set -eu; \
    blender --version; \
    convert -version; \
    rsvg-convert --version; \
    node --version; \
    gh --version; \
    cargo --version; \
    rustc --version; \
    cmake --version; \
    /opt/hsm/cad-venv/bin/python --version

# THE DIGEST OF THE FILES THIS IMAGE WAS MADE OF, carried in the image. `derive` recomputes
# it from its own checkout and compares — an image lagging the tree that pulled it is a run
# whose environment is not the one the tree names, and it says so rather than guessing.
ARG HSM_REQ_SHA=unknown
ENV HSM_REQ_SHA=${HSM_REQ_SHA}
