# 🏡 RentalHub – Django Property Rental Platform

RentalHub is a fully–featured property listing and management system built with **Django**, designed to connect landlords and tenants.  
Landlords can upload properties with multiple photos, while tenants can browse, filter, and favorite listings with ease.

This project is optimized for performance, responsive design, clean architecture, and maintainability.

---

## 🚀 Features

### **👨‍💼 Landlord Features**
- Add, update, and delete properties  
- Upload **multiple photos** per property  
- Manage availability status  
- Edit and remove uploaded images via AJAX  
- Personal dashboard showing:
  - Total properties  
  - Available properties  
  - Paginated list of owned units  

### **🏘️ Tenant Features**
- Browse all properties  
- Search by house number, county, town, or location  
- Filter by house type and availability  
- Property cards with swipeable image carousel  
- Favorite a property (if enabled)  
- Mobile-friendly and responsive interface  

### **📸 Image System**
- Supports **multiple file uploads** via a custom Django widget  
- Images stored in `/media/property_photos/`  
- Each property can have unlimited images  
- Old images removable from landlord edit page  
- File uploads handled safely with CSRF & Django media config  

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | Django 5.x |
| Frontend | HTML5, CSS3, Bootstrap, SwiperJS carousel |
| Database | SQLite (dev) / PostgreSQL (recommended) |
| Authentication | Django Auth |
| Media Handling | Django File Storage |
| Deployment Ready | ✔ Yes |

---

## 📂 Project Structure

project_root/
│
├── accounts/ # User accounts, auth, roles
├── landlords/ # Landlord dashboard, CRUD, forms
├── properties/ # Property models + PropertyImage model
│ ├── templates/
│ │ ├── properties/
│ │ │ ├── browse_properties.html
│
├── media/
│ └── property_photos/ # Uploaded images
│
├── static/ # JS, CSS, assets
├── templates/ # Base templates
│ └── base.html
│
└── manage.py

yaml
Copy code

---

## ⚙️ Installation & Setup

### **1. Clone the repository**
```bash
git clone https://github.com/yourusername/rentalhub.git
cd rentalhub

2. Create a virtual environment
bash

python3 -m venv venv
source venv/bin/activate

3. Install dependencies
bash
pip install -r requirements.txt

4. Apply migrations
bash
python manage.py migrate

5. Create superuser
bash
python manage.py createsuperuser

6. Run development server
bash
python manage.py runserver

7. Ensure MEDIA files work
In settings.py ensure:
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
And update your urls.py:

py
Copy code
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

🧪 Key Models
Property
py

class Property(models.Model):
    landlord = models.ForeignKey(LandlordProfile, on_delete=models.CASCADE)
    house_type = models.CharField(...)
    house_number = models.CharField(...)
    rent = models.IntegerField()
    county = models.CharField(...)
    town = models.CharField(...)
    location = models.CharField(...)
    available = models.BooleanField(default=True)

PropertyImage
py
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_photos/')