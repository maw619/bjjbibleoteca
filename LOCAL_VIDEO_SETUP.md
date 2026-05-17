# Use local `/mnt/BJJ_STORAGE` videos instead of S3

Your mounted disk is available at `/mnt/BJJ_STORAGE`, so the app can store video URLs like `/media/videos/bjj/Category/Section/video.mp4` instead of S3 URLs.

## 1. Make the mount readable

```bash
sudo chmod -R a+rX /mnt/BJJ_STORAGE
```

## 2. Preview what will be imported

From the repo directory:

```bash
python manage.py import_local_videos --root /mnt/BJJ_STORAGE --url-prefix /media/videos/ --dry-run
```

By default, the importer drops a leading `bjj/` folder before deciding category names, so this local file:

```text
/mnt/BJJ_STORAGE/bjj/Guard/Retention/video.mp4
```

becomes:

- Category: `Guard`
- Section: `Retention`
- Title: `video`
- URL: `/media/videos/bjj/Guard/Retention/video.mp4`

If your files do **not** have a leading `bjj/` folder, run with an empty strip prefix:

```bash
python manage.py import_local_videos --root /mnt/BJJ_STORAGE --url-prefix /media/videos/ --strip-prefix '' --dry-run
```

## 3. Populate or update the database

```bash
python manage.py import_local_videos --root /mnt/BJJ_STORAGE --url-prefix /media/videos/
```

The command creates missing categories, sections, and videos. If a matching video title already exists in the same section, it updates that row's URL from S3 to the local `/media/videos/...` URL.

## 4. Serve the files

In development, Django serves `/media/videos/` from `/mnt/BJJ_STORAGE` when `DEBUG=True`.

For nginx, add this inside your `server { ... }` block:

```nginx
location /media/videos/ {
    alias /mnt/BJJ_STORAGE/;
    types {
        video/mp4 mp4;
        video/webm webm;
        video/x-matroska mkv;
        video/quicktime mov;
    }
    add_header Accept-Ranges bytes;
}
```

Then reload nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Optional environment variables

You can change defaults without editing code:

```bash
export LOCAL_VIDEO_ROOT=/mnt/BJJ_STORAGE
export LOCAL_VIDEO_URL=/media/videos/
```
