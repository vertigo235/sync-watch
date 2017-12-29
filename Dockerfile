FROM phusion/baseimage:0.9.22

RUN \
	apt-get update && \
	apt-get install -y \
	python \
	python-dev \	
	python-pip \
	nano \
	wget \
	curl \
	unzip \
	tzdata \
	htop 

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt
RUN cd /tmp && \
	curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip && \
	unzip rclone-current-linux-amd64.zip && \
	cd rclone-*-linux-amd64 && \
	cp rclone /usr/bin/ && \
	chown root:root /usr/bin/rclone && \
	chmod 755 /usr/bin/rclone && \
	mkdir -p /usr/local/share/man/man1 && \
	cp rclone.1 /usr/local/share/man/man1/ 

RUN mkdir -p /app/syncwatch /volume1 /volume2 /opt /config

COPY ./syncwatch /app/syncwatch
COPY ./start_syncwatch.sh /etc/my_init.d/start_syncwatch.sh

RUN chmod +x /etc/my_init.d/start_syncwatch.sh
	
RUN	apt-get clean && rm -rf \ 
			/tmp/* \
			/var/lib/apt/lists/* \
			/var/tmp/* 			

# create user 
RUN \ 
  groupmod -g 100 users && \ 
  useradd -u 1000 -U -d /config -s /bin/false rclone && \ 
  usermod -G users abc     

VOLUME ["/opt","/volume1","/volume2","/config"]
WORKDIR /app/syncwatch

ENTRYPOINT ["/sbin/my_init"]
