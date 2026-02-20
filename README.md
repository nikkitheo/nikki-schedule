# Availability Schedule Page

A lightweight static website showing your weekly calendar availability,
automatically refreshed from your calendar app's ICS feed every day via GitHub Actions.

Your colleague visits one URL — it always shows your up-to-date availability.
**Event titles are never shown** — only grey "Busy" blocks appear, for privacy.

---

## How it works

```
Your calendar app  →  ICS feed URL  →  GitHub Action (daily)  →  schedule.json  →  index.html
```

1. GitHub Actions runs `generate_schedule.py` every day at 05:00 UTC
2. The script fetches your ICS feed(s) and writes `schedule.json`
3. Your GitHub Pages site serves `index.html`, which reads `schedule.json`
4. Your colleague sees a fresh availability view whenever they open the link

---

## Setup (step by step)

### Step 1 — Get your ICS / iCal URL

Most calendar apps let you export a shareable `.ics` URL.
Find the instructions for your app below.

#### Google Calendar
1. Go to **calendar.google.com → Settings (⚙️) → Settings**
2. On the left sidebar, click the calendar you want to share
3. Scroll down to **"Integrate calendar"**
4. Copy the **"Secret address in iCal format"** (the link ending in `.ics`)
   > Keep this link private — anyone with it can see your calendar.

#### Apple Calendar / iCloud
1. On Mac: right-click the calendar → **Share Calendar**
2. Tick **"Public Calendar"** → copy the link shown
3. Change `webcal://` at the start to `https://` before adding it to the `ICS_URLS` secret

#### Outlook / Microsoft 365
1. Go to **Outlook on the web → Settings → View all Outlook settings**
2. **Calendar → Shared calendars → Publish a calendar**
3. Choose the calendar and set permissions to **"Can view all details"**
4. Click **Publish** and copy the **ICS** link (not the HTML link)

#### Fantastical / BusyCal / other apps
Most apps that sync with Google, iCloud, or Exchange will also show you an ICS
export URL in their settings. Look for "Share", "Publish", or "Export" options.

If you use **multiple calendars** (e.g. work + personal), you can add more than
one URL to the `ICS_URLS` secret, separated by commas — the script merges them all.

---

### Step 2 — Edit config.json

Open `config.json` and update the values:

```json
{
  "ownerName": "Nikki",
  "weeklyProjectHours": 20,
  "timezone": "Europe/London",
  "workdayStart": 8,
  "workdayEnd": 19
}
```

| Field | Description |
|-------|-------------|
| `ownerName` | Your name, shown in the page heading |
| `weeklyProjectHours` | Hours/week you've committed to the project |
| `timezone` | Your local timezone (e.g. `Europe/London`, `America/New_York`, `Europe/Paris`) |
| `workdayStart` | Hour the calendar grid starts (24-hour, e.g. `8` = 8am) |
| `workdayEnd` | Hour the calendar grid ends (24-hour, e.g. `19` = 7pm) |

A list of timezone names is at: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
(use the value in the **TZ identifier** column)

### Step 2b — Add your ICS URL(s) as a GitHub Secret

Your calendar URLs are stored as an encrypted GitHub Secret, not in the code, so they're never visible to anyone.

1. In your repo, go to **Settings → Secrets and variables → Actions → New repository secret**
2. Name it exactly: `ICS_URLS`
3. Paste your ICS URL(s) as the value — if you have more than one, separate them with a comma:
   ```
   https://first-calendar.ics,https://second-calendar.ics
   ```
4. Click **Add secret**

---

### Step 3 — Push the files to a GitHub repository

If you haven't already:

1. Create a **new repository** on github.com (can be private or public)
2. Push all these files to the `main` branch:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

---

### Step 4 — Enable GitHub Pages

1. In your repo, go to **Settings → Pages**
2. Under **"Source"**, select **"Deploy from a branch"**
3. Choose branch: `main`, folder: `/ (root)` → click **Save**
4. After a minute, your page will be live at:
   `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`

---

### Step 5 — Run the Action for the first time

1. Go to your repo → **Actions** tab
2. Click **"Update Schedule"** on the left
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait ~30 seconds for it to finish
5. Refresh your GitHub Pages URL — you should now see your schedule!

---

### Step 6 — Share the link

Send your colleague the GitHub Pages URL:
```
https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/
```

The schedule updates automatically every morning. No action needed from you
unless you want to change the config.

---

## Customising

**Change update frequency:** Edit `.github/workflows/update-schedule.yml`.
Find the `cron:` line and adjust. Use https://crontab.guru to build cron expressions.

**Show more weeks in advance:** The script fetches 8 weeks by default.
Adjust `timedelta(weeks=8)` in `generate_schedule.py` if needed.

**Multiple ICS URLs:** Add them all to the `ICS_URLS` secret, separated by commas.

---

## Files in this repo

| File | Purpose |
|------|---------|
| `index.html` | The public-facing webpage (reads `schedule.json`) |
| `schedule.json` | Auto-generated availability data (updated by GitHub Action) |
| `config.json` | Your display settings (name, timezone, hours) — edit this |
| `generate_schedule.py` | Script that fetches ICS and writes `schedule.json` |
| `.github/workflows/update-schedule.yml` | GitHub Action that runs the script daily |
