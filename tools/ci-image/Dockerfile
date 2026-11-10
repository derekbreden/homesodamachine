# This image supplies the native build, browser rendering and manual Blender workflows.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl gnupg git tar zstd unzip xz-utils sudo \
      build-essential \
      imagemagick librsvg2-bin \
      libglu1-mesa libgl1 libegl1 libxi6 libxxf86vm1 libxfixes3 libxrender1 \
      libxkbcommon0 libsm6 libice6 libx11-6 \
    && rm -rf /var/lib/apt/lists/*

ARG BLENDER_VERSION=5.1.2
RUN curl -fsSL "https://download.blender.org/release/Blender${BLENDER_VERSION%.*}/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
      | tar -xJ -C /opt \
    && mv "/opt/blender-${BLENDER_VERSION}-linux-x64" /opt/blender \
    && ln -s /opt/blender/blender /usr/local/bin/blender

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
      libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 libatspi2.0-0t64 libcairo2 \
      libcups2t64 libdbus-1-3 libdrm2 libgbm1 libglib2.0-0t64 libnspr4 libnss3 \
      libpango-1.0-0 libpangocairo-1.0-0 libx11-6 libxcb1 libxcomposite1 libxdamage1 \
      libxext6 libxfixes3 libxrandr2 libxss1 libxtst6 \
      fonts-liberation fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/homebrew/bin /usr/local/bin

ENV PUPPETEER_CACHE_DIR=/opt/hsm/puppeteer
COPY tools/render/package.json tools/render/package-lock.json /opt/hsm/render/
RUN cd /opt/hsm/render && npm ci --no-audit --no-fund

COPY web/package.json web/package-lock.json /opt/hsm/web/
RUN cd /opt/hsm/web && npm ci --omit=dev --no-audit --no-fund

ARG RUST_VERSION=1.99.1
RUN curl -fsSL "https://static.rust-lang.org/dist/rust-${RUST_VERSION}-x86_64-unknown-linux-gnu.tar.xz" \
      | tar -xJ -C /tmp \
    && "/tmp/rust-${RUST_VERSION}-x86_64-unknown-linux-gnu/install.sh" --prefix=/usr/local \
      --components=rustc,cargo,rust-std-x86_64-unknown-linux-gnu \
    && rm -rf "/tmp/rust-${RUST_VERSION}-x86_64-unknown-linux-gnu"

RUN apt-get update && apt-get install -y --no-install-recommends mesa-vulkan-drivers libvulkan1 fonts-dejavu-core poppler-utils \
    && rm -rf /var/lib/apt/lists/*

ENV HSM_RENDER_MODULES=/opt/hsm/render/node_modules \
    HSM_WEB_MODULES=/opt/hsm/web/node_modules

RUN set -eu; \
    blender --version; \
    convert -version; \
    rsvg-convert --version; \
    node --version; \
    gh --version; \
    cargo --version; \
    rustc --version

ARG HSM_REQ_SHA=unknown
ENV HSM_REQ_SHA=${HSM_REQ_SHA}
