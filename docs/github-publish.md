# Publishing to GitHub

The generated package is ready to push as a public repository.

```bash
cd NextUSinger
git init
git add .
git commit -m "Initial NextUSinger Studio prototype"
git branch -M main
git remote add origin https://github.com/<your-user>/NextUSinger.git
git push -u origin main
```

Do not commit real voicebank/model files unless you own redistribution rights. `.gitignore` already excludes common model weight extensions.
