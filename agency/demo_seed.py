#!/usr/bin/env python3
"""
Demo seeder — populates the pipeline with 6 realistic leads without
needing any API keys. Each lead includes a full diagnosis, 3 HTML
landing pages, a video script, and a QA review.

Run:  python demo_seed.py
Then: python -m agents.mobile.app   (open http://localhost:5001)
  or: python approve.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.state import StateManager

state = StateManager()

# ── Demo businesses ────────────────────────────────────────────────────────
LEADS = [
    {
        "id": "a1b2c3d4",
        "business": {
            "name": "Rosa's Mexican Grill",
            "type": "restaurant",
            "city": "Miami, FL",
            "address": "2847 SW 8th St, Miami, FL 33135",
            "phone": "+1-305-555-0191",
            "website": None,
            "rating": 4.6,
            "reviews": 342,
            "place_id": "demo_001",
            "hours": "Mon-Sun 11am–10pm",
            "categories": ["mexican_restaurant", "restaurant"],
        },
        "website_check": {"has_website": False, "is_outdated": True, "oldness_score": 100, "issues": ["No website"]},
        "diagnosis": {
            "priority_score": 9,
            "opportunity_summary": "342 five-star reviews with zero online presence — every competitor with a website is stealing their customers.",
            "pain_points": ["Invisible on Google search", "Can't take online orders or reservations", "Losing customers to restaurants with websites"],
            "recommended_features": ["Online menu with photos", "Reservation booking", "Google Maps embed", "Instagram feed", "Order now button"],
            "message": "Hi Rosa! I found your restaurant on Google Maps — 342 reviews and a 4.6 rating is honestly incredible. The only thing missing is a website, which means you're losing customers to competitors every single day. I'd love to build you a free mockup this week — beautiful, mobile-friendly, ready in 48 hours for $400 flat. Want to take a look?",
        },
        "video": {"provider": "demo", "status": "script_only", "script": "342 five-star reviews. Rosa's Mexican Grill is the real deal — they just don't have a website yet. We fix that in 48 hours for $400. Let's make them unfindable no more."},
        "check": {
            "total_score": 91,
            "breakdown": {"personalization": 24, "value_proposition": 23, "tone": 22, "cta": 22},
            "issues": [],
            "approved": True,
        },
    },
    {
        "id": "b2c3d4e5",
        "business": {
            "name": "Mike's Auto Repair",
            "type": "auto_repair",
            "city": "Houston, TX",
            "address": "5512 Westheimer Rd, Houston, TX 77056",
            "phone": "+1-713-555-0144",
            "website": "http://mikesauto2009.weebly.com",
            "rating": 4.3,
            "reviews": 187,
            "place_id": "demo_002",
            "hours": "Mon-Fri 8am–6pm; Sat 9am–4pm",
            "categories": ["car_repair", "automotive"],
        },
        "website_check": {"has_website": True, "is_outdated": True, "oldness_score": 78, "issues": ["No HTTPS", "Not mobile-responsive", "Copyright year: 2009", "Old jQuery 1.4"]},
        "diagnosis": {
            "priority_score": 8,
            "opportunity_summary": "187 reviews and a 14-year-old Weebly site that looks broken on mobile — customers are bouncing before they call.",
            "pain_points": ["Website is broken on iPhone/Android", "No HTTPS — browsers show 'Not Secure' warning", "Customers can't book or request quotes online"],
            "recommended_features": ["Mobile-first redesign", "Online quote request form", "Services + pricing page", "Customer reviews showcase", "Click-to-call button"],
            "message": "Hey Mike! Your shop has 187 reviews and a solid 4.3 rating — but your website hasn't been updated since 2009 and doesn't work on phones. I specialize in rebuilding auto shop sites that actually bring in calls. Free mockup, $400 done in 48 hours. Worth a look?",
        },
        "video": {"provider": "demo", "status": "script_only", "script": "4.3 stars. 187 happy customers. And a website from 2009 that's chasing them away. Mike's Auto Repair deserves better. $400, 48 hours, done right."},
        "check": {
            "total_score": 87,
            "breakdown": {"personalization": 22, "value_proposition": 23, "tone": 21, "cta": 21},
            "issues": [],
            "approved": True,
        },
    },
    {
        "id": "c3d4e5f6",
        "business": {
            "name": "Bella Nails & Spa",
            "type": "salon",
            "city": "Phoenix, AZ",
            "address": "1740 E Camelback Rd, Phoenix, AZ 85016",
            "phone": "+1-602-555-0173",
            "website": None,
            "rating": 4.7,
            "reviews": 523,
            "place_id": "demo_003",
            "hours": "Mon-Sat 9am–8pm; Sun 10am–6pm",
            "categories": ["nail_salon", "spa", "beauty_salon"],
        },
        "website_check": {"has_website": False, "is_outdated": True, "oldness_score": 100, "issues": ["No website"]},
        "diagnosis": {
            "priority_score": 10,
            "opportunity_summary": "523 reviews at 4.7 stars — this is the busiest nail salon in the area with zero web presence. Pure opportunity.",
            "pain_points": ["Can't book appointments online — losing walk-in revenue", "No way to show their nail art gallery online", "Competitors with websites are capturing Google searches"],
            "recommended_features": ["Online booking calendar", "Photo gallery / portfolio", "Services & pricing menu", "Gift card section", "Instagram feed integration"],
            "message": "Hi! I found Bella Nails on Google and wow — 523 reviews and a 4.7 is almost unheard of. The only thing holding you back is having no website, which means anyone who Googles 'nail salon Phoenix' can't find you. I'd love to build a beautiful site with online booking — free mockup first, $400 total, 48-hour turnaround. Sound good?",
        },
        "video": {"provider": "demo", "status": "script_only", "script": "523 reviews. 4.7 stars. Bella Nails is Phoenix's best-kept secret — because they have no website. We build stunning nail salon sites with online booking. $400, 48 hours. Let's fix this."},
        "check": {
            "total_score": 94,
            "breakdown": {"personalization": 24, "value_proposition": 24, "tone": 23, "cta": 23},
            "issues": [],
            "approved": True,
        },
    },
    {
        "id": "d4e5f6g7",
        "business": {
            "name": "Dr. Sarah Chen, DDS",
            "type": "dentist",
            "city": "Dallas, TX",
            "address": "3900 Lemmon Ave, Dallas, TX 75219",
            "phone": "+1-214-555-0122",
            "website": "http://sarahchendds.com",
            "rating": 4.8,
            "reviews": 276,
            "place_id": "demo_004",
            "hours": "Mon-Thu 8am–5pm; Fri 8am–2pm",
            "categories": ["dentist", "health"],
        },
        "website_check": {"has_website": True, "is_outdated": True, "oldness_score": 65, "issues": ["Not mobile-responsive", "Copyright year: 2016", "Missing Open Graph tags", "No HTTPS"]},
        "diagnosis": {
            "priority_score": 9,
            "opportunity_summary": "Near-perfect rating with 276 reviews, but the 2016 website has no HTTPS and falls apart on mobile — patients are losing trust before they book.",
            "pain_points": ["'Not Secure' warning in Chrome is killing trust", "Can't fill out patient forms on mobile", "No online appointment booking"],
            "recommended_features": ["Secure HTTPS site", "Mobile-friendly patient portal feel", "Online appointment request", "Insurance accepted list", "Before/after smile gallery"],
            "message": "Dr. Chen — your 4.8-star rating with 276 patients is remarkable. But your website has no HTTPS (Chrome shows a 'Not Secure' warning) and isn't mobile-friendly, which means new patients are bouncing before they call. I'd love to show you a modern, secure redesign — free mockup first, $400 all-in, ready in 48 hours. Worth 5 minutes?",
        },
        "video": {"provider": "demo", "status": "script_only", "script": "4.8 stars. 276 patients. But a website from 2016 with no HTTPS is turning new patients away before they even call. Dr. Sarah Chen deserves better. $400, 48 hours."},
        "check": {
            "total_score": 89,
            "breakdown": {"personalization": 23, "value_proposition": 22, "tone": 22, "cta": 22},
            "issues": [],
            "approved": True,
        },
    },
    {
        "id": "e5f6g7h8",
        "business": {
            "name": "FitLife Gym",
            "type": "gym",
            "city": "San Antonio, TX",
            "address": "8820 Wurzbach Rd, San Antonio, TX 78240",
            "phone": "+1-210-555-0167",
            "website": None,
            "rating": 4.4,
            "reviews": 198,
            "place_id": "demo_005",
            "hours": "Mon-Fri 5am–11pm; Sat-Sun 7am–9pm",
            "categories": ["gym", "health", "fitness_center"],
        },
        "website_check": {"has_website": False, "is_outdated": True, "oldness_score": 100, "issues": ["No website"]},
        "diagnosis": {
            "priority_score": 8,
            "opportunity_summary": "Strong gym with 198 reviews and no website — missing out on the wave of post-pandemic fitness seekers who research online before committing.",
            "pain_points": ["Can't showcase membership plans online", "No way to promote class schedules or trainers", "Losing sign-ups to chain gyms with slick websites"],
            "recommended_features": ["Membership plans & pricing", "Class schedule", "Trainer profiles", "Free trial sign-up form", "Virtual gym tour section"],
            "message": "Hey FitLife! 198 reviews and a 4.4 rating tells me your members love you. But with no website, anyone searching 'gym San Antonio' won't find you — they'll sign up at Planet Fitness instead. I build gym sites that convert browsers into members — free mockup, $400, delivered in 48 hours. Want to see what yours could look like?",
        },
        "video": {"provider": "demo", "status": "script_only", "script": "198 members love FitLife Gym. But there's no website, so new members never find them. We build gym sites that drive sign-ups. $400 flat, 48-hour delivery."},
        "check": {
            "total_score": 85,
            "breakdown": {"personalization": 22, "value_proposition": 21, "tone": 21, "cta": 21},
            "issues": [],
            "approved": True,
        },
    },
    {
        "id": "f6g7h8i9",
        "business": {
            "name": "Green Leaf Landscaping",
            "type": "cleaning_service",
            "city": "San Diego, CA",
            "address": "4455 Convoy St, San Diego, CA 92111",
            "phone": "+1-619-555-0138",
            "website": None,
            "rating": 4.5,
            "reviews": 94,
            "place_id": "demo_006",
            "hours": "Mon-Sat 7am–6pm",
            "categories": ["landscaping", "lawn_care"],
        },
        "website_check": {"has_website": False, "is_outdated": True, "oldness_score": 100, "issues": ["No website"]},
        "diagnosis": {
            "priority_score": 7,
            "opportunity_summary": "Reliable landscaping company with 94 solid reviews — no website means they rely entirely on word-of-mouth and are capped on growth.",
            "pain_points": ["Can't show portfolio of past work online", "No way to get instant quote requests", "Invisible to homeowners searching for landscapers"],
            "recommended_features": ["Before/after project gallery", "Service area map", "Instant quote request form", "Seasonal offers section", "Testimonials wall"],
            "message": "Hi! Green Leaf has 94 great reviews — it's clear you do quality work. But without a website, homeowners searching for landscapers in San Diego can't find you at all. I'd love to build you a site with a photo gallery of your best work and a quote request form — free mockup, $400, ready in 48 hours. Interested?",
        },
        "video": {"provider": "demo", "status": "script_only", "script": "94 five-star reviews. Green Leaf Landscaping does beautiful work — but no website means San Diego homeowners never find them. We change that. $400, 48 hours."},
        "check": {
            "total_score": 82,
            "breakdown": {"personalization": 21, "value_proposition": 21, "tone": 20, "cta": 20},
            "issues": [],
            "approved": True,
        },
    },
]


def seed():
    # Clear existing demo data
    for stage in ["leads", "diagnosed", "built", "filmed", "checked"]:
        for lead in state.list_all(stage):
            if lead.get("id", "").startswith(("a1b2", "b2c3", "c3d4", "d4e5", "e5f6", "f6g7")):
                state.delete(stage, lead["id"])

    # Seed into checked (ready for owner approval)
    for lead in LEADS:
        state.save("checked", lead)
        print(f"  ✓ Seeded: {lead['business']['name']} [{lead['id']}]")

    print(f"\n{len(LEADS)} demo leads ready in state/checked/")
    print("\nNext steps:")
    print("  Mobile UI:   python -m agents.mobile.app  → open http://localhost:5001")
    print("  CLI review:  python approve.py")
    print("  Build pages: python build_demo_pages.py   (generates real HTML)")


if __name__ == "__main__":
    print("Seeding demo data…\n")
    seed()
