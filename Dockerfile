FROM ubuntu:18.04

ARG DEBIAN_FRONTEND=noninteractive
ENV XDG_CONFIG_HOME="/config" XDG_DATA_HOME="/config"
ENV LANG='C.UTF-8' LANGUAGE='C.UTF-8' LC_ALL='C.UTF-8'
ENV TERM="xterm"
ENV DOCKER="YES"

COPY requirements.txt /tmp/requirements.txt

RUN \
	apt-get update \
    && apt-get upgrade -y \
	&& apt-get install -y software-properties-common \
	&& add-apt-repository -y ppa:longsleep/golang-backports \
	&& apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    apt-utils \
	apt-transport-https ca-certificates \
	python3 \
	python3-pip \
	python3-setuptools \	
	build-essential \
	libssl-dev \
	libffi-dev \
	python3-dev \	
	nano \
	wget \
	curl \
	unzip \
	tzdata \
	htop \
	git \
	golang-go \
	# install s6-overlay
    && curl -fsSL "https://github.com/just-containers/s6-overlay/releases/download/v1.22.1.0/s6-overlay-amd64.tar.gz" | tar xzf - -C / \
	&& pip3 install wheel \
	&& pip3 install -r /tmp/requirements.txt \
	&& cd /tmp/ \
	&& git clone https://github.com/rclone/rclone.git \
	&& cd rclone \
	&& git checkout fix-1205-order-by \
	&& go build \
	&& ./rclone version \
	&& cp ./rclone /usr/sbin/ \
	&& cd / \
	&& apt-get autoremove -y \
	&& apt-get clean && rm -rf \  
	/tmp/* \
	/var/lib/apt/lists/* \
	/var/tmp/* 			

RUN mkdir -p /app/syncwatch /volume1 /volume2 /opt /config

# create user 
RUN useradd -u 1000 -U -d /config -s /bin/false abc \
    && usermod -G users abc

# Copy Syncwatch to App Folder
COPY ./syncwatch /app/syncwatch

# Copy etc files
COPY root/ /

VOLUME ["/opt","/volume1","/volume2","/config"]
WORKDIR /app/syncwatch

ENTRYPOINT ["/init"]
