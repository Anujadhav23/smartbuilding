from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import date

from .forms import SignupForm, LoginForm, ProfileForm
from .models import Signup, Complaint, Notice, VisitorPass, AmenityBooking
from django.http import Http404


def signup(request):
	"""Render and process the signup form.

	GET: show empty form
	POST: validate and save the signup, then redirect back with a success message
	"""
	if request.method == "POST":
		form = SignupForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Signup successful.")
			return redirect("signup")
	else:
		form = SignupForm()

	return render(request, "signup_page.html", {"form": form})


def login_view(request):
	"""Render and process login by contact number and password.

	On success store `user_id` in session and redirect to dashboard.
	"""
	if request.method == "POST":
		form = LoginForm(request.POST)
		if form.is_valid():
			contact = form.cleaned_data["contact_number"]
			password = form.cleaned_data["password"]

			# Use filter() instead of get() to avoid MultipleObjectsReturned.
			# If multiple accounts exist with the same contact number we pick the most recent
			# and show a warning so the admin can consolidate duplicates later.
			users = Signup.objects.filter(contact_number=contact).order_by("-created_at")
			user = users.first() if users.exists() else None

			if users.count() > 1:
				messages.warning(
					request,
					"Multiple accounts found with this contact number; using the most recent. Please contact admin to consolidate accounts.",
				)

			if user and check_password(password, user.password):
				request.session["user_id"] = user.id
				messages.success(request, "Login successful.")
				return redirect("dashboard")
			else:
				messages.error(request, "Invalid contact number or password.")
	else:
		form = LoginForm()

	return render(request, "login.html", {"form": form})


def logout_view(request):
	"""Clear session and redirect to login."""
	request.session.flush()
	messages.success(request, "You have been logged out.")
	return redirect("login")


def dashboard(request):
	"""Simple dashboard that requires a logged-in user (session-based)."""
	user_id = request.session.get("user_id")
	if not user_id:
		messages.info(request, "Please log in to access the dashboard.")
		return redirect("login")

	try:
		user = Signup.objects.get(id=user_id)
	except Signup.DoesNotExist:
		messages.error(request, "User not found. Please log in again.")
		return redirect("login")

	# Handle profile image upload
	if request.method == "POST":
		form = ProfileForm(request.POST, request.FILES, instance=user)
		if form.is_valid():
			form.save()
			messages.success(request, "Profile updated.")
			return redirect("dashboard")
	else:
		form = ProfileForm(instance=user)

	# If the user clicked the Profile quick-action, show full profile details
	show_profile = False
	if request.GET.get('show_profile') in ('1', 'true', 'True'):
		show_profile = True

	return render(request, "dashboard.html", {"user": user, "form": form, "show_profile": show_profile})




