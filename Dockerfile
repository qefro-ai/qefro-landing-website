FROM python:3.12-alpine AS generator
RUN apk add --no-cache librsvg
WORKDIR /site
COPY generate.py ./
COPY assets ./assets
COPY llms.txt ./
RUN python3 generate.py

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=generator /site/*.html /usr/share/nginx/html/
COPY --from=generator /site/robots.txt /site/sitemap.xml /site/llms.txt /usr/share/nginx/html/
COPY --from=generator /site/assets /usr/share/nginx/html/assets
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
