    # # Dockerfile untuk Frontend Container (Final Fix)
    # FROM nginx:stable-alpine 

    # # Salin konfigurasi Nginx kustom Anda
    # # default.conf adalah lokasi umum untuk server blocks di Nginx Alpine
    # COPY nginx.conf /etc/nginx/conf.d/default.conf

    # # Setel direktori kerja ke root dokumen Nginx
    # WORKDIR /usr/share/nginx/html

    # # Salin file HTML frontend Anda ke direktori root Nginx
    # COPY index.html .

    # EXPOSE 80 

    # # Perbaiki CMD: Gunakan path lengkap ke executable Nginx
    # # Ini adalah solusi paling robust untuk 'nginx: not found'
    # CMD ["/usr/sbin/nginx", "-g", "daemon off;"]
    

    # Dockerfile Final untuk Frontend Container
FROM nginx:stable-alpine

# Hapus file konfigurasi Nginx default
RUN rm /etc/nginx/conf.d/default.conf

# Salin file konfigurasi Nginx kustom Anda
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Salin file HTML frontend Anda
COPY index.html /usr/share/nginx/html/index.html

# Pastikan semua file tersalin dengan benar
WORKDIR /usr/share/nginx/html

EXPOSE 80
CMD ["/usr/sbin/nginx", "-g", "daemon off;"]