def dashboard_page(request, page):
	"""Render a simple dashboard sub-page for the selected option.

	Available pages: facilities, contact, events, info, parking, apartment, maintenance, gym
	"""
	allowed = {
		'facilities': 'Facilities',
		'contact': 'Contact',
		'events': 'Events',
		'info': 'Info',
		'parking': 'Parking',
		'apartment': 'Apartment',
		'maintenance': 'Maintenance',
		'gym': 'Gym',
		'flat_sales': 'Flat Sales',
	}

	if page not in allowed:
		raise Http404()

	user_id = request.session.get("user_id")
	if not user_id:
		messages.info(request, "Please log in to access this page.")
		return redirect("login")

	user = Signup.objects.filter(id=user_id).first()
	if not user:
		messages.error(request, "User not found. Please log in again.")
		return redirect("login")

	# If user requested the Profile page, render the main dashboard template
	# with the profile visible. This keeps the same layout and upload form.

	title = allowed[page]
	# Placeholder content — can be extended per-page later
	content = f"This is the {title} page. Add details here."

	context = {"user": user, "title": title, "content": content}

	# Add specific data for facilities page
	if page == 'facilities':
		# provide slugs so individual facility pages can be linked
		facilities = [
			{"name": "Water tank capacity", "slug": "water-tank"},
			{"name": "Electricity", "slug": "electricity"},
			{"name": "Gas line", "slug": "gas-line"},
			{"name": "WiFi", "slug": "wifi"},
			{"name": "Plumbing", "slug": "plumbing"},
			{"name": "Sewage treatment", "slug": "sewage-treatment"},
		]
		context['facilities'] = facilities
	# Contact quick numbers
	if page == 'contact':
		contacts = [
			{'name': 'Fire brigade', 'numbers': ['101', '+91-11-23456789']},
			{'name': 'Gas connection', 'numbers': ['1906', '+91-22-12345678']},
			{'name': 'Electricity (faults)', 'numbers': ['1912', '+91-22-87654321']},
			{'name': 'WiFi support', 'numbers': ['1800-123-WIFI', '+91-999000111']},
			{'name': 'Lift service', 'numbers': ['1800-234-LIFT', '+91-888777666']},
			{'name': 'Cleaning', 'numbers': ['+91-700000001']},
			{'name': 'Police (station)', 'numbers': ['100', '+91-11-922222222']},
			{'name': 'Ambulance', 'numbers': ['102', '+91-11-933333333']},
			{'name': 'Plumbing', 'numbers': ['+91-700000002']},
			{'name': 'Security', 'numbers': ['+91-700000003']},
		]
		context['contacts'] = contacts
	# Events list (Indian festivals with ideas)
	if page == 'events':
		events = [
			{"month": "January", "festival": "Makar Sankranti / Pongal / Lohri", "ideas": "Kite flying, traditional sweets sharing"},
			{"month": "March", "festival": "Holi", "ideas": "Organic color celebration, music, sweets"},
			{"month": "March–April", "festival": "Ram Navami / Easter", "ideas": "Cultural prayers, kids’ activities"},
			{"month": "April", "festival": "Gudi Padwa / Ugadi / Baisakhi / Tamil New Year", "ideas": "Traditional dress, decoration, potluck"},
			{"month": "August", "festival": "Raksha Bandhan", "ideas": "Rakhi tying ceremony for kids & elders"},
			{"month": "August", "festival": "Independence Day (15 Aug)", "ideas": "Flag hoisting, patriotic songs, games"},
			{"month": "August–September", "festival": "Janmashtami", "ideas": "Dahi handi, fancy dress (Krishna/Radha)"},
			{"month": "September", "festival": "Ganesh Chaturthi", "ideas": "Idol installation, cultural nights, visarjan"},
			{"month": "October", "festival": "Navratri / Dussehra / Durga Puja", "ideas": "Garba nights, rangoli, pooja, drama"},
			{"month": "October–November", "festival": "Diwali", "ideas": "Diyas lighting, sweets exchange, decoration contest"},
			{"month": "December", "festival": "Christmas", "ideas": "Secret Santa, decoration, carol singing"},
		]
		context['events'] = events
	# Info page details
	if page == 'info':
		info = {
			'society_name': 'Sunshine Residency Co-operative Housing Society',
			'address': 'Plot No. 12, Green Park Road, Wakad, Pune – 411057',
			'registration_no': 'MH/PUNE/CHS/2020/214',
			'total_flats': '80',
			'buildings': 'A, B, C, D',
			'secretary': 'Mr. Rajesh Nair',
			'treasurer': 'Mrs. Priya Patil',
			'chairman': 'Mr. Sanjay Deshmukh',
			'maintenance_due': '10th of every month',
		}
		context['info'] = info
	# Parking details and rules
	if page == 'parking':
		parking_rules = [
			"Each flat is allotted one car and one bike parking slot.",
			"Visitors must park only in designated visitor slots (V1–V10).",
			"Overnight visitor parking requires security approval.",
			"No commercial or outsider parking allowed.",
			"EV charging is allowed only at marked EV slots.",
			"Parking stickers must be displayed on all vehicles.",
			"Any illegal or double parking will attract a fine of ₹500.",
		]
		parking_locations = [
			{"location": "Basement-1", "capacity": "25 Slots", "type": "4-Wheeler", "cctv": "Yes", "lighting": "LED", "remarks": "Reserved for flat owners"},
			{"location": "Basement-2", "capacity": "15 Slots", "type": "4-Wheeler", "cctv": "Yes", "lighting": "LED", "remarks": "Includes EV charging"},
			{"location": "Ground Level", "capacity": "20 Slots", "type": "2-Wheeler & Visitors", "cctv": "Yes", "lighting": "Solar", "remarks": "Open access for guests"},
			{"location": "Open Area (Rear)", "capacity": "10 Slots", "type": "Visitor Parking", "cctv": "Partial", "lighting": "Normal", "remarks": "Used during festivals"},
		]



		ev_chargers = [
			{"point_id": "EV-01", "slot_no": "EV1", "charger_type": "7.2kW Type 2", "status": "Working", "contact": "Society Electrician (Sunil More)"},
			{"point_id": "EV-02", "slot_no": "EV2", "charger_type": "Fast DC 15kW", "status": "Under Maintenance", "contact": "Vendor – GreenCharge Pvt. Ltd."},
		]

		context['parking_locations'] = parking_locations
		context['parking_rules'] = parking_rules
		context['ev_chargers'] = ev_chargers

	# Apartment directory
	if page == 'apartment':
		apartments = [
			{"flat_no": "A-101", "name": "Rajesh Nair", "role": "Chairman", "contact": "9876543210", "email": "rajesh.nair@example.com", "members": 4, "vehicle": "MH12AB1234"},
			{"flat_no": "A-202", "name": "Priya Patil", "role": "Treasurer", "contact": "9865321478", "email": "priya.patil@example.com", "members": 3, "vehicle": "MH12CD5678"},
			{"flat_no": "B-303", "name": "Anil Joshi", "role": "Owner", "contact": "9823456712", "email": "anil.joshi@example.com", "members": 5, "vehicle": "MH12EF8910"},
			{"flat_no": "C-102", "name": "Sneha Kulkarni", "role": "Tenant", "contact": "9897654321", "email": "sneha.kulkarni@example.com", "members": 2, "vehicle": "MH12GH2345"},
			{"flat_no": "D-401", "name": "Rohit Sharma", "role": "Owner", "contact": "9776543211", "email": "rohit.sharma@example.com", "members": 3, "vehicle": "MH12IJ8765"},
			{"flat_no": "B-201", "name": "Meena Gupta", "role": "Secretary", "contact": "9812345678", "email": "meena.gupta@example.com", "members": 4, "vehicle": "MH12KL4321"},
			{"flat_no": "A-303", "name": "Vishal Deshmukh", "role": "Owner", "contact": "9856743210", "email": "vishal.deshmukh@example.com", "members": 3, "vehicle": "MH12MN6789"},
			{"flat_no": "C-204", "name": "Kavita Singh", "role": "Tenant", "contact": "9845123987", "email": "kavita.singh@example.com", "members": 2, "vehicle": "MH12OP4567"},
			{"flat_no": "D-101", "name": "Suresh Menon", "role": "Owner", "contact": "9834678910", "email": "suresh.menon@example.com", "members": 5, "vehicle": "MH12QR7891"},
			{"flat_no": "B-402", "name": "Alka Verma", "role": "Tenant", "contact": "9801234567", "email": "alka.verma@example.com", "members": 3, "vehicle": "MH12ST2348"},
			{"flat_no": "E-303", "name": "Deepak Jadhav", "role": "Owner", "contact": "9822198765", "email": "deepak.jadhav@example.com", "members": 4, "vehicle": "MH12UV6754"},
			{"flat_no": "E-102", "name": "Reema Bhattacharjee", "role": "Owner", "contact": "9819988776", "email": "reema.bhatt@example.com", "members": 3, "vehicle": "MH12WX0987"},
			{"flat_no": "A-104", "name": "Tushar Mehta", "role": "Tenant", "contact": "9871234569", "email": "tushar.mehta@example.com", "members": 2, "vehicle": "MH12YZ5643"},
			{"flat_no": "C-305", "name": "Neha Bansal", "role": "Owner", "contact": "9865321201", "email": "neha.bansal@example.com", "members": 4, "vehicle": "MH12AB9988"},
			{"flat_no": "D-204", "name": "Sunil Pawar", "role": "Owner", "contact": "9856012345", "email": "sunil.pawar@example.com", "members": 3, "vehicle": "MH12CD3421"},
		]
		context['apartments'] = apartments

	# Maintenance info
	if page == 'maintenance':
		maintenance = {
			'standard_amount': '₹3,000 / flat / quarter',
			'due_date': '5th of the starting month of each quarter',
			'late_fee': '₹100/week after due date',
			'accepted_modes': ['UPI', 'Bank Transfer', 'Cash', 'Cheque'],
			'contact': 'Society Treasurer – Priya Patil (9865321478)'
		}
		context['maintenance'] = maintenance

	# Gym information and members
	if page == 'gym':
		gym = {
			'gym_name': 'SmartFit Club – GreenView Society',
			'location': 'Clubhouse – 1st Floor, Block B',
			'timings': '6:00 AM – 10:00 AM, 5:00 PM – 9:00 PM',
			'trainer_name': 'Mr. Rohan Deshmukh',
			'trainer_contact': '9876543215',
			'trainer_availability': 'Morning (6 AM–10 AM), Evening (6 PM–9 PM)',
			'members_enrolled': '85 Active Members',
			'membership_fee': '₹500 / month or ₹1,200 / quarter',
			'equipment': 'Treadmills (4), Cross Trainers (2), Dumbbells (2–30kg), Leg Press, Bench Press, Yoga Mats, Cycling Machines (3)',
			'facilities': 'Locker Room, Water Dispenser, Changing Room, CCTV Security',
			'rules': [
				'Proper gym attire required',
				'Carry towel & water bottle',
				'Equipment to be wiped after use',
				'No loud music',
				'Entry restricted to members only',
			],
			'emergency_contact': 'Society Security Desk – 9999988888',
			'maintenance_day': 'Every Monday (Morning – Closed for cleaning)',
		}

		gym_members = [
			{"id": "GYM001", "name": "Sneha Kulkarni", "flat": "C-102", "type": "Quarterly", "start": "2025-10-01", "end": "2025-12-31", "mode": "UPI", "fee": 1200, "status": "Active"},
			{"id": "GYM002", "name": "Rajesh Nair", "flat": "A-101", "type": "Monthly", "start": "2025-11-01", "end": "2025-11-30", "mode": "Cash", "fee": 500, "status": "Active"},
			{"id": "GYM003", "name": "Rohit Sharma", "flat": "D-401", "type": "Monthly", "start": "2025-10-10", "end": "2025-11-09", "mode": "UPI", "fee": 500, "status": "Expiring Soon"},
			{"id": "GYM004", "name": "Priya Patil", "flat": "A-202", "type": "Quarterly", "start": "2025-09-01", "end": "2025-11-30", "mode": "Bank Transfer", "fee": 1200, "status": "Active"},
			{"id": "GYM005", "name": "Deepak Jadhav", "flat": "E-303", "type": "Monthly", "start": "2025-11-01", "end": "2025-11-30", "mode": "UPI", "fee": 500, "status": "Active"},
		]

		context['gym'] = gym
		context['gym_members'] = gym_members

	# Flat sales listings (sample data)
	if page == 'flat_sales':
		flats_for_sale = [
			{"flat_no": "A-105", "price": "₹12,50,000", "area": "950 sqft", "contact": "9876543210", "status": "Available"},
			{"flat_no": "B-204", "price": "₹15,00,000", "area": "1100 sqft", "contact": "9812345678", "status": "Under Negotiation"},
			{"flat_no": "C-301", "price": "₹10,75,000", "area": "820 sqft", "contact": "9823456712", "status": "Available"},
			{"flat_no": "D-402", "price": "₹18,20,000", "area": "1300 sqft", "contact": "9856743210", "status": "Reserved"},
		]
		context['flats_for_sale'] = flats_for_sale

	return render(request, "dashboard_option.html", context)


