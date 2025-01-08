FROM nginx:1.27

RUN rm /etc/nginx/conf.d/default.conf
COPY custom_404.html /usr/share/nginx/html/custom_404.html
COPY ./default.conf /etc/nginx/conf.d/default.conf