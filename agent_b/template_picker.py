import json

# Map business type to Framer reference templates
# Add your own Framer links here as you collect them
TEMPLATES = {
    "real estate": [
        {
            "name": "Vertical Editorial",
            "url": "https://vertical.framer.media/",
            "style": "Bold, black & white, editorial, premium",
            "best_for": "Luxury real estate, high-end agencies"
        },
        {
            "name": "Modern Property",
            "url": "https://realestate.framer.website/",
            "style": "Clean, minimal, property listings focused",
            "best_for": "Mid-range agencies, residential"
        },
        {
            "name": "Agency Bold",
            "url": "https://agency.framer.media/",
            "style": "Bold typography, strong CTA, trust-focused",
            "best_for": "Commercial real estate, corporate"
        },
        {
            "name": "Property Showcase",
            "url": "https://property.framer.media/",
            "style": "Image-heavy, gallery style, warm tones",
            "best_for": "Residential, plots, apartments"
        }
    ],
    "restaurant": [
        {
            "name": "Food Editorial",
            "url": "https://foodie.framer.media/",
            "style": "Warm, food photography focused",
            "best_for": "Restaurants, cafes, fine dining"
        }
    ],
    "retail": [
        {
            "name": "Shop Modern",
            "url": "https://shop.framer.media/",
            "style": "Clean ecommerce, product focused",
            "best_for": "Retail stores, boutiques"
        }
    ]
}

def get_templates(business_type: str) -> list:
    business_type = business_type.lower()
    for key in TEMPLATES:
        if key in business_type:
            return TEMPLATES[key]
    # Default fallback
    return TEMPLATES["real estate"]

def pick_best_template(business_name: str, city: str, rating: float) -> dict:
    templates = get_templates("real estate")

    # Pick based on rating — higher rated = premium template
    if rating >= 4.5:
        return templates[0]  # Vertical Editorial — premium
    elif rating >= 4.0:
        return templates[1]  # Modern Property
    elif rating >= 3.5:
        return templates[2]  # Agency Bold
    else:
        return templates[3]  # Property Showcase

def run(lead: dict) -> dict:
    template = pick_best_template(
        lead.get("name", ""),
        lead.get("city", ""),
        lead.get("rating", 0)
    )
    print(f"[Agent B] {lead['name']} → Template: {template['name']}")
    return {
        "lead": lead,
        "template": template
    }

if __name__ == "__main__":
    # Test
    test_lead = {
        "name": "Sharma Real Estate",
        "city": "Mumbai",
        "rating": 4.6
    }
    result = run(test_lead)
    print(json.dumps(result, indent=2))