def facility_detail(request, facility):
	"""Show detail/report form for a specific facility (slug).

	For 'water-tank' show the requested four options. On POST, accept the values and show a success message.
	"""
	# simple mapping for facility display names
	names = {
		'water-tank': 'Water tank capacity',
		'electricity': 'Electricity',
		'gas-line': 'Gas line',
		'wifi': 'WiFi',
		'plumbing': 'Plumbing',
		'sewage-treatment': 'Sewage treatment',
	}

	if facility not in names:
		raise Http404()

	facility_name = names[facility]

	if request.method == 'POST':
		# collect submitted values (no DB persistence implemented)
		report = {
			'filter_water': request.POST.get('filter_water'),
			'hot_water': request.POST.get('hot_water'),
			'flushing': request.POST.get('flushing'),
			'regular_water': request.POST.get('regular_water'),
		}
		# Here you could save the report to a model or send an email. For now, we show a confirmation.
		messages.success(request, f"Report submitted for {facility_name}.")
		# Optionally include submitted values in a message (short)
		messages.info(request, f"Values: filter={report['filter_water'] or 'N/A'}, hot={report['hot_water'] or 'N/A'}, flushing={report['flushing'] or 'N/A'}, regular={report['regular_water'] or 'N/A'}")
		return redirect('facility_detail', facility=facility)

	# For non-POST, provide demo data per facility so template can render appropriate view
	context = {'facility_name': facility_name}

	if facility == 'water-tank':
		# Provide static dummy defaults for the three percent fields and flushing option
		context.update({
			'filter_default': 70,
			'hot_default': 40,
			'regular_default': 60,
			'flushing_default': 'ok',
		})

	elif facility == 'electricity':
		# demo electricity billing records
		context['electricity_records'] = [
			{"flat_no": "A-101", "block": "A", "owner": "Rohan Deshmukh", "units": 245, "meter": "MTR-001", "month": "Oct-2025", "prev": 1820, "curr": 2065, "bill": "1,470", "status": "Paid", "payment_date": "2025-11-02", "connection_type": "Residential"},
			{"flat_no": "A-102", "block": "A", "owner": "Sneha Patil", "units": 310, "meter": "MTR-002", "month": "Oct-2025", "prev": 2340, "curr": 2650, "bill": "1,860", "status": "Pending", "payment_date": "—", "connection_type": "Residential"},
			{"flat_no": "A-103", "block": "A", "owner": "Amit Joshi", "units": 185, "meter": "MTR-003", "month": "Oct-2025", "prev": 950, "curr": 1135, "bill": "1,110", "status": "Paid", "payment_date": "2025-11-04", "connection_type": "Residential"},
			{"flat_no": "B-201", "block": "B", "owner": "Priya Mehta", "units": 480, "meter": "MTR-004", "month": "Oct-2025", "prev": 4210, "curr": 4690, "bill": "2,640", "status": "Paid", "payment_date": "2025-11-03", "connection_type": "Residential"},
			{"flat_no": "B-202", "block": "B", "owner": "Ankit Sharma", "units": 120, "meter": "MTR-005", "month": "Oct-2025", "prev": 1200, "curr": 1320, "bill": "720", "status": "Pending", "payment_date": "—", "connection_type": "Residential"},
			{"flat_no": "C-301", "block": "C", "owner": "Neha Kulkarni", "units": 520, "meter": "MTR-006", "month": "Oct-2025", "prev": 5100, "curr": 5620, "bill": "2,880", "status": "Paid", "payment_date": "2025-11-05", "connection_type": "Residential"},
			{"flat_no": "C-302", "block": "C", "owner": "Rajesh Singh", "units": 670, "meter": "MTR-007", "month": "Oct-2025", "prev": 3050, "curr": 3720, "bill": "3,690", "status": "Pending", "payment_date": "—", "connection_type": "Residential"},
			{"flat_no": "C-303", "block": "C", "owner": "Aparna Nair", "units": 95, "meter": "MTR-008", "month": "Oct-2025", "prev": 880, "curr": 975, "bill": "570", "status": "Paid", "payment_date": "2025-11-01", "connection_type": "Residential"},
			{"flat_no": "Shop-1", "block": "D", "owner": "Kiran Traders", "units": 910, "meter": "MTR-009", "month": "Oct-2025", "prev": 11000, "curr": 11910, "bill": "5,460", "status": "Paid", "payment_date": "2025-11-03", "connection_type": "Commercial"},
			{"flat_no": "Shop-2", "block": "D", "owner": "Green Café", "units": 1050, "meter": "MTR-010", "month": "Oct-2025", "prev": 5200, "curr": 6250, "bill": "6,300", "status": "Pending", "payment_date": "—", "connection_type": "Commercial"},
		]

	elif facility == 'gas-line':
		context['gas_records'] = [
			{"flat_no": "A-101", "block": "A", "owner": "Rohan Deshmukh", "elec_units": 245, "elec_bill": "1,470", "gas_units": 22, "gas_bill": 660, "total": "2,130", "month": "Oct-2025", "status": "Paid", "payment_date": "2025-11-02", "meter": "MTR-001", "gas_id": "GAS-001"},
			{"flat_no": "A-102", "block": "A", "owner": "Sneha Patil", "elec_units": 310, "elec_bill": "1,860", "gas_units": 28, "gas_bill": 840, "total": "2,700", "month": "Oct-2025", "status": "Pending", "payment_date": "—", "meter": "MTR-002", "gas_id": "GAS-002"},
			{"flat_no": "A-103", "block": "A", "owner": "Amit Joshi", "elec_units": 185, "elec_bill": "1,110", "gas_units": 17, "gas_bill": 510, "total": "1,620", "month": "Oct-2025", "status": "Paid", "payment_date": "2025-11-04", "meter": "MTR-003", "gas_id": "GAS-003"},
			{"flat_no": "B-201", "block": "B", "owner": "Priya Mehta", "elec_units": 480, "elec_bill": "2,640", "gas_units": 34, "gas_bill": 1020, "total": "3,660", "month": "Oct-2025", "status": "Paid", "payment_date": "2025-11-03", "meter": "MTR-004", "gas_id": "GAS-004"},
			{"flat_no": "B-202", "block": "B", "owner": "Ankit Sharma", "elec_units": 120, "elec_bill": "720", "gas_units": 12, "gas_bill": 360, "total": "1,080", "month": "Oct-2025", "status": "Pending", "payment_date": "—", "meter": "MTR-005", "gas_id": "GAS-005"},
			{"flat_no": "C-301", "block": "C", "owner": "Neha Kulkarni", "elec_units": 520, "elec_bill": "2,880", "gas_units": 36, "gas_bill": 1080, "total": "3,960", "month": "Oct-2025", "status": "Paid", "payment_date": "2025-11-05", "meter": "MTR-006", "gas_id": "GAS-006"},
			{"flat_no": "C-302", "block": "C", "owner": "Rajesh Singh", "elec_units": 670, "elec_bill": "3,690", "gas_units": 42, "gas_bill": 1260, "total": "4,950", "month": "Oct-2025", "status": "Pending", "payment_date": "—", "meter": "MTR-007", "gas_id": "GAS-007"},
			{"flat_no": "C-303", "block": "C", "owner": "Aparna Nair", "elec_units": 95, "elec_bill": "570", "gas_units": 10, "gas_bill": 300, "total": "870", "month": "Oct-2025", "status": "Paid", "payment_date": "2025-11-01", "meter": "MTR-008", "gas_id": "GAS-008"},
			{"flat_no": "Shop-1", "block": "D", "owner": "Kiran Traders", "elec_units": 910, "elec_bill": "5,460", "gas_units": 50, "gas_bill": 1500, "total": "6,960", "month": "Oct-2025", "status": "Paid", "payment_date": "2025-11-03", "meter": "MTR-009", "gas_id": "GAS-009"},
			{"flat_no": "Shop-2", "block": "D", "owner": "Green Café", "elec_units": 1050, "elec_bill": "6,300", "gas_units": 58, "gas_bill": 1740, "total": "8,040", "month": "Oct-2025", "status": "Pending", "payment_date": "—", "meter": "MTR-010", "gas_id": "GAS-010"},
		]

	elif facility == 'wifi':
		context['wifi_records'] = [
			{"flat_no": "A-101", "block": "A", "owner": "Rohan Deshmukh", "plan": "Silver Plan", "speed": 100, "used_gb": 220, "limit_gb": 250, "bill": "799", "status": "Paid", "payment_date": "2025-11-02", "provider": "Airtel Fiber", "router": "WIFI-001", "month": "Oct-2025"},
			{"flat_no": "A-102", "block": "A", "owner": "Sneha Patil", "plan": "Gold Plan", "speed": 200, "used_gb": 340, "limit_gb": 500, "bill": "999", "status": "Pending", "payment_date": "—", "provider": "JioFiber", "router": "WIFI-002", "month": "Oct-2025"},
			{"flat_no": "A-103", "block": "A", "owner": "Amit Joshi", "plan": "Basic Plan", "speed": 50, "used_gb": 130, "limit_gb": 150, "bill": "499", "status": "Paid", "payment_date": "2025-11-03", "provider": "ACT Broadband", "router": "WIFI-003", "month": "Oct-2025"},
			{"flat_no": "B-201", "block": "B", "owner": "Priya Mehta", "plan": "Premium Plan", "speed": 300, "used_gb": 460, "limit_gb": 600, "bill": "1,299", "status": "Paid", "payment_date": "2025-11-05", "provider": "Airtel Fiber", "router": "WIFI-004", "month": "Oct-2025"},
			{"flat_no": "B-202", "block": "B", "owner": "Ankit Sharma", "plan": "Basic Plan", "speed": 50, "used_gb": 120, "limit_gb": 150, "bill": "499", "status": "Pending", "payment_date": "—", "provider": "Hathway", "router": "WIFI-005", "month": "Oct-2025"},
			{"flat_no": "C-301", "block": "C", "owner": "Neha Kulkarni", "plan": "Silver Plan", "speed": 100, "used_gb": 240, "limit_gb": 250, "bill": "799", "status": "Paid", "payment_date": "2025-11-04", "provider": "JioFiber", "router": "WIFI-006", "month": "Oct-2025"},
			{"flat_no": "C-302", "block": "C", "owner": "Rajesh Singh", "plan": "Gold Plan", "speed": 200, "used_gb": 410, "limit_gb": 500, "bill": "999", "status": "Pending", "payment_date": "—", "provider": "ACT Broadband", "router": "WIFI-007", "month": "Oct-2025"},
			{"flat_no": "C-303", "block": "C", "owner": "Aparna Nair", "plan": "Basic Plan", "speed": 50, "used_gb": 100, "limit_gb": 150, "bill": "499", "status": "Paid", "payment_date": "2025-11-01", "provider": "Airtel Fiber", "router": "WIFI-008", "month": "Oct-2025"},
			{"flat_no": "Shop-1", "block": "D", "owner": "Kiran Traders", "plan": "Business Pro", "speed": 500, "used_gb": 700, "limit_gb": 1000, "bill": "1,999", "status": "Paid", "payment_date": "2025-11-03", "provider": "Tata Play Fiber", "router": "WIFI-009", "month": "Oct-2025"},
			{"flat_no": "Shop-2", "block": "D", "owner": "Green Café", "plan": "Business Pro", "speed": 500, "used_gb": 850, "limit_gb": 1000, "bill": "1,999", "status": "Pending", "payment_date": "—", "provider": "ACT Broadband", "router": "WIFI-010", "month": "Oct-2025"},
		]

	elif facility == 'plumbing':
		context['plumbing_records'] = [
			{"flat_no": "A-101", "block": "A", "owner": "Rohan Deshmukh", "issue": "Leaky tap", "reported": "2025-11-01", "status": "Resolved", "assigned_to": "Plumber-1"},
			{"flat_no": "B-201", "block": "B", "owner": "Priya Mehta", "issue": "Clogged drain", "reported": "2025-11-03", "status": "In Progress", "assigned_to": "Plumber-2"},
			{"flat_no": "C-301", "block": "C", "owner": "Neha Kulkarni", "issue": "Low pressure", "reported": "2025-10-29", "status": "Scheduled", "assigned_to": "Plumber-3"},
		]

	elif facility == 'sewage-treatment':
		context['sewage_records'] = [
			{"plant": "STP-1", "status": "Working", "last_maintenance": "2025-10-15", "ph_level": 7.2, "effluent_quality": "Pass", "remarks": "Normal"},
			{"plant": "STP-2", "status": "Under Maintenance", "last_maintenance": "2025-09-30", "ph_level": 6.9, "effluent_quality": "Monitoring", "remarks": "Aeration issue"},
		]

	return render(request, 'facility_detail.html', context)


