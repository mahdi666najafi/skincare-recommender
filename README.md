# skincare-recommender
A skincare recommendation system with product catalog, filtering, personalized routines, and a basic recommendation engine.


## Data model diagrams


![دیاگرام مدل های پروژه](test.png)


## API reference

### 1. Register - ثبت‌نام کاربر جدید
**Endpoint:** `POST /api/register/`  

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "username",
  "skin_type": "dry",
  "concerns": ["acne", "aging"],
  "preferences": ["vegan", "cruelty_free"],
  "device_type": "mobile"
}
```
**Response:**
- **201 Created - Successful**
```json
{
  "success": true,
  "message": "User created successfully",
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "name": "username",
    "skin_type": "dry"
  }
}
```
- **400 Bad Request - Error**
```json
{
  "success": false,
  "error": "User already exists"
}
```

### 2. Login - ورود کاربر
**Endpoint:** `POST /api/login/`  

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response:**
- **200 OK - Successful**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "abc123token456",
  "user": {
    "user_id": 1,
    "email": "user@example.com",
    "name": "username",
    "skin_type": "dry"
  }
}
```
- **401 Unauthorized - Error**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

---
## Product Endpoints

### 3. Product List - لیست محصولات
**Endpoint:** `GET /api/products/`  
**Headers:** `Authorization: Token abc123token456`  

**Response:**
```json
{
  "count": 100,
  "next": "http://api.example.com/products/?page=2",
  "previous": null,
  "results": [
    {
      "product_id": 1,
      "name": "کرم مرطوب کننده",
      "description": "توضیحات محصول",
      "price": "250000",
      "category": 1,
      "skin_type": "dry",
      "ingredients": "مواد تشکیل دهنده",
      "usage_instructions": "دستورالعمل استفاده",
      "image": "/media/products/cream.jpg"
    }
  ]
}
```

### 4. Product Detail - جزئیات محصول
**Endpoint:** `GET /api/products/{product_id}/`  

