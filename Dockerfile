FROM python:3.13-alpine3.22 AS build-stage

# install dependencies to run pyinstaller
RUN apk add --no-cache \
    bash \
    build-base \
    && rm -rf /var/cache/apk/*

# Install astral uv
RUN pip install --no-cache-dir --upgrade uv pip

WORKDIR /app

# Copy the application code
# Install dependencies
COPY ./pyproject.toml ./uv.lock ./README.md ./
COPY ./src ./src
COPY ./dl_easylist.sh ./dl_ranklists.sh ./
RUN uv sync --no-cache-dir

# Build the application binary with pyinstaller
COPY ./build_bin.sh ./
RUN ["chmod", "+x", "./build_bin.sh"]
RUN ./build_bin.sh


FROM python:3.13-alpine3.22

ARG TARGETARCH

# Install necessary packages
RUN apk add --no-cache \
    bash \
    curl \
    git \
    gnupg \
    lsb-release \
    ca-certificates \
    jq \
    git \
    && rm -rf /var/cache/apk/*

# Entrypoint
#COPY docker/entrypoint.sh /entrypoint
#RUN ["chmod", "+x", "/entrypoint"]
#ENTRYPOINT ["/entrypoint"]

# Create a non-root user
RUN addgroup -S app &&  \
    adduser -S app -G app

RUN mkdir -p /app && \
    chown -R app:app /app && \
    chown app:app /usr/local/bin/*

# Set the working directory
WORKDIR /app
# Copy the virtual environment and binary from the build stage
COPY --from=build-stage /app/dist/bin /usr/local/bin

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["webcheckcli", "--help"]
USER app