# ══════════════════════════════════════════════════════════
#  FEATURE 1 : Complaint Management
# ══════════════════════════════════════════════════════════

def complaints(request):
	"""Submit a new complaint and view own complaint history."""
	user_id = request.session.get("user_id")
	if not user_id:
		messages.info(request, "Please log in first.")
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user:
		return redirect("login")

	if request.method == "POST":
		category = request.POST.get("category", "")
		description = request.POST.get("description", "").strip()
		if category and description:
			Complaint.objects.create(resident=user, category=category, description=description)
			messages.success(request, "Complaint submitted successfully! A ticket has been created.")
			return redirect("complaints")
		else:
			messages.error(request, "Please fill in all required fields.")

	my_complaints = Complaint.objects.filter(resident=user)
	return render(request, "complaints.html", {
		"user": user,
		"complaints": my_complaints,
		"categories": Complaint.CATEGORY_CHOICES,
	})


def all_complaints(request):
	"""Secretary-only view: all complaints across the society."""
	user_id = request.session.get("user_id")
	if not user_id:
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user or user.role != Signup.ROLE_SECRETARY:
		messages.error(request, "Access denied. Secretary only.")
		return redirect("dashboard")

	status_filter = request.GET.get("status", "")
	qs = Complaint.objects.select_related('resident').all()
	if status_filter:
		qs = qs.filter(status=status_filter)

	return render(request, "all_complaints.html", {
		"user": user,
		"complaints": qs,
		"status_filter": status_filter,
	})