**Response:**
```json
{
  "product_id": 1,
  "name": "کرم مرطوب کننده",
  "description": "توضیحات کامل محصول",
  "price": "250000",
  "category": 1,
  "skin_type": "dry",
  "ingredients": "مواد تشکیل دهنده",
  "usage_instructions": "دستورالعمل استفاده",
  "image": "/media/products/cream.jpg",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 5. Create Product - ایجاد محصول جدید
**Endpoint:** `POST /api/products/create/`  
**Headers:** `Authorization: Token abc123token456`  

**Request Body (FormData):**
- name (required) - نام محصول
- description (required) - توضیحات
- price (required) - قیمت
- category (required) - دسته‌بندی
- skin_type (required) - نوع پوست
- ingredients - مواد تشکیل دهنده
- usage_instructions - دستورالعمل
- image - تصویر محصول

**Response:**
- **201 Created - موفق**
```json
{
  "product_id": 1,
  "name": "کرم جدید",
  "price": "300000",
  "message": "Product created successfully"
}
```

---
## Interaction Endpoints

### 6. Log Interaction - ثبت تعامل کاربر
**Endpoint:** `POST /api/interactions/log/`  
**Headers:** `Authorization: Token abc123token456`  

**Request Body:**
```json
{
  "product_id": 1,
  "interaction_type": "view"
}
```
**Interaction Types:**
- view - مشاهده محصول
- click - کلیک روی محصول
- purchase - خرید محصول
- wishlist - افزودن به لیست علاقه‌مندی

**Response:**
- **201 Created - موفق**
```json
{
  "status": "Interaction logged successfully."
}
```

---
## Recommendation Endpoints

### 7. Get Recommendations - دریافت پیشنهادات
**Endpoint:** `GET /api/recommendations/`  
**Headers:** `Authorization: Token abc123token456`  

**Query Parameters:**
- limit - تعداد پیشنهادات (default: 10, max: 50)
- season - فصل (summer, winter, etc.)
- device - نوع دستگاه (mobile, desktop)

**Response:**
```json
{
  "count": 10,
  "context": {
    "season": "winter",
    "device": "mobile"
  },
  "recommendations": [
    {
      "product_id": 1,
      "name": "کرم زمستانی",
      "price": "350000",
      "reason": "Based on your skin type and winter season"
    }
  ]
}
```

---
## Quiz Endpoints

### 8. Get Quiz Questions - دریافت سوالات کوییز
**Endpoint:** `GET /api/quiz/questions/`  
**Headers:** `Authorization: Token abc123token456`  

**Response:**
```json
{
  "success": true,
  "questions": [
    {
      "question_id": 1,
      "question_text": "What is your skin type?",
      "question_type": "single",
      "options": [
        {"value": "oily", "text": "Oily", "related_field": "skin_type"}
      ]
    }
  ],
  "total_questions": 4
}
```

### 9. Submit Quiz Answers - ارسال پاسخ‌های کوییز
**Endpoint:** `POST /api/quiz/submit/`  
**Headers:** `Authorization: Token abc123token456`  

**Request Body:**
```json
{
  "answers": {
    "skin_type": "dry",
    "concerns": ["acne", "aging"],
    "preferences": ["vegan"],
    "budget_range": "medium"
  }
}
```
**Response:**
- **201 Created - موفق**
```json
{
  "success": true,
  "message": "Quiz submitted successfully",
  "quiz_id": 123,
  "results": {
    "skin_type": "dry",
    "concerns": ["acne", "aging"],
    "preferences": ["vegan"],
    "budget_range": "medium"
  }
}
```

### 10. Get Quiz Results - دریافت نتایج کوییز
**Endpoint:** `GET /api/quiz/results/`  
**Headers:** `Authorization: Token abc123token456`  

**Response:**
```json
{
  "success": true,
  "count": 3,
  "results": [
    {
      "quiz_id": 123,
      "skin_type": "dry",
      "concerns": ["acne"],
      "preferences": ["vegan"],
      "budget_range": "medium",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---
## Routine Endpoints

### 11. Generate Routine - ایجاد روتین مراقبتی
**Endpoint:** `POST /api/routines/generate/`  
**Headers:** `Authorization: Token abc123token456`  

**Request Body:**
```json
{
  "quiz_data": {
    "skin_type": "dry",
    "concerns": ["aging"]
  }
}
```
**Response:**
- **201 Created - موفق**
```json
{
  "success": true,
  "message": "Routines generated successfully",
  "data": [
    {
      "routine_id": 1,
      "plan_name": "روتین صبحگاهی",
      "steps": [
        {"product_id": 1, "step": 1, "instructions": "تمیز کردن"}
      ]
    }
  ]
}
```

### 12. Get User Routines - دریافت روتین‌های کاربر
**Endpoint:** `GET /api/routines/`  
**Headers:** `Authorization: Token abc123token456`  

**Response:**
```json
{
  "success": true,
  "count": 2,
  "routines": [
    {
      "routine_id": 1,
      "plan_name": "روتین صبحگاهی",
      "steps": [
        {"product_id": 1, "step": 1}
      ],
      "created_at": "2024-01-15T10:30:00Z",
      "user_email": "user@example.com"
    }
  ]
}
```

### 13. Get Routine Detail - جزئیات روتین
**Endpoint:** `GET /api/routines/{routine_id}/`  
**Headers:** `Authorization: Token abc123token456`  

**Response:**
```json
{
  "success": true,
  "routine": {
    "routine_id": 1,
    "plan_name": "روتین صبحگاهی",
    "steps": [
      {
        "product_id": 1,
        "product_name": "کرم مرطوب کننده",
        "step": 1,
        "instructions": "صبح ها استفاده شود"
      }
    ],
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 14. Delete Routine - حذف روتین
**Endpoint:** `DELETE /api/routines/{routine_id}/`  
**Headers:** `Authorization: Token abc123token456`  

**Response:**
- **200 OK - موفق**
```json
{
  "success": true,
  "message": "Routine deleted successfully"
}
```

---
## Permission Requirements
- عمومی: Register, Login
- نیاز به احراز هویت: تمام endpoints به جز Register/Login
- مدیریتی: Create Product (فقط ادمین)

## Error Responses
**Common Error Format:**
```json
{
  "success": false,
  "error": "Error message description"
}
```

**Status Codes:**
- 400 Bad Request - داده‌های ورودی نامعتبر
- 401 Unauthorized - توکن معتبر ارائه نشده
- 403 Forbidden - دسترسی غیرمجاز
- 404 Not Found - منبع یافت نشد
- 500 Internal Server Error - خطای سرور

---
## دستورالعمل اجرای پروژه و تست

### اجرای پروژه (Running)
1. ابتدا مطمئن شوید Python 3 و pip روی سیستم شما نصب باشد.
2. وابستگی‌های پروژه را نصب کنید:
   ```bash
   pip install -r requirements.txt
   ```
3. مهاجرت‌های پایگاه داده را اعمال کنید:
   ```bash
   python manage.py migrate
   ```
4. (اختیاری) ساخت کاربر ادمین برای ورود به پنل مدیریتی:
   ```bash
   python manage.py createsuperuser
   ```
5. اجرای سرور توسعه:
   ```bash
   python manage.py runserver
   ```

پروژه روی آدرس زیر در دسترس خواهد بود:  
[http://127.0.0.1:8000](http://127.0.0.1:8000)

### تست پروژه (Testing)
برای اجرای تست‌های خودکار جنگو:
```bash
python manage.py test
```
اگر پروژه از pytest یا ابزار تست دیگری استفاده کرده باشد، دستور می‌تواند به شکل زیر باشد:
```bash
pytest
```

---
## توضیح مختصر Recommendation System

### الف) پایگاه محتوا (Content-Based) - 50% وزن
ورودی‌ها:
- تاریخچه بازدید کاربر
- نتایج کوئیز
- ویژگی‌های محصول

استفاده از شباهت کسینوسی بین بردار ویژگی‌ها:
```python
feature_text = f"{product.category} {product.skin_types} {product.concerns_targeted} {product.ingredients}"
feature_matrix = self.vectorizer.fit_transform(features)
similarity_scores = cosine_similarity(user_profile, feature_matrix)
```

مراحل پردازش:
1. استخراج ویژگی‌ها
2. ساخت پروفایل کاربر
3. محاسبه شباهت

**مزایا:** عدم نیاز به داده سایر کاربران، مناسب برای کاربران جدید  
**معایب:** محدود به محتوای موجود، کشف نکردن سلیقه‌های جدید

### ب) فیلتر مشارکتی (Collaborative) - 30% وزن
ورودی:
- رفتار کاربران مشابه
- تعاملات آن‌ها

تکنیک: User-User Similarity  
```python
intersection = len(user_viewed_products.intersection(other_viewed))
union = len(user_viewed_products.union(other_viewed))
similarity = intersection / union if union > 0 else 0
```

معیار شباهت: Jaccard Similarity  
```text
Jaccard(A,B) = |A ∩ B| / |A ∪ B|
```

**مزایا:** کشف محتوای جدید، شخصی‌سازی قوی  
**معایب:** Cold Start، نیاز به داده زیاد

### ج) زمینه‌ای (Contextual) - 20% وزن
فاکتورهای موثر:
1. فصل سال (Seasonal)
```python
seasonal_keywords = {
    'summer': ['sunscreen', 'spf', 'lightweight', 'gel', 'oil-free'],
    'winter': ['hydrating', 'cream', 'rich', 'moisturizing', 'balm'],
    'spring': ['lightweight', 'refreshing', 'toner', 'serum'],
    'fall': ['repair', 'serum', 'moisturizer', 'treatment']
}
```
2. نوع دستگاه (Device)
- موبایل: محصولات ساده
- دسکتاپ: محصولات تخصصی
3. شرایط محیطی (آب و هوا، موقعیت، ساعت روز)

الگوریتم وزندهی:
```python
if season and self.is_seasonal_product(product, season):
  scores[i] *= 1.5

if device == 'mobile' and product.category in ['cleanser', 'moisturizer']:
  scores[i] *= 1.3
```

**مزایا:** در نظرگیری شرایط واقعی کاربر، افزایش relevancy  
**معایب:** نیاز به داده زمینه‌ای دقیق، پیچیدگی جمع‌آوری context

**امتیاز نهایی:**
```
Final Score = (0.5 × Content) + (0.3 × Collaborative) + (0.2 × Contextual)
```

---
## توضیح مختصر Routine Builder

سیستم Routine Builder یک موتور هوشمند برای ایجاد روتین‌های شخصی‌سازی‌شده است.

### اهداف:
- ایجاد روال‌های مراقبت پوست شخصی‌سازی شده
- ارائه چندین گزینه بر اساس سبک زندگی کاربر
- یکپارچه‌سازی با سیستم پیشنهاد‌دهی
- ذخیره و مدیریت روال‌های کاربران

### ساختار روتین‌ها
```python
ROUTINE_STEPS = {
    'full': ['cleanser', 'toner', 'serum', 'moisturizer', 'sunscreen'],
    'hydration': ['cleanser', 'serum', 'moisturizer'],
    'minimalist': ['cleanser', 'moisturizer', 'sunscreen']
}
```

### انواع روتین‌ها
- Complete Care (5 مرحله)
- Hydration Boost (3 مرحله)
- Essential Minimal (3 مرحله)

### مراحل تولید روتین
1. دریافت داده‌های کاربر
2. فیلتر محصولات بر اساس پروفایل
3. انتخاب محصولات برای هر مرحله
4. ذخیره روال در دیتابیس

### الگوریتم انتخاب محصول
مراحل:
1. فیلتر اولیه
2. فیلتر پیشرفته
3. دریافت پیشنهادات recommender
4. Fallback به انتخاب تصادفی

### ساختار خروجی
```json
{
  "plan_name": "full",
  "plan_display_name": "Complete Care Routine",
  "steps": [
    {
      "step": "cleanser",
      "product_name": "Hydrating Cleanser",
      "instructions": "Apply to damp skin...",
      "category": "cleanser"
    }
  ],
  "total_steps": 5,
  "estimated_time": "10-15 minutes"
}
```

### یکپارچه‌سازی
- با Recommender System  
- با مدل‌های دیتابیس: Product, QuizResult, RoutinePlan, Users

### مدیریت خطاها
- Fallback به محصولات تصادفی
- Handling عدم وجود داده کوئیز
- مدیریت محصولات ناموجود
