FROM ubuntu:eoan

RUN apt-get update -y \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
          software-properties-common \
          apt-transport-https \
          gpg-agent \
          wget \
          unzip \
  # Install wine
  && dpkg --add-architecture i386 \
  && wget -O- -nv https://dl.winehq.org/wine-builds/winehq.key | apt-key add - \
  && apt-add-repository "deb https://dl.winehq.org/wine-builds/ubuntu/ eoan main" \
  && apt-get update -y \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --install-recommends winehq-stable \
  # Cleanup package installs
  && apt-get remove -y software-properties-common apt-transport-https gpg-agent \
  && apt-get clean -y \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/*

# Install mono (for running .net code outside of Windows)
RUN mkdir -p /usr/share/wine/mono
RUN wget -nv https://dl.winehq.org/wine/wine-mono/4.9.4/wine-mono-4.9.4.msi -O /usr/share/wine/mono/wine-mono-4.9.4.msi

# Initialize wine
ENV WINEPREFIX /.wine
RUN wine wineboot --init

# Unpack CMS code
RUN wget -nc https://github.com/InstituteforDiseaseModeling/IDM-CMS/releases/download/v0.9/compartments.zip && \
    unzip compartments.zip

ENTRYPOINT ["wine", "compartments.exe"]
