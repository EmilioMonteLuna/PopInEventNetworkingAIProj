# 📊 CSV Import Guide for PopIn

## 🎯 **Easy Attendee Data Import**

Your Event Networking AI System now supports **easy CSV import** for bulk attendee management!

## 📁 **CSV Import Endpoints**

### **1. Import Attendees**
```bash
POST /api/v1/import/attendees-csv?event_id=1&auto_register=true
Content-Type: multipart/form-data
File: attendees.csv
```

### **2. Download Template**
```bash
GET /api/v1/import/csv-template
# Downloads: attendee_import_template.csv
```

### **3. Validate CSV**
```bash
POST /api/v1/import/validate-csv
Content-Type: multipart/form-data
File: attendees.csv
```

## 📋 **CSV Format**

### **Required Columns:**
- `name` - Full name of attendee
- `email` - Email address (unique identifier)

### **Optional Columns:**
- `job_title` - Professional title
- `company` - Company name
- `industry` - Industry category
- `bio` - Professional bio/description
- `experience_years` - Years of experience (number)
- `interests` - Comma-separated interests
- `goals` - Comma-separated networking goals
- `linkedin_url` - LinkedIn profile URL

## 📄 **Sample CSV Format:**

```csv
name,email,job_title,company,industry,bio,experience_years,interests,goals,linkedin_url
Alice Chen,alice@company.com,AI Engineer,TechCorp,Technology,AI specialist with focus on machine learning,4,"Machine Learning,Python,AI Ethics","Find cofounders,Learn about startups",https://linkedin.com/in/alice
Bob Martinez,bob@vc.com,Partner,Venture Capital,Finance,Venture capital investor focused on AI startups,8,"Investment,Startups,AI","Find deals,Meet entrepreneurs",https://linkedin.com/in/bob
Carol Thompson,carol@university.edu,Research Scientist,University,Education,PhD researcher in computational biology,6,"Research,Healthcare AI","Find collaborators,Industry partnerships",https://linkedin.com/in/carol
```

## 🚀 **How PopIn Uses This:**

### **Step 1: Prepare Data**
```bash
# Export from their event platform
# Or create CSV from their attendee database
# Download template: GET /api/v1/import/csv-template
```

### **Step 2: Validate CSV**
```bash
# Test the format before importing
POST /api/v1/import/validate-csv
```

### **Step 3: Import Attendees**
```bash
# Bulk import and auto-register for event
POST /api/v1/import/attendees-csv?event_id=1&auto_register=true
```

### **Step 4: Generate AI Recommendations**
```bash
# System automatically generates networking suggestions
POST /api/v1/recommendations/generate
```

## 📊 **Import Response Example:**

```json
{
  "message": "CSV import completed successfully",
  "event_id": 1,
  "event_name": "AI Innovation Summit 2025",
  "statistics": {
    "total_rows": 50,
    "users_created": 35,
    "users_updated": 15,
    "users_registered": 50,
    "errors": []
  }
}
```

## 🛠️ **Advanced Features:**

### **Flexible Interest/Goals Format:**
```csv
# Multiple separators supported
interests: "Machine Learning,Python,AI Ethics"
interests: "Machine Learning;Python;AI Ethics"  
interests: "Machine Learning|Python|AI Ethics"
```

### **Error Handling:**
- ✅ **Duplicate emails** - Updates existing users
- ✅ **Missing data** - Uses defaults, continues processing
- ✅ **Invalid formats** - Reports specific errors
- ✅ **Partial failures** - Imports valid rows, reports errors

### **Auto-Registration:**
- ✅ **Bulk event registration** - All imported users auto-registered
- ✅ **Duplicate prevention** - Won't double-register existing attendees
- ✅ **Statistics tracking** - Complete import/registration reporting

## 🎯 **PopIn Integration Scenarios:**

### **Scenario 1: Eventbrite Export**
```bash
# PopIn exports CSV from Eventbrite
# Maps columns to our format
# Bulk imports to Event Networking AI
```

### **Scenario 2: Corporate Event**
```bash
# HR provides employee list
# Adds professional goals/interests
# Creates networking event automatically
```

### **Scenario 3: Conference Speakers**
```bash
# Speaker database with rich profiles
# Includes expertise and topics
# Generates high-quality recommendations
```

## 🔗 **Integration with Existing System:**

### **API Workflow:**
```python
# 1. Create event
POST /api/v1/events

# 2. Import attendees  
POST /api/v1/import/attendees-csv

# 3. Generate recommendations
POST /api/v1/recommendations/generate

# 4. Create cluster map
GET /api/v1/visualization/cluster-map

# 5. Get analytics
GET /api/v1/analytics/event/{id}
```

## 🎉 **Benefits for PopIn:**

- ✅ **Quick Setup** - Import hundreds of attendees in minutes
- ✅ **Data Validation** - Catches errors before import
- ✅ **Flexible Format** - Works with various data sources
- ✅ **Auto-Registration** - One-step event setup
- ✅ **Rich Profiles** - Supports detailed attendee information
- ✅ **Error Recovery** - Partial imports with error reporting

**This makes your AI system immediately usable with PopIn's existing attendee data! 🚀📊**