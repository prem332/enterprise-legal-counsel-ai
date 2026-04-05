from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

os.makedirs('tests/data', exist_ok=True)

doc = SimpleDocTemplate(
    'tests/data/Indian_Rental_Agreement_v2.pdf',
    pagesize=A4,
    rightMargin=72, leftMargin=72,
    topMargin=72, bottomMargin=72
)

styles = getSampleStyleSheet()
h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=12, spaceAfter=6)
n = ParagraphStyle('N', parent=styles['Normal'], fontSize=9, spaceAfter=4, leading=14)
story = []

def add(text, style):
    story.append(Paragraph(text, style))

def sp():
    story.append(Spacer(1, 6))

add('RESIDENTIAL RENTAL AGREEMENT', styles['Title'])
add('Tenant-Friendly Agreement as per Indian Contract Act 1872', n)
sp()

add('PARTIES TO THE AGREEMENT', h1)
add('LANDLORD: Mr. Rajesh Kumar Sharma, Flat No. 201, Sunshine Apartments, Banjara Hills, Hyderabad 500034.', n)
add('TENANT: Mr. Arun Venkat Reddy, Plot No. 45, Madhapur, Hyderabad 500081.', n)
sp()

add('PROPERTY DETAILS', h1)
add('Property Address: Flat No. 304, Green Valley Residency, Kondapur, Hyderabad 500084.', n)
add('Property Type: 2BHK Residential Apartment. Carpet Area: 950 square feet.', n)
sp()

add('RENT AND SECURITY DEPOSIT', h1)
add('Monthly Rent: Rs. 18,000 per month.', n)
add('Security Deposit: Rs. 54,000 (3 months rent), refunded within 30 days of vacating after deducting damages.', n)
add('Rent Due Date: On or before 5th of every month.', n)
add('Late Payment Penalty: Rs. 500 per day after 10th of the month.', n)
sp()

add('DURATION', h1)
add('This agreement is valid for 11 months from 1st January 2025 to 30th November 2025. Either party may terminate with 2 months written notice.', n)
sp()

add('TENANT RIGHTS AND BENEFITS', h1)
add('1. Right to Peaceful Enjoyment: The Landlord must give at least 24 hours advance notice before visiting the property except in genuine emergencies.', n)
add('2. Security Deposit Protection: The Landlord MUST return the full deposit of Rs. 54,000 within 30 days of vacating. Deductions only for actual damages beyond normal wear and tear.', n)
add('3. Rent Increase Protection: The Landlord CANNOT increase rent during the 11-month agreement period. Any increase for renewal must not exceed 10 percent of current rent.', n)
add('4. Maintenance and Repairs: The Landlord is responsible for all major structural repairs including roof leakage, electrical wiring, plumbing and painting of walls once per year.', n)
add('5. Guest and Visitor Rights: The Tenant has full right to have family members and guests visit without requiring Landlord permission.', n)
add('6. Work From Home Rights: The Tenant is permitted to work from home including video calls, online meetings and remote work. This does not constitute commercial use.', n)
add('7. Festival Celebration Rights: The Tenant has the right to celebrate all Indian festivals including Diwali, Holi, Eid, Christmas etc. with reasonable noise levels as per local guidelines.', n)
add('8. Cooking and Dietary Freedom: The Tenant has complete freedom regarding food preferences and cooking. The Landlord cannot impose dietary restrictions.', n)
sp()

add('HELPFUL SUGGESTIONS FOR TENANTS', h1)
add('Suggestion 1 - Document Everything: Take photographs and videos of the entire property before moving in. Share with Landlord via WhatsApp to create a digital record. This protects your security deposit when you move out.', n)
add('Suggestion 2 - Pay Rent via Bank Transfer: Always pay rent via bank transfer, UPI or cheque rather than cash. This creates a digital payment trail and protects you if Landlord claims non-payment.', n)
add('Suggestion 3 - Register Your Agreement: As per Registration Act 1908, rental agreements above 11 months must be registered. Registration gives stronger legal protection to both parties.', n)
add('Suggestion 4 - Know Your Rent Control Rights: The Telangana Rent Control Act protects tenants from arbitrary eviction. Approach the Rent Controller Office in Hyderabad if you face illegal eviction threats.', n)
add('Suggestion 5 - Maintain Good Communication: Keep all communication with Landlord in writing via WhatsApp or email. Good communication prevents 90 percent of landlord-tenant disputes.', n)
add('Suggestion 6 - Understand Utility Bills: Electricity and water bills are in the Tenant name. Always check meter reading on move-in day and keep all bill receipts.', n)
add('Suggestion 7 - Security Deposit Recovery Tips: Give 2 months notice in writing, clean property thoroughly, repair any damages, return all keys, clear utility dues, and do joint inspection with Landlord on vacating day.', n)
sp()

add('TENANT OBLIGATIONS', h1)
add('1. Use premises only for residential purposes.', n)
add('2. Do not sublet without written consent from Landlord.', n)
add('3. Maintain property in clean condition.', n)
add('4. Pay electricity and water charges separately.', n)
add('5. Do not make structural changes to the property.', n)
sp()

add('LANDLORD OBLIGATIONS', h1)
add('1. Ensure peaceful possession of property to Tenant.', n)
add('2. Maintain building structure and major repairs.', n)
add('3. Refund security deposit within 30 days of vacating.', n)
add('4. Not enter premises without prior 24-hour notice.', n)
sp()

add('GOVERNING LAW', h1)
add('This agreement is governed by Indian Contract Act 1872, Transfer of Property Act 1882, Telangana Rent Control Act 1960 and Registration Act 1908. Jurisdiction: Hyderabad courts.', n)

doc.build(story)
print('PDF created successfully at tests/data/Indian_Rental_Agreement_v2.pdf')