def update_complaint(request, complaint_id):
	"""Secretary-only: update complaint status and add remarks."""
	user_id = request.session.get("user_id")
	if not user_id:
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user or user.role != Signup.ROLE_SECRETARY:
		messages.error(request, "Access denied.")
		return redirect("dashboard")

	complaint = Complaint.objects.filter(id=complaint_id).first()
	if not complaint:
		raise Http404

	if request.method == "POST":
		new_status = request.POST.get("status", "")
		remarks = request.POST.get("secretary_remarks", "")
		if new_status in dict(Complaint.STATUS_CHOICES):
			complaint.status = new_status
			complaint.secretary_remarks = remarks
			if new_status == 'resolved' and not complaint.date_resolved:
				complaint.date_resolved = timezone.now()
			complaint.save()
			messages.success(request, f"Complaint {complaint.ticket_number} updated.")

	return redirect("all_complaints")


# ══════════════════════════════════════════════════════════
#  FEATURE 2 : Digital Notice Board
# ══════════════════════════════════════════════════════════

def notice_board(request):
	"""Display all active notices to any logged-in user."""
	user_id = request.session.get("user_id")
	if not user_id:
		messages.info(request, "Please log in first.")
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user:
		return redirect("login")

	notices = Notice.objects.filter(is_active=True)
	return render(request, "notice_board.html", {"user": user, "notices": notices})


