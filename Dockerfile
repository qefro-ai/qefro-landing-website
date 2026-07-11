FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html features.html how-it-works.html use-cases.html security.html pricing.html faq.html benchmark.html contact.html 404.html what-is-qefro.html qefro-pricing.html /usr/share/nginx/html/
COPY robots.txt sitemap.xml llms.txt /usr/share/nginx/html/
COPY assets /usr/share/nginx/html/assets

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
