# 🧩 Task Manager API

A **role-based Task & Project Management system** built using **Django REST Framework**, supporting **project-level permissions**, **task workflows**, **Redis caching**, and **scalable API design**.

---

## 🚀 Features

### ✅ User Management

* Custom `User` model
* Global roles:

  * `superadmin`
  * `staff`
  * `user`
* Job roles (Backend Dev, QA, PM, etc.)
* Online / last seen tracking

### ✅ Project Management

* Create, update, delete projects
* Project members with roles:

  * `owner`
  * `admin`
  * `member`
  * `viewer`
* Project-level permissions
* Recently updated projects shown first

### ✅ Task Management

* CRUD operations for tasks
* Assign tasks to users
* Filters:

  * Status
  * Priority
  * Project
  * Search (name / description)
* Pagination
* Superadmin can create tasks in any project

### ✅ Permission System

* Global permissions (Superadmin / Staff)
* Project-level permissions (via `ProjectMember`)
* Dynamic permission checks per project
* Permission summary sent to frontend

### ✅ Performance & Caching

* Redis caching using `django-redis`
* Cache versioning for task search
* Automatic cache invalidation on task changes

---

## 🏗️ Tech Stack

| Layer            | Technology                    |
| ---------------- | ----------------------------- |
| Backend          | Django, Django REST Framework |
| Database         | PostgreSQL                    |
| Caching          | Redis                         |
| Auth             | JWT (DRF SimpleJWT)           |
| ORM              | Django ORM                    |
| Deployment Ready | Docker, Gunicorn compatible   |

---

## 📁 Project Structure

```
task-manager-api/
│
├── users/
│   ├── models.py
│   ├── serializers.py
│   └── views.py
│
├── projects/
│   ├── models.py
│   ├── views.py
│   ├── permissions/
│   └── serializers.py
│
├── tasks/
│   ├── models.py
│   ├── views.py
│   ├── permissions.py
│   └── serializers.py
│
├── core/
│   ├── permissions.py
│   └── utils.py
│
├── settings.py
├── urls.py
└── manage.py
```

---

## 🔐 Permission Design

### Global Roles

| Role       | Capabilities                    |
| ---------- | ------------------------------- |
| Superadmin | Full access across all projects |
| Staff      | Limited admin privileges        |
| User       | Project-based permissions       |

### Project Roles

| Role   | Permissions            |
| ------ | ---------------------- |
| Owner  | Full project control   |
| Admin  | Manage tasks & members |
| Member | Task CRUD              |
| Viewer | Read-only              |

---

## 🧠 Dynamic Permission Example

```json
"permissions": {
  "can_create_task": true,
  "can_edit_task": true,
  "can_delete_task": false,
  "can_add_member": true,
  "can_remove_member": false,
  "can_update_project": true,
  "can_delete_project": false
}
```

---

## 🔄 Redis Cache Versioning

Used for task search cache invalidation.

```python
TASK_SEARCH_VERSION_KEY = "task_search_version"

def bump_task_search_version():
    cache.add(TASK_SEARCH_VERSION_KEY, 1)
    cache.incr(TASK_SEARCH_VERSION_KEY)
```

Cache invalidated on:

* Task create
* Task update
* Task delete

---

## 📦 Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/VishalNeosoft24/drf-task-manager-api.git
cd task-manager-api
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Environment Variables

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost:5432/taskdb
REDIS_URL=redis://127.0.0.1:6379/1
```

### 5️⃣ Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6️⃣ Create Superuser

```bash
python manage.py createsuperuser
```

### 7️⃣ Run Server

```bash
python manage.py runserver
```

---

## 🔍 Redis Debugging

```bash
redis-cli
SELECT 1
GET :1:task_search_version
```

---

## 📑 API Highlights

### Create Task

```
POST /api/tasks/
```

### List Projects

```
GET /api/projects/?search=crm&page=1
```

### Project Members with Tasks

```
GET /api/projects/{id}/members/
```

---

## 🧪 Best Practices Used

* DRF permissions instead of hardcoding logic
* `select_related` & `prefetch_related`
* Query optimizations
* Pagination everywhere
* Clean separation of concerns
* Cache versioning pattern

---

## 🛣️ Roadmap

* [ ] Activity logs
* [ ] WebSocket notifications
* [ ] Task comments & mentions
* [ ] Audit trails
* [ ] Role-based UI controls

---

## 👨‍💻 Author

**Vishal Prajapati**
Python Backend Developer
Django | DRF | Redis | PostgreSQL
