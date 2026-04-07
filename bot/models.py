from django.db import models
from django.contrib.auth.hashers import make_password


class Signup(models.Model):
	ROLE_SECURITY = 'security'
	ROLE_SECRETARY = 'secretary'
	ROLE_FLAT_OWNER = 'flat_owner'

	ROLE_CHOICES = [
		(ROLE_SECURITY, 'Security'),
		(ROLE_SECRETARY, 'Secretary'),
		(ROLE_FLAT_OWNER, 'Flat Owner'),
	]

	role = models.CharField(max_length=20, choices=ROLE_CHOICES)
	full_name = models.CharField(max_length=150)
	contact_number = models.CharField(max_length=15)
	aadhar_number = models.CharField(max_length=20)
	dob = models.DateField()
	password = models.CharField(max_length=128)
	created_at = models.DateTimeField(auto_now_add=True)
	profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)

	def save(self, *args, **kwargs):
		# Hash the password if it isn't already hashed
		if self.password and not self.password.startswith('pbkdf2_') and not self.password.startswith('argon2'):
			self.password = make_password(self.password)
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.full_name} ({self.get_role_display()})"


# ─────────────────────────────────────────────────────────
#  FEATURE 1 : Complaint Management
# ─────────────────────────────────────────────────────────
class Complaint(models.Model):
	CATEGORY_CHOICES = [
		('plumbing', 'Plumbing'),
		('electricity', 'Electricity'),
		('noise', 'Noise'),
		('cleanliness', 'Cleanliness'),
		('lift', 'Lift'),
		('parking', 'Parking'),
		('other', 'Other'),
	]
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('in_progress', 'In Progress'),
		('resolved', 'Resolved'),
	]

	ticket_number = models.CharField(max_length=10, unique=True, editable=False)
	resident = models.ForeignKey(Signup, on_delete=models.CASCADE, related_name='complaints')
	category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
	description = models.TextField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	date_filed = models.DateTimeField(auto_now_add=True)
	date_resolved = models.DateTimeField(null=True, blank=True)
	secretary_remarks = models.TextField(blank=True, default='')

	def save(self, *args, **kwargs):
		if not self.ticket_number:
			last = Complaint.objects.order_by('-id').first()
			next_num = 1
			if last and last.ticket_number:
				try:
					next_num = int(last.ticket_number.split('-')[1]) + 1
				except (ValueError, IndexError):
					next_num = (last.id or 0) + 1
			self.ticket_number = f'TKT-{next_num:04d}'
		super().save(*args, **kwargs)

	class Meta:
		ordering = ['-date_filed']

	def __str__(self):
		return f'{self.ticket_number} – {self.get_category_display()}'


# ─────────────────────────────────────────────────────────
#  FEATURE 2 : Digital Notice Board
# ─────────────────────────────────────────────────────────
class Notice(models.Model):
	CATEGORY_CHOICES = [
		('general', 'General'),
		('maintenance', 'Maintenance'),
		('meeting', 'Meeting'),
		('emergency', 'Emergency'),
		('event', 'Event'),
		('water_supply', 'Water Supply'),
		('electricity', 'Electricity'),
	]

	title = models.CharField(max_length=200)
	content = models.TextField()
	category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
	is_urgent = models.BooleanField(default=False)
	posted_by = models.ForeignKey(Signup, on_delete=models.CASCADE, related_name='notices')
	posted_on = models.DateTimeField(auto_now_add=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ['-is_urgent', '-posted_on']

	def __str__(self):
		return self.title


# ─────────────────────────────────────────────────────────
#  FEATURE 3 : Visitor Pre-Approval
# ─────────────────────────────────────────────────────────
class VisitorPass(models.Model):
	STATUS_CHOICES = [
		('approved', 'Approved'),
		('arrived', 'Arrived'),
		('cancelled', 'Cancelled'),
		('expired', 'Expired'),
	]

	flat_owner = models.ForeignKey(Signup, on_delete=models.CASCADE, related_name='visitors')
	visitor_name = models.CharField(max_length=150)
	visitor_contact = models.CharField(max_length=15)
	purpose = models.CharField(max_length=200)
	expected_date = models.DateField()
	expected_time = models.TimeField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
	vehicle_number = models.CharField(max_length=20, blank=True, default='')
	flat_number = models.CharField(max_length=20, blank=True, default='')
	arrived_at = models.DateTimeField(null=True, blank=True)
	marked_by = models.ForeignKey(
		Signup, on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_visitors'
	)

	class Meta:
		ordering = ['-expected_date', '-expected_time']

	def __str__(self):
		return f'{self.visitor_name} → Flat {self.flat_number}'


# ─────────────────────────────────────────────────────────
#  FEATURE 4 : Amenity Booking
# ─────────────────────────────────────────────────────────
class AmenityBooking(models.Model):
	AMENITY_CHOICES = [
		('community_hall', 'Community Hall'),
		('terrace', 'Terrace'),
		('bbq_area', 'BBQ Area'),
		('swimming_pool', 'Swimming Pool'),
		('conference_room', 'Conference Room'),
	]
	TIME_SLOT_CHOICES = [
		('morning', 'Morning (6 AM – 12 PM)'),
		('afternoon', 'Afternoon (12 PM – 6 PM)'),
		('evening', 'Evening (6 PM – 11 PM)'),
	]
	STATUS_CHOICES = [
		('confirmed', 'Confirmed'),
		('cancelled', 'Cancelled'),
	]

	amenity_name = models.CharField(max_length=30, choices=AMENITY_CHOICES)
	booked_by = models.ForeignKey(Signup, on_delete=models.CASCADE, related_name='bookings')
	booking_date = models.DateField()
	time_slot = models.CharField(max_length=20, choices=TIME_SLOT_CHOICES)
	purpose = models.CharField(max_length=200)
	num_guests = models.IntegerField(default=1)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
	booked_on = models.DateTimeField(auto_now_add=True)
	cancellation_reason = models.TextField(blank=True, default='')

	class Meta:
		ordering = ['-booking_date']

	def __str__(self):
		return f'{self.get_amenity_name_display()} on {self.booking_date}'