def post_notice(request):
	"""Secretary-only: create a new notice."""
	user_id = request.session.get("user_id")
	if not user_id:
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user or user.role != Signup.ROLE_SECRETARY:
		messages.error(request, "Access denied. Secretary only.")
		return redirect("dashboard")

	if request.method == "POST":
		title = request.POST.get("title", "").strip()
		content = request.POST.get("content", "").strip()
		category = request.POST.get("category", "general")
		is_urgent = request.POST.get("is_urgent") == "on"
		if title and content:
			Notice.objects.create(
				title=title, content=content, category=category,
				is_urgent=is_urgent, posted_by=user,
			)
			messages.success(request, "Notice posted successfully!")
			return redirect("notice_board")
		else:
			messages.error(request, "Title and content are required.")

	return render(request, "post_notice.html", {
		"user": user, "categories": Notice.CATEGORY_CHOICES,
	})


def delete_notice(request, notice_id):
	"""Secretary-only: soft-delete a notice."""
	user_id = request.session.get("user_id")
	if not user_id:
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user or user.role != Signup.ROLE_SECRETARY:
		messages.error(request, "Access denied.")
		return redirect("dashboard")

	notice = Notice.objects.filter(id=notice_id).first()
	if not notice:
		raise Http404
	notice.is_active = False
	notice.save()
	messages.success(request, f'Notice "{notice.title}" deleted.')
	return redirect("notice_board")


