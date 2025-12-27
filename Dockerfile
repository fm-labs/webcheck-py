FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy AS build-stage

# install dependencies to run pyinstaller
RUN apt-get update && apt-get install -y \
    bash \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install astral uv
RUN pip install --no-cache-dir --upgrade uv pip

WORKDIR /app

# Copy the application code
# Install dependencies
COPY ./pyproject.toml ./uv.lock ./README.md ./
COPY ./src ./src
RUN uv sync --no-cache-dir

# Build the application binary with pyinstaller
COPY ./build_bin.sh ./
RUN ["chmod", "+x", "./build_bin.sh"]
RUN ./build_bin.sh


# UI build stage
FROM node:24 AS uibuild-stage
WORKDIR /app/
COPY ./ui ./
RUN npm -g install bun
RUN bun install --frozen-lockfile
RUN bun run build


FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

ARG TARGETARCH

# Install necessary packages
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    git \
    gnupg \
    lsb-release \
    ca-certificates \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install astral uv
#RUN pip install --no-cache-dir --upgrade uv pip

# Create a non-root user on debian-based image
RUN groupadd -r app &&  \
    useradd -r -g app app

# Set the working directory
WORKDIR /app

# copy webcheckcli binary from build-stage
COPY --from=build-stage /app/dist/bin/webcheckcli /usr/local/bin/webcheckcli
COPY --from=build-stage /app/dist/bin/webchecksrv /usr/local/bin/webchecksrv

# copy wappalyzer binary from fmlabs/wappalyzer:latest
COPY --from=fmlabs/wappalyzer:latest /app/scan /usr/local/bin/wappalyzer

# Entrypoint
COPY container/entrypoint.sh /usr/local/bin/entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint"]

# Set permissions
RUN mkdir -p /app && \
    chown -R app:app /app && \
    chown app:app /usr/local/bin/* && \
    chmod +x /usr/local/bin/webcheckcli && \
    chmod +x /usr/local/bin/webchecksrv && \
    chmod +x /usr/local/bin/wappalyzer && \
    chmod +x /usr/local/bin/entrypoint

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV WEBCHECK_DATA_DIR=/app/data
ENV WAPPALYZER_CLI_PATH=/usr/local/bin/wappalyzer

CMD ["scan", "--help"]
USER app
