# Smart Curriculum, Activity & Attendance System

A web-based campus management system built for the **ICT Department, Marwadi University**. It replaces manual roll calls with **rotating QR codes plus face verification**, and gives students, faculty and the department head one place to manage attendance, grades, timetables and campus updates.

The whole app is a single Python file (`app.py`). It starts a small local web server and serves an embedded React front end.

---

## Problem it solves

- Roll calls waste lecture time.
- Proxy attendance (a friend marking you present) is easy on paper.
- Students and faculty have no single dashboard for attendance, results, assignments and announcements.

## Key features

### Student
- Dashboard with attendance overview
- **Scan the live QR code** shown by the faculty to mark attendance
- **Face verification** against the enrolled photo (camera enrollment)
- Timetable, assignments, results/transcript, curriculum progress, holidays and events

### Faculty
- **Live attendance session** with an auto-rotating QR code (expires quickly, so screenshots can't be shared)
- Recorded sessions dashboard
- Post campus updates and assignments
- Grade entry
- Live quiz / poll
- Assignment plagiarism and similarity checker
- Mass alerts for low-attendance students

### Admin (HOD / Class Coordinator)
- User directory (add and manage users, reset face data)
- Analytics and **defaulter list**
- **Adjustable biometric sensitivity** (face-match confidence threshold)
- Classroom allocator and master curriculum view
- Activity logs: expired QR, duplicate scan and face-mismatch incidents

## Anti-proxy checks

| Check | What it blocks |
|---|---|
| Rotating QR token | Sharing a screenshot of the QR |
| Face match against the enrolled photo | Another person scanning for you |
| Duplicate scan detection | Marking the same session twice |
| Mismatch logging | Gives the admin a trail of suspicious attempts |

## Tech stack

- **Backend:** Python 3 (standard library only: `http.server`, `socketserver`)
- **Frontend:** React 18, Tailwind CSS, Babel (in-browser), Lucide icons
- **QR:** `qrcodejs` (generate) and `jsQR` (scan)
- **Real-time device sync:** PeerJS (laptop to mobile) with optional Firebase Firestore
- **Storage:** browser `localStorage` (demo data seeded at first load)

## Project structure

```
.
├── app.py       # Python server + complete React front end
└── README.md
```

## How to run

**Requirements:** Python 3.8+ and an internet connection (the front-end libraries load from CDNs). No `pip install` is needed.

```bash
git clone https://github.com/mgovardhanreddy047/Smart-Curriculum-and-Attendance-App.git
cd Smart-Curriculum-and-Attendance-App
python app.py
```

The app opens automatically at **http://localhost:8080**. If it doesn't, open that address in your browser.

> Camera features (QR scan and face enrollment) need a browser that allows camera access. `localhost` is allowed. To test from a phone, use an HTTPS deployment.

## Demo login

Demo accounts are seeded in the app. Pick a role on the login screen to continue.

| Role | ID | Password |
|---|---|---|
| Student | `92500133047` | `Govardhan@123` |
| Faculty | `FAC01` | `Kawal@123` |
| Admin | `ADMIN-01` | `Admin@123` |

## Suggested demo flow

1. Log in as **Faculty** and open **Live Attendance** to show the rotating QR.
2. On another device or browser window, log in as **Student** and scan it.
3. Show face verification passing, then a mismatch being logged.
4. Log in as **Admin** and open **Analytics**, **Defaulters** and **Activity Logs**.

## Limitations and future work

- Data is stored in the browser, so a real deployment would need a database (PostgreSQL or Firestore).
- Passwords are plain text in demo data; production use needs hashing and proper authentication.
- Face matching is a lightweight comparison; a trained face-recognition model would be more accurate.
- Add email/SMS notifications for defaulters.

## Author

**M. Govardhan Reddy** · ICT, Marwadi University
GitHub: [@mgovardhanreddy047](https://github.com/mgovardhanreddy047)