# ══════════════════════════════════════════════════════════
#  FEATURE 3 : Visitor Pre-Approval
# ══════════════════════════════════════════════════════════

def visitor_pass(request):
	"""Flat Owner: pre-approve a visitor and view visitor list."""
	user_id = request.session.get("user_id")
	if not user_id:
		messages.info(request, "Please log in first.")
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user:
		return redirect("login")

	# Auto-expire past approved visitors
	VisitorPass.objects.filter(status='approved', expected_date__lt=date.today()).update(status='expired')

	if request.method == "POST" and user.role == Signup.ROLE_FLAT_OWNER:
		vname = request.POST.get("visitor_name", "").strip()
		vcontact = request.POST.get("visitor_contact", "").strip()
		purpose = request.POST.get("purpose", "").strip()
		exp_date = request.POST.get("expected_date", "")
		exp_time = request.POST.get("expected_time", "")
		vehicle = request.POST.get("vehicle_number", "").strip()
		flat_num = request.POST.get("flat_number", "").strip()

		if vname and vcontact and purpose and exp_date and exp_time:
			VisitorPass.objects.create(
				flat_owner=user, visitor_name=vname, visitor_contact=vcontact,
				purpose=purpose, expected_date=exp_date, expected_time=exp_time,
				vehicle_number=vehicle, flat_number=flat_num,
			)
			messages.success(request, f"Visitor '{vname}' pre-approved!")
			return redirect("visitor_pass")
		else:
			messages.error(request, "Please fill in all required fields.")

	if user.role == Signup.ROLE_SECRETARY:
		visitors = VisitorPass.objects.select_related('flat_owner').all()
	else:
		visitors = VisitorPass.objects.filter(flat_owner=user)

	return render(request, "visitor_pass.html", {"user": user, "visitors": visitors})


def cancel_visitor(request, visitor_id):
	"""Flat Owner cancels a pre-approved visitor."""
	user_id = request.session.get("user_id")
	if not user_id:
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user:
		return redirect("login")

	visitor = VisitorPass.objects.filter(id=visitor_id, flat_owner=user).first()
	if not visitor:
		raise Http404
	if visitor.status == 'approved':
		visitor.status = 'cancelled'
		visitor.save()
		messages.success(request, f"Visitor '{visitor.visitor_name}' cancelled.")
	else:
		messages.warning(request, "This visitor pass cannot be cancelled.")
	return redirect("visitor_pass")


