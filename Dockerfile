# This line specifies the base image for the Docker container. 
# It uses a pre-built image from GitHub Container Registry that includes Python 3.12 on an Alpine Linux base, 
# optimized for running applications with the 'uv' package manager (https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile).
FROM ghcr.io/astral-sh/uv:python3.12-alpine


# Install the project into `/app`
# This sets the working directory inside the container to `/app`. 
# Any subsequent commands will be executed in this directory, making it the context for file operations.
WORKDIR /app

# Enable bytecode compilation
# This environment variable enables bytecode compilation for Python files. 
# Setting it to `1` means that Python will compile `.py` files to `.pyc` files, which can improve startup time.
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
# This environment variable configures the linking mode for the 'uv' package manager. 
# Setting it to `copy` ensures that files are copied from the cache instead of being linked, 
# which is useful when using mounted volumes to avoid issues with file permissions or changes.
ENV UV_LINK_MODE=copy

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Install the project's dependencies using the lockfile and settings
# This RUN command uses Docker's BuildKit features to create a layer that installs project dependencies.
# It mounts a cache directory for 'uv' to speed up future builds, and binds the `uv.lock` and `pyproject.toml` files from the host.
# The `uv sync` command synchronizes dependencies based on the lock file without installing the project or development dependencies.
RUN --mount=type=cache,target=/root/.cache/uv,Z \
    --mount=type=bind,source=uv.lock,target=uv.lock,Z \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml,Z \
    uv sync --frozen --no-install-project --no-dev

# This command copies all files from the current directory on the host into the `/app` directory in the container. 
# This includes the application code and any other necessary files.
# Add the project files. 
ADD . /app
# Install the package in editable mode using pip. 
# The `-e` flag allows changes made to the source code to be reflected immediately without needing to reinstall.
# It also uses a cache for 'uv' to optimize the installation process.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -e .

# Reset the entrypoint, don't invoke `uv`
# This line resets the entrypoint of the container to an empty array. 
# This means that the container will not invoke any default command when it starts, allowing the CMD to define the behavior.
ENTRYPOINT []

# Set environment variable 'KEGG_MAP_WIZARD_DATA' within the container. 
# This variable can be accessed by the application running inside the container, providing a configurable path.
ENV KEGG_MAP_WIZARD_DATA=/KEGG_MAP_WIZARD_DATA

# This specifies the default command to run when the container starts. 
# It runs the Python interpreter with the specified script `main.py` located in the `keggmapwizard` directory.
CMD [ "python", "./keggmapwizard/main.py"]