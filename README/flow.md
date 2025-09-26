# Application Flow
- Here is the basic flow of the app for Dev and Prod
- As of 9/24/25

# Development / Production
- The following steps should be done in order unless already completed.  

## Initial set up (skip if already had running)

### Environment
- pip install -r requirements.txt

### Superuser
- python manage.py createsuperuser

### Group Permissions
Start app / log in with superuser
- Owner - gets everything
- Admin - gets all the app permissions (not admin/auth/content/sessions)
- HR - gets all userApp but delete and all of clientProfile
- Employee - gets all views for all apps with small exceptions and has some add and changes (see auth.sql file for example)

### ProposalApp set up
With Owner login
- Set up base settings, Catalog Items, Cost Tiers, and Job Rates

### AnnounceApp set up
With Owner login
- Create Version


## Creating users
- Employees
    1. make sure to add emails to each new employee you add before adding the next one, set role to position
- Clients
    1. do not create until company is created