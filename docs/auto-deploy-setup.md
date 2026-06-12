# Auto-Deploy Setup (GitHub Actions → EC2)

Every push to `main` automatically deploys the app to the EC2 instance (~10-20s downtime).

---

## Prerequisites

- SSH access to the EC2 instance (Ubuntu)
- Admin access to the GitHub repo (to add secrets)

---

## Setup Steps

### 1. Generate deploy SSH key (on EC2)

```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions -N ""
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
cat ~/.ssh/github_actions   # copy the entire output — needed in step 4
```

### 2. Get the EC2 public IP (on EC2)

```bash
curl -s http://169.254.169.254/latest/meta-data/public-ipv4
```

### 3. Verify git remote is configured (on EC2)

```bash
cd ~/MMM-guildin && git remote -v
```

Should show the GitHub repo URL. If empty:

```bash
git remote add origin https://github.com/<your-org>/MMM-guildin.git
```

### 4. Rename the running container to a fixed name (on EC2)

```bash
docker stop optimistic_northcutt
docker rm optimistic_northcutt
docker run -d \
  --name mmm-guildin-app \
  --restart unless-stopped \
  -p 8501:8501 \
  mmm-guildin_1
```

### 5. Encode the `.env.rds` file as base64 (on local machine)

```bash
base64 -i .env.rds
```

Copy the output — needed in the next step.

### 6. Add GitHub secrets

Go to: GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `EC2_HOST` | Public IP from step 2 |
| `EC2_SSH_KEY` | Private key output from step 1 |
| `ENV_RDS` | Base64 string from step 5 |

### 7. Push the workflow (on local machine)

```bash
git add .github/workflows/deploy.yml .gitignore
git commit -m "Add auto-deploy workflow and secure env handling"
git push origin main
```

---

## How the deploy works

The workflow (`.github/workflows/deploy.yml`) runs on every push to `main`:

1. SSHes into the EC2 instance
2. Runs `git pull origin main`
3. Writes the `.env.rds` file from the GitHub secret (base64 decoded)
4. Rebuilds the Docker image
5. Stops and replaces the running container

---

## Testing

**Watch a deploy live:**
GitHub repo → **Actions** tab → click the running workflow → expand "Deploy to EC2"

**Trigger manually:**
GitHub → Actions → "Deploy to EC2" → **Run workflow**

**Verify on EC2 after deploy:**
```bash
docker ps
docker logs mmm-guildin-app --tail 20
```

**End-to-end test:**
Make a small change (e.g., edit `README.md`), push to `main`, confirm the Actions tab picks it up and the container restarts.

---

## Notes

- `.env.rds` is gitignored — never commit it
- The `--restart unless-stopped` flag ensures the container survives EC2 reboots
- To add more environment variables in the future, update the `ENV_RDS` secret with a re-encoded `.env.rds`
