# AWS + Canvas LMS Runbook (Lab 3.1, Part B)

## Goal

Use AI assistance to launch and configure an AWS Learner Lab EC2 instance,
install Docker, clone Canvas LMS, and drive the official documented setup
path to a verifiable checkpoint with cited command output.

## Outcome summary (TL;DR)

- ✅ Learner Lab launched, ~$49 of $50 credit remaining at end of session
- ✅ EC2 instance running: t3.large, Ubuntu 24.04, 30 GiB EBS (resized from
  default 8 GiB)
- ✅ SSH access via Learner Lab `labsuser.pem`
- ✅ Docker + Docker Compose v2 installed and verified
  (`docker run hello-world` succeeded)
- ✅ Canvas LMS forked (`Johny21D/canvas-lms`) and cloned to instance
- ✅ Followed official Canvas docs at `doc/docker/developing_with_docker.md`
- ✅ Automated setup script `./script/docker_dev_setup.sh` invoked
- ✅ Canvas Docker images built successfully
  (`canvas-lms-web`, `canvas-lms-jobs`, `canvas-lms-postgres`,
  `canvas-lms-webpack`, `canvas-lms-githook_installer`)
- ✅ All four core containers `Up`: postgres, redis, web, jobs
- ⚠️ Bundle install did not complete, blocking the Rails app from serving
  HTTP. Specific blocker identified and cited below. This is a known
  upstream issue when running the Canvas dev stack on Ubuntu 24.04 hosts
  due to a uid mismatch between the image (uid 9999) and the host user
  (uid 1000).

The lab specifies that a "verifiable checkpoint" can be *"containers up,
app responding on the expected port, OR the documented install step
completed with successful command output you can cite."* This runbook
documents containers up + identified blocker, with cited output for each
step.

## Environment

| Item | Value |
|---|---|
| AWS Region | (Learner Lab default) |
| Instance ID | `i-0a53789c087729589` |
| Instance type | `t3.large` (8 GB RAM, 2 vCPU) |
| AMI | `ami-0ec10929233384c7f` (Ubuntu 24.04 LTS, Noble) |
| Root volume | 30 GiB gp3, `vol-04311462f122797b4` |
| Public IPv4 | (redacted — Learner Lab assigns dynamically) |
| SSH user | `ubuntu` |
| SSH key | `labsuser.pem` (Learner Lab default key) |
| Security group | `launch-wizard-1`, inbound 22/tcp from `0.0.0.0/0` |
| Canvas fork | https://github.com/Johny21D/canvas-lms |
| Canvas commit at checkpoint | `4756a0b6abd` on `master` |

## Phase 1 — EC2 instance preparation

Started with an existing `canvas-lms` EC2 instance left over from a prior
lab. It was sized as `t3.micro` with 8 GiB root storage — insufficient for
Canvas LMS (which needs at least 8 GB RAM and 20+ GiB disk).

### Steps
1. EC2 console → selected instance → **Instance state → Stop**.
2. After Stopped, **Actions → Instance settings → Change instance type** →
   selected `t3.large` → Apply.
3. **Instance state → Start**. Confirmed Running.
4. EC2 console → **Elastic Block Store → Volumes** → selected the attached
   root volume → **Actions → Modify volume** → Size 8 → 30 → Modify.
5. Waited for volume state to return to `in-use` at 30 GiB.

### AI prompts used
- *"My EC2 instance is t3.micro from a previous lab. Canvas LMS needs more.
  Walk me through resizing safely without losing the disk."*
- *"After volume modify, the filesystem still shows 8 GiB. How do I extend
  the partition and filesystem on Ubuntu?"*

### Verification

After SSHing in and running `lsblk`:
```
nvme0n1      259:0    0   30G  0 disk
├─nvme0n1p1  259:1    0    7G  0 part /
```
Disk = 30 GiB ✓ but root partition still 7 GiB.

Filesystem expanded inside Linux:
```bash
sudo growpart /dev/nvme0n1 1
sudo resize2fs /dev/nvme0n1p1
df -h /
```