def security_visitors(request):
	"""Security view: today's pre-approved visitors."""
	user_id = request.session.get("user_id")
	if not user_id:
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user or user.role != Signup.ROLE_SECURITY:
		messages.error(request, "Access denied. Security only.")
		return redirect("dashboard")

	VisitorPass.objects.filter(status='approved', expected_date__lt=date.today()).update(status='expired')
	today_visitors = VisitorPass.objects.filter(
		expected_date=date.today(), status__in=['approved', 'arrived'],
	).select_related('flat_owner')

	return render(request, "security_visitors.html", {
		"user": user, "visitors": today_visitors, "today": date.today(),
	})


def mark_arrived(request, visitor_id):
	"""Security marks a visitor as Arrived."""
	user_id = request.session.get("user_id")
	if not user_id:
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user or user.role != Signup.ROLE_SECURITY:
		messages.error(request, "Access denied.")
		return redirect("dashboard")

	visitor = VisitorPass.objects.filter(id=visitor_id, status='approved').first()
	if not visitor:
		raise Http404
	visitor.status = 'arrived'
	visitor.arrived_at = timezone.now()
	visitor.marked_by = user
	visitor.save()
	messages.success(request, f"Visitor '{visitor.visitor_name}' marked as arrived.")
	return redirect("security_visitors")


# ══════════════════════════════════════════════════════════
#  FEATURE 4 : Amenity Booking
# ══════════════════════════════════════════════════════════

def book_amenity(request):
	"""Book an amenity and view own bookings."""
	user_id = request.session.get("user_id")
	if not user_id:
		messages.info(request, "Please log in first.")
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user:
		return redirect("login")

	if request.method == "POST":
		amenity = request.POST.get("amenity_name", "")
		booking_date_str = request.POST.get("booking_date", "")
		time_slot = request.POST.get("time_slot", "")
		purpose = request.POST.get("purpose", "").strip()
		num_guests = request.POST.get("num_guests", "1")

		if amenity and booking_date_str and time_slot and purpose:
			conflict = AmenityBooking.objects.filter(
				amenity_name=amenity, booking_date=booking_date_str,
				time_slot=time_slot, status='confirmed',
			).exists()
			if conflict:
				messages.error(request, "This slot is already booked. Please choose another.")
			else:
				try:
					guests = int(num_guests)
				except ValueError:
					guests = 1
				AmenityBooking.objects.create(
					amenity_name=amenity, booked_by=user, booking_date=booking_date_str,
					time_slot=time_slot, purpose=purpose, num_guests=guests,
				)
				messages.success(request, "Amenity booked successfully!")
				return redirect("book_amenity")
		else:
			messages.error(request, "Please fill in all required fields.")

	today = date.today()
	upcoming = AmenityBooking.objects.filter(booked_by=user, booking_date__gte=today, status='confirmed').order_by('booking_date')
	past = AmenityBooking.objects.filter(booked_by=user).exclude(booking_date__gte=today, status='confirmed')

	return render(request, "amenity_booking.html", {
		"user": user, "upcoming_bookings": upcoming, "past_bookings": past,
		"amenities": AmenityBooking.AMENITY_CHOICES,
		"time_slots": AmenityBooking.TIME_SLOT_CHOICES,
		"today": today.isoformat(),
	})


def cancel_booking(request, booking_id):
	"""Cancel an upcoming amenity booking."""
	user_id = request.session.get("user_id")
	if not user_id:
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user:
		return redirect("login")

	booking = AmenityBooking.objects.filter(id=booking_id, booked_by=user).first()
	if not booking:
		raise Http404
	if booking.booking_date < date.today():
		messages.error(request, "Cannot cancel a past booking.")
	elif booking.status == 'cancelled':
		messages.warning(request, "Already cancelled.")
	else:
		booking.status = 'cancelled'
		booking.cancellation_reason = request.POST.get("cancellation_reason", "") if request.method == "POST" else ""
		booking.save()
		messages.success(request, "Booking cancelled.")
	return redirect("book_amenity")


def all_bookings(request):
	"""Secretary-only: view all amenity bookings."""
	user_id = request.session.get("user_id")
	if not user_id:
		return redirect("login")
	user = Signup.objects.filter(id=user_id).first()
	if not user or user.role != Signup.ROLE_SECRETARY:
		messages.error(request, "Access denied. Secretary only.")
		return redirect("dashboard")

	amenity_filter = request.GET.get("amenity", "")
	qs = AmenityBooking.objects.select_related('booked_by').all()
	if amenity_filter:
		qs = qs.filter(amenity_name=amenity_filter)

	return render(request, "all_bookings.html", {
		"user": user, "bookings": qs,
		"amenity_filter": amenity_filter,
		"amenities": AmenityBooking.AMENITY_CHOICES,
	})
