FROM nginx:1.19
ADD . /web/nginx

RUN printf "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ buster main contrib non-free\ndeb http://mirrors.tuna.tsinghua.edu.cn/debian/ buster-updates main contrib non-free\ndeb http://mirrors.tuna.tsinghua.edu.cn/debian/ buster-backports main contrib non-free\ndeb http://mirrors.tuna.tsinghua.edu.cn/debian-security buster/updates main contrib non-free\n" > /etc/apt/sources.list
RUN apt-get update \
    && apt-get install -y python3-certbot-nginx vim \
    && ln -svf /web/nginx/nginx.conf /etc/nginx/nginx.conf # certbot detection

WORKDIR /web
CMD nginx -c /web/nginx/nginx.conf