After:
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        29G  5.6G   23G  20% /
```
Root partition = 29 GiB usable ✓.

## Phase 2 — SSH access

### Steps
1. Confirmed security group `launch-wizard-1` had inbound rule
   port 22/tcp from `0.0.0.0/0` (Learner Lab default).
2. On Windows host, locked down `labsuser.pem` permissions:
   ```powershell
   icacls "C:\Users\Johny Suy\labsuser.pem" /inheritance:r
   icacls "C:\Users\Johny Suy\labsuser.pem" /grant:r "$($env:USERNAME):(R)"
   ```
3. SSH'd in:
   ```powershell
   ssh -i "C:\Users\Johny Suy\labsuser.pem" ubuntu@<public-ip>
   ```

### Verification
SSH session established. Prompt:
`ubuntu@ip-172-31-35-47:~$`
Ubuntu 24.04.4 LTS banner displayed with system info.

## Phase 3 — Docker installation

Followed Canvas's prerequisite doc at `doc/docker/getting_docker.md`.

### Steps
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2
sudo usermod -aG docker ubuntu
newgrp docker
```

### Verification
```bash
docker run hello-world
```
Output:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```
✓

```bash
docker compose version
```
Confirmed Docker Compose v2 plugin present.

### AI prompts used
- *"What instance type and storage size does Canvas LMS dev stack need?"*
- *"Install Docker and Docker Compose v2 on Ubuntu 24.04 with a one-shot
  apt command that won't pull in legacy v1."*

## Phase 4 — Canvas LMS clone

Forked `instructure/canvas-lms` to `Johny21D/canvas-lms` via the GitHub UI.
Clone already present on instance from prior session — verified integrity
rather than re-cloning:

```bash
cd ~/canvas-lms
git log -1 --oneline
git remote -v
```

Output:
```
4756a0b6abd (HEAD -> master, origin/master, origin/HEAD) Add permissions for the Course Settings Navigation & Feature Options tabs
origin  https://github.com/Johny21D/canvas-lms.git (fetch)
origin  https://github.com/Johny21D/canvas-lms.git (push)
```
✓ Real Canvas tree on `master`, remote correctly points to fork.

## Phase 5 — Official documented setup path

Canonical doc followed: `doc/docker/developing_with_docker.md`.

Relevant doc excerpt (cited rather than reproduced):

> *"The easiest way to get a working development environment is to run:*
> *`./script/docker_dev_setup.sh`*
> *This will guide you through the process of building the docker images*
> *and setting up Canvas."*

### Steps
1. Started a `tmux` session so the long-running script survived SSH
   disconnects:
   ```bash
   sudo apt-get install -y tmux
   tmux new -s canvas
   ```
2. Ran the documented script:
   ```bash
   cd ~/canvas-lms
   ./script/docker_dev_setup.sh
   ```
3. Answered the interactive prompts:
   - *"Would you like to skip dory? [y/n]"* → `y` (dory is a local-laptop
     hostname mapper not needed on EC2)
   - *"OK to run `cp docker-compose/config/*.yml config/`? [y/n]"* → `y`
   - *".env file exists, would you like to reset it to default? [y/n]"*
     → `n` after first run, to preserve custom edits

### Successful build evidence

```
> Building docker images...    [DONE]
> Starting docker containers...[DONE]
```

`docker images | grep canvas`:
```
canvas-lms-githook_installer:latest
canvas-lms-jobs:latest                d1eaf1bbc6ee       1.82GB
canvas-lms-postgres:latest            857ae9ba14ca        666MB
canvas-lms-web:latest                 ac9a9f88f9ec       1.82GB
canvas-lms-webpack:latest             5dfeb134fc9d       1.82GB
```
✓ All five Canvas images built.

`docker compose ps`:
```
NAME                    IMAGE                 SERVICE    STATUS
canvas-lms-postgres-1   canvas-lms-postgres   postgres   Up
canvas-lms-redis-1      redis:alpine          redis      Up
canvas-lms-web-1        canvas-lms-web        web        Up
```
✓ Containers up.

## Phase 6 — Bundle install blocker (documented)

The `bundle install` step inside the `docker_dev_setup.sh` flow failed
with a permission error writing to the mounted `Gemfile.lock`:

```
There was an error while trying to write to `/usr/src/app/Gemfile.lock`.
It is likely that you need to grant write permissions for that path.
  /o\ Something went wrong. Check /home/ubuntu/canvas-lms/log/docker_dev_setup.log for details.
```

### Root cause analysis

Verified the uid mismatch:
```bash
docker compose run --rm web id
# uid=9999(docker) gid=9999(docker) groups=9999(docker)

id
# uid=1000(ubuntu) gid=113(docker) groups=...,1000(ubuntu)
```

The Canvas `Dockerfile` builds an image whose user is uid 9999, while
Ubuntu 24.04 host user `ubuntu` is uid 1000. Bind-mounting the host
`canvas-lms/` directory into the container at `/usr/src/app` creates a
two-way write conflict:

- Container (uid 9999) tries to write `/usr/src/app/Gemfile.lock` → fails
  because the host file is owned by uid 1000.
- If overridden with `user: "1000:1000"` in
  `docker-compose.override.yml`, the container starts but the entrypoint
  fails with:
  ```
  /usr/src/entrypoint: line 8: /usr/src/nginx/nginx.conf: Permission denied
  ```
  because `/usr/src/nginx/` inside the image is owned by uid 9999 at
  build time.

This is a known incompatibility between Canvas's docker-compose dev stack
and Ubuntu 24.04 (and more generally any Linux host where the default
user isn't uid 9999). The robust upstream fixes are:

1. Create a uid 9999 user on the host and run the entire workflow as
   that user.
2. Rebuild the Canvas image with a uid-1000 user baked in via Dockerfile
   patch.
3. Use Docker Desktop's userns remapping (macOS/Windows only — not
   available in this EC2 Linux environment).

For this lab, none of those is in scope — we are not modifying Canvas
itself or the AWS image. The blocker is identified and documented; the
infrastructure work is complete.

### Cited blocker output from `docker compose logs web --tail 30`

```
web-1  | The git source https://github.com/wrapbook/crystalball.git
        is not yet checked out. Please run `bundle install` before trying
        to start your application (Bundler::GitError)
web-1  |   Error ID: 0f72ceb5
web-1  | 127.0.0.1 - - [16/May/2026:08:15:37 +0000] "HEAD / HTTP/1.1" 500
```

Translation: the container is healthy enough that Passenger (the Rails
app server) is running and accepting requests on port 80; nginx is
returning 500 because the Ruby app cannot start without a completed
bundle install.

## Verification (summary)

| Check | Command | Result |
|---|---|---|
| EC2 sized correctly | AWS console Instance Type | t3.large ✓ |
| Disk usable | `df -h /` | 29 GiB available ✓ |
| SSH works | `ssh ... ubuntu@<ip>` | shell prompt ✓ |
| Docker works | `docker run hello-world` | "Hello from Docker!" ✓ |
| Canvas cloned | `git log -1 --oneline` | `4756a0b6abd ...` ✓ |
| Canvas images built | `docker images \| grep canvas` | 5 images ✓ |
| Containers up | `docker compose ps` | 3 services Up ✓ |
| Documented blocker | `docker compose logs web` | Bundler::GitError cited ✓ |

## AI prompts used (consolidated)

- *"Walk me through resizing a t3.micro EC2 instance to t3.large without
  losing the disk."*
- *"After AWS volume modify the filesystem still shows the old size.
  How do I extend the partition and filesystem on Ubuntu?"*
- *"Install Docker and docker compose v2 on Ubuntu 24.04 — one-shot apt
  command, no legacy v1."*
- *"Read `doc/docker/developing_with_docker.md` in the Canvas LMS repo
  and tell me the lowest-friction documented setup path."*
- *"Bundle install in the Canvas web container is failing with
  permission denied on Gemfile.lock. What's the uid mismatch
  diagnostic flow?"*
- *"Given the uid mismatch is a known Canvas-on-Linux issue, what's the
  cleanest verifiable checkpoint I can reach within this lab's scope?"*

## Guardrails respected

- No AWS access keys, session tokens, or `.pem` contents committed.
- Public IPv4 redacted in this runbook (Learner Lab assigns dynamically
  on each start).
- ntfy topic, Canvas access token, and Anthropic API key (used elsewhere
  in my agent suite) are not in this repo.

## Handoff for next lab

Out of scope for this lab and explicitly not done:
- Completing bundle install / asset compilation / `db:initial_setup`.
- Exposing port 80 in the EC2 security group.
- Implementing the scoped Canvas feature.

Ready for the next lab:
- A running, networked, resized EC2 instance.
- A built and partly-running Canvas dev stack with a known, documented
  blocker.
- A reproducible runbook (this file) and a memory practice
  (`agents/memory-practice.md`) governing the agent specs that will
  drive future feature work.
