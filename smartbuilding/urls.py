"""
URL configuration for smartbuilding project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

# import views from the bot app
from bot import views as bot_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', bot_views.signup, name='signup'),
    path('login/', bot_views.login_view, name='login'),
    path('logout/', bot_views.logout_view, name='logout'),
    path('dashboard/', bot_views.dashboard, name='dashboard'),
    path('dashboard/<slug:page>/', bot_views.dashboard_page, name='dashboard_page'),
    path('dashboard/facilities/<slug:facility>/', bot_views.facility_detail, name='facility_detail'),

    # Feature 1: Complaints
    path('complaints/', bot_views.complaints, name='complaints'),
    path('complaints/all/', bot_views.all_complaints, name='all_complaints'),
    path('complaints/<int:complaint_id>/update/', bot_views.update_complaint, name='update_complaint'),

    # Feature 2: Notices
    path('notices/', bot_views.notice_board, name='notice_board'),
    path('notices/post/', bot_views.post_notice, name='post_notice'),
    path('notices/<int:notice_id>/delete/', bot_views.delete_notice, name='delete_notice'),

    # Feature 3: Visitors
    path('visitors/', bot_views.visitor_pass, name='visitor_pass'),
    path('visitors/<int:visitor_id>/cancel/', bot_views.cancel_visitor, name='cancel_visitor'),
    path('visitors/security/', bot_views.security_visitors, name='security_visitors'),
    path('visitors/<int:visitor_id>/arrived/', bot_views.mark_arrived, name='mark_arrived'),

    # Feature 4: Amenity Booking
    path('amenities/', bot_views.book_amenity, name='book_amenity'),
    path('amenities/<int:booking_id>/cancel/', bot_views.cancel_booking, name='cancel_booking'),
    path('amenities/all/', bot_views.all_bookings, name='all_bookings'),
]

# Serve media files during development
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
