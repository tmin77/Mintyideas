# mintyideas.com

Website for Minty Ideas, a marketing consultancy by Tyler Minear. Hosted on GitHub Pages.

## How it works

- All page copy, services, FAQs, and work videos live in `src/content.py`.
- On every push to `main`, GitHub Actions (`.github/workflows/deploy.yml`) runs `python3 src/build.py` and publishes `dist/site` to GitHub Pages.
- To edit: open `src/content.py` on GitHub, click the pencil icon, change text, and commit to `main`. The live site updates in a minute or two (watch the **Actions** tab).
- The contact form posts to [FormSubmit](https://formsubmit.co), which emails each message to Tyler@mintyideas.com. The very first submission triggers a one-time activation email to that inbox; click the link in it to start receiving messages.

## One-time setup

1. **Turn on Pages:** repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. **Custom domain:** in the same Pages screen, enter `mintyideas.com` and save. (The build also writes a `CNAME` file.)
3. **DNS** at your domain registrar:

   | Type  | Host / Name | Value                 |
   |-------|-------------|-----------------------|
   | A     | `@`         | `185.199.108.153`     |
   | A     | `@`         | `185.199.109.153`     |
   | A     | `@`         | `185.199.110.153`     |
   | A     | `@`         | `185.199.111.153`     |
   | AAAA  | `@`         | `2606:50c0:8000::153` |
   | AAAA  | `@`         | `2606:50c0:8001::153` |
   | AAAA  | `@`         | `2606:50c0:8002::153` |
   | AAAA  | `@`         | `2606:50c0:8003::153` |
   | CNAME | `www`       | `tmin77.github.io`    |

   Remove any other A/AAAA records for `@` (e.g. registrar "parking" records). Don't touch MX records, which keep your email working.
4. Once DNS propagates (minutes to a few hours), tick **Enforce HTTPS** in Settings → Pages.
5. Optional but recommended: verify the domain under your GitHub account **Settings → Pages → Verified domains**, which stops anyone else from claiming it.

## Preview locally (optional)

```
python3 src/build.py
cd dist/site && python3 -m http.server 8000
```
Then open http://localhost:8000
