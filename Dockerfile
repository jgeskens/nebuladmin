FROM python:3.8-alpine

RUN apk add --no-cache gettext bash

# logging to the console breaks without this
ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1

RUN mkdir -p /app

WORKDIR /app

ADD requirements.txt /app/requirements.txt
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN apk add --no-cache --virtual .build-deps build-base linux-headers libffi-dev && \
    apk add --no-cache git postgresql-dev jpeg-dev zlib-dev freetype-dev && \
    pip install -r requirements.txt && \
    apk del git postgresql-dev jpeg-dev zlib-dev freetype-dev && \
    apk del .build-deps

RUN apk add --no-cache jpeg zlib freetype postgresql libffi wget

#RUN mkdir -p /usr/local/bin && \
#    cd /usr/local/bin && \
#    wget https://github.com/slackhq/nebula/releases/download/v1.0.0/nebula-linux-amd64.tar.gz && \
#    tar -zxf nebula-linux-amd64.tar.gz && \
#    rm nebula-linux-amd64.tar.gz && \
#    cd -

#RUN mkdir -p /chroot && \
#    cd /tmp && \
#    wget http://www.archlinux.org/packages/core/x86_64/glibc/download/ -O glibc.pkg.tar.xz && \
#    wget http://www.archlinux.org/packages/community/x86_64/busybox/download/ -O busybox.pkg.tar.xz && \
#    mkdir -p /chroot/usr/bin/ /chroot/dev /chroot/proc /chroot/root /chroot/etc /chroot/bin && \
#    tar xfJ glibc.pkg.tar.xz -C /chroot && \
#    tar xfJ busybox.pkg.tar.xz -C /chroot && \
#    cp /etc/resolv.conf /chroot/etc/ && \
#    cp /usr/local/bin/nebula* /chroot/usr/bin && \
#    ln -s /usr/bin/busybox /chroot/bin/sh && \
#    ln -s /usr/bin/busybox /chroot/bin/ln

RUN apk add --no-cache git make musl-dev go

# Configure Go
ENV GOROOT /usr/lib/go
ENV GOPATH /go
ENV PATH /go/bin:$PATH

RUN mkdir -p ${GOPATH}/src ${GOPATH}/bin

# Install Nebula
RUN cd /tmp && \
    wget https://github.com/slackhq/nebula/archive/v1.0.0.tar.gz && \
    tar -zxf v1.0.0.tar.gz && \
    cd nebula-1.0.0 && \
    make bin-linux && \
    make install

COPY . /app

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD python manage.py runserver 0.0.0.0:8000
